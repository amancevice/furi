""" SFTP File objects. """


import io
import pysftp
import re
import tempfile
from . import base


class SftpFile(base.RemoteFile):
    """ File on SFTP server.

        Ex. sftp://user:pass@host/path/to/file.ext """

    def connect(self):
        """ Connect to remote. Uses credentials passed as part of URI. """
        try:
            user, pswd, host = re.match('^(.*?):(.*)@(.*)$', self.uri.netloc).groups()
        except (ValueError, AttributeError):
            user = pswd = None
            host = self.uri.netloc
        sftp = pysftp.Connection(host, username=user, password=pswd)
        sftp.chdir(self.workdir)
        return sftp

    def download(self, target):
        """ Download remote file to local target URI. """
        raise NotImplementedError

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
