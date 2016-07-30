import furi
from nose.tools import assert_equal, raises


def test_dispatch_local_no_scheme():
    returned = type(furi.open('/abs/path/test'))
    expected = furi.furifile.File
    assert_equal(returned, expected)


def test_dispatch_local_with_scheme():
    returned = type(furi.open('file:///abs/path/test'))
    expected = furi.furifile.File
    assert_equal(returned, expected)


def test_dispatch_s3():
    returned = type(furi.open('s3://bucket/path/to/test'))
    expected = furi.aws.S3File
    assert_equal(returned, expected)


def test_dispatch_sftp():
    returned = type(furi.open('sftp://user:pass@host/path/test'))
    expected = furi.sftp.SftpFile
    assert_equal(returned, expected)


@raises(furi.exceptions.SchemeError)
def test_bad_scheme():
    furi.open('foo://bar/path/test')


def test_not_exists():
    assert not furi.exists("/foo/bar")
