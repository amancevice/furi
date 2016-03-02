""" AWS backed File and FileMap implementations. """

import collections
import os
import re
import boto3
import botocore
from urlparse import urlparse
from . import furifile
from . import utils


class S3File(furifile.RemoteFile):
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
        for key in self.bucket.objects.filter(Prefix=self.key.key):
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


class DynamoMap(collections.Iterable):
    """ DynamoDB-backed mappings. """
    def __init__(self, uri, **connectkw):
        self.uri = urlparse(uri)
        self.connection = boto3.resource('dynamodb', **connectkw)
        self.table = self.connection.Table(self.uri.netloc)

    def __str__(self):
        return self.uri.geturl()

    def __repr__(self):
        return "<%s: %s>" % (type(self).__name__, self.uri.geturl())

    def __getitem__(self, key):
        try:
            ikey = { self.table.key_schema[0]['AttributeName'] : key }
            return self.__read(self.table.get_item(Key=ikey))['Item']
        except KeyError:
            raise KeyError(key)

    def __iter__(self):
        response = self.table.scan()
        items = response.get('Items') or []
        for item in items:
            yield item
        while 'LastEvaluatedKey' in response:
            response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items = response.get('Items') or []
            for item in items:
                yield item

    def __len__(self):
        return self.table.item_count

    def __setitem__(self, key, value):
        origin = self[key].get('Item', key).items()
        update = value.items()
        return self.table.put_item(Item=dict(origin + update))

    def __delitem__(self, key):
        self.table.delete_item(Key=key)

    def __read(self, results=None):
        """ Read Dynamo result and throw ValueError on non-200 response code. """
        results = results or self.table.scan()
        response = results.get('ResponseMetadata') or {}
        httpcode = response.get('HTTPStatusCode')
        if httpcode != 200:
            raise ValueError(response)
        return results


utils.add_handler('s3', S3File, 'file')
utils.add_handler('dynamodb', DynamoMap, 'map')
