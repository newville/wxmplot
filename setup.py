#!/usr/bin/env python


import distutils
from distutils.core import setup, Extension

import lib
setup(
    name = 'wxmplot',
    version = lib.__version__,
    author = 'Matthew Newville',
    author_email = 'newville@cars.uchicago.edu',
    license = 'Python',
    description = 'high level wxPython Components for 2D plotting and image display using matplotlib.',
    package_dir = {'wxmplot': 'lib'},
    packages = ['wxmplot'],
)
