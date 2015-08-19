# fURI
Interact with local &amp; remote files by URI

Last updated: `0.0.1`

## Installation

```
pip install furi
```

## Usage

### Read a local file

```python
import furi

local = furi.open('/Users/amancevice/path/to/some/file.ext')
print local.read()
# => Hello, world!
```

### Read an S3-backed remote file

boto credentials in ~/.boto or ENV
```python
s3file = furi.open('s3://bucket/path/to/key')
print s3file.read()
# => Hello, world!
```

Manually provide credentials
```python
s3file = furi.open(
    's3://bucket/path/to/key', access_key='ACCESS', secret_key='SECRET' )
print s3file.read()
# => Hello, world!
```

### Download an S3-backed remote file by URI

Use default ~/Downloads/ location
```python
local = furi.download('s3://bucket/path/to/key')
print local.path
# => ~/Downloads/key
```

Custom download location
```python
local = furi.download('s3://bucket/path/to/key', '/abs/path/to/download/key')
print local.path
# => /abs/path/to/download/key
```

Manually provide credentials and download location
```python
local = furi.download(
    's3://bucket/path/to/key', '/abs/path/to/download/key', 
    access_key='ACCESS', secret_key='SECRET' )
```

### Write to an s3-backed remote file

Write a string
```python
s3file = furi.open('s3://bucket/path/to/key', mode='w')
s3file.write("Hello, world!")
```

Write a stream
```python
local  = furi.open('/abs/path/to/file.ext')
s3file = furi.open('s3://bucket/path/to/key', mode='w')
s3file.write(local.stream())
```
