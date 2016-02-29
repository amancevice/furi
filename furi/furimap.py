""" fURI Mappings. """

import collections
import json
import logging
import os
import yaml
from . import utils


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

    def __repr__(self):
        return "<%sMap: %s>" % (type(self.source).__name__, self.source)

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


utils.add_handler('' , FileMap, 'map')
utils.add_handler('file', FileMap, 'map')
utils.add_handler('s3', FileMap, 'map')
