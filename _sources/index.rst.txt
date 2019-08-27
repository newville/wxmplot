.. wxmplot documentation master file

wxmplot: plotting widgets using wxPython and matplotlib
========================================================

.. _wxPython: http://www.wxpython.org/
.. _matplotlib:  http://matplotlib.sourceforge.net/

`wxmplot` provides easy-to-use and high-level `wxPython`_ widgets and
python functions for plotting and displaying of numerical data.

While `matplotlib`_ provides excellent general-purpose plotting and
supports many backends, it does not have tight integration with any
particular GUI toolkit.  In addition, while the `matplotlib.pyplot` module
provides interactive plots and image displays, the features of its
Navigation Toolbars are minimal.  On the other hand, `wxPython`_ has some
basic plotting functionality but nothing as good as `matplotlib`_.

`wxmplot` bridges the gap between `matplotlib` and `wxPython` by providing
both wxPython widgets and top-level functions for basic 2D line plots,
image display, and some custom plots.  The displays made with `wxmplot`
give end-users highly interactive displays of their data that allow zooming
and unzooming, reporting mouse positions, and rotating images.  The
displays are also highly configurable, allow the user to change many
aspects of the plot such as colors, line types, labels, marker type, color
tables, smoothing.  Although `wxmplot` does not expose all of matplotlib's
capabilities, it does provide basic plotting and image display with
wxPython widgets that are easy to add to wxPython applications to handle
many common plotting and image display needs for scientific data.

`wxmplot` enables script writers to make basic 2D line plots or images from
their data and the interact and configure these displays of their data. In
addition, programmers who want to include high quality scientific graphics
in their applications can easily use `wxmplot` to provide their end-users
with highly customizable displays to better explore their data.


.. toctree::
   :maxdepth: 2

   installation
   overview
   interactive
   plotpanel
   imagepanel
   examples
   other
