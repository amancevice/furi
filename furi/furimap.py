""" fURI Mappings. """

import collections
import logging
import os
from . import exceptions
from . import utils


class FileMap(collections.Mapping):
    """ Base configuration for file objects. """

    def __init__(self, uri, **kwargs):
        self.source = utils.open(uri, **kwargs)

    def __str__(self):
        return str(self.source)

    def __repr__(self):
        return "<%sMap: %s>" % (type(self.source).__name__, self.source)

    def __getitem__(self, key):
        try:
            return self._read()[key]
        except Exception as err:
            raise KeyError(err.message)

    def __iter__(self):
        try:
            return iter(self._read())
        except Exception as err:
            raise StopIteration(err.message)

    def __len__(self):
        try:
            return len(self._read())
        except Exception as err:
            raise ValueError(err.message)

    def _read(self):
        """ Read contents and parse from __dispatch__. """
        ext = os.path.splitext(str(self))[-1]
        try:
            func = utils.__extdispatch__[ext]
        except KeyError:
            raise exceptions.ExtensionError("Unsupported file extension: '%s'" % ext)
        return func(self.source.read())


class ChainedMap(collections.Mapping):
    """ Chained AWS or locally backed mappings. """
    def __init__(self, *mappings):
        self.mappings = mappings

    def __getitem__(self, key):
        return self._read('__getitem__', key)

    def __iter__(self):
        return self._read('__iter__')

    def __len__(self):
        return self._read('__len__')

    def _read(self, func, *args, **kwargs):
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


utils.add_mapper('', FileMap)
utils.add_mapper('file', FileMap)
utils.add_mapper('s3', FileMap)
