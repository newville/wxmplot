
==========================================================
Speciality WXMPLOT displays
==========================================================

There are a few custom classes for speciality plots included in
wxmplot.  Since these build on the :class:`PlotPanel` and
:class:`ImagePanel` clases, these are described briefly here and an
example shown for each. 


MultiPlotFrame
==========================================================

.. class:: MultiPlotFrame(parent, rows=1, cols=1, framesize=(600, 350), **kws)

A MultiPlotFrame supports a grid of :class:`PlotPanel` on a single plot frame.

This supports the standard methods from :class:`PlotPanel`, with each
method taking and additional `panel` keyword argument that contains a
two-element tuple for the address of that panel in the grid of
:class:`PlotPanel` .  The address starts at (0, 0) for the upper left
plot panel, and counts to left to right and top to bottom.


.. method:: plot(self,x,y, panel=(0, 0), **kws)

   plot to specified panel.

.. method:: plot(self,x,y, panel=(0, 0), **kws)

   overplot to specified panel.
 
.. method:: clear(self, panel=(0, 0))
   
   clear plot in specified panel

.. method:: configure(self, panel=(0, 0))
   
   configure plot in specified panel

Many more methods are supported -- essentially all of those for :class:`PlotFrame`.

MultiPlotFrame Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


.. literalinclude:: ../examples/multiplot.py

This gives a window with a plot that looks like this:

.. image:: images/multiplot.png
   :width: 85 %


StackedPlotFrame
==========================================================

.. class:: StackedPlotFrame(parent, framesize=(850, 450), panelsize=(550, 450), ratio=3, **kws)

This supports two :class:`PlotPanel`s stacked on top of one another,
and sharing an X axis.  Since the two plots are meant to share axes,
there is very little space between the plots, so that they share axes
labels.  Furthermore, zooming in on either plot panel zooms into the
corresponding X range for both panels. qThe `ratio` parameter sets the
ratio of the height of the top panel to the height of the bottom
panel.


:class:`StackedPlotFrame` supports most of the methods of
:class:`PlotFrame`, with the specific panel addressed either as
`panel='top'` or `panel='bot'`.

.. method:: plot(self,x,y, panel='top', **kws)

   plot to specified panel.

.. method:: plot(self,x,y, panel='top', **kws)

   overplot to specified panel.
 
.. method:: clear(self, panel='top')
   
   clear plot in specified panel

.. method:: configure(self, panel='top')
   
   configure plot in specified panel


StackedPlotFrame Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../examples/stackedplot.py

This gives a window with a plot that looks like this:

.. image:: images/stackedplot.png
   :width: 70 %

ImageMatrixFrame
==========================================================

.. class:: ImageMatrixFrame(parent, size=(900, 600), **kws)

An :class:`ImageMatrixFrame` supports the simultaneous display of 2
related images, such as 2-dimensional data taken at different
wavelengths or at different sampling times.  The display is presented
as a 2 x 2 grid, with the individual images displayed along the
diagonal (upper left to lower right).  These can be shown in any of
the simple color schemes of (red, green, blue, magenta, cyan, or
yellow), with user-controllable levels.

The upper right panel shows the superposition of the two individual
images.  The lower left panel shows the simple scatter plot of the
intensities of each image for every pixel in the image, illustrating
the correlation between the two images.

The user can zoom in on any of the images, and the other panels will
follow that zoom level.  Using the scatter plot, the user can draw a
lasso around any of the pixels.  These will then be highlighted on the
superposition image in the upper right panel.


.. method:: display( map1, map2, title=None, name1='Map1', name2='Map2',  xlabel='x', ylabel='y', x=None, y=None)

display two images or maps on the :class:`ImageMatrixFrame`


ImageMatrixFrame Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../examples/imagematrix.py

This gives a window with a plot that looks like this:

.. image:: images/imagematrix.png
   :width: 85 %


