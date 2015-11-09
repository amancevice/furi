import os
from setuptools import setup

NAME    = "furi"
VERSION = "0.3.4"
AUTHOR  = "amancevice"
EMAIL   = "smallweirdnum@gmail.com"
DESC    = "fURI File access through URIs."

CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 2.7",
    "Topic :: Utilities" ]
REQUIRES = [
    "boto>=2.38.0",
    "nose",
    "mock",
    "moto",
    "pysftp==0.2.8" ]

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name                 = NAME,
    version              = VERSION,
    author               = AUTHOR,
    author_email         = EMAIL,
    packages             = [ NAME ],
    package_data         = { "%s" % NAME : ['README.md'] },
    include_package_data = True,
    url                  = 'http://www.smallweirdnumber.com',
    description          = DESC,
    long_description     = read('README.md'),
    classifiers          = CLASSIFIERS,
    install_requires     = REQUIRES,
    test_suite           = "nose.collector" )
