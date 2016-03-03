""" fURI File access through URIs. """


__author__  = "amancevice"
__email__   = "smallweirdnum@gmail.com"
__version__ = "0.6.5"


from .furimap import chain
from .utils import add_handler
from .utils import download
from .utils import exists
from .utils import map
from .utils import open
from .utils import walk

try:
    from . import aws
except ImportError:
    pass

try:
    from . import sftp
except ImportError:
    pass
