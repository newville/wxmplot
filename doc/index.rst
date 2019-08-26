.. wxmplot documentation master file

wxmplot: wxPython plotting widgets using matplotlib
========================================================

.. _wxPython: http://www.wxpython.org/
.. _matplotlib:  http://matplotlib.sourceforge.net/

`wxmplot` provides easy-to-use and high-level `wxPython`_ widgets for
plotting and displaying of numerical data.

While `matplotlib`_ provides excellent general purpose plotting and
supports many backends, it does not have tight integration with any
particular GUI toolkit.  In addition, while the `matplotlib.pyplot` module
provides interactive plots and image displays, the features of its
Navigation Toolbars are minimal.  On the other hand, `wxPython`_ has some
basic plotting functionality but nothing as good as `matplotlib`_.

`wxmplot` bridges the gap between `matplotlib` and `wxPython` by providing
wx.Panels for basic 2D line plots, image display, and some custom plots.
The displays made with `wxmplot` are provide end-users with highly
interactive and customizable displays of their data that allow zooming and
unzooming, reporting mouse positions, and rotating images as well as
changing many aspects of the plot such as colors, line types, labels,
marker type, color tables, smoothing.  Although `wxmplot` does not expose
all of matplotlib's capabilities, it does provide basic plotting and image
display with wxPython widgets that are easy to add to wxPython applications
to handle many common plotting and image display needs for scientific data.

With `wxmplot`, script writers who want to make basic line plots or display
image data are able to get interactive and configurable displays of their
data. In addition, programmers who want to include high quality scientific
graphics in their applications can easily use `wxmplot` to provide their
end-users with highly customizable displays to better explore their data.



.. toctree::
   :maxdepth: 2

   installation
   interactive
   plotpanel
   imagepanel
   other
