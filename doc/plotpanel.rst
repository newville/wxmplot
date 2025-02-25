==========================================================
:class:`PlotPanel`:  A wx.Panel for Basic Line Plots
==========================================================

.. module:: plotpanel

The :class:`PlotPanel` class supports standard line plots, including
scatter plots.  It has both an easy-to-use programming interface, and a rich
graphical user interface for manipulating the plot after it has been drawn.
The :class:`PlotPanel` class is derived from a :class:`wx.Panel` and so that
it can be included anywhere in a wx Window object that a normal
:class:`wx.Panel` can be put.  In addition to drawing a plot, a
:class:`PlotPanel` provides the following capabilities to the end-user:

   1. display x, y coordinates as the mouse move.
   2. display x, y coordinates of last left-click.
   3. zoom in on a particular region of the plot with left-drag in a
      lineplot, or draw a 'lasso' around selected points in a scatterplot.
   4. customize titles, labels, legend, colors, linestyles, markers, and
      whether a grid and a legend is shown.  A separate configuration
      window is displayed to give users control of these settings.
   5. save high-quality plot images (as PNGs), or copy to system
      clipboard, or print.

In addition, there is a :class:`PlotFrame` widget which creates a
stand-alone :class:`wx.Frame` that contains a :class:`PlotPanel`, a
:class:`wx.StatusBar`, and a :class:`wx.MenuBar`.  Both :class:`PlotPanel`
and :class:`PlotFrame` classes have the basic plotting methods of
:meth:`plot` to make a new plot with a single trace, and :meth:`oplot` to
overplot another trace on top of an existing plot.  These each take 2
equal-length numpy arrays (abscissa, ordinate) for each trace, and a host
of optional arguments.  The :class:`PlotPanel` and :class:`PlotFrame` have
many additional methods to interact with the plots.

.. class:: PlotPanel(parent, size=(700, 450), dpi=150, fontsize=9, **kws)

   Create a Plot Panel, a :class:`wx.Panel` with a matplotlib Figure.
   This takes many optional arguments:

   :param parent: wx parent object.
   :param size:   figure size in wxPython pixel coordinates ((700, 450)).
   :type  size:    wx.Size  or tuple of 2 integers.
   :param dpi:    dots per inch for figure (150).
   :type  dpi:    integer
   :param axisbg:    background colour for Axis ('#FEFEFE').
   :type  axisbg:  valid colour name
   :param fontsize:  font size for wxFont for labels and ticks (9).
   :type  fontsize:  integer
   :param output_title:  string to use for output plots ('plot').
   :param messenger:     function to use for writing output messages  (``None``).
   :type  messenger:     callable or ``None``
   :param trace_color_callback: function to call when a color changes (``None``).
   :type  trace_color_callback: callable or ``None``
   :param show_config_popup: whether to enable a popup-menu on right-click.
   :type show_config_popup: ``True``/``False``

   The *size*, and *dpi* arguments are sent to matplotlib's
   :class:`Figure`.  The *messenger* should should be a function that
   accepts text messages from the panel for informational display.  The
   default value is to use :func:`sys.stdout.write`.

   The *show_config_popup* arguments controls whether to bind right-click
   to showing a poup menu with options to zoom in or out, configure the
   plot, or save the image to a file.

   Keyword parameters in ``**kws`` other than those listed above are sent to the wx.Panel.


:class:`PlotPanel` conventions and common arguments
============================================================

