""" fURI Exceptions """


class DownloadError(TypeError): pass


class ExtensionError(KeyError): pass


class FileNotFoundError(ValueError): pass


class ModeError(ValueError): pass


class SchemeError(KeyError): pass