.. wxmplot documentation master file

wxmplot: wxPython plotting widgets using matplotlib
========================================================

.. _wxPython: http://www.wxpython.org/
.. _matplotlib:  http://matplotlib.sourceforge.net/

`wxmplot` provides easy-to-use, high-level `wxPython`_ widgets for plotting
and displaying numerical data.  While `matplotlib`_ provides excellent
general purpose plotting and supports many GUI and non-GUI backends, it
does not have tight integration with any particular GUI toolkit.  In
addition, while `matplotlib`s `pyplot` module provides interactive plots
and image displays, the its Navigation Toolbars are minimal.  Similarly
`wxPython`_ has some plotting functionality but nothing as good as
`matplotlib`_.

`wxmplot` bridges the gap between `matplotlib` and `wxPython`, by providing
wx.Panels for basic 2D line plots, image display, and some custom plots.
The displays made with `wxmplot` are richly featured and provide end-users
with highly interactive displays of their data with zooming, changing
colors, line types, labels, marker type, color tables, smoothing, reporting
mouse positions, rotating images, and so forth, all from the display
itself.  `wxmplot` does not expose all of matplotlib's capabilities, but
does provide basic plotting and image display Panels and Frames that are
easy to add to wxPython applications to handle many common plotting and
image display needs for scientific data.

With `wxmplot`, script writers who want to make some basic line plots or
display image data are able to get richer, and more interactive displays of
their data. In addition, programmers who want to include high quality
scientific graphics in their applications can easily use `wxmplot` to
provide their end-users with highly customizable displays to better explore
their data.



.. toctree::
   :maxdepth: 2

   installation
   interactive
   plotpanel
   imagepanel
   other
