""" fURI File access through URIs. """


import os
import urlparse
from . import base, s3, sftp


_DISPATCHER = {
    ''     : base.File,
    'file' : base.File,
    's3'   : s3.S3File,
    'sftp' : sftp.SftpFile }


def open(uri, **kwargs):
    """ Returns a File object given a URI. """
    uri = urlparse.urlparse(os.path.expanduser(uri))
    try:
        return _DISPATCHER[uri.scheme](uri.geturl(), **kwargs)
    except KeyError:
        raise ValueError("Unsupported URI scheme: '%s'" % uri.scheme)


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

    if not isinstance(src, base.RemoteFile):
        raise TypeError("Cannot download from non-RemoteFile.")
    if isinstance(tgt, base.RemoteFile):
        raise TypeError("Cannot download RemoteFile to other RemoteFile. Use local URI.")

    return src.download(tgt)
