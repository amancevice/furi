""" fURI utilities """


import json
import os
from urlparse import urlparse
import yaml
from . import furifile
from . import exceptions


def add_handler(scheme, cls):
    """ Add a new class to the dispatcher

        Arguments:
            scheme (str):    URI scheme prefix
            cls    (class):  Reference to class that extends furi.base """
    __dispatch__[scheme] = cls


def add_mapper(scheme, cls):
    """ Add a new class to the dispatcher

        Arguments:
            scheme (str):    URI scheme prefix
            cls    (class):  Reference to class that extends furi.base """
    __mapdispatch__[scheme] = cls


def add_mapext(ext, func):
    """ Add an extension handler for FileMap.

        Arguments:
            ext  (str):   File extension
            func (func):  Function to parse FileMap """
    __extdispatch__[ext] = func


def exists(uri, **kwargs):
    """ Returns True if URI exists. """
    with open(uri, **kwargs) as exister:
        return exister.exists()


def map(uri, **kwargs): # pylint: disable=redefined-builtin
    """ Return a Mapping object from a URI. """
    uri = urlparse(os.path.expanduser(uri))
    try:
        return __mapdispatch__[uri.scheme](uri.geturl(), **kwargs)
    except KeyError:
        raise exceptions.SchemeError("Unsupported URI scheme: '%s'" % uri.scheme)


def open(uri, **kwargs): # pylint: disable=redefined-builtin
    """ Returns a File object given a URI. """
    uri = urlparse(os.path.expanduser(uri))
    try:
        return __dispatch__[uri.scheme](uri.geturl(), **kwargs)
    except KeyError:
        raise exceptions.SchemeError("Unsupported URI scheme: '%s'" % uri.scheme)


def walk(uri, **kwargs):
    """ Walk a Directory given a URI. """
    with open(uri, **kwargs) as walker:
        return walker.walk()


def download(source, target=None, **credentials):
    """ Download contents of a source URI into a target URI. If target URI is omitted,
        source is downloaded to ~/Downloads using the same filename.

        Arguments:
            source      (str):   URI of source file
            target      (str):   URI of target file (optional)
            credentials (dict):  Optional source connection credentials

        Returns:
            Handle to target file """
    src = open(source)
    src.connect(**credentials)
    tgt = open(target or os.path.expanduser("~/Downloads/%s" % src.filename), mode='rw')

    if not isinstance(src, furifile.RemoteFile):
        raise exceptions.DownloadError("Cannot download from non-RemoteFile.")
    if isinstance(tgt, furifile.RemoteFile):
        raise exceptions.DownloadError(
            "Cannot download RemoteFile to other RemoteFile. Use local URI.")

    return src.download(tgt)


__dispatch__ = {
    '': furifile.File,
    'file': furifile.File
}


__mapdispatch__ = {}


__extdispatch__ = {
    '.json' : json.loads,
    '.yaml' : yaml.load,
    '.yml'  : yaml.load
}
