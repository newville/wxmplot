.. wxmplot documentation master file

wxmplot: plotting widgets using wxPython and matplotlib
========================================================

.. _wxPython: http://www.wxpython.org/
.. _matplotlib:  http://matplotlib.sourceforge.net/

`wxmplot` provides `wxPython`_ widgets and python functions for displaying
numerical data.

While `matplotlib`_ provides excellent general-purpose plotting
functionality supports many backends, it does not have tight integration
with any particular GUI toolkit.  While The `matplotlib.pyplot` module provides
easy-to-use functions for plotting and displaying data, the features of its
Navigation Toolbars for interactivity and customizations are minimal.  On
the other hand, while `wxPython`_ has some basic plotting functionality, it
has nothing as good as `matplotlib`_.

`wxmplot` bridges the gap between `matplotlib`_ and `wxPython`_ by
providing wxPython widgets and user-friendly functions for basic 2D line
plots, image display, and some custom plots.  The displays made with
`wxmplot` give end-users highly interactive displays of their data that
allow zooming and unzooming, reporting mouse positions, rotating images,
and changing color themes.  The displays are highly configurable, helping
the user to change many aspects of the plot such as colors, line types,
labels, marker type, color tables, smoothing.  To be clear, `wxmplot` does
not expose all of matplotlib's capabilities, but it does provide plotting
and image display tools that handle many of the most common plotting and
image display needs for scientific data.

In particular, the :mod:`wxmplot.interactive` funtions enables script
writers to make 2D line plots and image displays from their data, and to
interact with and configure these displays as part of exploratory data
analysis. In addition, programmers can use the `wxmplot` widgets to include
these high quality graphical displays of data in their wxPython
applications to enable users to explore their data.

.. toctree::
   :maxdepth: 2

   installation
   overview
   interactive
   plotpanel
   imagepanel
   examples
   other
