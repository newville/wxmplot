#!/usr/bin/env python
"""
Interactive wxmplot

 provides simple 'plot()' and 'imshow()' functions to python interpreter

 plot(x, y):  display a simple XY line plot to a wxmplot.PlotFrame

 imshow(array): display image of 2D array data on a wxmplot.ImageFrame

 set_theme(themename): set plotting theme ('light', 'dark', 'seaborn', ...).

"""

import time
import os
import sys
import atexit

import wx

from . import inputhook
from .plotframe import PlotFrame
from .imageframe import ImageFrame
from .stackedplotframe import StackedPlotFrame
from .config import Themes

IMG_DISPLAYS = {}
PLOT_DISPLAYS = {}
MAX_WINDOWS = 100
MAX_CURSHIST = 100
DEFAULT_THEME = 'light'

__all__ = ['wxapp', 'plot', 'newplot', 'imshow', 'get_wxapp', 'set_theme',
           'available_themes', 'get_plot_window', 'get_image_window',
           'update_trace', 'plot_setlimits', 'plot_text', 'plot_arrow',
           'plot_marker', 'plot_axhline', 'plot_axvline', 'hist',
           'contour', 'DEFAULT_THEME']


wxapp = None
def get_wxapp(redirect=False, clearSigInt=True):
    """get wx App"""
    global wxapp
    if wxapp is None:
        wxapp = wx.GetApp()
        if wxapp is None:
            wxapp = wx.App(redirect=redirect, clearSigInt=clearSigInt)
    return wxapp

@atexit.register
def __wxmainloop__():
    """run wxApp mainloop, allowing widget interaction
    until all plotting and image image windows are closed.
    Note that this should not be necessary to run explicitly,
    as it is registered to run when Python exits
    """
    get_wxapp().MainLoop()


def set_theme(theme):
    """set plotting theme by name with a theme name such as
    'light', 'dark', 'matplotlib', 'seaborn',
    'ggplot', 'bmh', 'fivethirtyeight', ...

    See `available_themes()` for the list of available themes.
    """
    global DEFAULT_THEME
    if theme.lower() in Themes.keys():
        DEFAULT_THEME = theme.lower()
    else:
        raise ValueError("theme '%s' unavailable. use `availabale_themes()`" % theme)

def available_themes():
    """list of available themes"""
    return [name for name in Themes.keys()]

