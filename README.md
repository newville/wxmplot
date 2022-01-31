[![Version](https://img.shields.io/pypi/v/wxmplot.svg)](https://pypi.org/project/wxmplot)
[![Downloads](https://pepy.tech/badge/wxmplot/month)](https://pepy.tech/project/wxmplot)


wxmplot provides advanced `wxPython`_ widgets for plotting and image display
of numerical data based on `matplotlib`_. While `matplotlib`_ provides
excellent general purpose plotting functionality and supports many GUI and
non-GUI backends it does not have a very tight integration with any
particular GUI toolkit. With a large number of plotting components and
options, it is not easy for programmers to select plotting options for every
stuation and not easy for end users to manipulate `matplotlib`_ plots.
Similarly, while `wxPython`_ has some plotting functionality, it has nothing
as good or complete as `matplotlib`_. The wxmplot package attempts to bridge
that gap.  With the plotting and image display Panels and Frames from
wxmplot, programmers are able to provide plotting widgets that make it easy
for end users to customize plots and interact with their data.

WXMplot provides wx.Panels for basic 2D line plots and image display that are
richly featured and provide end-users with interactivity (zooming, reading
positions, rotating images) and customization (line types, labels, marker
type, colors, and color tables) of the graphics without having to know
matplotlib.  wxmplot does not expose all of matplotlib's capabilities, but
does provide 2D plotting and image display Panels and Frames that are easy to
add to wxPython applications to handle many common plotting and image display
needs.

The wxmplot package is aimed at programmers who want to include high quality
scientific graphics in their applications that can be manipulated by the
end-user.  If you're a python programmer who is comfortable writing complex
pyplot scripts or plotting interactively from IPython, this package may seem
too limiting for your needs.  On the other hand, wxmplot provides more and
and better customizations than matplotlib's basic navigation toolbars.

The main widigets provided by wxmplot are:

	  PlotPanel: wx.Panel for basic 2-D line plots (roughly matplotlib `plot`)

	  PlotFrame: wx.Frame containing a PlotPanel

	  ImagePanel: wx.Panel for image display (roughly matplotlib `imshow`)

	  ImageFrame: wx.Frame containing ImagePanel

2D Line plotting with PlotPanel  /PlotFrame
------------------------------------

 PlotPanel and PlotFrame give the end-user the ability  to:

   1. display x, y coordinates (left-click)
   2. zoom in on a particular region of the plot (left-drag)
   3. customize titles, labels, legend, color, linestyle, marker,
	  and whether a grid is shown.  A separate configuration frame
	  is used to set these attributes.
   4. save high-qualiy plot images (as PNGs), copy to system
	  clipboard, or print.

For the programmer, these provide simple plotting methods:

   plot(x,y):  start a new plot, and plot data x,y

Some of the optional arguments (all keyword/values) include

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

Image Display with ImagePanel and ImageFrame
------------------------------------------

This displays a numpy array as an greyscale or false color image.  The end
user can zoom in, rotate, or flip the image, and adjust the smoothing of
the image and adjust the color table and intensity scale.

Programmatically, one can make the same adjustments to an ImagePanel by
changing its configuaration attributes and running the redraw() method.

=====

last update: 2018-Oct-13   Matthew Newville <newville@cars.uchicago.edu>
