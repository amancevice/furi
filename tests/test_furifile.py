import os
import re
import tempfile
try:
    from unittest import mock
except ImportError:
    import mock

import pytest

import furi


def test_matches():
    pattern = re.compile(r'[A-Z][a-z]+\.[Yy][Aa]?[Mm][Ll]')
    furifile = furi.open('/abs/path/to/Hello.yml')
    assert furifile.matches(pattern)


def test_not_matches():
    pattern = re.compile(r'[A-Z][a-z]+\.[Yy][Aa]?[Mm][Ll]')
    furifile = furi.open('/abs/path/to/Hello.txt')
    assert not furifile.matches(pattern)


def test_file_exists():
    furifile = furi.open(__file__)
    assert furifile.exists()


def test_not_file_exists():
    furifile = furi.open('/foo/bar/fizz/buzz')
    assert not furifile.exists()


def test_read():
    with open(__file__, 'r') as this:
        furifile = furi.open(__file__)
        returned = furifile.read()
        expected = this.read()
        assert returned == expected


def test_stream_resets():
    with open(__file__, 'r') as this:
        furifile = furi.open(__file__)
        stream = furifile.stream()
        stream.read()
        returned = furifile.read()
        expected = this.read()
        assert returned == expected


def test_write():
    value = "Hello, world!\n\nGoodbye, cruel world."
    with tempfile.NamedTemporaryFile() as tmp:
        furifile = furi.open(tmp.name, mode='w+')
        furifile.write(value)
        furifile.stream().seek(0)
        assert furifile.read() == value


'''
@moto.mock_s3
def test_download():
    value = "Hello, world!\n\nGoodbye, cruel world."
    ms3 = boto.connect_s3()
    bkt = ms3.create_bucket('furi')
    key = boto.s3.key.Key(bkt, 'foo/bar/bizz/buzz')
    key.set_contents_from_string(value)

    with tempfile.NamedTemporaryFile() as tmp:
        furifile = furi.download('s3://furi/foo/bar/bizz/buzz', tmp.name)
        assert_equal(furifile.read(), value)


@moto.mock_s3
def test_s3_stream():
    value = "Hello, world!\n\nGoodbye, cruel world."
    ms3 = boto3.client('s3')
    bkt = ms3.create_bucket('furi')
    key = boto.s3.key.Key(bkt, 'foo/bar/bizz/buzz')
    key.set_contents_from_string(value)

    with furi.open('s3://furi/foo/bar/bizz/buzz') as tmp:
        tmp.stream()
        tmp.stream()


@moto.mock_s3
def test_s3_exists():
    value = "Hello, world!\n\nGoodbye, cruel world."
    ms3 = boto.connect_s3()
    bkt = ms3.create_bucket('furi')
    key = boto.s3.key.Key(bkt, 'foo/bar/bizz/buzz')
    key.set_contents_from_string(value)

    s3furi = furi.open('s3://furi/foo/bar/bizz/buzz')
    assert s3furi.exists()


@moto.mock_s3
def test_s3_not_exists():
    ms3 = boto.connect_s3()
    bkt = ms3.create_bucket('furi')

    s3furi = furi.open('s3://furi/foo/bar/bizz/buzz')
    assert not s3furi.exists()


@moto.mock_s3
def test_s3_read():
    ms3 = boto.connect_s3()
    bkt = ms3.create_bucket('furi')
    key = boto.s3.key.Key(bkt)
    key.name = 'foo/bar/bizz/buzz'
    value = "Hello, world!\n\nGoodbye, cruel world.".encode("utf-8")
    key.set_contents_from_string(value)

    with furi.open('s3://furi/foo/bar/bizz/buzz', mode='w') as s3furi:
        assert_equal(s3furi.read(), value)


@moto.mock_s3
def test_s3_read_stream():
    ms3 = boto.connect_s3()
    bkt = ms3.create_bucket('furi')
    key = boto.s3.key.Key(bkt)
    key.name = 'foo/bar/bizz/buzz'
    value = "Hello, world!\n\nGoodbye, cruel world.".encode("utf-8")
    key.set_contents_from_string(value)

    with furi.open('s3://furi/foo/bar/bizz/buzz', mode='w') as s3furi:
        assert_equal(s3furi.read(), value)


@moto.mock_s3
def test_s3_walk():
    value = "Hello, world!\n\nGoodbye, cruel world."
    ms3 = boto.connect_s3()
    bkt = ms3.create_bucket('furi')

    keys = ['foo/baq/bug', 'foo/bar/bizz/buzz', 'foo/bar/bizz/fizz', 'foo/ban']
    for keyname in keys:
        key = boto.s3.key.Key(bkt)
        key.name = keyname
        key.set_contents_from_string(value)

    returned = list(furi.walk('s3://furi/foo/'))
    expected = [
        ('s3://furi/foo/', ['baq', 'bar'], ['ban']),
        ('s3://furi/foo/baq/', [], ['bug']),
        ('s3://furi/foo/bar/', ['bizz'], []),
        ('s3://furi/foo/bar/bizz/', [], ['buzz', 'fizz'])]
    assert returned == expected
'''