The :class:`PlotPanel` methods below share many conventions and use
common arguments where possible.  A list of common function argumets
for :meth:`plot`, :meth:`oplot`, and :meth:`scatterplot is given in
:ref:`Table of Plot Arguments <plotopt_table>`.  Many of these
arguments and terms are alsoe used in the other function methods.


.. _plotopt_table:

**Table of Plot Arguments** These arguments apply for the :meth:`plot`, :meth:`oplot`, and
:meth:`scatterplot` methods.  Except where noted, the arguments are available for :meth:`plot` and
:meth:`oplot`.  In addition, the :meth:`scatterplot` method uses many of the same arguments for the
same meaning, as indicated by the right-most column.


  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | argument         |   type     | default | meaning                                        |note | scatterplot? |
  +==================+============+=========+================================================+=====+==============+
  | title            | string     | None    | Plot title                                     |  1  |  yes         |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | ylabel           | string     | None    | abscissa label                                 |  1  |  yes         |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | y2label          | string     | None    | right-hand abscissa label                      |  1  |  yes         |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | label            | string     | None    | trace label (defaults to 'trace N')            |  1  |  yes         |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | theme            | str        | ''      | theme for colors and text size                 |  2  |  no          |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | color            | string     | blue    | color to use for trace                         |  3  |  yes         |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | bgcolor          | string     | #FEFEFE | color for background of Axis (plot area)       |  3  |  yes         |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | framecolor       | string     | white   | color for frame outside Axis                   |  3  |  yes         |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | gridcolor        | string     | #E5E5E5 | color for grid lines                           |  3  |  yes         |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | linewidth        | int        | 2       | linewidth for trace                            |     |  no          |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | alpha            | float      | 1.0     | opacity (from 0 to 1) for trace                |  4  |  no          |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | fill             | bool       | False   | fill to 0 or between [y-dy,y+dy]               |  5  |  no          |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | zorder           | int        | 10      | depth order of trace (what trace is on top)    |  6  |  no          |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | style            | string     | solid   | line-style for trace (solid, dashed, ...)      |  7  |  no          |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | drawstyle        | string     | line    | style connecting points of trace               |  8  |  no          |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | side             | string     | None    | location (side) for y-axes and label           |  9  |  no          |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | yaxes            | 1,2,3,4    | 1       | location (side) for y-axes and label           |  9  |  no          |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | yaxes_tracecolor | bool       | False   | use trace color for multiple y-axes            |  9  |  no          |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | marker           | string     | None    | symbol to show for each point (+, o, ....)     | 10  |  no          |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | markersize       | int        | 8       | size of marker shown for each point            |     |  no          |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | legendfontsize   | int        | 7       | text size for legend                           |     |  yes         |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | labelfontsize    | int        | 9       | text size for Axis labels                      |     |  yes         |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | dy               | array      | None    | uncertainties for y values; error bars         |     |  no          |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | xmin             | float      | None    | minimum displayed x value                      |  11 |  yes         |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | xmax             | float      | None    | maximum displayed x value                      |  11 |  yes         |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | ymin             | float      | None    | minimum displayed y value                      |  11 |  yes         |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | ymax             | float      | None    | maximum displayed y value                      |  11 |  yes         |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | viewpad          | float      | 2.5     | percent past data range to pad data limits     |  11 |  yes         |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | ylog_scale       | bool       | False   | draw y axis with log(base 10) scale            |     |  no          |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | autoscale        | bool       | True    | whether to automatically set plot limits       |     |  no          |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | fullbox          | bool       | True    | whether to show top and right Axes lines       |  12 |  no          |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | axes_style       | string     | 'box'   | whether to show top, left, right Axes lines    |  12 |  no          |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | grid             | None/bool  | None    | to show grid lines                             |     |  yes         |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | show_legend      | None/bool  | None    | whether to display legend (None: no change)    |     |  no          |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | legend_loc       | string     | 'ur'    | location of legend                             | 13  |  no          |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | legend_on        | bool       | True    | whether legend is on Axis                      | 13  |  no          |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | delay_draw       | bool       | False   | whether to delay draw until later.             | 14  |  no          |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | refresh          | bool       | True    | whether to refresh display                     |     |  no          |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | use_dates        | bool       | False   | to show dates in xlabel (:meth:`plot` only)    | 15  |  no          |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | timezone         | timezone   | None    | timezone data for date and time data           | 15  |  no          |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  |                  | **arguments that apply only for** :meth:`scatterplot`                       |              |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | size             | int        | 10      | size of marker                                 |     |  yes         |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | edgecolor        | string     | black   | edge color of marker                           |  3  |  yes         |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | selectcolor      | string     | red     | color for selected points                      |  3  |  yes         |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+
  | callback         | function   | None    | user-supplied callback to run on selection     |     |  yes         |
  +------------------+------------+---------+------------------------------------------------+-----+--------------+


  As a general note, the configuration for the plot (title, labels, grid displays) and
  for each trace (color, linewidth, ...) are preserved for a :class:`PlotPanel`. A few
  specific notes:

   1. The title, label, and grid arguments to :meth:`plot` default to ``None``, which
      means to use the previously used value.

   2. The *theme* will set the color palette and make stylistic choices.  Choices include
      'light' (the default), 'white-background', 'dark', 'matplotlib', 'seaborn',
      'ggplot', 'bmh', 'fivethirtyeight', 'grayscale', 'dark_background',
      'tableau-colorblind10', 'seaborn-bright', 'seaborn-colorblind', 'seaborn-dark',
      'seaborn-darkgrid', 'seaborn-dark-palette', 'seaborn-deep', 'seaborn-notebook',
      'seaborn-muted', 'seaborn-pastel', 'seaborn-paper', 'seaborn-poster',
      'seaborn-talk', 'seaborn-ticks', 'seaborn-white', 'seaborn-whitegrid', and

   3. All *color* arguments can be a common color name ("blue", "red", "black", etc), a
      standard X11 color names ("cadetblue3", "darkgreen", etc), or an RGB hex color
      string of the form "#RRGGBB".

   4. The *alpha* opacity value ranges from 0 (transpaent) to 1 (opaque) for the color
      used for the line trace and the *fill*.  While supplying a color string of the form
      "#RRGGBBAA" can also set *alpha*, setting it directly here is more robust and should
      be preferred.

   5. The *fill* value controls whether to fill under the curve to 0.  When `dy` is supplied
      for errorbars, using `fill=True` will not show error bars as vertical lines, but fill
      in the curve between `y-dy` and `y+dy`.

   6. *zorder* is the depth (that is, height above the plane of the screen) to draw the
      object at, controlling which element will be on top of others.  By default, each
      :meth:`oplot` plots at a zorder of 10*(n+1), where n is the counter for the trace.
      That is, each subsequent trace is drawn *over* the previous, by defualt.

   7. *style* is one of ('solid', 'dashed', 'short dashed', 'long dashed', 'dotted', or
      'dash-dot')

   8. *drawstyles* is one of (``None``, 'steps-pre', 'steps-mid', or 'steps-post').
      ``None`` connects points with a straight line between points.  The others give
      horizontal lines with a vertical step at the starting point ('step-pre'),
      mid-point ('step-mid') the ending point ('steps-post').  Note that if displaying
      discrete values as a function of time, left-to-right, and want to show a
      transition to a new value as a sudden step, you want 'steps-post'.

   9. *side* can by one of (``None``, 'left', 'right', 'right2', 'right3') (default=``None``)
      or *yaxes* can be one on (1, 2, 3, 4) (default=1, for left-hand axes).  Setting
      *yaxes_tracecolor* will make the Y axes use the same color as the trace using that
      Y axes. See :ref:`sect_yaxes_side` for details.

   10. *marker* is one of ('+', 'o', 'x', '^', 'v', '>', '<', '|', '_', 'square',
       'diamond', 'thin diamond', 'hexagon', 'pentagon', 'tripod 1', or 'tripod 2').

   11. By default, xmin, xmax, ymin, and ymax are set from the data. *viewpad* gives a
       percentage of the data range for the view to be extended.  That is, with xmin=0,
       xmin=100, viewpad=5, the range for x will be [-5, 105].

   12. *fullbox* can be used to turn on or off the top and right Axes lines (or spines),
       giving a more open figure.  The 'axes_style' option gives a little more control --
       you can set this to either 'box' for a complete box, 'open' for left and right
       Axes lines only (same as *fullbox=False*), or 'bottom' which will suppress the
       top, right, and left Axes.

   13. *legend_loc* sets the position of the legend on the plot, and is one of 'ur',
       'ul', 'cr', 'cl', 'lr' 'll', 'uc', 'lc', or 'cc' for 'upper right' , 'upper
       left', 'center right', 'center left', 'lower right', 'lower left', 'upper center',
       'lower center', or 'center'.

   14. The *delay_draw* option will delay the actual drawing the plot to the
       screen. This can be give a noticeable speed up when plotting multiple line traces
       at once.  See also :meth:`plot_many` for a convenience function to plot many
       traces at once.

   15. For more on using data with dates or times, see :ref:`sect_datetime`.


  All of these values, and a few more settings controlling whether and how to display a plot legend can be
  configured interactively (see Plot Configuration).


.. _sect_yaxes_side:

Selecting Y-axes (left- or right-hand side)
=======================================================

While a basic use of :class:`PlotPanel` will have a single Y-axes, it
is sometimes useful to plot multiple traces together that have
different ranges of Y values. Using 2 Y-axes -- the left- and
right-hand sides of the plot is a very common need. Sometimes 3 or
even 4 Y axes sharing an X axes can be helpful, and :class:`PlotPanel`
supports plots with up to 4 of these.

To specify which Y axes to use, we recommeded using the argument
`yaxes` which can be an integer 1, 2, 3, or 4, where 1 (the default)
means the left-hand side of the plot, 2 the right-hand side, and 3 and
4 additional axes displaced from the right-hand side.  (see
:ref:`example_leftright` and :ref:`example_multiple_yaxes`).  For backward
compatibility (and with no intention to deprecate this), this can also
be set with the argument `side`, which can be ``None`` (meaning "use
the value of `yaxes`") or one of ('left', 'right', 'right2',
'right3'), m (default=``None``).

Setting `yaxes_tracecolor` to ``True`` will make each of the Y axes
use the same color as the trace using that Y axes.


.. _sect_datetime:

Using date-time data with :func:`plot`
===========================================

If the `x` values to be plotted holds date or time data, it is
necessary to use `use_dates=True`.

Values for dates can be handled in a few different formats, but
eventually the values will be converted to `matplotlib.dates` object,
which uses a floating point number to represent the number of days
since 1970, and assumes the times are UTC.  See
:ref:`example_multiple_yaxes` for example.

If the source of the date data is Unix timestamps, this conversion is
fairly easy to do, as the values can simply be divided by 86400 -- and
you can do this on an array of timestamps.  When doing this, it is
best to also provide timezone information, as from the `pytz` module.

If data comes as a list of `datetime` objects, from the `datetime`
library, these will be automatically recognized and properly
converted.  These can have a timezone specified, or you can provide
one.  Finally, it is possible to pass in a list or array of strings as
`x`, and set `use_dates=True`.  In this case, the
`matplotlib.dates.datestr2num` function will be used convert the
string.  Wether this actually works well will depend on the ability of
this function to parse and interpret the date strings used.




:class:`PlotPanel` methods
=============================================


.. method:: plot(x, y, **kws)

   Draw a plot of the numpy arrays *x* and *y*, erasing any existing plot.  The
   displayed curve for these data is called a *trace*.  The :meth:`plot` method
   has many optional parameters, all using keyword/value argument.  Since most
   of these are shared with the :meth:`oplot` method, the full set of parameters
   is given in :ref:`Table of Plot Arguments <plotopt_table>`

.. method:: oplot(x, y, **kws)

   Draw a plot of the numpy arrays *x* and *y*, overplotting any existing
   plot, so that both traces are visible.

   The :meth:`oplot` method has many optional parameters,  as listed in
   :ref:`Table of Plot Arguments <plotopt_table>`

.. method:: update_line(trace, x, y, yaxes=1, side=None, update_limits=True, draw=False)

   update an existing trace.

   :param trace: integer index for the trace (0 is the first trace)
   :param x:     array of x values
   :param y:     array of y values
   :param side:  which y axis to use. See :ref:`sect_yaxes_side`.
   :param yaxes:  which y axis to use.
   :param update_limits:  whether to force an update of the limits.
   :param draw:    whether to force a redrawing of the canvas.

   This function is particularly useful for data that is changing and you
   wish to update traces from a previous :meth:`plot` or :meth:`oplot` with
   the new (x, y) data without completely redrawing the entire plot.  Using
   this method is substantially faster than replotting, and should be used
   for dynamic plots such as a StripChart.

.. method:: plot_many(xylist, side='left', title=None, xlabel=None, ylabel=None, **kws)

   Plot many x, y datasets at a single time. *xylist* should be a list or
   tuple of two-element list or tuple of (*x*, *y*) data arrays.  Many of
   the properties listed in :ref:`Table of Plot Arguments <plotopt_table>`
   can be specified.

   If plotting many datasets, this method can give a significant speed-up
   over calling :meth:`plot` followed by many calls of :meth:`oplot`, as
   that will render the full image after each call, while the
   :meth:`plot_many` will delay plotting until all the datasets are ready
   to be plotted.

.. method:: scatterplot(x, y, **kws)

   draws a 2d scatterplot.   This is a collection of points that are not meant to imply a specific
   order that can be connected by a continuous line.    A full list of arguments are listed in
   :ref:`Table of Plot Arguments <plotopt_table>`.

.. method:: clear()

   Clear the plot.

.. method:: add_text(text, x, y, yaxes=1, side=None, rotation=None, ha='left', va='center', family=None, **kws)

   add text to the plot.

   :param text: text to write
   :param x:    x coordinate for text
   :param y:    y coordinate for text
   :param side: which y-axes to use for coordinates. See :ref:`sect_yaxes_side`.
   :param yaxes: which y-axes to use for coordinates.
   :param rotation:  text rotation: angle in degrees or 'vertical' or 'horizontal'
   :param ha:  horizontal alignment ('left', 'center', 'right')
   :param va:  vertical alignment ('top', 'center', 'bottom', 'baseline')
   :param family:  name of font family ('serif', 'sans-serif', etc)

.. method:: add_arrow(x1, y1, x2, y2, yaxes=1, side=None, shape='full', color='black', wdith=0.01, head_width=0.03, overhang=0)


   draw arrow from (x1, y1) to (x2, y2).

   :param x1: starting x coordinate
   :param y1: starting y coordinate
   :param x2: endnig x coordinate
   :param y2: ending y coordinate
   :param side: which y-axes to use for coordinates. See :ref:`sect_yaxes_side`.
   :param yaxes: which y-axes to use for coordinates.
   :param shape:  arrow head shape ('full', 'left', 'right')
   :param color:  arrow fill color ('black')
   :param width:  width of arrow line (in points. default=0.01)
   :param head_width:  width of arrow head (in points. default=0.1)
   :param overhang:    amount the arrow is swept back (in points. default=0)


.. method:: set_xylims(limits[, axes=None[, side=None, yaxes=1]])

   Set the x and y limits for a plot based on a 2x2 list.

   :param limits: x and y limits
   :type limits: a 4-element list: [xmin, xmax, ymin, ymax]
   :param axes: instance of matplotlib axes to use (i.e, for right or left side y axes)
   :param side: which y-axes to use. See :ref:`sect_yaxes_side`.
   :param yaxes: which y-axis to use.

.. method:: get_xylims()

   return current x, y limits.

.. method:: unzoom()

   unzoom the plot.  The x, y limits for interactive zooms are stored, and this function unzooms one level.

.. method:: unzoom_all()

   unzoom the plot to the full data range.

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

   write a message to the messenger.  For a :class:`PlotPanel` embedded in
   a :class:`PlotFrame`, this will go the the Status Bar.

.. method:: save_figure()

   shows a File Dialog to save a PNG image of the current plot.

.. method:: configure()

   show plot configuration window for customizing plot.

.. method:: reset_config()

   reset the configuration to default settings.




:class:`PlotFrame`: a wx.Frame showing a :class:`PlotPanel`
====================================================================

.. module:: plotframe

A :class:`PlotFrame` is a wx.Frame -- a separate window -- that
contains a :class:`PlotPanel` and is decorated with a status bar and
menubar.  A :class:`PlotFrame` inherits many of the methods of a
:class:`PlotPanel`, and simply passes the arguments along to the
corresponding methods of the :class:`PlotPanel`.  The statusbar will
display live coordintes as the mouse moves on the plot.  The built-in
menus include methods for saving, printing and copying an image of the
plot to the system Clipboard, as well as ways to configure many of the
plot attributes.

.. class:: PlotFrame(parent[, size=(700, 450)[, title=None[, **kws]]])

   create a plot frame.  This frame will have a :data:`panel` member
   holding the underlying :class:`PlotPanel`, and have menus and statusbar
   for plot interaction.

.. method:: plot(x, y, **kws)

   Passed to panel.plot

.. method:: oplot(x, y, **kws)

   Passed to panel.oplot

.. method:: scatterplot(x, y, **kws)

   Passed to panel.scatterplot

.. method:: clear()

   Passed to panel.clear

.. method:: update_trace(x, y, **kws)

   Passed to panel.update_trace

.. method:: reset_config(x, y, **kws)

   Passed to panel.reset_config


:class:`PlotApp`: a wx.App showing a :class:`PlotFrame`
====================================================================

.. module:: plotapp

A :class:`PlotApp` is a wx.App -- an application -- that consists of a
:class:`PlotFrame`.  This show a frame that is decorated with a status bar
and menubar with menu items for saving, printing and configuring plots.

.. class:: PlotApp()

   create a plot application.  This has methods :meth:`plot`, :meth:`oplot`, and
   :meth:`write_message`, which are sent to the underlying :class:`PlotPanel`.
   This allows very simple scripts which give plot interactivity and
   customization.
