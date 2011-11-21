
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

   :param parent: wx parent object.
   :param size:   figure size in inches.
   :param dpi:    dots per inch for figure.
   :param messenger: function for accepting output messages.
   :type messenger: callable or ``None``
   :param data_callback: function to call with new data, on :meth:`display`
   :type data_callback: callable or ``None``

   The *size*, and *dpi* arguments are sent to matplotlib's
   :class:`Figure`.  The *messenger* should should be a function that
   accepts text messages from the panel for informational display.  The
   default value is to use :func:`sys.stdout.write`.

   The *data_callback* is useful if some parent frame wants to know if the
   data has been changed with :meth:`display`.  :class:`ImageFrame` uses
   this to display the intensity max/min values.

   Extra keyword parameters are sent to the wx.Panel.

   The configuration settings for an image (its colormap, smoothing,
   orientation, and so on) are controlled through configuration
   attributes.

:class:`ImagePanel` methods
====================================================================

.. method:: display(data[, x=None[, y=None[, **kws]]])

   display a new image from the 2-D numpy array *data*.  If provided, the
   *x* and *y* values will be used for display purposes, as to give scales
   to the pixels of the data.

   Additional keyword arguments will be sent to a *data_callback* function,
   if that has been defined.

.. method: clear()

  clear the image

.. method: redraw()

  redraw the image, as when the configuration attributes have been changed.

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

These options are all available programmatically as well, by setting the
configuration attributes and redrawing the image.

.. class:: ImageFrame(parent[, size=(550, 450)[, **kws]])


   Create an Image Frame, a :class:`wx.Frame`.


Image configuration with :class:`ImageConfig`
==============================================================

To change any of the attributes of the image on an :class:`ImagePanel`, you
can set the corresponding attribute of the panel's :attr:`conf`.   That is,
if you create an :class:`ImagePanel`, you can set the colormap with::

    import matplotlib.cm as cmap
    im_panel = ImagePanel(parent)
    im_panel.display(data_array)

    # now change colormap:
    im_panel.conf.cmap = cmap.cool
    im_panel.redraw()

    # now rotate the image by 90 degrees (clockwise):
    im_panel.conf.rot = True
    im_panel.redraw()

For a :class:`ImageFrame`, you can access this attribute as *frame.panel.conf.cmap*.

The list of configuration attributes and their meaning are given in the
:ref:`Table of Image Configuration attributes <imageconf_table>`

.. _imageconf_table:

Table of Image Configuration attributes:  All of these are members of the
*panel.conf* object, as shown in the example above.

  +----------------+------------+---------+---------------------------------------------+
  | attribute      |   type     | default | meaning                                     |
  +================+============+=========+=============================================+
  | rot            | bool       | False   | rotate image 90 degrees clockwise           |
  +----------------+------------+---------+---------------------------------------------+
  | flip_ud        | bool       | False   | flip image top/bottom                       |
  +----------------+------------+---------+---------------------------------------------+
  | flip_lr        | bool       | False   | flip image left/right                       |
  +----------------+------------+---------+---------------------------------------------+
  | log_scale      | bool       | False   | display log(image)                          |
  +----------------+------------+---------+---------------------------------------------+
  | auto_intensity | bool       | True    | auto-scale the intensity                    |
  +----------------+------------+---------+---------------------------------------------+

cmap cmap_reverse interp xylims cmap_lo cmap_hi int_lo int_hi

Examples and Screenshots
====================================================================

A basic plot from a :class:`ImageFrame` looks like this:

.. image:: images/imagedisplay.png

This screenshot (from Mac OS X) doesn't show the top menu, which includes
menus for rotating or flipping the image, selecting an interpolation
scheme, or saving PNG images of either the image or the colormap.
