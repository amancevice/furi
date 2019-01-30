import json
try:
    from unittest import mock
except ImportError:
    import mock

import pytest

import furi


def mock_extfunc(x):
    return x


def test_add_mapext():
    furi.utils.add_mapext('fizz', mock_extfunc)
    returned = furi.utils.__extdispatch__['fizz']
    expected = mock_extfunc
    assert 'fizz' in furi.utils.__extdispatch__
    assert returned == expected
    assert 'x' == returned('x')


def test_map_err():
    with pytest.raises(KeyError):
        furi.utils.map('foo://fizz/buzz.json')


def test_download_src_err():
    with pytest.raises(furi.exceptions.DownloadError):
        furi.utils.download('/path/to/local')


@mock.patch('boto3.client')
def test_download_tgt_err(mock_s3):
    with pytest.raises(furi.exceptions.DownloadError):
        furi.utils.download(
            's3://bucket/path/to/aws',
            's3://bucket/path/to/other',
        )


def test_extfunc():
    returned = furi.utils.extfunc('.json')
    expected = json.loads
    assert returned == expected


def test_extfunc_keyerr():
    with pytest.raises(KeyError):
        furi.utils.extfunc('buzz')
