.. wxmplot documentation master file

WXMPLOT:  simple, rich plotting widgets for wxPython using matplotlib
============================================================================

.. _wxPython: http://www.wxpython.org/
.. _matplotlib:  http://matplotlib.sourceforge.net/

The wxmplot python package provides simple, rich plotting widgets for
`wxPython`_.  These are built on top of the `matplotlib`_ library, which
provides a wonderful library for 2D plots and image display.  The wxmplot
package does not attempt to expose all of matplotlib's capabilities, but
does provide widgets (wxPython panels) for basic 2D plotting and image
display that handle many use cases.  The widgets are designed to be very
easy to program with, and provide end-users with interactivity and
customization of the graphics without knowing matplotlib.

The wxmplot package is aimed at programmers who want decent scientific
graphics for their applications that can be manipulated by the end-user.
If you're a python programmer, comfortable writing matplotlib / pylab
scripts, or plotting interactively from IPython, this package may seem to
limiting for your needs.


.. toctree::
   :maxdepth: 2

   installation
   plotpanel
   imagepanel

