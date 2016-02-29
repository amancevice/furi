""" SFTP backed File implementation. """

import io
import os
import re
import tempfile
import pysftp
from . import furifile
from . import utils


class SftpFile(furifile.RemoteFile):
    """ File on SFTP server.

        Ex. sftp://user:pass@host/path/to/file.ext """

    def connect(self, **connectkw):
        """ Connect to remote. Credentials can be passed as part of URI. """
        if connectkw:
            self.__connect__ = connectkw

        # Get user, pswd, and host from URI
        match = re.match('^((?P<user>.*?)(:(?P<pswd>.*))?@)?(?P<host>.*?):?(?P<port>\d+)?$', self.uri.netloc)
        user  = match.group('user')
        pswd  = match.group('pswd')
        host  = match.group('host')
        port  = int(match.group('port') or '22')

        self.__connect__.setdefault('username', user)
        self.__connect__.setdefault('password', pswd)
        self.__connect__.setdefault('port', port)

        self._connection = pysftp.Connection(host, **self.__connect__)
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

    def _walk_impl(self):
        """ Implementation of walk(). """
        def __walk_impl(dirpath):
            """ Iterator for _walk_impl(). """
            wtcb = pysftp.WTCallbacks()
            self.connection.walktree(
                dirpath, wtcb.file_cb, wtcb.dir_cb, wtcb.unk_cb, recurse=False)
            yield dirpath, wtcb.dlist, map(lambda x: os.path.split(x)[-1], wtcb.flist)
            for dirname in wtcb.dlist:
                for dirpath, dirnames, filenames in __walk_impl(dirname):
                    yield dirpath, dirnames, filenames
        return __walk_impl(".%s" % self.path)


utils.add_handler('sftp', SftpFile, 'file')
