""" fURI utilities """


import os
from urlparse import urlparse
from .furifile import File
from .furifile import RemoteFile
from .furifile import S3File
from .furifile import SftpFile


def add_handler(scheme, handler_class):
    """ Add a new class to the dispatcher

        Arguments:
            scheme        (str):    URI scheme prefix
            handler_class (class):  Reference to class that extends furi.base """
    _DISPATCHER[scheme] = handler_class


def exists(uri, **kwargs):
    """ Returns True if URI exists. """
    with open(uri, **kwargs) as exister:
        return exister.exists()


def open(uri, **kwargs):
    """ Returns a File object given a URI. """
    uri = urlparse(os.path.expanduser(uri))
    try:
        return _DISPATCHER[uri.scheme](uri.geturl(), **kwargs)
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

    if not isinstance(src, RemoteFile):
        raise TypeError("Cannot download from non-RemoteFile.")
    if isinstance(tgt, RemoteFile):
        raise TypeError("Cannot download RemoteFile to other RemoteFile. Use local URI.")

    return src.download(tgt)


_DISPATCHER = {
    ''     : File,
    'file' : File,
    's3'   : S3File,
    'sftp' : SftpFile }
