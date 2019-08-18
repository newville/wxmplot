#!/usr/bin/env python
"""
Interactive wxmplot

provides simple 'plot()', 'oplot()', and 'imshow()' functions to python interpreter

 plot:  display a simple X, Y line plot to an enhanced, configurable Plot Frame
 oplot: overplot a line plot on an existing Plot Frame

 imshow: display image of 2D array data on a configurable Image Display Frame.

"""

import time
import os
import sys
import wx

from . import inputhook


from .plotframe import PlotFrame
from .imageframe import ImageFrame
from .stackedplotframe import StackedPlotFrame

from matplotlib.axes import Axes
HIST_DOC = Axes.hist.__doc__

IMG_DISPLAYS = {}
PLOT_DISPLAYS = {}
MAX_WINDOWS = 20
MAX_CURSHIST = 100

WXAPP = None

def get_wxapp():
    global WXAPP
    if WXAPP is None:
        _app = wx.GetApp()
        if _app is not None:
            WXAPP = _app
    if WXAPP is None:
        WXAPP = wx.App(redirect=False, clearSigInt=False)


class PlotDisplay(PlotFrame):
    def __init__(self, wxparent=None, window=1, size=None, **kws):
        get_wxapp()
        PlotFrame.__init__(self, parent=None, size=size,
                           output_title='plot',
                           exit_callback=self.onExit, **kws)

        self.Show()
        self.Raise()
        self.panel.cursor_callback = self.onCursor
        self.panel.cursor_mode = 'zoom'
        self.window = int(window)
        self.cursor_hist = []
        self.panel.canvas.figure.set_facecolor('#FDFDFB')
        if window not in PLOT_DISPLAYS:
            PLOT_DISPLAYS[window] = self

    def onExit(self, o, **kw):
        if self.window in PLOT_DISPLAYS:
            PLOT_DISPLAYS.pop(self.window)
        self.Destroy()

    def onCursor(self, x=None, y=None, **kw):
        self.cursor_hist.insert(0, (x, y, time.time()))
        if len(self.cursor_hist) > MAX_CURSHIST:
            self.cursor_hist = self.cursor_hist[:MAX_CURSHIST]

class ImageDisplay(ImageFrame):
    def __init__(self, wxparent=None, window=1, size=None, **kws):
        get_wxapp()
        ImageFrame.__init__(self, parent=None, size=size,
                                  exit_callback=self.onExit, **kws)
        self.Show()
        self.Raise()
        self.cursor_hist = []
        self.panel.cursor_callback = self.onCursor
        self.window = int(window)
        if self.window not in IMG_DISPLAYS:
            IMG_DISPLAYS[self.window] = self

    def onExit(self, o, **kw):
        if self.window in IMG_DISPLAYS:
            IMG_DISPLAYS.pop(self.window)
        self.Destroy()

    def onCursor(self,x=None, y=None, ix=None, iy=None, val=None, **kw):
        self.cursor_hist.insert(0, (x, y, ix, iy, time.time()))
        if len(self.cursor_hist) > MAX_CURSHIST:
            self.cursor_hist = self.cursor_hist[:MAX_CURSHIST]

def getPlotDisplay(win=1, wxparent=None, size=None, wintitle=None):
    """make a plot window"""
    win = max(1, min(MAX_WINDOWS, int(abs(win))))
    if win in PLOT_DISPLAYS:
        display = PLOT_DISPLAYS[win]
    else:
        display = PlotDisplay(window=win, wxparent=wxparent, size=size)
    if wintitle is None:
        wintitle   = 'Plot Window %i' % win
    display.SetTitle(wintitle)
    return display

def getImageDisplay(win=1, wxparent=None, size=None, wintitle=None):
    """make an image window"""
    win = max(1, min(MAX_WINDOWS, int(abs(win))))
    if win in IMG_DISPLAYS:
        display = IMG_DISPLAY[win]
    else:
        display = ImageDisplay(window=win, wxparent=wxparent, size=size)
    if wintitle is None:
        wintitle  = 'Image Window %i' % win
    display.SetTitle(wintitle)
    return display


