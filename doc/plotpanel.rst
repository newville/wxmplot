
==========================================================
:class:`PlotPanel`:  A wx.Panel for Basic 2D Line Plots
==========================================================

The :class:`PlotPanel` class supports standard 2-d plots (line plots,
scatter plots) with a simple-to-use programming interface.  This is derived
from a :class:`wx.Panel` and so can be included in a wx GUI anywhere a
:class:`wx.Panel` can be.    A :class:`PlotPanel` provides the following
capabilities for the end-user:
   1. display x, y coordinates (left-click)
   2. zoom in on a particular region of the plot (left-drag)
   3. customize titles, labels, legend, color, linestyle, marker,
      and whether a grid is shown.  A separate window is used to
      set these attributes.
   4. save high-qualiy plot images (as PNGs), copy to system
      clipboard, or print.

A :class:`PlotFrame` that includes a :class:`PlotPanel`, menus, and
statusbar is also provided to give a separate plotting window to an
application.  These both have the basic plotting methods of :meth:`plot` to
make a new plot with a single trace, and :meth:`oplot` to overplot another
trace on top of an existing plot.  These each
take 2 equal-length numpy arrays (abscissa, ordinate) for each trace.
The :class:`PlotPanel` and :class:`PlotFrame` have many additional methods
to interact with the plots.

.. class:: PlotPanel(parent[, size=(6.0, 3.7)[, dpi=96[, messenger=None[, **kws]]]])

   Create a Plot Panel.

   :param parent: wx parent object.
   :param size:   figure size in inches.
   :param dpi:    dots per inch for figure.
   :param messenger: function for accepting output messages.
   :type messenger: callable or ``None``

   Note that a separate call to :meth:`BuildPanel` will be required.

