import io
import os
import re
import tempfile

import boto
import furi
import mock
import moto
from nose.tools import assert_equal
from nose.tools import assert_is_instance
from nose.tools import raises


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


@moto.mock_s3
def test_download():
    value = "Hello, world!\n\nGoodby, cruel world."
    ms3 = boto.connect_s3()
    bkt = ms3.create_bucket('furi')
    key = boto.s3.key.Key(bkt, 'foo/bar/bizz/buzz')
    key.set_contents_from_string(value)

    with tempfile.NamedTemporaryFile() as tmp:
        furifile = furi.download('s3://furi/foo/bar/bizz/buzz', tmp.name)
        assert_equal(furifile.read(), value)


@moto.mock_s3
def test_s3_stream():
    value = "Hello, world!\n\nGoodby, cruel world."
    ms3 = boto.connect_s3()
    bkt = ms3.create_bucket('furi')
    key = boto.s3.key.Key(bkt, 'foo/bar/bizz/buzz')
    key.set_contents_from_string(value)

    with furi.open('s3://furi/foo/bar/bizz/buzz') as tmp:
        tmp.stream()
        tmp.stream()


@moto.mock_s3
def test_exists():
    value = "Hello, world!\n\nGoodby, cruel world."
    ms3 = boto.connect_s3()
    bkt = ms3.create_bucket('furi')
    key = boto.s3.key.Key(bkt, 'foo/bar/bizz/buzz')
    key.set_contents_from_string(value)

    s3furi = furi.open('s3://furi/foo/bar/bizz/buzz')
    assert s3furi.exists()


@moto.mock_s3
def test_not_exists():
    ms3 = boto.connect_s3()
    bkt = ms3.create_bucket('furi')

    s3furi = furi.open('s3://furi/foo/bar/bizz/buzz')
    assert not s3furi.exists()


@moto.mock_s3
def test_write():
    ms3 = boto.connect_s3()
    bkt = ms3.create_bucket('furi')
    key = boto.s3.key.Key(bkt)
    key.name = 'foo/bar/bizz/buzz'
    value = "Hello, world!\n\nGoodby, cruel world."
    key.set_contents_from_string(value)

    with furi.open('s3://furi/foo/bar/bizz/buzz', mode='w') as s3furi:
        yield assert_equal, s3furi.read(), value


@moto.mock_s3
def test_write_stream():
    ms3 = boto.connect_s3()
    bkt = ms3.create_bucket('furi')
    key = boto.s3.key.Key(bkt)
    key.name = 'foo/bar/bizz/buzz'
    value = "Hello, world!\n\nGoodby, cruel world."
    key.set_contents_from_stream(io.StringIO(unicode(value)))

    with furi.open('s3://furi/foo/bar/bizz/buzz', mode='w') as s3furi:
        yield assert_equal, s3furi.read(), value


@moto.mock_s3
def test_s3_walk():
    value = "Hello, world!\n\nGoodby, cruel world."
    ms3 = boto.connect_s3()
    bkt = ms3.create_bucket('furi')

    keys = ['foo/baq/bug', 'foo/bar/bizz/buzz', 'foo/bar/bizz/fizz', 'foo/ban']
    for keyname in keys:
        key = boto.s3.key.Key(bkt)
        key.name = keyname
        key.set_contents_from_string(value)

    returned = list(furi.walk('s3://furi/foo/'))
    expected = [
        ('s3://furi/foo/',          ['baq', 'bar'],  ['ban']),
        ('s3://furi/foo/baq/',      [],              ['bug']),
        ('s3://furi/foo/bar/',      ['bizz'],        []),
        ('s3://furi/foo/bar/bizz/', [],              ['buzz', 'fizz'])]
    assert_equal(returned, expected)


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
                tmpf.write("Hello, world!\n\nGoodby, cruel world.")

        returned = list(furi.walk('foo'))
        expected = [
            ('foo',          ['baq', 'bar'],  ['ban']),
            ('foo/baq',      [],              ['bug']),
            ('foo/bar',      ['bizz'],        []),
            ('foo/bar/bizz', [],              ['buzz', 'fizz'])]
        assert_equal(returned, expected)


@raises(furi.exceptions.ModeError)
def test_bad_mode():
    furi.open("foo.txt", mode="j")


def test_repr():
    furifile = furi.open("/path/to/file")
    returned = repr(furifile)
    expected = "<File: /path/to/file>"
    assert_equal(returned, expected)


def test_iter():
    lines = [
        "This is line 1\n",
        "This is line 2\n"]
    with tempfile.NamedTemporaryFile() as tmp:
        for line in lines:
            tmp.write(line)
        tmp.flush()
        furifile = furi.open(tmp.name)
        returned = list(iter(furifile))
    assert_equal(returned, lines)


@raises(furi.exceptions.FuriFileNotFoundError)
def test_cant_stream():
    furi.open("/path/to/file").stream()


@mock.patch("furi.furifile.RemoteFile._connect")
def test_connectkw(mock_connect):
    expected = dict(connect_kw1="fizz", connect_kw2="buzz")
    furifile = furi.furifile.RemoteFile("s3://bucket/path/to/file")
    furifile.connect(**expected)
    returned = furifile.__connect__
    assert_equal(returned, expected)


@raises(NotImplementedError)
def test__connect():
    furifile = furi.furifile.RemoteFile("s3://bucket/path/to/file")
    furifile._connect()


@raises(NotImplementedError)
def test__download():
    furifile = furi.furifile.RemoteFile("s3://bucket/path/to/file")
    furifile._download(None)


@raises(NotImplementedError)
def test__exists():
    furifile = furi.furifile.RemoteFile("s3://bucket/path/to/file")
    furifile._exists()


@raises(NotImplementedError)
def test__write():
    furifile = furi.furifile.RemoteFile("s3://bucket/path/to/file")
    furifile._write(None)


@raises(NotImplementedError)
def test__walk():
    furifile = furi.furifile.RemoteFile("s3://bucket/path/to/file")
    furifile._walk()


@raises(NotImplementedError)
def test__stream():
    furifile = furi.furifile.RemoteFile("s3://bucket/path/to/file")
    furifile._stream()
