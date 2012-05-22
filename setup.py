#!/usr/bin/env python

from setuptools import setup
import lib
setup(
    name = 'wxmplot',
    version = lib.__version__,
    author = 'Matthew Newville',
    author_email = 'newville@cars.uchicago.edu',
    url = 'http://newville.github.com/wxmplot/',
    license = 'Python',
    description = 'high level wxPython Components for 2D plotting and image display using matplotlib.',
    classifiers=['Intended Audience :: Science/Research'
                 'Topic :: Scientific/Engineering',
                 'Topic :: Scientific/Engineering :: Visualization'],
    package_dir = {'wxmplot': 'lib'},
    packages = ['wxmplot'],
)
