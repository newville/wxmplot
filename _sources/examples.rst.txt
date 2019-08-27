.. _ch_examples:

==========================================================
wxmplot Examples
==========================================================

The :ref:`ch_overview` showed a few illustrative  examples using `wxmplot`.
Here we show a few more examples.  These and more are given in the *examples*
directory in the source distribution kit.


Examples not shown here
----------------------------------

Several examples are not shown here either because they show many plots or are
otherwise more complex.  They are worth trying out.

*demo.py* will show several 2D Line plot examples, including a plot which uses
a timer to simulate a dynamic plot, updating the plot as fast as it can -
typically 10 to 30 times per second, depending on your machine.

*stripchart.py* also shows a dynamic, time-based plot.

*theme_compare.py* renders the same plot with a selection of different themes.

*image_scroll.py* shows an updating set of images on a single display.
Perhaps surprisingly, this can be faster than updating the 2D line plots.


Scatterplot Example
-------------------------

An example scatterplot can be produced with a script like this:

.. literalinclude:: ../examples/scatterplot.py

and gives a plot (after having selected by "lasso"ing) that looks like this:

.. image:: images/scatterplot.png
   :width: 85 %

Plotting with errorbars
----------------------------

An example plotting with error bars:


.. literalinclude:: ../examples/errorbar.py

gives:

.. image:: images/errorbar.png
   :width: 85 %

Plotting data from a datafile
-----------------------------------------

Reading data with `numpy.loadtext` and plotting:


.. literalinclude:: ../examples/plot_fromdatafile.py

gives:

.. image:: images/datafile_plot.png
   :width: 85 %


Using Left and Right Axes
----------------------------

An example using both right and left axes with different scales can be
created with:

.. literalinclude:: ../examples/leftright.py

and gives a plot that looks like this:

.. image:: images/two_axes.png
   :width: 85 %



Displaying and image of a TIFF file
--------------------------------------

Reading a TIFF file and showing the image:


.. literalinclude:: ../examples/tiff_display.py

gives:

.. image:: images/tifffile_image.png
   :width: 85 %


3-Color Image
-----------------

If the data array has three dimensions, and has a shape of (NY, NX, 3), it
is assumed to be a 3 color map, holding Red, Green, and Blue intensities.
In this case, the Image Frame will show sliders and min/max controls for
each of the three colors.

.. literalinclude:: ../examples/rgb_image.py

giving a plot that would look like this:

.. image:: images/image_3color.png
   :width: 85%

Note that there is also an Image->Toggle Background Color
(Black/White) menu selection that can switch the zero intensity color
between black and white.  The same image with a white background looks
like:


.. image:: images/image_3color_white.png
   :width: 85%

This gives a slightly different view of the same data, with results that
may be more suitable for printed documents and presentations.
