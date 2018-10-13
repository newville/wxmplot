.. wxmplot documentation master file

wxmplot: wxPython plotting widgets using matplotlib
========================================================

.. _wxPython: http://www.wxpython.org/
.. _matplotlib:  http://matplotlib.sourceforge.net/

wxmplot provides advanced `wxPython`_ widgets for plotting and image display
of numerical data based on `matplotlib`_. While `matplotlib`_ provides
excellent general purpose plotting functionality and supports many GUI and
non-GUI backends it does not have a very tight integration with any
particular GUI toolkit. With a large number of plotting components and
options, it is not easy for programmers to select plotting options for every
stuation and not easy for end users to manipulate `matplotlib`_ plots.
Similarly, while `wxPython`_ has some plotting functionality, it has nothing
as good or complete as `matplotlib`_. The wxmplot package attempts to bridge
that gap.  With the plotting and image display Panels and Frames from
wxmplot, programmers are able to provide plotting widgets that make it easy
for end users to customize plots and interact with their data.

WXMplot provides wx.Panels for basic 2D line plots and image display that are
richly featured and provide end-users with interactivity (zooming, reading
positions, rotating images) and customization (line types, labels, marker
type, colors, and color tables) of the graphics without having to know
matplotlib.  wxmplot does not expose all of matplotlib's capabilities, but
does provide 2D plotting and image display Panels and Frames that are easy to
add to wxPython applications to handle many common plotting and image display
needs.

The wxmplot package is aimed at programmers who want to include high quality
scientific graphics in their applications that can be manipulated by the
end-user.  If you're a python programmer who is comfortable writing complex
pyplot scripts or plotting interactively from IPython, this package may seem
too limiting for your needs.  On the other hand, wxmplot provides more and
and better customizations than matplotlib's basic navigation toolbars.

.. toctree::
   :maxdepth: 2

   installation
   plotpanel
   imagepanel
   other
