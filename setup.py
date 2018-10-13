#!/usr/bin/env python

from setuptools import setup

import versioneer

long_desc = """
WXMPlot provides advanced wxPython widgets for plotting and image
display based on matplotlib. The plotting and image display wx Panels
and Frames it provides are easy for the programmer to include and work
with from wx programs.  More importantly, the widgets created by WXMPlot
give the end user a flexible set of tools for interacting with their
data and customizing the plots and displays.  WXMPlot panels are more
interactive than typical displayss from matplotlib's pyplot module.
"""

install_reqs = ['six', 'matplotlib', 'numpy', 'wx']

setup(name = 'wxmplot',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      author = 'Matthew Newville',
      author_email = 'newville@cars.uchicago.edu',
      url          = 'http://newville.github.io/wxmplot/',
      download_url = 'http://github.com/newville/wxmplot/',
      requires     = install_reqs,
      install_requires = install_reqs,
      license      = 'OSI Approved :: MIT License',
      description  = 'wxPython plotting tools using matplotlib',
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
