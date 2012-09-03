#!/usr/bin/env python

from setuptools import setup
# try:
#     import lib.__version__ as version
# except:
#     version = 'unknown'

long_desc = ''' A library for wxPython based on matplotlib for
high-level, richly featured 2-D plotting and displaying 3-D data
as intensity maps and contour plots.  Easy-to-use wx Panels and
Frame provide high-quality plots and allow some user interaction
and customization of the plots.'''

setup(name = 'wxmplot',
      version = '0.9.10',
      author = 'Matthew Newville',
      author_email = 'newville@cars.uchicago.edu',
      url = 'http://newville.github.com/wxmplot/',
      download_url = 'http://newville.github.com/wxmplot/',
      requires = ('wx', 'numpy', 'matplotlib'),
      license = 'OSI Approved :: MIT License',
      description = 'A library for plotting in wxPython using matplotlib',
      long_description = long_desc,
      platforms = ('Windows', 'Linux', 'Mac OS X'),
      classifiers=['Intended Audience :: Science/Research',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Scientific/Engineering :: Visualization'],
      package_dir = {'wxmplot': 'lib'},
      packages = ['wxmplot'],
)

m = '''
Author: Matthew Newville
Author-email: newville@cars.uchicago.edu
Platform: Windows, Linux, Mac OS X
Download-url: http://newville.github.com/wxmplot/
Intended Audience :: Science/Research


'''
