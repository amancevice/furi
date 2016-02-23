""" fURI File access through URIs. """


__author__  = "amancevice"
__email__   = "smallweirdnum@gmail.com"
__version__ = "0.5.0"


from .furifile import File
from .furifile import RemoteFile
from .furifile import S3File
from .furifile import SftpFile
from .furimap import chain
from .furimap import map
from .utils import download
from .utils import exists
from .utils import open
from .utils import walk
