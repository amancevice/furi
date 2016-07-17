""" fURI Utils Tests. """

import json

import furi
from nose.tools import assert_equal, assert_in
from nose.tools import raises


def mock_extfunc(x):
    return x


def test_add_mapext():
    furi.utils.add_mapext("fizz", mock_extfunc)
    returned = furi.utils.__extdispatch__["fizz"]
    expected = mock_extfunc
    yield assert_in, "fizz", furi.utils.__extdispatch__
    yield assert_equal, returned, expected


@raises(KeyError)
def test_map_err():
    furi.utils.map("foo://fizz/buzz.json")


@raises(furi.exceptions.DownloadError)
def test_download_src_err():
    furi.utils.download("/path/to/local")


@raises(furi.exceptions.DownloadError)
def test_download_tgt_err():
    furi.utils.download("s3://bucket/path/to/aws", "s3://bucket/path/to/other")


def test_extfunc():
    returned = furi.utils.extfunc("json")
    expected = json.loads
    assert_equal(returned, expected)


@raises(KeyError)
def test_extfunc():
    furi.utils.extfunc("buzz")
