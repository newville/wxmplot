.. _ch_interactive:

==========================================================
Interactive wxmplot displays
==========================================================

.. module:: wxmplot.interactive

The :ref:`ch_overview` describes the main features of `wxmplot` and shows
how `wxmplot` plotting functions give a richer level of customization and
interactivity to the end user than is available from the standard
`matplotlib.pyplot` when run from a script or program.

Here, the emphasis is on the immediacy of the interactivity of the
data displays especially when used from interactive sessions,
including plain Python REPL, IPython/Jupyter consoles or Jupyter
Notebooks.

An important feature of the :func:`plot`, :func:`imshow` and other
functions of the :mod:`interactive` module is that they display their
results immediately, without having to execute a `show()` method to
render the display. For interactive work from the Python REPL or one of
the Jupyter consoles or notebook prompt, the displayed windows do not
block the Python session.  This means that not only can you zoom in,
change themes, etc from the Plot window, you can can also easily plot
other functions or data, either on the same window or in a new
top-level plotting window.

For Jupyter Notebooks, it should be noted that while other plotting
libraries (matplotlib, plotly, and bokeh) will show graphics in-line,
as part of the Notebook, wxmplot will use separate display windows,
outside of the browser.  While the interactive plots are then not
saved directly in the Notebook, the code to generate the plots can be
re-run. And images of the plot results can be copied and pasted as
Markdown cells.


The functions in the :mod:`interactive` are described in detail below.
While the functions :func:`plot`, :func:`imshow` are roughly
equivalent to those in `matplotlib.pyplot`, they are not exact drop-in
replacements for the `pyplot` functions.


Plotting in an interactive session or Jupyter
===========================================================


As an example using :mod:`wxmplot.interactive` in a Jupyter console
session might look like this::

    ~> jupyter console
    Jupyter console 6.6.3

    Python 3.13.9 | packaged by conda-forge | (main, Oct 22 2025, 23:31:04) [Clang 19.1.7 ]
    Type 'copyright', 'credits' or 'license' for more information
    IPython 9.7.0 -- An enhanced Interactive Python. Type '?' for help.
    Tip: Use `%timeit` or `%%timeit`, and the  `-r`, `-n`, and `-o`
    option    s to easily profile your code.

    In [1]: import numpy as np
    In [2]: import wxmplot.interactive as wi
    In [3]: x = np.linspace(0, 20, 101)
    In [4]: wi.plot(x, np.sin(x), xlabel='t (sec)')
    Out[4]: <wxmplot.interactive.PlotDisplay at 0x11ef74290>

    In [5]:


At this point a plot like this will be displayed:

.. image:: images/interactive1.png
   :width: 50 %

The `wxmplot` display will have full interatvity and can be configured
after it is drown.

For example, from the Plot Configuration window we could change the
theme to 'Seaborn' and set the label for this trace to be 'sine'.
Then from the Jupyter console we can continue::

    In [5]: wi.plot(x, np.cos(1.5*x), label='cosine', show_legend=True)
    Out[5]: <wxmplot.interactive.PlotDisplay at 0x10db88678>

    In [6]:

which will now show:

.. image:: images/interactive2.png
   :width: 50 %

which is again a fully interactive and configurable display. For example,
with the legend displayed, clicking on any of the labels in the legend will
toggle the display of that curve.  If we want to clear the data and plot
something new, we might do something like::

    In [6]: wi.plot(x, x*np.log(x+1), label='xlogx', new=True)
    Out[6]: <wxmplot.interactive.PlotDisplay at 0x10db88678>

    In [7]:

We can also place a text string, arrow, horizontal, or vertical line on the
plot, as with::

    In [7]: wi.plot_text('hello!', 9.1, 0.87)

    In [8]:


and so forth.

If we wanted to bring up a second Line Plot window, we can use the
**win=2** option::


    In [8]: wi.plot(x, np.sin(x)*np.exp(-x/8) , win=2, theme='ggplot')
    Out[8]: <wxmplot.interactive.PlotDisplay at 0x110b2fb88>

    In [9]:

and then control which of the displays any additional plot functions use by
passing the `win` option to the plotting functions.


The immediacy of the rendering and the ability to customize the plots makes
these plotting functions well-suited for exploratory displays of data.


Using the :mod:`interactive` functions from a script
===========================================================

When using the :mod:`interactive` functions by running a script in a
non-interactive way, the display will still appear. It does not block
further execution of the script and the display does not disappear
when the script is complete.  Instead, the plots and images will
remain displayed and fully operational until all windows have been
closed or until the running script is explicitly closed (say, with
Ctrl-D).  That means that you can add `wi.plot()` and `wi.imshow()` to
your short- or long-running scripts and the plots will be displayed
until you no longer want to use them.


Line Plotting with :func:`plot` and related functions
==========================================================================

.. autofunction:: plot

More details of Plot Options are given in
:ref:`Table of Plot Arguments <plotopt_table>`.

.. autofunction:: hist

.. autofunction:: update_trace

.. autofunction:: set_data_generator

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

.. autofunction:: set_theme

.. autofunction:: available_themes

.. autofunction:: get_wxapp

.. autofunction:: get_plot_window

The returned :class:`wx.PlotFrame` will have the many attributes and
methds, with some of the most useful described in the table below.
This include access to the underlying matplotlib Axes and Canvas
objects.

.. _plotframe_objects_table:

**Table of PlotFrame attributes and methods**

  +-----------------+-----------------------------------------------------+
  | name            |  object type                                        |
  +=================+=====================================================+
  | .cursor_history | [(x, y, timestamp), ...] of cursor selections       |
  +-----------------+-----------------------------------------------------+
  | .save_figure()  | method to save image to a png file                  |
  +-----------------+-----------------------------------------------------+
  | .configure      | method to show Configuration window                 |
  +-----------------+-----------------------------------------------------+
  | .get_config     | method to return configuration dictionary           |
  +-----------------+-----------------------------------------------------+
  | .set_config     | method to update configuration with keyword/values  |
  +-----------------+-----------------------------------------------------+
  | .panel          | wxmplot.PlotPanel, a wx.Panel                       |
  +-----------------+-----------------------------------------------------+
  | .panel.conf     | wxmplot.PlotConfig                                  |
  +-----------------+-----------------------------------------------------+
  | .panel.axes     | matplotlib.axes.AxesSubPlot                         |
  +-----------------+-----------------------------------------------------+
  | .panel.fig      | matplotlib.figure.Figure                            |
  +-----------------+-----------------------------------------------------+
  | .panel.canvas   | matplotlib.backends.backend_wxagg.FigureCanvasWxAgg |
  +-----------------+-----------------------------------------------------+

Note that the `cursor_history` attribute will be a list of (`x`, `y`,
`timestamp`) values with `x` and `y` being in "user coordinates,
`timestamp` being the Unix timestamp for each even of pressing the
left mouse button on the plot. The most recent event will be in
`cursor_history[0]`, and the list will be in descending time
order. Only the most recent 100 cursor events will be retained.

Each new plot will clear the `cursor_history`.

.. autofunction:: get_image_window

As with :class:`wx.PlotFrame`, the returned :class:`wx.ImageFrame` will
have the same principle attributes to access the matplotlib Axes and Canvas
objects.
