
==========================================================
:class:`PlotPanel`:  A wx.Panel for Basic 2D Line Plots
==========================================================

The :class:`PlotPanel` class supports standard 2-d plots (line plots,
scatter plots) with a simple-to-use programming interface.  This is derived
from a :class:`wx.Panel` and so can be included in a wx GUI anywhere a
:class:`wx.Panel` can be.   A :class:`PlotPanel` provides the following
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

.. class:: PlotPanel(parent[, size=(6.0, 3.7)[, dpi=96[, messenger=None[, show_config_popup=True[, **kws]]]]])

   Create a Plot Panel, a :class:`wx.Panel`

   :param parent: wx parent object.
   :param size:   figure size in inches.
   :param dpi:    dots per inch for figure.
   :param messenger: function for accepting output messages.
   :type messenger: callable or ``None``
   :param show_config_popup: whether to enable a popup-menu on right-click.
   :type show_config_popup: ``True``/``False``

   The *size*, and *dpi* arguments are sent to matplotlib's
   :class:`Figure`.  The *messenger* should should be a function that
   accepts text messages from the panel for informational display.  The
   default value is to use :func:`sys.stdout.write`.

   The *show_config_popup* arguments controls whether to bind right-click
   to showing a poup menu with options to zoom in or out, configure the
   plot, or save the image to a file.


   Extra keyword parameters are sent to the wx.Panel.


:class:`PlotPanel` methods
====================================================================

.. method:: plot(x, y, **kws)

   Draw a plot of the numpy arrays *x* and *y*, erasing any existing plot.  The
   displayed curve for these data is called a *trace*.  The :meth:`plot` method
   has many optional parameters, all using keyword/value argument.  Since most
   of these are shared with the :meth:`oplot` method, the full set of parameters
   is given in :ref:`Table of Arguments for plot() and oplot() <plotopt_table>`

.. method:: oplot(x, y, **kws)

   Draw a plot of the numpy arrays *x* and *y*, overwriting any existing plot.

   The :meth:`oplot` method has many optional parameters,  as listed in
   :ref:`Table of Arguments for plot() and oplot() <plotopt_table>`


.. _plotopt_table:

Table of Arguments for plot() and oplot():   Except where noted,
the arguments are available for both :meth:`plot` and :meth:`oplot`.

  +-------------+------------+---------+------------------------------------------------+
  | argument    |   type     | default | meaning                                        |
  +=============+============+=========+================================================+
  | title       | string     | None    | Plot title (:meth:`plot` only)                 |
  +-------------+------------+---------+------------------------------------------------+
  | xlabel      | string     | None    | ordinate label (:meth:`plot` only)             |
  +-------------+------------+---------+------------------------------------------------+
  | ylabel      | string     | None    | abscissa label (:meth:`plot` only)             |
  +-------------+------------+---------+------------------------------------------------+
  | y2label     | string     | None    | right-hand abscissa label (:meth:`plot` only)  |
  +-------------+------------+---------+------------------------------------------------+
  | label       | string     | None    | trace label (defaults to 'trace N')            |
  +-------------+------------+---------+------------------------------------------------+
  | side        | left/right | left    | side for ylabel                                |
  +-------------+------------+---------+------------------------------------------------+
  | use_dates   | bool       | False   | to show dates in xlabel (:meth:`plot` only)    |
  +-------------+------------+---------+------------------------------------------------+
  | grid        | None/bool  | None    | to show grid lines (:meth:`plot` only)         |
  +-------------+------------+---------+------------------------------------------------+
  | color       | string     | blue    | color to use for trace                         |
  +-------------+------------+---------+------------------------------------------------+
  | linewidth   | int        | 2       | linewidth for trace                            |
  +-------------+------------+---------+------------------------------------------------+
  | style       | string     | solid   | line-style for trace (solid, dashed, ...)      |
  +-------------+------------+---------+------------------------------------------------+
  | drawstyle   | string     | line    | style connecting points of trace               |
  +-------------+------------+---------+------------------------------------------------+
  | marker      | string     | None    | symbol to show for each point (+, o, ....)     |
  +-------------+------------+---------+------------------------------------------------+
  | markersize  | int        | 8       | size of marker shown for each point            |
  +-------------+------------+---------+------------------------------------------------+
  | dy          | array      | None    | uncertainties for y values; error bars         |
  +-------------+------------+---------+------------------------------------------------+
  | ylog_scale  | bool       | False   | draw y axis with log(base 10) scale            |
  +-------------+------------+---------+------------------------------------------------+
  | xmin        | float      | None    | minimum displayed x value                      |
  +-------------+------------+---------+------------------------------------------------+
  | xmax        | float      | None    | maximum displayed x value                      |
  +-------------+------------+---------+------------------------------------------------+
  | ymin        | float      | None    | minimum displayed y value                      |
  +-------------+------------+---------+------------------------------------------------+
  | ymax        | float      | None    | maximum displayed y value                      |
  +-------------+------------+---------+------------------------------------------------+
  | xylims      | 2x2 list   | None    | [[xmin, xmax], [ymin, ymax]]                   |
  +-------------+------------+---------+------------------------------------------------+
  | autoscale   | bool       | True    | whether to automatically set plot limits       |
  +-------------+------------+---------+------------------------------------------------+

  As a general note, the configuration for the plot (title, labels, grid
  displays) and for each trace (color, linewidth, ...) are preserved for a
  :class:`PlotPanel`. A few specific notes:

   1. The title, label, and grid arguments to :meth:`plot` default to ``None``,
   which means to use the previously used value.

   2. The *use_dates* option is not very rich, and simply turns x-values that
   are Unix timestamps into x labels showing the dates.

   3. While the default is to auto-scale the plot from the data ranges,
   specifying any of the limits will override the corresponding limit(s).

   4. The *color* argument can be any color name ("blue", "red", "black", etc),
   standard X11 color names ("cadetblue3", "darkgreen", etc), or an RGB hex
   color string of the form "#RRGGBB".

   5. Valid *style* arguments are 'solid', 'dashed', 'dotted', or 'dash-dot',
   with 'solid' as the default.

   6. Valid *marker* arguments are '+', 'o', 'x', '^', 'v', '>', '<', '|', '_',
   'square', 'diamond', 'thin diamond', 'hexagon', 'pentagon', 'tripod 1', or
   'tripod 2'.

   7. Valid *drawstyles* are None (which connects points with a straight line),
   'steps-pre', 'steps-mid', or 'steps-post', which give a step between the
   points, either just after a point ('steps-pre'), midway between them
   ('steps-mid') or just before each point ('steps-post').   Note that if displaying
   discrete values as a function of time, left-to-right, and want to show a
   transition to a new value as a sudden step, you want 'steps-post'.

  All of these values, and a few more settings controlling whether and how to
  display a plot legend can be configured interactively (see Plot Configuration).


