.. _ch_comparisons:

.. _matplotlib:  https://matplotlib.org/

==========================================================
Comparisons of wxmplot with other Python Plotting tools
==========================================================

Disclaimer: this section is essentially opinion of the leasd author of
`wxmplot`. While biased, it also aims to be fair. If you have comments or
suggestions for improving this, please use the Github discussion page.

We believe that `wxmplot`, and especially :mod:`wxmplot.interactive` make
exploratory data analysis with Python particularly easy and useful.  Of
course, we are obviously biased towards `wxmplot`, but here we give a few
comparisons of `wxmplot` with some other tools and libraries for plotting
scientific data with Python.  We should be clear that most of the
high-quality graphics features come from `matplotlib`_, and that `wxmplot`
is an attempt to make the most common needs as easy, as beautiful, and as
interactive as possible.

For both exploratory data analysis and for displays of scientific data from
within data analysis applications, we value the following characteristics:

  1. **brevity**, or simplicity of code.  We're using Python because it is
     succint and elegant.

  2. **beauty**. The rendered plots should be high-quality with attractive
     fonts.  Ideally, images made would be directly suitable for
     presentations and publications.

  3. **interactivity**.  After the plot or image of data is rendered, we want
     to be able to manipulate and modify the display, including zooming in
     on certain portions of the data, changing scales, color schemes, line
     types, and even plot labels.  In fact, not only do we want to be able
     to do that, we want *users* of the plotting scripts and applications
     to be able to do that.

The comparisons we make with other packages are mostly in regard to these
three characteristics.  In all cases, the *interactivity* of data displayed
with `wxmplot` is simply unmatched as is the ability of the end-user to
manipulate the details of the display, including for basic line plots:

   1. change color, line widths, line types, marker types, marker sizes,
      display order for each "trace" (x, y pair) in the plot.

   2. change the color theme of the entire display, the color of each
      component of the display window, the size of the plot
      margins, how to set the data display range.

   3. whether and where a legend is shown, whether grid lines are shown,
      and whether the plot is enclosed in a full box or only the left and
      bottom axes are drawn.

   4. changing the label for each trace, and the title and label for each
      axis, including setting font sizes.

   5. changing whether each axis is displayed linearly or logarithmically,
      and apply common manipulations such as showing derivative or y*x,
      1/y, and so forth.

   6. copy image to the system clipboard, save image to PNG file, or send
      directly to a system printer.

For 2-D image display, users can lookup tables for mapping intensity to
color, set thresholds and contrast levels, as well as showing axes and
setting the size and location of a scalebar, and its label.  Images can be
flipped, rotated (and reset).  Smoothing of pixelated data can be adjusted.
Images can be toggled back-and-forth between "image mode" and "contour
mode".



Comparison with Matplotlib.pyplot
========================================

`wxmplot` use `matplotlib`.  Any aspect of "beauty" in `wxmplot` comes from
`matplotlib`, which makes plots and images of scientific data that are of
excellent quality.  Allowing `LaTeX` rendering for mathematical symbols and
expressions in labels is particularly helpful for plotting data from the
physical sciences.

Of course, `matplotlib` is much more comprehensive than `wxmplot` and
supports a number of plot types that `wxmplot` does not. `wxmplot` focuses
its attention on "Line Plots" and display of grey-scale and false-color
images, and essentially re-imagines the `pyplot` functions `plot` and
`imshow`. It also gives you access to the underlying `matplotlib` objects
so that you can add more complex components and manipulate the plot as
needed, assuming that you know the `matplotlib` interface.


In :ref:`ch_overview`, we give a brief comparsion of
:mod:`matplotlib.pyplot` and :mod:`wxmplot.plot` and will not repeat those
examples here.  From the point of view of "brevity" and "beauty", these are
approximately equal.  The `matplotlib` API is certainly much more common,
and deliberately mimicks the plotting functions in `matlab`, so will be
familiar to many people.  mod:`wxmplot.plot` puts a lot more arguments into
a single function call.

