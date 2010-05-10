#!/usr/bin/env python


import distutils
from distutils.core import setup, Extension


setup(
    name = 'MPlot',
    version = '0.9.1',
    author = 'Matthew Newville',
    author_email = 'newville@cars.uchicago.edu',
    license = 'Python',
    description = 'high level wxPython Components for 2D plotting and image display using matplotlib.',
    package_dir = {'MPlot': 'lib'},
    packages = ['MPlot'],
)
