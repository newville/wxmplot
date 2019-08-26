
==========================================================
:mod:`wxmplot.interactive`:  Interactive wxmplot displays
==========================================================

.. module:: wxmplot.interactive

The :mod:`interactive` modules provides simple entry-level functions
:mod:`interactive.plot` for plotting X/Y data and :mod:`interactive.imshow`
for displaying 2D image data.  These functions are similar to the
:mod:`matplotlib.pyplot` methods :func:`pyplot.plot` and
:func:`pyplot.imshow` but with a few important differences.


First, the :mod:`interactive` functions give noticeably better
interactivity to the user, with options to customize every important aspect
of the display both before and after the display is shown.

Second, the :mod:`interactive` functions display their results immediately,
without having to execute a `show()` method to render the display. For
interactive work from the Python (or one of the Jupyter consoles or
notebook) prompt, the displayed windows do not block the Python session.
That means you can easily plot other functions or data, either on the same
window or ih an entirely new top-level plotting window (a
:class:`PlotFrame`).  Furthermore, when running from a script that calls an
:mod:`interactive` function, the display does not disappear when the script
is complete but remains displayed and fully operational until all
displayed windows have been closed or until the running script is
explicitly clased as with Crtl-C.

Third, although they do provide roughly equivalent functionality, the
:mod:`interactive` functions are not complete drop-in replacements for
:mod:`pyplot`.  For one thing, there are many missing plot types.  For
another, the :mod:`interactive` functions do not follow the :mod:`pyplot`
syntax and API for specifying options, but use those of
:mod:`plotpanel.plot` and :mod:`imagepanel.display`.

As a result, the :mod:`interactive` module gives very useful displays of
data and you may find yourself replacing :mod:`pyplot` for interactive
work.

Plotting with :func:`wxmplot.interactive.plot` and related functions
========================================================================


.. function:: plot

A wrapper around :method:`PlotPanel.plot`

An example of using :func:`wxmplot.interactive.plot` is:

.. literalinclude:: ../examples/basic_screenshot.py

which gives a plot that looks like this:


.. image:: images/basic_screenshot.png
   :width: 85 %


.. autofunction:: newplot

.. autofunction:: hist


.. autofunction:: update_trace

.. autofunction:: plot_setlimits

.. autofunction:: plot_text

.. autofunction:: plot_arrow

.. autofunction:: plot_marker

.. autofunction:: plot_axhline

.. autofunction:: plot_axvline


Displaying images
====================


.. autofunction:: imshow

.. autofunction:: contour

Other routines
====================

.. autofunction:: get_wxapp

.. autofunction:: set_theme

.. autofunction:: available_themes

.. autofunction:: get_plot_window

.. autofunction:: get_image_window