Plots made with `matplotlib.pyplot` have some interactivity and
customizability after the plot is displayed with its Navigation Toolbar, so
that users can read plot coordinates as the mouse moves around, zoom in and
out, pan around the plot area, and save the image.  `wxmplot` includes all
of those features, and has much more flexibility at run-time for the user
to be able to manipulate the display of the data.




Comparison with PLPlot
===============================

`PLPlot` (http://plplot.sourceforge.net/) is a general purpose plotting
library with bindings for many languages, including Python.  It supports
many plot types, including map displays which is outside the scope of
wxmplot. Since it is not specifically written for Python, it is not too
surprising that its Python interface is not quite as elegant as
`matplotlib` or `wxmplot`.  Their Python example for a basic 2-D plot is::


    from numpy import *

    NSIZE = 101

    def main(w):
	xmin = 0.
	xmax = 1.
	ymin = 0.
	ymax = 100.

	# Prepare data to be plotted.
	x = arange(NSIZE) / float( NSIZE - 1 )
	y = ymax*x**2

	# Create a labelled box to hold the plot.
	w.plenv( xmin, xmax, ymin, ymax, 0, 0 )
	w.pllab( "x", "y=100 x#u2#d", "Simple PLplot demo of a 2D line plot" )

	# Plot the data that was prepared above.
	w.plline( x, y )

	# Restore defaults
	# Must be done independently because otherwise this changes output files
	# and destroys agreement with C examples.
	#w.plcol0(1)

which is not too bad from the point of view of "brevity".  But it is
actually not complete code, so it is not clear how to actually run the
example -- some sort of `import` must be missing.  The result at
http://plplot.sourceforge.net/examples-data/demo00/x00.01.png is not too
bad, though a bit hard to call "beautiful".  I believe `PLPlot` has
essentially no interactivity for the plots themselves, though some programs
may be able to have the user advance through a series of plots.

Converting that to `wxmplot` would be::

    import numpy as np
    import wxmplot.interactive as wi

    x = np.linspace(0, 1, 101)
    y = 100*x**2

    wi.plot(x, y, color='red', xlabel='x', ylabel=r'$y=100 x^2$',
	    title="Simple PLplot demo of a 2D line plot", theme='dark')


and give a plot of

.. _plot_compare_plplot:

    .. image:: images/plot_compare_plplot.png
       :width: 75%


Comparison with Dislin
===============================

Like `PLPlot`, `Dislin` (https://dislin.de/) is a plotting library with
bindings for many languages, including Python. It also supports many plot
types, including 3-d volume displays which is outside the scope of
wxmplot. Since it is not specifically written for Python, it is not too
surprising that its Python interface is not quite as elegant as
`matplotlib` or `wxmplot`.  Their Python example for a basic 2-D plot is::


    mport math
    import dislin

    n = 101
    f = 3.1415926 / 180.
    x = range (n)
    y1 = range (n)
    y2 = range (n)
    for i in range (0,n):
      x[i] = i * 3.6
      v = i * 3.6 * f
      y1[i] = math.sin (v)
      y2[i] = math.cos (v)

    dislin.scrmod ('revers')
    dislin.metafl ('xwin')
    dislin.disini ()
    dislin.complx ()
    dislin.pagera ()

    dislin.axspos (450, 1800)
    dislin.axslen (2200, 1200)

    dislin.name   ('X-axis', 'X')
    dislin.name   ('Y-axis', 'Y')

    dislin.labdig (-1, 'X')
    dislin.ticks  (9, 'X')
    dislin.ticks  (10, 'Y')

    dislin.titlin ('Demonstration of CURVE', 1)
    dislin.titlin ('SIN (X), COS (X)', 3)

    ic = dislin.intrgb (0.95, 0.95, 0.95)
    dislin.axsbgd (ic)

    dislin.graf   (0., 360., 0., 90., -1., 1., -1., 0.5)
    dislin.setrgb (0.7, 0.7, 0.7)
    dislin.grid   (1,1)

    dislin.color  ('fore')
    dislin.height (50)
    dislin.title  ()

    dislin.color  ('red')
    dislin.curve  (x, y1, n)
    dislin.color  ('green')
    dislin.curve  (x, y2, n)
    dislin.disfin ()

with a result at https://dislin.de/exa_curv.html.  For "brevity" and
"beauty", this is difficult to recommend.  I believe there is essentially
no interactivity. Converting that to `wxmplot` would be::


    import numpy as np
    import wxmplot.interactive as wi

    x  = 3.6*np.arange(101)
    y1 = np.cos(np.pi*x/180)
    y2 = np.sin(np.pi*x/18)0

    wi.plot(x, y1, color='red', xlabel='x', ylabel='y',
	    title='DISLIN Comparison\nsin(x) and cos(x)')
    wi.plot(x, y2, color='green3', marker='+')


and give a plot of

.. _plot_compare_dislin:

    .. image:: images/plot_compare_dislin.png
       :width: 75%


Comparison with WxPlot
===============================



Comparison with PyQtGraph and PyQt/matplotlib
==================================================

In this section we compare to tutorials at
https://www.pythonguis.com/tutorials/ which describe using using GUIs with
the PyQt and PySide family of GUI toolkits based on Qt.  The existence of
this chapter was inspired by seeing these tutorials, especially advertised
as being aimed at showing how to make "simple and highly interactive plots"
plots.

I agree strongly with the quote introducing these tutorials::

    One of the major strengths of Python is in exploratory data science and
    visualization, using tools such as Pandas, numpy, sklearn for data
    analysis and matplotlib plotting.

and I believe the authors of those tutorials mean well, but when

    In this tutorial we'll walk through the first steps of creating a plot
    widget with PyQtGraph

I am obligated to reply "There has to be a better way", and demostrate
below that, indeed, there is.  The tutorials make a slight distinction
between using PySide and PyQt -- I'll ignore that below.

Plotting with PyQtGraph
---------------------------


The tutorials at
https://www.pythonguis.com/tutorials/pyqt6-plotting-pyqtgraph/ and
https://www.pythonguis.com/tutorials/pyside6-plotting-pyqtgraph/
start with a "simple" plot. There code is::

    from PyQt6 import QtWidgets
    from pyqtgraph import PlotWidget, plot
    import pyqtgraph as pg
    import sys  # We need sys so that we can pass argv to QApplication
    import os

    class MainWindow(QtWidgets.QMainWindow):

	def __init__(self, *args, **kwargs):
	    super(MainWindow, self).__init__(*args, **kwargs)

	    self.graphWidget = pg.PlotWidget()
	    self.setCentralWidget(self.graphWidget)

	    hour = [1,2,3,4,5,6,7,8,9,10]
	    temperature = [30,32,34,32,33,31,29,32,35,45]

	    # plot data: x, y values
	    self.graphWidget.plot(hour, temperature)


    def main():
	app = QtWidgets.QApplication(sys.argv)
	main = MainWindow()
	main.show()
	sys.exit(app.exec())


    if __name__ == '__main__':
	main()

producing a very, very basic plot (there are no links to the images
available).  That is 20 lines of code, and three levels of indendation! The
data is buried in a class!  Yikes!

With `wxmplot`, that becomes:

    from wxmplot import PlotApp

    hour = [1,2,3,4,5,6,7,8,9,10]
    temperature = [30,32,34,32,33,31,29,32,35,45]

    plotapp = PlotApp()
    plotapp.plot(hour, temperature)
    plotapp.run()

That is 6 lines of code -- 30% of the PyQt example.  Yes, that matters,
especially for a stated goal of "exploratory data analysis".  Importantly, the
data is not buried in the initialization of the main Window.  The resulting
plot from `wxmplot` is

.. _plot_compare_qttutorial1:

    .. image:: images/plot_compare_qttutorial1.png
       :width: 75%


As far as I can 	      






Plotting with Matplotlib
-------------------------------

https://www.pythonguis.com/tutorials/pyqt6-plotting-matplotlib/

https://www.pythonguis.com/tutorials/pyside6-plotting-matplotlib/
