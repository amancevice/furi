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

    def _connect(self):
        """ Connect to remote. Credentials can be passed as part of URI. """
        # Get user, pswd, and host from URI
        ptn = r'^((?P<user>.*?)(:(?P<pswd>.*))?@)?(?P<host>.*?):?(?P<port>\d+)?$'
        match = re.match(ptn, self.uri.netloc)
        user = match.group('user')
        pswd = match.group('pswd')
        host = match.group('host')
        port = int(match.group('port') or '22')

        self.__connect__.setdefault('username', user)
        self.__connect__.setdefault('password', pswd)
        self.__connect__.setdefault('port', port)

        return pysftp.Connection(host, **self.__connect__)

    def _download(self, target):
        """ Download remote file to local target URI. """
        self.connection.get(self.filename, str(target))
        return target

    def _exists(self):
        """ Test file existence. """
        return self.connection.exists(self.path)

    def _write(self, stream):
        """ Write stream to file. """
        raise NotImplementedError

    def _stream(self):
        """ Implementation of stream(). """
        with tempfile.NamedTemporaryFile() as tmp:
            self.connection.get(self.path, tmp.name)
            tmp.flush()
            return io.StringIO(unicode(tmp.read()))

    def _walk(self):
        """ Implementation of walk(). """
        def __walk(dirpath):
            """ Iterator for _walk_impl(). """
            wtcb = pysftp.WTCallbacks()
            self.connection.walktree(
                dirpath, wtcb.file_cb, wtcb.dir_cb, wtcb.unk_cb, recurse=False)
            yield dirpath, wtcb.dlist, [os.path.split(x)[-1] for x in wtcb.flist]
            for dirname in wtcb.dlist:
                for dirpath, dirnames, filenames in __walk(dirname):
                    yield dirpath, dirnames, filenames
        return __walk(".%s" % self.path)


utils.add_handler('sftp', SftpFile)
