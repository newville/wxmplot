
The wxmplot python package provides simple, rich plotting widgets for
wxPython.  These are built on top of the matplotlib library, which provides
a wonderful library for 2D plots and image display.  The wxmplot package
does not attempt to expose all of matplotlib's capabilities, but does
provide widgets (wxPython panels) for basic 2D plotting and image display
that handle many use cases.  The widgets are designed to be very easy to
program with, and provide end-users with interactivity and customization of
the graphics without knowing matplotlib.

The principle objects provided by wxmplot are:

== PlotPanel:     a wx.Panel containing a 2D Plot.
== PlotFrame:    a wx.Frame containing a PlotPanel

For the end-user, these provides the abilities to:

   1. display x, y coordinates (left-click)
   2. zoom in on a particular region of the plot (left-drag)
   3. customize titles, labels, legend, color, linestyle, marker,
      and whether a grid is shown.  A separate window is used to
      set these attributes.
   4. save high-qualiy plot images (as PNGs), copy to system
      clipboard, or print.

For the programmer, these provide simple plotting methods:

   plot(x,y):  start a new plot, and plot data x,y
      optional arguments (all keyword/value types):
          color='Blue'       for any X11 color name, (rgb) tuple, or '#RRGGBB'
          style='solid'      'solid,'dashed','dotted','dot-dash'
          linewidth=2      integer 0 (no line) to 10
          marker='None'  any of a wide range of marker symbols
          markersize=8    integer 0 to 30
          xlabel=' '           label for X axis
          ylabel=' '           label for Y axis
          title=' '              title for top of PlotFrame
          grid=True         boolean for whether to show grid.

   oplot(x,y):  plot data x,y, on same plot as current data
      with optional arguments as plot()

   clear():      clear plot
   save_figure():     bring up file dialog for saving image of figure

== ImagePanel: a wx.Panel containing an image.
== ImageFrame: a wx.Frame containing an ImagePanel and widgets
     for configuring the image.

This displays a numpy array as an greyscale or false color image.  The end
user can zoom in, rotate, or flip the image, and adjust the smoothing of
the image and adjust the color table and intensity scale.

Programmatically, one can make the same adjustments to an ImagePanel by
changing its configuaration attributes and runnign the redraw() method.

=====

last update: 2011-Nov-20   Matt Newville <newville@cars.uchicago.edu>

