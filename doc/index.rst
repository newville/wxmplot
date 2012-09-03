
.. wxmplot documentation master file

WXMPLOT:  simple, rich plotting widgets for wxPython using matplotlib
============================================================================

.. _wxPython: http://www.wxpython.org/
.. _matplotlib:  http://matplotlib.sourceforge.net/

The wxmplot python package provides easy to use, richly featured plotting
widgets for `wxPython`_ built on top of the wonderful `matplotlib`_
library.  While matplotlib provides excellent general purpose plotting
functionality, and supports a variety of GUI and non-GUI backends, it does
not have a very tight integration with any particular GUI toolkit.
Similarly, while wxPython has some plotting functionality, it has nothing
as good as matplotlib.  The wxmplot package attempts to bridge this gap,
providing wx.Panels for basic 2D line plots and image display that are
richly featured and provide end-users with interactivity and customization
of the graphics without having to know matplotlib.  While wxmplot does not
expose all of matplotlib's capabilities, but does provide widgets, the
plotting and imaging Panels and Frames can be used simply in wxPython
applications to handle many use cases.

The wxmplot package is aimed at programmers who want high quality
scientific graphics for their applications that can be manipulated by the
end-user.  If you're a python programmer who is comfortable writing
matplotlib / pylab scripts or plotting interactively from IPython, this
package may seem too limiting for your needs.


.. toctree::
   :maxdepth: 2

   installation
   plotpanel
   imagepanel

