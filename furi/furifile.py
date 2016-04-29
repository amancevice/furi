""" fURI Files. """

import collections
import os
import re
from urlparse import urlparse
from . import exceptions


class File(collections.Iterable):
    """ Local File implementation.

        Exs. file:///abs/path/to/file.ext
             /abs/path/to/file.ext """

    __modes__ = {'r', 'rb', 'r+', 'rb+', 'w', 'wb', 'w+', 'wb+', 'a', 'ab', 'a+', 'ab+'}

    def __init__(self, uri, mode='r'):
        if mode not in self.__modes__ and not set(mode).issubset(self.__modes__):
            raise exceptions.ModeError(
                "Cannot open %s in %s-mode" % (type(self).__name__, mode))
        self.uri = urlparse(uri)
        self.path = self.uri.path
        self.mode = mode
        self.workdir, self.filename = os.path.split(self.path)
        self.__stream__ = None

    def __str__(self):
        return self.uri.geturl()

    def __repr__(self):
        return "<%s: %s>" % (type(self).__name__, str(self))

    def __iter__(self):
        return iter(self.stream())

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        """ Close stream. """
        return self._close()

    def exists(self):
        """ Test file existence. """
        return self._exists()

    def matches(self, pattern):
        """ Filename matches pattern.

            Arguments:
                pattern (regex or str):  Regular Expression to match.

            Returns:
                RegEx match object. """
        return re.compile(pattern).match(self.filename)

    def read(self, *size):
        """ Read file stream. """
        return self._read(*size)

    def stream(self):
        """ Get file contents as stream. """
        if self.__stream__ is not None and hasattr(self.__stream__, 'seek'):
            self.__stream__.seek(0)
        else:
            if not self.exists() and 'w' not in self.mode:
                raise exceptions.FileNotFoundError("%s does not exist" % self.uri.geturl())
            self.__stream__ = self._stream()
        return self.__stream__

    def walk(self, **kwargs):
        """ Walk the contents of a directory. """
        return self._walk(**kwargs)

    def write(self, stream):
        """ Write stream. """
        self._write(stream)

    def _close(self):
        """ Close stream implementation. """
        try:
            self.__stream__.close()
        except:  # pylint: disable=bare-except
            pass
        finally:
            self.__stream__ = None

    def _exists(self):
        """ Test file existence implementation. """
        return os.path.exists(self.path)

    def _read(self, *size):
        """ Read file stream implementation. """
        return self.stream().read(*size)

    def _stream(self):
        """ Implementation of stream(). """
        return open(self.path, self.mode)

    def _walk(self, **kwargs):
        """ Implementation of walk(). """
        return os.walk(self.path, **kwargs)

    def _write(self, stream):
        """ Write stream implementation. """
        if not os.path.exists(self.workdir) and ('w' in self.mode or 'a' in self.mode):
            os.makedirs(self.workdir)
        try:
            return self.stream().write(stream.read())
        except AttributeError:
            return self.stream().write(stream)


class RemoteFile(File):
    """ Remote file implementation. """
    def __init__(self, uri, mode='r', **connectkw):
        super(RemoteFile, self).__init__(uri, mode=mode)
        self.__connect__ = connectkw
        self.__connection__ = None

    @property
    def connection(self):
        """ Remote connection. """
        if self.__connection__ is None:
            self.connect()
        return self.__connection__

    def connect(self, **connectkw):
        """ Connect to remote. """
        if any(connectkw):
            self.__connect__ = connectkw
        self.__connection__ = self._connect()

    def download(self, target):
        """ Download remote file to local target URI. """
        return self._download(target)

    def _connect(self):
        """ Connect to remote implementation. """
        raise NotImplementedError

    def _download(self, target):
        """ Download remote file to local target URI implementation. """
        raise NotImplementedError

    def _exists(self):
        """ Test file existence. """
        raise NotImplementedError

    def _write(self, stream):
        """ Write stream to file. """
        raise NotImplementedError

    def _walk(self, **kwargs):
        """ Implementation of walk(). """
        raise NotImplementedError

    def _stream(self):
        """ Implementation of stream(). """
        raise NotImplementedError
