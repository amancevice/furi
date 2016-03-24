""" fURI Exceptions """


class DownloadError(TypeError):
    """ Error downloading object. """
    pass


class ExtensionError(KeyError):
    """ Error mapping file from extension. """
    pass


class FileNotFoundError(ValueError):
    """ File does not exist. """
    pass


class ModeError(ValueError):
    """ File cannot be opened in given mode. """
    pass


class SchemeError(KeyError):
    """ Error finding class to open fURI. """
    pass
