.. _ch_interactive:

==========================================================
Interactive wxmplot displays
==========================================================

.. module:: wxmplot.interactive

The :ref:`ch_overview` describes the features available in `wxmplot`, and
shows how `wxmplot` plotting functions give a richer level of interactivity
and customization to the end user.  Here, the functions in the
:mod:`interactive` are described in more detail.  An important feature of the
:func:`plot`, :func:`imshow` and other functions of the :mod:`interactive`
module is that they display their results immediately, without having to
execute a `show()` method to render the display. In addition, for interactive
work from the Python (or one of the Jupyter consoles or notebook) prompt, the
displayed windows do not block the Python session.  This means you can easily
plot other functions or data, either on the same window or in a new top-level
plotting window (a :class:`PlotFrame`).  Furthermore, when running from a
script that calls an :mod:`interactive` function, the display does not
disappear when the script is complete but remains displayed and fully
operational until all displayed windows have been closed or until the running
script is explicitly clased as with Crtl-C.

While `wxmplot` provides :func:`plot`, :func:`imshow` and other functions
that are roughly equivalent to the functions from `matplotlib.pyplot`, the
functions are here not exact drop-in replacements for the `pyplot` functions.
For one thing, there are many missing plot types and functions.  For another,
the syntax for specifying options is different.  For example, `wxmplot`
prefers a long list of keyword arguments to :func:`plot` over a series of
separate function calls.

The immediacy of the rendering and the ability to customize the plots either
before or after they are made means that the functions here are very useful
for exploratory displays of data, and you may find yourself replacing
:mod:`pyplot` for interactive work.

2D Plotting with :func:`wxmplot.interactive.plot` and related functions
==========================================================================

.. autofunction:: plot


More details of Plot Optons are given in
:ref:`Table of Plot Arguments <plotopt_table>`.

.. autofunction:: hist

.. autofunction:: update_trace

.. autofunction:: plot_setlimits

.. autofunction:: plot_text

.. autofunction:: plot_arrow

.. autofunction:: plot_marker

.. autofunction:: plot_axhline

.. autofunction:: plot_axvline


Displaying images with :func:`imshow` and :func:`contour`
==============================================================

.. autofunction:: imshow

.. autofunction:: contour

Functions for working with the interactive windows
======================================================

.. autofunction:: get_wxapp

.. autofunction:: set_theme

.. autofunction:: available_themes

.. autofunction:: get_plot_window

.. autofunction:: get_image_window
