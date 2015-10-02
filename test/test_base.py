import furi
import re
import tempfile
from nose.tools import assert_equal


def test_matches():
    pattern = re.compile('[A-Z][a-z]+\.[Yy][Aa]?[Mm][Ll]')
    furifile = furi.open('/abs/path/to/Hello.yml')
    assert furifile.matches(pattern)


def test_not_matches():
    pattern = re.compile('[A-Z][a-z]+\.[Yy][Aa]?[Mm][Ll]')
    furifile = furi.open('/abs/path/to/Hello.txt')
    assert not furifile.matches(pattern)


def test_exists():
    furifile = furi.open(__file__)
    assert furifile.exists()


def test_not_exists():
    furifile = furi.open('/foo/bar/fizz/buzz')
    assert not furifile.exists()


def test_read():
    with open(__file__, 'r') as this:
        furifile = furi.open(__file__)
        returned = furifile.read()
        expected = this.read()
        assert_equal(returned, expected)


def test_stream_resets():
    with open(__file__, 'r') as this:
        furifile = furi.open(__file__)
        stream = furifile.stream()
        stream.read()
        returned = furifile.read()
        expected = this.read()
        assert_equal(returned, expected)


def test_write():
    value = "Hello, world!\n\nGoodby, cruel world."
    with tempfile.NamedTemporaryFile() as tmp:
        furifile = furi.open(tmp.name, mode='w+')
        furifile.write(value)
        furifile.stream().seek(0)
        assert_equal(furifile.read(), value)
