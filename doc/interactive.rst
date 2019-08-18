
==========================================================
:mod:`wxmplot.interactive`:  Interactive wxmplot displays
==========================================================

.. module:: interactive

The :mod:`interactive` modules provides simple, entry-level functions for
plotting X/Y data and for image display.  These are similar in aim to the
`matplotlib.pyplot` methods such as :func:`pyplot.plot` and
:func:`pyplot.imshow`.  The functions are not drop-in replacements for
those functions, as the syntax for the options are different, following
:mod:`plotpanel.plot`. and :mod:`imagepanel.display`, and the interactivity
provided is dramatically different (we might even say better).

One important difference is that when using the functions here such as
:func:`plot` and :func:`imshow` in an interactive Python session, the
displays are created and shown immediately, and the Python prompt is
returned for further processing.  That is, there is no need for
:func:`pyplot.show` to render the display and block the Python session.  On
the other hand, if running from a script, you can suspend the script and
allow interaction with the displays with :func:`wxloop`, which will block
execution until all of the window displays have been closed.


In addition, it is very easy to plot multiple
traces, either on the same plot dispay windows or on completely new and
independent display windows.


.. function:: plot(x, y, **kws)

   plot `y` vs `x` data.   This takes many optional arguments, including
   essentially all those of :mod:`plotpanel.plot`.


.. literalinclude:: ../examples/leftright.py

and gives a plot that looks like this...



.. function:: imshow(imgdata, **kws)

   display a false-color map of a 2D numerical array. This takes many optional arguments, including
   essentially all those of :mod:`imagepanel.display`.


.. function:: wxloop()

   suspend the Python interpreter with a wxPython main loop.  This allows
   complete interactivity with the display windows and will only return
   when all of the displays are destroyed.
