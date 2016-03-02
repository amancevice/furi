# furi Changelog

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
