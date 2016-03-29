# fURI

<img src="https://travis-ci.org/amancevice/furi.svg?branch=master"/>

Interact with local &amp; remote files by URI

Last updated: `0.6.9`


## Installation

```
pip install furi # Install basic support

pip install furi[all] # Install AWS & SFTP dependencies

pip intsall furi[aws] # Install AWS dependencies

pip install furi[sftp] # Install SFTP dependencies
```


## Usage

#### Reading Files

```python
import furi

with furi.open('/path/to/some/file.ext') as local:
    print local.read()
    # => Hello, world!

with furi.open('file:///path/to/local/file.ext') as local:
    print local.read()
    # => Hello from Local file system
```

If `furi` was installed with AWS dependencies S3 files can be read as well:

```python
with furi.open('s3://bucket/path/to/key') as s3:
    print s3.read()
    # => Hello from S3!
```

Same for SFTP files:

```python
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
credentials = {
    'aws_access_key_id'     : '<access_key>',
    'aws_secret_access_key' : '<secret_key>' }
for dirpath, dirnames, filenames in furi.walk('s3://bucket/path/to/key/', **credentials):
    print dirpath
    print dirnames
    print filenames

```

## S3-backed files

Example S3-file access:

```python
# Using ~/.boto or ENV variables to authenticate
s3file = furi.open('s3://bucket/path/to/key')

# Supply credentials
s3file = furi.open('s3://bucket/path/to/key', 
    aws_access_key_id='ACCESS', aws_secret_access_key='SECRET' )
```


## SFTP-backed files

Supply the credentials as a part of the URI:

```python
sftpfile = furi.open('sftp://user:password@host/workdir/file.ext')
```

Or with a key:

```python
sftpfile = furi.open('sftp://user@host/workdir/file.ext', private_key='/path/to/ssh_id')
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


## Configurations/Mappings

Structured JSON or YAML files can be loaded into a mapping object using the `furi.map()` function.


### Local & S3 File Mapping

Mapping local or S3-backed file contents operations are not cached so every read has some cost to it. If numerous reads are expected it is recommended that the object is mapped into a dictionary. File-based mapping objects do not support write operations at this time.

```python
mymap = furi.map('s3://buket/path/to/mapping.json')
mymap = furi.map('/path/to/local/mapping.yaml')

print mymap['key']
# => "Hello, world!"

print mymap['otherkey'] # Reads file from S3 again
# => "Goodby, cruel world!"

# Reads the file once and caches it in `mymap`
mymap = dict(furi.map('s3://buket/path/to/mapping.json')) 
```


### DynamoDB Mapping

Single partition-key DynamoDB tables without sort-keys are also supported and use the URI format `"dynamodb://<tablename>/"`. The returned mapping object can be queried like a dictionary.

```python
mynamo = furi.mapping('dynamodb://mytable/', region_name='us-east-1')

print mynamo['partition_key_value']
# => { "partition_key_name" : "partition_key_value",
#      "field1": "Hello, world!",
#      "field2": "Goodbye, cruel world!" }
```


## Chained Mappings

It may be the case that you have a prioritized list of mapping files, where if a key cannot be found in the first map, the second is queried, then the third, and so on until a match is found or a `KeyError` is thrown. Use the `furi.chain()` function to chain mappings together.

```python
chains = 's3://bucket/path/to/map.yml', '/path/to/local.json'
chainmap = furi.chain(*map(furi.map, chains))

print chainmap['key']
# => "Hello, world!"

print chainmap['otherkey']
# => WARNING:root:s3://bucket/path/to/map.yml :: KeyError('otherkey',)
#    "Goodby, cruel world!"
```
