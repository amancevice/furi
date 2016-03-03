""" fURI Files. """

import collections
import os
import re
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
        self.close()

    def close(self):
        """ Close stream. """
        if self.exists():
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
        if not self.exists() and ('w' in self.mode or 'a' in self.mode):
            os.makedirs(self.workdir)
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
