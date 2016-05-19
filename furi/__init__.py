""" fURI File access through URIs. """

from . import exceptions
from .furimap import chain
from .utils import add_handler
from .utils import add_mapper
from .utils import add_mapext
from .utils import download
from .utils import exists
from .utils import map  # pylint: disable=redefined-builtin
from .utils import open # pylint: disable=redefined-builtin
from .utils import walk
try:
    from . import aws
except ImportError:
    pass
try:
    from . import sftp
except ImportError:
    pass


__author__ = "amancevice"
__email__ = "smallweirdnum@gmail.com"
__version__ = "0.6.12"
