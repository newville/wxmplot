.. wxmplot documentation master file

WXMPLOT: plotting widgets for Python
========================================================

.. _wxPython: https://www.wxpython.org/
.. _matplotlib:  https://matplotlib.org/

`wxmplot` provides high-level plotting of numerical data for Python, combining
`wxPython`_ widgets and `matplotlib`_.

While `matplotlib`_ provides excellent general-purpose plotting functionality
supporting many backends, it does not have tight integration with any
particular GUI toolkit.  The `matplotlib.pyplot` module provides high-level
functions for plotting and displaying data, but interacting with and
customizing the plots from it Navigation Toolbars are minimal.  On the other
hand, `wxPython`_ has some basic plotting functionality, but it has nothing as
good as `matplotlib`_.

`wxmplot` bridges the gap between `matplotlib`_ and `wxPython`_ by providing
wxPython widgets and user-friendly functions for basic line plots, image
display, and some custom plots.  The displays made with `wxmplot` give
end-users highly interactive displays of their data that allow zooming and
un-zooming, reporting mouse positions, rotating images, and changing color
themes.  The displays are highly configurable, helping the user to change many
aspects of the plot such as colors, line types, labels, marker type, color
tables, smoothing.  While `wxmplot` does not directly expose all of
matplotlib's capabilities, it focuses on highly-interactive plotting and image
display tools that handle many of the most common plotting and image display
needs for scientific data, and permits access and to the underlying matplotlib
API for those that need it.

The :mod:`wxmplot.interactive` functions are particularly easy to use, and
enable script writers to make XY line plots and image displays from their data,
and to interact with and configure these displays as part of exploratory data
analysis.  Programmers can use the `wxmplot` widgets to include these high
quality graphical displays of data in their wxPython applications to enable
users to explore their data.

.. toctree::
   :maxdepth: 2

   installation
   overview
   interactive
   plotpanel
   imagepanel
   examples
   other
   comparisons
