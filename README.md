# fURI

<img src="https://travis-ci.org/amancevice/furi.svg?branch=master"/>

Interact with local &amp; remote files by URI

Last updated: `0.2.1`


## Installation

```
pip install furi
```


## Usage

#### Reading Files

```python
import furi

with furi.open('/path/to/some/file.ext') as local:
    print local.read()
    # => Hello, world!

with furi.open('s3://bucket/path/to/key') as s3:
    print s3.read()
    # => Hello from S3!

with furi.open('sftp://user:pass@host/path/to/file.ext') as sftp:
    print sftp.read()
    # => Hello from SFTP
```

#### Walking Directories

```python
# Walk S3 key
for dirpath, dirnames, filenames in furi.walk('s3://bucket/path/to/key/'):
    print dirpath
    print dirnames
    print filenames

# Walk S3 with supplied credentials
walkgen = furi.walk('s3://bucket/path/to/key/',
    access_key='ACCESS', secret_key='SECRET')
for dirpath, dirnames, filenames in walkgen:
    print dirpath
    print dirnames
    print filenames

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
# Use ~/.boto or ENV variables to authenticate
s3file = furi.open('s3://bucket/path/to/key')

# Supply credentials
s3file = furi.open('s3://bucket/path/to/key', 
    access_key='ACCESS', secret_key='SECRET' )
```


## SFTP-backed files

Supply the credentials as a part of the URI:

```python
sftpfile = furi.open('sftp://user:password@host/workdir/file.ext')
```


## Supported operations

```python
# Open a file in a supported open-mode
with furi.open('<uri>', mode='<mode>') as furifile: 
    furifile.exists()                  # Test if file exists
    furifile.matches('regex pattern')  # Match pattern to filename (not including path)
    furifile.read()                    # Read file contents' stream as string
    furifile.stream()                  # Get handle to file contents stream
    furifile.write('str or stream')    # Write a string or stream to file
    furifile.connect(**credentials)    # Connect to a remote file service (such as S3)
```
