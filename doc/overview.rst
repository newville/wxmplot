
==========================================================
Overview:
==========================================================

.. module:: wxmplot

`wxmplot` provides simple functions for making 2D plots and displaying
image data.  It is not easy to convey the interactivity in a static
document, but I will try.


Let's start with a simple script using  :mod:`matplotlib.pyplot`::

    #!/usr/bin/python
    import numpy as np
    import matplotlib.pyplot as plt
    x  = 3.6*np.arange(101)
    yc = np.cos(np.pi*x/180)
    ys = np.sin(np.pi*x/180)

    plt.plot(x, ys, '-+', label='sin')
    plt.plot(x, yc, '-', label='cos')
    plt.title('sin(x) and cos(x)')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    plt.show()


which is pretty straight-forward and produces a plot like this (depending
somewhat on the backend being used):

.. image:: images/mpl_basic.png
   :width: 75 %

From this screen, moving the mouse around updates the display of x and y
values displayed to those of the mouse.  Clicking on the magnifying glass
icon and then clicking and dragging a box to zoom in.  allows the user to
zoom in on portions of the plot.  Clicking on the icon with 4 arrows allows
the user to pan to other parts of the data range.  Clicking on the icon
with 3 bars (equalizer?) allows the user to adjust the plot margins. The
diskette icon allows the user to save a PNG file of the plot display.  For
many uses, this is enough interaction.

With `wxmplot`, that script would be rewritten as::

    #!/usr/bin/python
    import numpy as np
    from wxmplot.interactive import plot
    x  = 3.6*np.arange(101)
    yc = np.cos(np.pi*x/180)
    ys = np.sin(np.pi*x/180)

    plot(x, ys, label='sin', marker='+', xlabel='x', ylabel='y',
         title='sin(x) and cos(x)', show_legend=True)
    plot(x, yc, label='cos')

and yield a similar plot on the left below:

.. image:: images/wxmplot_basic.png
   :width: 75 %

As with the `pyplot` example, moving the mouse around updates the display
of x and y values displayed to those of the mouse.  To zoom in on a region,
the user can simply click and drag to draw a box to zoom in.  The
Navigation Toolbar is gone, but there are more options for configuring the
plot either from the File and Options menus, as will be described in the
next section.

User Interaction and Configuring 2D line plots
==================================================

The plot displayed above supports a few basic user interactions.  First, as
mentioned above, the user can zoom in by drawing a box: Clicking the left
mouse button and dragging will draw a rectangular box, and releasing the
mouse button will zoom in to that rectangle.  This can be repeated multiple
time to continue zooming in. Typing "Ctrl-Z" (or "Apple-Z" for Mac OS X)
will zoom out to the previous zoom level, or until the show the full plot.

A second important user interaction is that when the Plot Legend is
displayed, clicking on the Legend entry for any trace will toggle whether
that trace is displayed. For the display in the example above this may not
be so important, but this ability to easily turn on and off traces can be
very useful when many traces are displayed.

Finally, Right-clicking with the Axes (that is the part of the Frame
showing the Data) will show a pop-up window that allows the user to quickly
Unzoom, Display the Plot Configuration Window, or Save the Image.

Each Plot Window will have a File and Option menu that gives even more
functionality.  From the File menu, the user can:

   * Save an image of the plot to a PNG file [Ctrl-S]
   * Copy the image to system clipboard so that it can be pasted
     into other applications [Ctrl-C].
   * Export the data in the plot to a plain text file [Ctrl-D]
   * Setup and preview printing.
   * Print the image [Ctrl-P]

From the Options menu, the user can:

   * Display the Plot Configuration Window to configure nearly any aspect of
      the Plot [Ctrl-K]
   * Un-Zoom all to the full data range [Ctrl-Z]
   * Toggle whether the Legend is displayed [Ctrl-L]
   * Toggle whether the Grid is displayed [Ctrl-G]
   * Select whether the X and Y Axes are Linear or Log Scale.
   * Perform some simple data transformations, to show the derivative
      :math:`dy/dx`, or :math:`yx`, :math:`yx^2`, :math:`y^2`,
      :math:`\sqrt{y}`, or :math:`1/y`.

The Configuration Window is a tabbed window with 4 panels to allow the user
to configure:

    * Colors and Line Properties
    * Ranges and Margins
    * Text, Labels, and Legend
    * Scatterplot displays


Color and Line Properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The **Colors and Line Properties** tab allows the user to configure the
basic colors for the plot.  This includes setting the plotting Theme.  Each
of the themes available (there are more than 25 themes available, about
half of them derived from the Seaborn themes) will reset all the default
colors for the plot components and for each line trace, and many of the
resource settings of `matplotlib`.  The themes and their color selections
are carefully chosen and aim to make pleasing and informative color
choices, some with special attention to color-blindness.

The user can change the colors for Text, Grid, Background, and Outer Frame,
and select whether the Grid is shown, whether the Legend is Shown, and
Whether the Top and Right Axes Spines are shown. The user can also set the
attributes for each trace: the label, color, line style, line width, symbol
to use for a marker, marker size, z-order, and join style for each trace
drawn can be customized.

.. image:: images/PlotConfig_LineProps.png
   :width: 85 %


Ranges and Margins Properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The **Ranges and Margins** tab allows the user to change the display data
ranges and the outer margins of the plot.  Here, the user can alsoe select a
Linear or Log scale for the X and Y axes.

The user can also set the exact X and Y ranges to show for the plot, or
allow
displayed, and allow precise control of the margins around the plot.

.. image:: images/PlotConfig_Ranges.png
   :width: 85 %


Text Properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The **Text and Labels** tab allows the user to set the title and labels for the
X and Y axes, and to adjust the fontsize for these text and the text shown
in the plot legend.  The legend can also be customized: whether it is
shown, it's location, and whether the legend entries can be clicked on to
toggle the display of the corresponding line.  The experimental "Draggable
Legend" option allows the user to drag the legend on the plot to fine-tune
its placement.



.. image:: images/PlotConfig_Text.png
   :width: 85 %



ScatterPlot Properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The **Scatterplot** tab allows the user to set the colors and marker sizes
for scatter plots.


.. image:: images/PlotConfig_Scatter.png
   :width: 85 %






From

Selecting that Configure choice, or Options->Configure from the
Menubar, or typing Ctrl-K will bring up a Plot Configuration Frame:


.. image:: images/PlotConfig_LineProps.png
   :width: 90 %









:mod:`interactive.plot` for 2D plotting of X, Y data and
:mod:`interactive.imshow` for displaying image data.  These functions are
similar to the :mod:`matplotlib.pyplot` methods :func:`pyplot.plot` and
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


An example of using :func:`wxmplot.interactive.plot` is:

.. literalinclude:: ../examples/basic_screenshot.py

which gives a plot that looks like this:


.. image:: images/basic_screenshot.png
   :width: 85 %

Displaying images with :func:`imshow` and :func:`contour`
==============================================================

#
# .. autofunction:: imshow
#
# .. autofunction:: contour
#
# Functions for working with the interactive windows
# ======================================================
#
# .. autofunction:: get_wxapp
#
# .. autofunction:: set_theme
#
# .. autofunction:: available_themes
#
# .. autofunction:: get_plot_window
#
# .. autofunction:: get_image_window
