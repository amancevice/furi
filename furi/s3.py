""" S3 File objects. """


import boto
import os
import re
from . import base


__all__ = ['S3File']


class S3File(base.RemoteFile):
    """ S3-backed file implementation.

        Ex. s3://bucket/path/to/key """

    @property
    def bucket(self):
        """ Remote bucket. """
        try:
            return self._bucket
        except AttributeError:
            self._bucket = self.connection.get_bucket(self.uri.netloc)
            return self._bucket

    @property
    def key(self):
        """ Remote key. """
        try:
            return self._key
        except AttributeError:
            self._key = self.bucket.get_key(self.uri.path)
            return self._key

    def connect(self, **connectkw):
        """ Connect to remote. Uses environmental configuration by default, unless
            access/secret are supplied

            Arguments:
                access_key (str):  AWS access key
                secret_key (str):  AWS secret key

            Returns:
                Boto connection object. """
        if connectkw:
            self.__connect__ = connectkw
        access_key  = self.__connect__.get('access_key')
        secret_key  = self.__connect__.get('secret_key')
        self._connection = boto.connect_s3(access_key, secret_key, **self.__connect__)
        return self._connection

    def download(self, target):
        """ Download remote file to local target URI. """
        self.key.get_contents_to_filename(str(target))
        return target

    def exists(self):
        """ Test file existence. """
        return self.key is not None

    def write(self, stream):
        """ Write stream to file. """
        if not self.exists():
            self._key = self.bucket.new_key(self.uri.path)
        try:
            return self.key.set_contents_from_string(stream)
        except AttributeError:
            return self.key.set_contents_from_string(stream.read())

    def _stream_impl(self):
        """ Implementation of stream(). """
        return self.key

    def _walk_impl(self, **kwargs):
        """ Implementation of walk(). """
        root = str(re.sub('^/', '', self.uri.path))
        tree = { root : { 'dirnames' : set(), 'filenames' : set() } }
        for key in self.bucket.list(root):
            rel, filename = map(str, os.path.split(re.split("^%s" % root, key.name)[-1]))
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