def test_walk():
    with tempfile.NamedTemporaryFile() as tmp:
        path = os.path.split(tmp.name)[0]
        os.chdir(path)
        keys = [
            'foo/baq/bug', 'foo/bar/bizz/buzz', 'foo/bar/bizz/fizz', 'foo/ban']
        for keyname in keys:
            fpath, fname = os.path.split(keyname)
            if not os.path.exists(fpath):
                os.makedirs(fpath)
            with open(keyname, 'w') as tmpf:
                tmpf.write("Hello, world!\n\nGoodbye, cruel world.")

        returned = list(furi.walk('foo'))
        expected = [
            ('foo', ['baq', 'bar'], ['ban']),
            ('foo/baq', [], ['bug']),
            ('foo/bar', ['bizz'], []),
            ('foo/bar/bizz', [], ['buzz', 'fizz'])]
        assert returned == expected


def test_bad_mode():
    with pytest.raises(furi.exceptions.ModeError):
        furi.open("foo.txt", mode="j")


def test_repr():
    furifile = furi.open("/path/to/file")
    returned = repr(furifile)
    expected = "<File: /path/to/file>"
    assert returned == expected


def test_iter():
    lines = [
        "This is line 1\n",
        "This is line 2\n"]
    with tempfile.NamedTemporaryFile() as tmp:
        for line in lines:
            tmp.write(line.encode("utf8"))
        tmp.flush()
        furifile = furi.open(tmp.name)
        returned = list(iter(furifile))
    assert returned == lines


def test_cant_stream():
    with pytest.raises(furi.exceptions.FuriFileNotFoundError):
        furi.open("/path/to/file").stream()


@mock.patch("furi.furifile.RemoteFile._connect")
def test_connectkw(mock_connect):
    expected = dict(connect_kw1="fizz", connect_kw2="buzz")
    furifile = furi.furifile.RemoteFile("s3://bucket/path/to/file")
    furifile.connect(**expected)
    returned = furifile.__connect__
    assert returned == expected


def test__connect():
    with pytest.raises(NotImplementedError):
        furi.furifile.RemoteFile("s3://bucket/path/to/file")._connect()


def test__download():
    with pytest.raises(NotImplementedError):
        furi.furifile.RemoteFile("s3://bucket/path/to/file")._download(None)


def test__exists():
    with pytest.raises(NotImplementedError):
        furi.furifile.RemoteFile("s3://bucket/path/to/file")._exists()


def test__write():
    with pytest.raises(NotImplementedError):
        furi.furifile.RemoteFile("s3://bucket/path/to/file")._write(None)


def test__walk():
    with pytest.raises(NotImplementedError):
        furi.furifile.RemoteFile("s3://bucket/path/to/file")._walk()


def test__stream():
    with pytest.raises(NotImplementedError):
        furi.furifile.RemoteFile("s3://bucket/path/to/file")._stream()
