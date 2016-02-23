""" fURI Files. """

import collections
import io
import os
import re
import tempfile
import boto3
import botocore
import pysftp
from urlparse import urlparse


MODES = 'r', 'rb', 'r+', 'rb+', 'w', 'wb', 'w+', 'wb+', 'a', 'ab', 'a+', 'ab+'


class File(collections.Iterable):
    """ Local File implentation.

        Exs. file:///abs/path/to/file.ext
             /abs/path/to/file.ext """

    modes = set(MODES)

    def __init__(self, uri, mode='r'):
        if mode not in self.modes and not set(mode).issubset(self.modes):
            raise ValueError("Cannot open %s in %s-mode" % (type(self).__name__, mode))
        self.uri  = urlparse(uri)
        self.path = self.uri.path
        self.mode = mode
        self.workdir, self.filename = os.path.split(self.path)

    def __str__(self):
        return self.uri.geturl()

    def __repr__(self):
        return "<%s: %s>" % (type(self).__name__, str(self))

    def __iter__(self):
        return self.stream()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def close(self):
        """ Close stream. """
        return self.stream().close()

    def matches(self, pattern):
        """ Filename matches pattern.

            Arguments:
                pattern (regex or str):  Regular Expression to match.

            Returns:
                RegEx match object. """
        return re.compile(pattern).match(self.filename)

    def exists(self):
        """ Test file existence. """
        return os.path.exists(self.path)

    def read(self, *size):
        """ Read file stream. """
        return self.stream().read(*size)

    def write(self, stream):
        """ Write stream to file. """
        try:
            return self.stream().write(stream)
        except TypeError:
            return self.stream().write(stream.read())

    def stream(self):
        """ Get file contents as stream. """
        try:
            self._stream.seek(0)
            return self._stream
        except AttributeError:
            if not self.exists() and 'w' not in self.mode:
                raise ValueError("%s does not exist" % self.uri.geturl())
            self._stream = self._stream_impl()
            return self._stream

    def walk(self, **kwargs):
        """ Walk the contents of a directory. """
        return self._walk_impl(**kwargs)

    def _walk_impl(self, **kwargs):
        """ Implementation of walk(). """
        return os.walk(self.path, **kwargs)

    def _stream_impl(self):
        """ Implementation of stream(). """
        return open(self.path, self.mode)


class RemoteFile(File):
    """ Remote file implentation. """

    def __init__(self, uri, mode='r', **connectkw):
        super(RemoteFile, self).__init__(uri, mode=mode)
        self.__connect__ = connectkw

    @property
    def connection(self):
        """ Remote connection. """
        try:
            return self._connection
        except AttributeError:
            self._connection = self.connect()
            return self._connection

    def connect(self, **kwargs):
        """ Connect to remote. """
        raise NotImplementedError

    def download(self, target):
        """ Download remote file to local target URI. """
        raise NotImplementedError

    def exists(self):
        """ Test file existence. """
        raise NotImplementedError

    def write(self, stream):
        """ Write stream to file. """
        raise NotImplementedError

    def _walk_impl(self, **kwargs):
        """ Implementation of walk(). """
        raise NotImplementedError

    def _stream_impl(self):
        """ Implementation of stream(). """
        raise NotImplementedError


class S3File(RemoteFile):
    """ S3-backed file implementation.

        Ex. s3://bucket/path/to/key """

    @property
    def bucket(self):
        """ Remote bucket. """
        try:
            return self._bucket
        except AttributeError:
            self._bucket = self.connection.Bucket(self.uri.netloc)
            return self._bucket

    @property
    def key(self):
        """ Remote key. """
        try:
            return self._key
        except AttributeError:
            self._key = self.connection.Object(
                self.uri.netloc, self.uri.path.lstrip('/'))
            return self._key

    def connect(self, **connectkw):
        if connectkw:
            self.__connect__ = connectkw
        self._connection = boto3.resource('s3', **self.__connect__)
        return self._connection

    def download(self, target):
        """ Download remote file to local target URI. """
        self.key.download_file(str(target))
        return target

    def exists(self):
        """ Test file existence. """
        try:
            self.key.load()
        except botocore.exceptions.ClientError as err:
            if err.response['Error']['Code'] == "404":
                return False
            raise err
        return True

    def write(self, stream):
        """ Write stream to file. """
        try:
            return self.key.put(Body=stream)
        except AttributeError:
            return self.key.put(Body=stream.read())

    def _stream_impl(self):
        """ Implementation of stream(). """
        return self.key.get().get('Body')

    def _walk_impl(self, **kwargs):
        """ Implementation of walk(). """
        root = str(re.sub('^/', '', self.uri.path))
        tree = { root : { 'dirnames' : set(), 'filenames' : set() } }
        for key in self.bucket.objects.all():
            rel, filename = map(str, os.path.split(re.split("^%s" % root, key.key)[-1]))
            history = root
            for subdir in rel.split('/'):
                if subdir:
                    tree[history]['dirnames'].add(subdir)
                history = os.path.normpath(os.path.join(history, subdir)) + '/'
                if history not in tree:
                    tree[history] = { 'dirnames' : set(), 'filenames' : set() }
            if filename:
                tree[history]['filenames'].add(filename)

        for dirpath in sorted(tree.keys()):
            dirdata   = tree[dirpath]
            dirnames  = sorted(dirdata['dirnames'])
            filenames = sorted(dirdata['filenames'])
            dirpath = "s3://%s/%s" % (self.bucket.name, dirpath)
            yield dirpath, dirnames, filenames



class SftpFile(RemoteFile):
    """ File on SFTP server.

        Ex. sftp://user:pass@host/path/to/file.ext """

    def connect(self, **connectkw):
        """ Connect to remote. Credentials can be passed as part of URI. """
        if connectkw:
            self.__connect__ = connectkw

        # Get user, pswd, and host from URI
        match = re.match('^((?P<user>.*?)(:(?P<pswd>.*))?@)?(?P<host>.*?):?(?P<port>\d+)?$', self.uri.netloc)
        user  = match.group('user')
        pswd  = match.group('pswd')
        host  = match.group('host')
        port  = int(match.group('port') or '22')

        self.__connect__.setdefault('username', user)
        self.__connect__.setdefault('password', pswd)
        self.__connect__.setdefault('port', port)

        self._connection = pysftp.Connection(host, **self.__connect__)
        return self._connection

    def download(self, target):
        """ Download remote file to local target URI. """
        self.connection.get(self.filename, str(target))
        return target

    def exists(self):
        """ Test file existence. """
        return self.connection.exists(self.path)

    def write(self, stream):
        """ Write stream to file. """
        raise NotImplementedError

    def _stream_impl(self):
        """ Implementation of stream(). """
        with tempfile.NamedTemporaryFile() as tmp:
            self.connection.get(self.filename, tmp.name)
            tmp.flush()
            return io.StringIO(unicode(tmp.read()))

    def _walk_impl(self):
        """ Implementation of walk(). """
        def __walk_impl(dirpath):
            """ Iterator for _walk_impl(). """
            wtcb = pysftp.WTCallbacks()
            self.connection.walktree(
                dirpath, wtcb.file_cb, wtcb.dir_cb, wtcb.unk_cb, recurse=False)
            yield dirpath, wtcb.dlist, map(lambda x: os.path.split(x)[-1], wtcb.flist)
            for dirname in wtcb.dlist:
                for dirpath, dirnames, filenames in __walk_impl(dirname):
                    yield dirpath, dirnames, filenames
        return __walk_impl(".%s" % self.path)
