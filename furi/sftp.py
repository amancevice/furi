""" SFTP File objects. """


import io
import pysftp
import re
import tempfile
import urlparse
from . import base


class SftpFile(base.RemoteFile):
    """ File on SFTP server.

        Ex. sftp://user:pass@host/path/to/file.ext """

    def __init__(self, uri, mode='r', private_key=None):
        super(SftpFile, self).__init__(uri, mode)
        self.private_key = private_key

    def connect(self, **kwargs):
        """ Connect to remote. Uses credentials passed as part of URI. """

        # Get user, pswd, and host from URI
        match = re.match('^((?P<user>.*?)(:(?P<pswd>.*))?@)?(?P<host>.*)$', self.uri.netloc)
        user  = match.group('user')
        pswd  = match.group('pswd')
        host  = match.group('host')

        kwargs.setdefault('username', user)
        kwargs.setdefault('password', pswd)
        kwargs.setdefault('private_key', self.private_key)

        sftp = pysftp.Connection(host, **kwargs)
        sftp.chdir(self.workdir)
        self._connection = sftp
        return self._connection

    def download(self, target):
        """ Download remote file to local target URI. """
        self.connection.get(self.filename, str(target))
        return target

    def exists(self):
        """ Test file existence. """
        return self.connection.exists(self.path)

    def write(self, stream):
        """ Write stream to file. """
        raise NotImplementedError

    def _stream_impl(self):
        """ Implementation of stream(). """
        with tempfile.NamedTemporaryFile() as tmp:
            self.connection.get(self.filename, tmp.name)
            tmp.flush()
            return io.StringIO(unicode(tmp.read()))