def plot(x,y, win=1, new=False, wxparent=None, size=None, wintitle=None, **kws):
    """plot(x, y[, win=1], options])

    Plot trace of x, y arrays in a Plot Frame, clearing any plot currently in the Plot Frame.

    Parameters:
    --------------
        x :  array of ordinate values
        y :  array of abscissa values (x and y must be same size!)

        win: index of Plot Frame (0, 1, etc).  May create a new Plot Frame.
        new: bool  (default False) for whether to start a new plot.
        label: label for trace

        size:  size of window
        wintitle: title for window frame

        **kws : keywords to pass to wxmplot.PlotPanel.plot()

        title:  title for Plot
        xlabel: x-axis label
        ylabel: y-axis label
        ylog_scale: whether to show y-axis as log-scale (True or False)
        grid: whether to draw background grid (True or False)

        color: color for trace (name such as 'red', or '#RRGGBB' hex string)
        style: trace linestyle (one of 'solid', 'dashed', 'dotted', 'dot-dash')
        linewidth:  integer width of line
        marker:  symbol to draw at each point ('+', 'o', 'x', 'square', etc)
        markersize: integer size of marker

        drawstyle: style for joining line segments

        dy: array for error bars in y (must be same size as y!)
        yaxis='left'??

    See Also: oplot, newplot
    """
    plotter = getPlotDisplay(wxparent=wxparent, win=win, size=size,
                             wintitle=wintitle)
    if plotter is None:
        return
    plotter.Raise()
    if new:
        plotter.plot(x, y, **kws)
    else:
        plotter.oplot(x, y, **kws)
    return plotter

def update_trace(x, y, trace=1, win=1, wxparent=None, **kws):
    """update a plot trace with new data, avoiding complete redraw"""
    plotter = getPlotDisplay(wxparent=wxparent, win=win)
    if plotter is None:
        return
    plotter.Raise()
    trace -= 1 # wxmplot counts traces from 0
    plotter.panel.update_line(trace, x, y, draw=True, **kws)

def plot_setlimits(xmin=None, xmax=None, ymin=None, ymax=None, win=1, wxparent=None):
    """set plot view limits for plot in window `win`"""
    plotter = getPlotDisplay(wxparent=wxparent, win=win)
    if plotter is None:
        return
    plotter.panel.set_xylims((xmin, xmax, ymin, ymax))

def oplot(x, y, win=1,  wxparent=None, **kws):
    """oplot(x, y[, win=1[, options]])

    Plot 2-D trace of x, y arrays in a Plot Frame, over-plotting any
    plot currently in the Plot Frame.

    This is equivalent to
    plot(x, y[, win=1[, new=False[, options]]])

    See Also: plot, newplot
    """
    kws['new'] = False
    return plot(x, y, win=win, wxparent=wxparent, **kws)

def newplot(x, y, win=1, wxparent=None, wintitle=None, **kws):
    """newplot(x, y[, win=1[, options]])

    Plot 2-D trace of x, y arrays in a Plot Frame, clearing any
    plot currently in the Plot Frame.

    This is equivalent to
    plot(x, y[, win=1[, new=True[, options]]])

    See Also: plot, oplot
    """
    return plot(x, y, win=win, new=True, wxparent=wxparent, wintitle=wintitle, **kws)

def plot_text(text, x, y, win=1, side='left', size=None,
              rotation=None, ha='left', va='center',
              wxparent=None,  **kws):
    """plot_text(text, x, y, win=1, options)

    add text at x, y coordinates of a plot

    Parameters:
    --------------
        text:  text to draw
        x:     x position of text
        y:     y position of text
        win:   index of Plot Frame (0, 1, etc).  May create a new Plot Frame.
        side:  which axis to use ('left' or 'right') for coordinates.
        rotation:  text rotation. angle in degrees or 'vertical' or 'horizontal'
        ha:    horizontal alignment ('left', 'center', 'right')
        va:    vertical alignment ('top', 'center', 'bottom', 'baseline')

    See Also: plot, oplot, plot_arrow
    """
    plotter = getPlotDisplay(wxparent=wxparent, win=win, size=size)
    if plotter is None:
        return
    plotter.Raise()
    plotter.add_text(text, x, y, side=side,
                     rotation=rotation, ha=ha, va=va, **kws)

