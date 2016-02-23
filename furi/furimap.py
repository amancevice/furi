""" fURI Mappings. """

import collections
import json
import logging
import os
import yaml
from urlparse import urlparse
import boto3
from . import utils


class DynamoMap(collections.Iterable):
    """ DynamoDB-backed mappings. """
    def __init__(self, uri, **connectkw):
        self.uri = urlparse(uri)
        self.connection = boto3.resource('dynamodb', **connectkw)
        self.table = self.connection.Table(self.uri.netloc)

    def __str__(self):
        return self.uri.geturl()

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


class FileMap(collections.Mapping):
    """ Base configuration for file objects. """
    __dispatch__ = {
        '.json' : json.loads,
        '.yaml' : yaml.load,
        '.yml'  : yaml.load}

    def __init__(self, uri, **kwargs):
        self.source = utils.open(uri, **kwargs)

    def __str__(self):
        return str(self.source)

    def __getitem__(self, key):
        try:
            return self.__read()[key]
        except Exception as err:
            raise KeyError(err.message)

    def __iter__(self):
        try:
            return iter(self.__read())
        except Exception as err:
            raise StopIteration(err.message)

    def __len__(self):
        try:
            return len(self.__read())
        except Exception as err:
            raise ValueError(err.message)

    def __read(self):
        """ Read contents and parse from __dispatch__. """
        ext = os.path.splitext(str(self))[-1]
        func = self.__dispatch__.get(ext, lambda x: x)
        return func(self.source.read())


class ChainedMap(collections.Mapping):
    """ Chained AWS or locally backed mappings. """
    def __init__(self, *mappings):
        self.mappings = mappings

    def __getitem__(self, key):
        return self.__read('__getitem__', key)

    def __iter__(self):
        return self.__read('__iter__')

    def __len__(self):
        return self.__read('__len__')

    def __read(self, func, *args, **kwargs):
        """ Try to access mappings in chain, return the first success.

            Arguments:
                func   (str):    Name of self-function to run against each cfg
                args   (tuple):  Tuple of arguments to func
                kwargs (dict):   Dictionary of arguments to func

            Returns:
                The return value of 'func(*args, **kwargs)' for the first
                cfg that does not throw an Exception. """
        for cfg in self.mappings:
            try:
                return getattr(cfg, func)(*args, **kwargs)
            except (KeyError, ValueError, StopIteration) as err:
                logging.warn("%s :: %r", cfg, err)
        raise err


def chain(*mappings):
    """ Chain mappings together. """
    return ChainedMap(*mappings)


def map(uri, **kwargs):
    """ Return a Mapping object from a URI. """
    uri = urlparse(os.path.expanduser(uri))
    try:
        return _DISPATCHER[uri.scheme](uri.geturl(), **kwargs)
    except KeyError:
        raise ValueError("Unsupported URI scheme: '%s'" % uri.scheme)


_DISPATCHER = {
    ''         : FileMap,
    'file'     : FileMap,
    's3'       : FileMap,
    'dynamodb' : DynamoMap }