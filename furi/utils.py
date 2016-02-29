""" fURI utilities """


import os
from urlparse import urlparse
from . import furifile


def add_handler(scheme, handler_class, handler_type='file'):
    """ Add a new class to the dispatcher

        Arguments:
            scheme        (str):    URI scheme prefix
            handler_class (class):  Reference to class that extends furi.base """
    if handler_type == 'file':
        _FILE_DISPATCHER[scheme] = handler_class
    elif handler_type == 'map':
        _MAP_DISPATCHER[scheme] = handler_class


def exists(uri, **kwargs):
    """ Returns True if URI exists. """
    with open(uri, **kwargs) as exister:
        return exister.exists()


def map(uri, **kwargs):
    """ Return a Mapping object from a URI. """
    uri = urlparse(os.path.expanduser(uri))
    try:
        return _MAP_DISPATCHER[uri.scheme](uri.geturl(), **kwargs)
    except KeyError:
        raise ValueError("Unsupported URI scheme: '%s'" % uri.scheme)


def open(uri, **kwargs):
    """ Returns a File object given a URI. """
    uri = urlparse(os.path.expanduser(uri))
    try:
        return _FILE_DISPATCHER[uri.scheme](uri.geturl(), **kwargs)
    except KeyError:
        raise ValueError("Unsupported URI scheme: '%s'" % uri.scheme)


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
        raise TypeError("Cannot download from non-RemoteFile.")
    if isinstance(tgt, furifile.RemoteFile):
        raise TypeError("Cannot download RemoteFile to other RemoteFile. Use local URI.")

    return src.download(tgt)


_FILE_DISPATCHER = {
    ''     : furifile.File,
    'file' : furifile.File }


_MAP_DISPATCHER = {}