def plot_arrow(x1, y1, x2, y2, win=1, side='left',
                shape='full', color='black',
                width=0.00, head_width=0.05, head_length=0.25,
                wxparent=None, size=None, **kws):

    """plot_arrow(x1, y1, x2, y2, win=1, **kws)

    draw arrow from x1, y1 to x2, y2.

    Parameters:
    --------------
        x1: starting x coordinate
        y1: starting y coordinate
        x2: ending x coordinate
        y2: ending y coordinate
        side: which axis to use ('left' or 'right') for coordinates.
        shape:  arrow head shape ('full', 'left', 'right')
        color:  arrow color ('black')
        width:  width of arrow line (in points. default=0.0)
        head_width:  width of arrow head (in points. default=0.05)
        head_length:  length of arrow head (in points. default=0.25)
        overhang:    amount the arrow is swept back (in points. default=0)
        win:  window to draw too

    See Also: plot, oplot, plot_text
    """
    plotter = getPlotDisplay(wxparent=wxparent, win=win, size=size)
    if plotter is None:
        return
    plotter.Raise()
    plotter.add_arrow(x1, y1, x2, y2, side=side, shape=shape,
                      color=color, width=width, head_length=head_length,
                      head_width=head_width, **kws)

def plot_marker(x, y, marker='o', size=4, color='black', label='_nolegend_',
                wxparent=None, win=1,  **kws):

    """plot_marker(x, y, marker='o', size=4, color='black')

    draw a marker at x, y

    Parameters:
    -----------
        x:      x coordinate
        y:      y coordinate
        marker: symbol to draw at each point ('+', 'o', 'x', 'square', etc) ['o']
        size:   symbol size [4]
        color:  color  ['black']

    See Also: plot, oplot, plot_text
    """
    plotter = getPlotDisplay(wxparent=wxparent, win=win, size=None)
    if plotter is None:
        return
    plotter.Raise()
    plotter.oplot([x], [y], marker=marker, markersize=size, label=label,
                 color=color, wxparent=wxparent,  **kws)

def plot_axhline(y, xmin=0, xmax=1, win=1, wxparent=None,
                  size=None, delay_draw=False,  **kws):
    """plot_axhline(y, xmin=None, ymin=None, **kws)

    plot a horizontal line spanning the plot axes
    Parameters:
    --------------
        y:      y position of line
        xmin:   starting x fraction (window units -- not user units!)
        xmax:   ending x fraction (window units -- not user units!)
    See Also: plot, oplot, plot_arrow
    """
    plotter = getPlotDisplay(wxparent=wxparent, win=win, size=size)
    if plotter is None:
        return
    plotter.Raise()
    if 'label' not in kws:
        kws['label'] = '_nolegend_'
    plotter.panel.axes.axhline(y, xmin=xmin, xmax=xmax, **kws)
    if delay_draw:
        plotter.panel.canvas.draw()

def plot_axvline(x, ymin=0, ymax=1, win=1, wxparent=None, size=None,
                 delay_draw=False, **kws):
    """plot_axvline(y, xmin=None, ymin=None, **kws)

    plot a vertical line spanning the plot axes
    Parameters:
    --------------
        x:      x position of line
        ymin:   starting y fraction (window units -- not user units!)
        ymax:   ending y fraction (window units -- not user units!)
    See Also: plot, oplot, plot_arrow
    """
    plotter = getPlotDisplay(wxparent=wxparent, win=win, size=size)
    if plotter is None:
        return
    plotter.Raise()
    if 'label' not in kws:
        kws['label'] = '_nolegend_'
    plotter.panel.axes.axvline(x, ymin=ymin, ymax=ymax, **kws)
    if not delay_draw:
        plotter.panel.canvas.draw()


def hist(x, bins=10, win=1, new=False, wxparent=None, size=None,
         force_draw=True, *args, **kws):

    plotter = getPlotDisplay(wxparent=wxparent, win=win, size=size)
    if plotter is None:
        return
    plotter.Raise()
    if new:
        plotter.panel.axes.clear()

    out = plotter.panel.axes.hist(x, bins=bins, **kws)
    plotter.panel.canvas.draw()
    return out

def imshow(map, x=None, y=None, colormap=None, win=1, wxparent=None,
            size=None, **kws):

    """imshow(map[, options])

    Display an 2-D array of intensities as a false-color map

    map: 2-dimensional array for map
    """
    img = getImageDisplay(wxparent=wxparent, win=win, size=size)
    if img is not None:
        img.display(map, x=x, y=y, colormap=colormap, **kws)
    return img

def _contour(map, x=None, y=None, **kws):
    """contour(map[, options])

    Display an 2-D array of intensities as a contour plot

    map: 2-dimensional array for map
    """
    kws.update(dict(style='contour'))
    imshow(map, x=x, y=y, **kws)
