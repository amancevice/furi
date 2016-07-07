# furi Changelog

0.7.0
* Python3 support

0.6.11
* Bugfix so that _close() no longer calls exists() or stream() with side effects and possible exceptions

0.6.10
* Bugfix for FS walk

0.6.9
* Bugfix for stream() handling

0.6.7
* Bugfix for SFTP files to chdir before attempting to get

0.6.6
* Allow directories to already exists when we attempt to mak dirs

0.6.5
* make dirs for non-existent file on write/append mode

0.6.4
* Added backward-compat support for boto-style keyword args
* Try to import AWS and SFTP support by default

0.6.3
* Better setup.py

0.6.2
* Bugfix to S3 walk() implementation

0.6.1
* Re-added `add_handler` as first-level method

0.6.0
* Separated dependencies into extras_require. Import AWS support with `import furi.aws`. Import SFTP support with `import furi.sftp`

0.5.0
* Added support for mapping JSON and YAML files with furi.map()
* Added support to map single-key DynamoDB instance with furi.map()

0.3.6
* Bugfix for walking SFTP

0.3.5
* Bugfix for sending S3 keys as args instead of kwargs

0.3.4
* Bugfixes for SFTP.walk()

0.3.2
* Added walk() implementation for SFTP

0.3.0
* Fixed setup.py

0.2.3
* Added furi.exists()

0.2.2
* Added walk() capabilities

0.1.0
* Added SSH private key support for SftpFile

0.0.4
* Added no-op __enter__ and __exit__ definitions for "with" functionality
* Added File.walk() method for directory-like URIs

0.0.3
* Allow users to supply their own handlers.

0.0.2
* Use self.key as _stream_impl for S3File

0.0.1
* Initial release
