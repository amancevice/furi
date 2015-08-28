import boto
import furi
import moto
import tempfile
from nose.tools import assert_equal, assert_is_instance


@moto.mock_s3
def test_connect():
    s3furi = furi.open('s3://bucket/path/file')
    returned = s3furi.connect()
    expected = boto.s3.connection.S3Connection
    assert_is_instance(returned, expected)


@moto.mock_s3
def test_download():
    value = "Hello, world!\n\nGoodby, cruel world."
    ms3   = boto.connect_s3()
    bkt   = ms3.create_bucket('furi')
    key   = boto.s3.key.Key(bkt, 'foo/bar/bizz/buzz')
    key.set_contents_from_string(value)

    with tempfile.NamedTemporaryFile() as tmp:
        furifile = furi.download('s3://furi/foo/bar/bizz/buzz', tmp.name)
        assert_equal(furifile.read(), value)

@moto.mock_s3
def test_exists():
    value = "Hello, world!\n\nGoodby, cruel world."
    ms3   = boto.connect_s3()
    bkt   = ms3.create_bucket('furi')
    key   = boto.s3.key.Key(bkt, 'foo/bar/bizz/buzz')
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
    value = "Hello, world!\n\nGoodby, cruel world."
    ms3   = boto.connect_s3()
    bkt   = ms3.create_bucket('furi')

    s3furi = furi.open('s3://furi/foo/bar/bizz/buzz', mode='w')
    s3furi.write(value)
    assert_equal(s3furi.read(), value)

@moto.mock_s3
def test_write_stream():
    value = "Hello, world!\n\nGoodby, cruel world."
    ms3   = boto.connect_s3()
    bkt   = ms3.create_bucket('furi')

    s3furi1 = furi.open('s3://furi/foo/bar/bizz/buzz', mode='w')
    s3furi1.write(value)
    s3furi2 = furi.open('s3://furi/foo/bar/bizz/fizz', mode='w')
    s3furi2.write(s3furi1.stream())

    assert_equal(s3furi1.read(), s3furi2.read())