class PlotDisplay(PlotFrame):
    def __init__(self, wxparent=None, window=1, size=None, theme=None,
                 wintitle=None, **kws):
        get_wxapp()
        theme = DEFAULT_THEME if theme is None else theme

        if wintitle is None:
            wintitle   = 'Plot Window %i' % window

        PlotFrame.__init__(self, parent=None, size=size, title=wintitle,
                           output_title='plot', exit_callback=self.onExit,
                           theme=theme, **kws)

        self.Show()
        self.Raise()
        self.panel.cursor_callback = self.onCursor
        self.panel.cursor_mode = 'zoom'
        self.window = int(window)
        self.cursor_hist = []
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
    def __init__(self, wxparent=None, window=1, size=None, theme=None,
                 wintitle=None, **kws):
        get_wxapp()
        if wintitle is None:
            wintitle   = 'Image Window %i' % window

        ImageFrame.__init__(self, parent=None, size=size, title=wintitle,
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

def get_plot_window(win=1, wxparent=None, size=None, wintitle=None, theme=None):
    """make a plot window"""
    win = max(1, min(MAX_WINDOWS, int(abs(win))))
    if win in PLOT_DISPLAYS:
        display = PLOT_DISPLAYS[win]
    else:
        display = PlotDisplay(window=win, wxparent=wxparent,
                              size=size, theme=theme, wintitle=wintitle)
    return display

def get_image_window(win=1, wxparent=None, size=None, wintitle=None):
    """make an image window"""
    win = max(1, min(MAX_WINDOWS, int(abs(win))))
    if win in IMG_DISPLAYS:
        display = IMG_DISPLAY[win]
    else:
        display = ImageDisplay(window=win, wxparent=wxparent, size=size,
                               wintitle=wintitle)

    return display


def plot(x,y, win=1, new=False, wxparent=None, size=None, wintitle=None,
         theme=None, **kws):
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

    See Also: newplot
    """
    plotter = get_plot_window(wxparent=wxparent, win=win, size=size,
                             wintitle=wintitle, theme=theme)
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
    plotter = get_plot_window(wxparent=wxparent, win=win)
    if plotter is None:
        return
    plotter.Raise()
    trace -= 1 # wxmplot counts traces from 0
    plotter.panel.update_line(trace, x, y, draw=True, **kws)

def plot_setlimits(xmin=None, xmax=None, ymin=None, ymax=None, win=1, wxparent=None):
    """set plot view limits for plot in window `win`"""
    plotter = get_plot_window(wxparent=wxparent, win=win)
    if plotter is None:
        return
    plotter.panel.set_xylims((xmin, xmax, ymin, ymax))

def newplot(x, y, win=1, wxparent=None, wintitle=None, **kws):
    """newplot(x, y[, win=1[, options]])

    Plot 2-D trace of x, y arrays in a Plot Frame, clearing any
    plot currently in the Plot Frame.

    This is equivalent to
    plot(x, y[, win=1[, new=True[, options]]])

    See Also: plot
    """
    kws['new'] = True
    return plot(x, y, win=win, wxparent=wxparent, wintitle=wintitle, **kws)

def plot_text(text, x, y, win=1, rotation=None, ha='left', va='center',
              side='left', wxparent=None, size=None, **kws):

    """plot_text(x, y, text, win=1, options)

    add text at x, y coordinates of a plot

    Parameters:
    --------------
        text:  text to draw
        x:     x position of text
        y:     y position of text
        win:   index of Plot Frame (0, 1, etc).  May create a new Plot Frame.
        rotation:  text rotation. angle in degrees or 'vertical' or 'horizontal'
        ha:    horizontal alignment ('left', 'center', 'right')
        va:    vertical alignment ('top', 'center', 'bottom', 'baseline')
        side: which axis to use ('left' or 'right') for coordinates.

    See Also: plot, plot_arrow
    """
    plotter = get_plot_window(wxparent=wxparent, win=win, size=size)
    if plotter is None:
        return
    plotter.Raise()
    plotter.add_text(text, x, y, rotation=rotation, ha=ha, va=va, **kws)

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

    See Also: plot, plot_text
    """
    plotter = get_plot_window(wxparent=wxparent, win=win, size=size)
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

    See Also: plot, plot_text
    """
    plotter = get_plot_window(wxparent=wxparent, win=win, size=None)
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
    See Also: plot, plot_arrow
    """
    plotter = get_plot_window(wxparent=wxparent, win=win, size=size)
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
    See Also: plot, plot_arrow
    """
    plotter = get_plot_window(wxparent=wxparent, win=win, size=size)
    if plotter is None:
        return
    plotter.Raise()
    if 'label' not in kws:
        kws['label'] = '_nolegend_'
    plotter.panel.axes.axvline(x, ymin=ymin, ymax=ymax, **kws)
    if not delay_draw:
        plotter.panel.canvas.draw()


def hist(x, bins=10, win=1, new=False, wxparent=None, size=None,
         force_draw=True, title=None, *args, **kws):

    plotter = get_plot_window(wxparent=wxparent, win=win, size=size)
    if plotter is None:
        return
    plotter.Raise()
    if new:
        plotter.panel.axes.clear()
    out = plotter.panel.axes.hist(x, bins=bins, **kws)
    if title is not None:
        plotter.panel.set_title(title)
    plotter.panel.canvas.draw()

    return out

def imshow(map, x=None, y=None, colormap=None, win=1, wxparent=None,
           wintitle=None, size=None, **kws):
    """imshow(map[, options])

    Display an 2-D array of intensities as a false-color map

    map: 2-dimensional array for map
    """
    img = get_image_window(wxparent=wxparent, win=win, size=size,
                          wintitle=wintitle)
    if img is not None:
        img.display(map, x=x, y=y, colormap=colormap, **kws)
    return img

def contour(map, x=None, y=None, **kws):
    """contour(map[, options])

    Display an 2-D array of intensities as a contour plot

    map: 2-dimensional array for map
    """
    kws.update(dict(style='contour'))
    imshow(map, x=x, y=y, **kws)
