#!/usr/bin/env python

from distutils.core import setup

execfile('modules/locksmith/version.py')

setup(name='locksmith',
    version=__version__,
    description='A simple network based locking client',
    author=__maintainer__,
#    author_email='',
    install_requires=["requests"],
    package_dir = {'': 'modules'},
    packages=['locksmith'],
    scripts=['locksmith']
)
