#!/usr/bin/env python


import distutils
from distutils.core import setup, Extension

setup(
    name = 'wxmplot',
    version = '0.9.6',
    author = 'Matthew Newville',
    author_email = 'newville@cars.uchicago.edu',
    license = 'Python',
    description = 'high level wxPython Components for 2D plotting and image display using matplotlib.',
    package_dir = {'wxmplot': 'lib'},
    packages = ['wxmplot'],
)
