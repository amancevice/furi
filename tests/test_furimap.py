""" fURI Map Tests. """
import json
import tempfile
try:
    from unittest import mock
except ImportError:
    import mock

import pytest

import furi


def test_repr():
    furimap = furi.map("/path/to/file.json")
    returned = repr(furimap)
    expected = "<FileMap: /path/to/file.json>"
    assert returned == expected


@mock.patch("furi.furimap.FileMap._read")
def test_getitem(mock_read):
    mock_read.return_value = {"fizz": "buzz"}
    furimap = furi.map("/path/to/map.json")
    returned = furimap["fizz"]
    expected = "buzz"
    assert returned == expected


@mock.patch("furi.furimap.FileMap._read")
def test_getitem_bad(mock_read):
    mock_read.return_value = {"fizz": "buzz"}
    furimap = furi.map("/path/to/map.json")
    with pytest.raises(KeyError):
        furimap["foo"]


@mock.patch("furi.furimap.FileMap._read")
def test_iter(mock_read):
    mock_read.return_value = {"fizz": "buzz"}
    furimap = furi.map("/path/to/map.json")
    returned = list(iter(furimap))
    expected = ["fizz"]
    assert returned == expected


@mock.patch("furi.furimap.FileMap._read")
def test_len(mock_read):
    mock_read.return_value = {"fizz": "buzz"}
    furimap = furi.map("/path/to/map.json")
    returned = len(furimap)
    expected = 1
    assert returned == expected


@mock.patch("furi.utils.extfunc")
def test_read(mock_ext):
    mock_ext.return_value = json.loads
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write('{"fizz": "buzz"}'.encode("utf-8"))
        tmp.flush()
        furimap = furi.map(tmp.name)
        returned = furimap._read()
        expected = {"fizz": "buzz"}
        assert returned == expected
