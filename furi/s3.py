""" S3 File objects. """

import os
import re
import boto3
import botocore
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
            self._bucket = self.connection.Bucket(self.uri.netloc)
            return self._bucket

    @property
    def key(self):
        """ Remote key. """
        try:
            return self._key
        except AttributeError:
            self._key = self.connection.Object(self.uri.netloc, self.uri.path)
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
