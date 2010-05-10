
MPlot: a collection of wxPython widgets for 2D Plotting and Image display, 
       using matplotlib and wx.

====
Contents:
  1. Directory Contents
  2. PlotFrame overview
  3. Notes, shortcomings and planned enhancements
  4. Suggested changes to matplotlib

====
Directory Contents:
   MPlot         package directory
   README        this file
   example_1.py  simplest example
   example_2.py  slightly more complicated example
   test.py       more elaborate example, including timing tests.

====
PlotFrame overview  

The principle object provided by MPlot are the PlotFrame and PlotPanel:

  MPlot.PlotFrame is a wxPython plotting component, that can be
  included in other applications to provide a simple way to plot
  2D data.  The PlotFrame provides capabilities for the user to:
     1. show X,Y coordinates (left-click)
     2. zoom in on a particular region of the plot (left-drag)
     3. customize titles, labels, legend, color, linestyle, marker,
        and whether a grid is shown.  A separate GUI window is used 
        to set these attributes.
     4. save plot images as PNGs, copy to system clipboard, or print.

For the programmer, MPlot.PlotFrame plots data in 1D Numeric (or numarray)
arrays, and provides these basic methods:
   plot(x,y):  start a new plot, and plot data x,y
      optional arguments (all keyword/value types):
          color='Blue'    for any X11 color name, (rgb) tuple, or '#RRGGBB'
          style='solid'   'solid,'dashed','dotted','dot-dash'
          linewidth=2     integer 0 (no line) to 10
          marker='None'   any of a wide range of marker symbols
          markersize=6    integer 0 to 30
          xlabel=' '      label for X Axis (MPlot text)    
          ylabel=' '      label for Y Axis (MPlot text)    
          title=' '       title for top of PlotFrame (MPlot text)    
          grid=True       boolean for whether to show grid.

   oplot(x,y):  plot data x,y, on same plot as current data
      optional arguments (all keyword/value types):
          color='Blue'    for any X11 color name, (rgb) tuple, or '#RRGGBB'
          style='solid'   'solid,'dashed','dotted','dot-dash'
          linewidth=2     integer 0 (no line) to 10
          marker='None'   any of a wide range of marker symbols
          markersize=6    integer 0 to 30

    clear():           clear plot
    save_figure():     bring up file dialog for saving image of figure
    set_statustext():  set text for statusbar.
    set_title():       set plot title
    set_xlabel():      set x label
    set_ylabel():      set y label

=====
Notes, shortcomings, and future work:

  1. The following matplotlib features are  not yet implemented,
     and are worth considering (no particular order):
       - error bars
       - automatic scaling for y-data with different ranges 
         (probably showing a second scale on the right side)
       - support for date data
       - different colors for marker interior/exterior
       - multiple subplots on a single PlotFrame/PlotPanel  
       

last update: 2005-Feb-05   Matt Newville <newville@cars.uchicago.edu>

