#!/usr/bin/env python

from setuptools import setup

import versioneer

long_desc = """
WXMPlot provides advanced wxPython widgets for plotting and image display
of numerical data based on matplotlib. While matplotlib provides excellent
general purpose plotting functionality and supports many GUI and non-GUI
backends it does not have a very tight integration with any particular GUI
toolkit. With a large number of plotting components and options, it is not
easy for programmers to select plotting options for every stuation and not
easy for end users to manipulate matplotlib plots.  Similarly, while
wxPython has some plotting functionality, it has nothing as good or
complete as matplotlib. The WXMPlot package attempts to bridge that gap.
With the plotting and image display Panels and Frames from WXMPlot,
programmers are able to provide plotting widgets that make it easy for end
users to customize plots and interact with their data.
"""

setup(name = 'wxmplot',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      author = 'Matthew Newville',
      author_email = 'newville@cars.uchicago.edu',
      url = 'http://newville.github.io/wxmplot/',
      download_url = 'http://github.com/newville/wxmplot/',
      license = 'OSI Approved :: MIT License',
      platforms=['Windows', 'Linux', 'Mac OS X'],
      description  = 'wxPython plotting widgets using matplotlib',
      long_description = long_desc,
      classifiers=['Intended Audience :: Science/Research',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Scientific/Engineering :: Visualization'],
      packages = ['wxmplot'],
 )
