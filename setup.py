from setuptools import setup

setup(
    author='amancevice',
    author_email='smallweirdnum@gmail.com',
    description='File access through URIs',
    extras_require={
        'aws': ['boto3 >= 1.2.3'],
        'sftp': ['pysftp >= 0.2.8'],
    },
    install_requires=['pyyaml >= 3.11.0'],
    name='furi',
    packages=['furi'],
    setup_requires=['setuptools_scm'],
    url='https://github.com/amancevice/furi',
    use_scm_version=True,
)
