
==========================================================
:class:`ImagePanel`:  A wx.Panel for Image Display
==========================================================

The :class:`ImagePanel` class supports image display (ie, gray-scale and
false-color intensity maps for 2-D arrays.  As with :class:`PlotPanel`,
this is derived from a :class:`wx.Panel` and so can be included in a wx GUI
anywhere a :class:`wx.Panel` can be.  While the image can be customized
programmatically, the only interactivity built in to the
:class:`ImagePanel` is the ability to zoom in and out.

In contrast, an :class:`ImageFrame` provides many more ways to manipulate
an image, and will be discussed below.

.. class:: ImagePanel(parent[, size=(4.5, 4.0)[, dpi=96[, messenger=None[, data_callback=None[, **kws]]]]])

   Create an Image Panel, a :class:`wx.Panel`

:class:`ImageFrame`:  A wx.Frame for Image Display
==========================================================

In addition to providing a top-level window frame holding an
:class:`ImagePanel`, an :class:`ImageFrame` provides the end-user with many ways to
manipulate the image:

   1. display x, y, intensity coordinates (left-click)
   2. zoom in on a particular region of the plot (left-drag).
   3. change color maps.
   4. flip and rotate image.
   5. select optional smoothing interpolation.
   6. modify intensity scales.
   7. save high-qualiy plot images (as PNGs), copy to system clipboard, or print.

These options are all available programmatically as well.

.. class:: ImageFrame(parent[, size=(550, 450)[, **kws]])


   Create an Image Frame, a :class:`wx.Frame`.


Examples and Screenshots
====================================================================

A basic plot from a :class:`PlotFrame` looks like this:

.. image:: images/imagedisplay.png

This screenshot (from Mac OS X) doesn't show the top menu, which includes
menus for rotating or flipping the image, selecting an interpolation
scheme, or saving PNG images of either the image or the colormap.
