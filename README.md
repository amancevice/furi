# fURI
Interact with local &amp; remote files by URI

Last updated: `0.0.1`

## Installation

```
pip install furi
```

## Usage

```python
import furi

local = furi.open('/Users/amancevice/path/to/some/file.ext')
print local.read()
# => Hello, world!

s3 = furi.open('s3://bucket/path/to/key')
print s3.read()
# => Hello from S3!

sftp = furi.open('sftp://user:pass@host/path/to/file.ext')
print sftp.read()
# => Hello from SFTP
```

## S3-backed files

Connect to S3 by supplying `access_key` & `secret_key`, or by creating the file `~/.boto` with contents:

```bash
# ~/.boto
[Credentials]
aws_access_key_id = ACCESS_KEY_HERE
aws_secret_access_key = SECRET_KEY_HERE
```

Example S3-file access:
```python
# Use ~/.boto
s3file = furi.open('s3://bucket/path/to/key')

# Supply credentials
s3file = furi.open(
    's3://bucket/path/to/key', access_key='ACCESS', secret_key='SECRET' )
```

## SFTP-backed files

Supply the credentials as a part of the URI

```python
sftpfile = furi.open('sftp://user:password@host/workdir/file.ext')
```

## Download remote files

```python
# Default download location will be ~/Downloads/key
furi.download('s3://bucket/path/to/key')

# Supply custom download location
furi.download('s3://bucket/path/to/key', '~/path/to/key')

# Supply AWS keys inline
furi.download(
    's3://bucket/path/to/key', '/abs/path/to/download/key', 
    access_key='ACCESS', secret_key='SECRET' )
```

## Supported operations

```python
furifile = furi.open('<uri>', mode='<mode>')  # Open a file in a supported open-mode
furifile.exists()                  # Test if file exists
furifile.matches('regex pattern')  # Match pattern to filename (not including path)
furifile.read()                    # Read file contents' stream as string
furifile.stream()                  # Get handle to file contents stream
furifile.write('str or stream')    # Write a string or stream to file

furifile.connect(**credentials)    # Connect to a remote file service (such as S3)
```
