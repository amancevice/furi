import boto3
import furi
import moto
import tempfile
from nose.tools import assert_equal, assert_is_instance


@moto.mock_s3
def test_connect():
    s3furi = furi.open('s3://bucket/path/file')
    returned = repr(s3furi.connect())
    expected = 's3.ServiceResource()'
    assert_equal(returned, expected)


@moto.mock_s3
def test_download():
    value = "Hello, world!\n\nGoodby, cruel world."
    ms3   = boto3.resource('s3')
    bkt   = ms3.create_bucket(Bucket='furi')
    key   = bkt.Object('/foo/bar/bizz/buzz')
    key.put(Body=value)

    with tempfile.NamedTemporaryFile() as tmp:
        furifile = furi.download('s3://furi/foo/bar/bizz/buzz', tmp.name)
        assert_equal(furifile.read(), value)

@moto.mock_s3
def test_exists():
    value = "Hello, world!\n\nGoodby, cruel world."
    ms3   = boto3.resource('s3')
    bkt   = ms3.create_bucket(Bucket='furi')
    key   = bkt.Object('/foo/bar/bizz/buzz')
    key.put(Body=value)

    with furi.open('s3://furi/foo/bar/bizz/buzz') as s3furi:
        assert s3furi.exists()


@moto.mock_s3
def test_not_exists():
    ms3 = boto3.resource('s3')
    bkt = ms3.create_bucket(Bucket='furi')

    with furi.open('s3://furi/foo/bar/bizz/buzz') as s3furi:
        assert not s3furi.exists()


@moto.mock_s3
def test_write():
    value = "Hello, world!\n\nGoodby, cruel world."
    ms3   = boto3.resource('s3')
    bkt   = ms3.create_bucket(Bucket='furi')

    s3furi = furi.open('s3://furi/foo/bar/bizz/buzz', mode='w')
    s3furi.write(value)
    assert_equal(s3furi.read(), value)

@moto.mock_s3
def test_write_stream():
    value = "Hello, world!\n\nGoodby, cruel world."
    ms3   = boto3.resource('s3')
    bkt   = ms3.create_bucket(Bucket='furi')

    s3furi1 = furi.open('s3://furi/foo/bar/bizz/buzz', mode='w')
    s3furi1.write(value)
    s3furi2 = furi.open('s3://furi/foo/bar/bizz/fizz', mode='w')
    s3furi2.write(s3furi1.stream())

    assert_equal(s3furi1.read(), s3furi2.read())

@moto.mock_s3
def test_walk():
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
