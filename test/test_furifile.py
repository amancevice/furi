import boto3
import furi
import moto
import re
import tempfile
from nose.tools import assert_equal
from nose.tools import assert_is_instance


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
def test_s3_connect():
    s3furi = furi.open('s3://bucket/path/file')
    returned = repr(s3furi.connect())
    expected = 's3.ServiceResource()'
    assert_equal(returned, expected)


@moto.mock_s3
def test_s3_download():
    value = "Hello, world!\n\nGoodby, cruel world."
    ms3   = boto3.resource('s3')
    bkt   = ms3.create_bucket(Bucket='furi')
    key   = bkt.Object('foo/bar/bizz/buzz')
    key.put(Body=value)

    with tempfile.NamedTemporaryFile() as tmp:
        furifile = furi.download('s3://furi/foo/bar/bizz/buzz', tmp.name)
        assert_equal(furifile.read(), value)

@moto.mock_s3
def test_s3_exists():
    value = "Hello, world!\n\nGoodby, cruel world."
    ms3   = boto3.resource('s3')
    bkt   = ms3.create_bucket(Bucket='furi')
    key   = bkt.Object('foo/bar/bizz/buzz')
    key.put(Body=value)

    with furi.open('s3://furi/foo/bar/bizz/buzz') as s3furi:
        assert s3furi.exists()


@moto.mock_s3
def test_s3_not_exists():
    ms3 = boto3.resource('s3')
    bkt = ms3.create_bucket(Bucket='furi')

    with furi.open('s3://furi/foo/bar/bizz/buzz') as s3furi:
        assert not s3furi.exists()


@moto.mock_s3
def test_s3_write():
    value = "Hello, world!\n\nGoodby, cruel world."
    ms3   = boto3.resource('s3')
    bkt   = ms3.create_bucket(Bucket='furi')

    s3furi = furi.open('s3://furi/foo/bar/bizz/buzz', mode='w')
    s3furi.write(value)
    assert_equal(s3furi.read(), value)

@moto.mock_s3
def test_s3_write_stream():
    value = "Hello, world!\n\nGoodby, cruel world."
    ms3   = boto3.resource('s3')
    bkt   = ms3.create_bucket(Bucket='furi')

    s3furi1 = furi.open('s3://furi/foo/bar/bizz/buzz', mode='w')
    s3furi1.write(value)
    s3furi2 = furi.open('s3://furi/foo/bar/bizz/fizz', mode='w')
    s3furi2.write(s3furi1.stream())

    assert_equal(s3furi1.read(), s3furi2.read())

@moto.mock_s3
def test_s3_walk():
    value = "Hello, world!\n\nGoodby, cruel world."
    ms3   = boto3.resource('s3')
    bkt   = ms3.create_bucket(Bucket='furi')

    with furi.open('s3://furi/foo/', mode='w') as s3k:
        s3k.write('')
    with furi.open('s3://furi/foo/bar/', mode='w') as s3k:
        s3k.write('')
    with furi.open('s3://furi/foo/baq/', mode='w') as s3k:
        s3k.write('')
    with furi.open('s3://furi/foo/baq/bug', mode='w') as s3k:
        s3k.write(value)
    with furi.open('s3://furi/foo/bar/bizz/', mode='w') as s3k:
        s3k.write('')
    with furi.open('s3://furi/foo/bar/bizz/buzz', mode='w') as s3k:
        s3k.write(value)
    with furi.open('s3://furi/foo/bar/bizz/fizz', mode='w') as s3k:
        s3k.write(value)
    with furi.open('s3://furi/foo/ban', mode='w') as s3k:
        s3k.write(value)

    returned = list(furi.walk('s3://furi/foo/'))
    expected = [
        ('s3://furi/foo/',          ['baq', 'bar'],  ['ban']),
        ('s3://furi/foo/baq/',      [],              ['bug']),
        ('s3://furi/foo/bar/',      ['bizz'],        []),
        ('s3://furi/foo/bar/bizz/', [],              ['buzz', 'fizz']) ]
    assert_equal(returned, expected)
