.. wxmplot documentation master file

wxmplot: wxPython plotting widgets using matplotlib
========================================================

.. _wxPython: http://www.wxpython.org/
.. _matplotlib:  http://matplotlib.sourceforge.net/

`wxmplot` provides easy-to-use, high-level `wxPython`_ widgets for plotting
and displaying numerical data.  It is based on `matplotlib`_ which provides
excellent general purpose plotting functionality and supports many GUI and
non-GUI backends, but which does not have a very tight integration with any
particular GUI toolkit.  With a large number of plotting components and
options, it is not easy for programmers to select plotting options for
every stuation and not easy for end users of applications to manipulate
most `matplotlib`_ plots.  In addition, while `matplotlib` has a `pyplot`
module that provides basic interactive plots and image displays, the basic
Navigation Toolbars provided are minimal -- the interactivity and options
to configure displays available with `wxmplot` are much more extensive.

Similarly, while `wxPython`_ has some plotting functionality, it has
nothing as good or complete as `matplotlib`_. The `wxmplot` package bridges
that gap.  With the plotting and image display Panels and Frames from
`wxmplot`, script writers are able to get richer, and more interactive
displays of their data, and programmers are able to provide plotting
widgets that make it easy for end users to customize plots and interact
with their data.

`wxmplot` provides wx.Panels for basic 2D line plots, image display, and some
custom plots.  The emphasis for these displays is to make them richly
featured and provide end-users with highly interactive displays of their
data with zooming, reporting mouse positions, rotating images, and so
forth.  Plots and images are highly customizable by the end-user --
changing colors, line types, labels, marker type, color tables, smoothing,
and so forth all from the display itself, without having to know
matplotlib.  To be clear `wxmplot` does not expose all of matplotlib's
capabilities, but does provide 2D plotting and image display Panels and
Frames that are easy to add to wxPython applications to handle many common
plotting and image display needs for scientific data.

The `wxmplot` package is aimed at programmers who want to include high
quality scientific graphics in their applications that can be manipulated
by the end-user. If you're a python programmer who is comfortable writing
complex pyplot scripts or plotting interactively with Jupyter, this package
may seem too limiting for your needs.  On the other hand, if you just want
to make some basic line plots or display image data but would like to be
able to interact with the data and plot such as zooming in or changing the
color, line thicknesses, and so on after the basic display is shown,
`wxmplot` may be exactly what you want.  And finally, if you are writing
GUI programs that will interact with and display numerical, scientific
data, then you may find that `wxmplot` provides rich and easy-to-use
plotting methods that all the end-user to explore their data.


.. toctree::
   :maxdepth: 2

   installation
   interactive
   plotpanel
   imagepanel
   other
