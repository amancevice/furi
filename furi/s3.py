""" S3 File objects. """


import boto
import io
import os
import re
from . import base


class S3File(base.RemoteFile):
    """ S3-backed file implementation.

        Ex. s3://bucket/path/to/key """

    modes = { 'r', 'r+', 'w', 'w+' }

    def __init__(self, uri, mode='r', access_key=None, secret_key=None):
        super(S3File, self).__init__(uri, mode)
        self.access_key = access_key
        self.secret_key = secret_key

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

    def connect(self, access_key=None, secret_key=None):
        """ Connect to remote. Uses environmental configuration by default, unless
            access/secret are supplied

            Arguments:
                access_key (str):  AWS access key
                secret_key (str):  AWS secret key

            Returns:
                Boto connection object. """
        self.access_key = access_key or self.access_key
        self.secret_key = secret_key or self.secret_key
        return boto.connect_s3(self.access_key, self.secret_key)

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

    def walk(self, **kwargs):
        root = str(re.sub('^/', '', self.key.name))
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

    def _stream_impl(self):
        """ Implementation of stream(). """
        return self.key
