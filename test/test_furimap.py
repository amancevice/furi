""" fURI Map Tests. """

import json
import tempfile

import furi
import mock
from nose.tools import assert_equal
from nose.tools import raises


def test_repr():
    furimap = furi.map("/path/to/file.json")
    returned = repr(furimap)
    expected = "<FileMap: /path/to/file.json>"
    assert_equal(returned, expected)


@mock.patch("furi.furimap.FileMap._read")
def test_getitem(mock_read):
    mock_read.return_value = {"fizz": "buzz"}
    furimap = furi.map("/path/to/map.json")
    returned = furimap["fizz"]
    expected = "buzz"
    assert_equal(returned, expected)


@raises(KeyError)
@mock.patch("furi.furimap.FileMap._read")
def test_getitem_bad(mock_read):
    mock_read.return_value = {"fizz": "buzz"}
    furimap = furi.map("/path/to/map.json")
    furimap["foo"]


@mock.patch("furi.furimap.FileMap._read")
def test_iter(mock_read):
    mock_read.return_value = {"fizz": "buzz"}
    furimap = furi.map("/path/to/map.json")
    returned = list(iter(furimap))
    expected = ["fizz"]
    assert_equal(returned, expected)


@mock.patch("furi.furimap.FileMap._read")
def test_len(mock_read):
    mock_read.return_value = {"fizz": "buzz"}
    furimap = furi.map("/path/to/map.json")
    returned = len(furimap)
    expected = 1
    assert_equal(returned, expected)


@mock.patch("furi.utils.extfunc")
def test_read(mock_ext):
    mock_ext.return_value = json.loads
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write('{"fizz": "buzz"}'.encode("utf-8"))
        tmp.flush()
        furimap = furi.map(tmp.name)
        returned = furimap._read()
        expected = {"fizz": "buzz"}
        assert_equal(returned, expected)


'''

def _read(self):
    """ Read contents and parse from __dispatch__. """
    ext = os.path.splitext(str(self))[-1]
    return utils.extfunc(ext)(self.source.read())


class ChainedMap(collections.Mapping):
    """ Chained AWS or locally backed mappings. """
    def __init__(self, *mappings):
        self.mappings = mappings

    def __getitem__(self, key):
        return self._read('__getitem__', key)

    def __iter__(self):
        return self._read('__iter__')

    def __len__(self):
        return self._read('__len__')

    def _read(self, func, *args, **kwargs):
        """ Try to access mappings in chain, return the first success.

            Arguments:
                func   (str):    Name of self-function to run against each cfg
                args   (tuple):  Tuple of arguments to func
                kwargs (dict):   Dictionary of arguments to func

            Returns:
                The return value of 'func(*args, **kwargs)' for the first
                cfg that does not throw an Exception. """
        for cfg in self.mappings:
            try:
                return getattr(cfg, func)(*args, **kwargs)
            except (KeyError, ValueError, StopIteration) as err:
                pass
        raise err


def chain(*mappings):
    """ Chain mappings together. """
    return ChainedMap(*mappings)
'''