.. method:: clear()

   Clear the plot.


.. method:: set_xylims(limits[, axes=None[, side=None[, autoscale=True]]])

   Set the x and y limits for a plot based on a 2x2 list.

   :param limits: x and y limits
   :type limits: 2x2 list: [[xmin, xmax], [ymin, ymax]]
   :param axes: instance of matplotlib axes to use (i.e, for right or left side y axes)
   :param side: set to 'right' to get right-hand axes.
   :param autoscale: whether to automatically scale to data range.

   That is, if `autoscale=False` is passed in, then the limits are use.

.. method:: get_xylims()

   return current x, y limits.

.. method:: unzoom()

   unzoom the plot.  The x, y limits for interactive zooms are stored, and this function unzooms one level.

.. method:: unzoom_all()

   unzoom the plot to the full data range.


.. method:: update_line(trace, x, y[, side='left'])

   update an existing trace.

   :param trace: integer index for the trace (0 is the first trace)
   :param x:     array of x values
   :param y:     array of y values
   :param side:  which y axis to use ('left' or 'right').

   This function is particularly useful for data that is changing and you wish
   to update the line with the new data without completely redrawing the entire
   plot.  Using this method is substantially faster than replotting.


.. method:: set_title(title)

   set the plot title.

.. method:: set_xlabel(label)

   set the label for the ordinate axis.

.. method:: set_ylabel(label)

   set the label for the left-hand abscissa axis.

.. method:: set_y2label(label)

   set the label for the right-hand abscissa axis.

.. method:: set_bgcol(color)

   set the background color for the PlotPanel.

.. method:: write_message(message)

   write a message to the messenger.  For a PlotPanel embedded in a PlotFrame,
   this will go the the StatusBar.

.. method:: save_figure()

   show a FileDialog to save a PNG image of the current plot.


.. method:: configure()

   show plot configuration window for customizing plot.



:class:`PlotFrame`: a wx.Frame showing a :class:`PlotPanel`
====================================================================

A :class:`PlotFrame` is a wx.Frame -- a separate plot window -- that
contains a :class:`PlotPanel` and is decorated with a status bar and
menubar with menu items for saving, printing and configuring plots..

.. class:: PlotFrame(parent[, size=(700, 450)[, title=None[, **kws]]])

   create a plot frame.

The frame will have a *panel* member holding the underlying :class:`PlotPanel`.


:class:`PlotApp`: a wx.App showing a :class:`PlotFrame`
====================================================================

A :class:`PlotApp` is a wx.App -- an application  -- that
consists of a :class:`PlotFrame`.   This  and is decorated with a status bar and
menubar with menu items for saving, printing and configuring plots..

.. class:: PlotAppp()

   create a plot application.  This has methods :meth:`plot`, :meth:`oplot`, and
   :meth:`write_message`, which are sent to the underlying :class:`PlotPanel`.

   This allows very simple scripts which give plot interactivity and
   customization::

        from wxmplot import PlotApp
        from numpy import arange, sin, cos, exp, pi

        xx  = arange(0.0,12.0,0.1)
        y1  = 1*sin(2*pi*xx/3.0)
        y2  = 4*cos(2*pi*(xx-1)/5.0)/(6+xx)
        y3  = -pi + 2*(xx/10. + exp(-(xx-3)/5.0))

        p = PlotApp()
        p.plot(xx, y1, color='blue',  style='dashed',
               title='Example PlotApp',  label='a',
               ylabel=r'$k^2\chi(k) $',
               xlabel=r'$  k \ (\AA^{-1}) $' )

        p.oplot(xx, y2,  marker='+', linewidth=0, label =r'$ x_1 $')
        p.oplot(xx, y3,  style='solid',          label ='x_2')
        p.write_message(Try Help->Quick Reference')
        p.run()


Examples and Screenshots
====================================================================

A basic plot from a :class:`PlotFrame` looks like this:

.. image:: images/basic_screenshot.png


The configuration window (Options->Configuration or Ctrl-K) for this plot looks
like this:

.. image:: images/configuration_frame.png

where all the options there will dynamically change the plot in the PlotPanel.

Many more examples are given in the *examples* directory in the source
distribution kit.  The *demo.py* script there will show several 2D Plot
panel examples, including a plot which uses a timer to simulate a dynamic
plot, updating the plot as fast as it can - typically 10 to 30 times per
second, depending on your machine.  The *stripchart.py* example script also
shows a dynamic, time-based plot.

