import os
import re
from setuptools import setup

NAME = "furi"
AUTHOR = "amancevice"
EMAIL = "smallweirdnum@gmail.com"
DESC = "fURI File access through URIs."
LONG = """See GitHub_ for documentation.
.. _GitHub: https://github.com/amancevice/furi"""
CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 2.7",
    "Topic :: Utilities"]
TESTS_REQUIRE = ["boto", "nose", "mock", "moto"]
AWS_REQUIRES = ["boto3>=1.2.3"]
SFTP_REQUIRES = ["pysftp>=0.2.8"]
REQUIRES = ["PyYAML>=3.11.0"]
EXTRAS_REQUIRE = {
    'aws': AWS_REQUIRES,
    'sftp': SFTP_REQUIRES,
    'test': TESTS_REQUIRE,
    'all': AWS_REQUIRES + SFTP_REQUIRES + REQUIRES}


def version():
    search = r"^__version__ *= *['\"]([0-9.]+)['\"]"
    initpy = open("./furi/__init__.py").read()
    return re.search(search, initpy, re.MULTILINE).group(1)

setup(
    name=NAME,
    version=version(),
    author=AUTHOR,
    author_email=EMAIL,
    packages=[NAME],
    url='http://www.smallweirdnumber.com',
    description=DESC,
    long_description=LONG,
    classifiers=CLASSIFIERS,
    install_requires=REQUIRES,
    tests_require=TESTS_REQUIRE,
    extras_require=EXTRAS_REQUIRE,
    test_suite="nose.collector")
