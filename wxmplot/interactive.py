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
    """get the wx App

    Args:
        redirect(bool): whether to redirect output that would otherwise
            be written to the Console [False]
        clearSigInt(bool): whether to clear interrupts of Ctrl-C [True]

    Returns:
        a wx.App instance


    """
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
    """set plotting theme by name with a theme name

    Args:
        theme(str): name of theme


    Returns:
        None

    Notes:
      1. Example themese are:'light', 'dark', 'white-background', 'matplotlib',
      'seaborn', 'ggplot', 'bmh', 'fivethirtyeight'.
      2. See available_themes() for the list of available themes.
    """
    global DEFAULT_THEME
    if theme.lower() in Themes.keys():
        DEFAULT_THEME = theme.lower()
    else:
        raise ValueError("theme '%s' unavailable. use `availabale_themes()`" % theme)

def available_themes():
    """list of available theme

    Returns:
        list of theme names.

    Notes:
        As of this writing, the list is:

      'light', 'dark', 'white-background', 'matplotlib', 'seaborn',
      'ggplot', 'bmh', 'fivethirtyeight', 'grayscale', 'dark_background',
      'tableau-colorblind10', 'seaborn-bright', 'seaborn-colorblind',
      'seaborn-dark', 'seaborn-darkgrid', 'seaborn-dark-palette',
      'seaborn-deep', 'seaborn-notebook', 'seaborn-muted',
      'seaborn-pastel', 'seaborn-paper', 'seaborn-poster', 'seaborn-talk',
      'seaborn-ticks', 'seaborn-white', 'seaborn-whitegrid',
      'Solarize_Light2'


    """
    return [name for name in Themes.keys()]

class PlotDisplay(PlotFrame):
    def __init__(self, window=1, size=None, theme=None,
                 wintitle=None, **kws):
        get_wxapp()
        theme = DEFAULT_THEME if theme is None else theme

        if wintitle is None:
            wintitle   = 'Plot Window %i' % window

        PlotFrame.__init__(self, parent=None, size=size, title=wintitle,
                           output_title='plot', exit_callback=self.onExit,
                           theme=theme, **kws)

        if size is not None:
            self.SetSize(size)
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
    def __init__(self, window=1, size=None, theme=None,
                 wintitle=None, **kws):
        get_wxapp()
        if wintitle is None:
            wintitle   = 'Image Window %i' % window

        ImageFrame.__init__(self, parent=None, size=size, title=wintitle,
                            exit_callback=self.onExit, **kws)

        if size is not None:
            self.SetSize(size)
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

def get_plot_window(win=1, size=None, wintitle=None, theme=None):
    """return a plot display

    Args:
        win (int): index of Plot Window (1 to 100)
        size (tuple): width, height in pixels of Plot Window
        wintitle(str): text for Window title [Plot Window N]
        theme (str): theme for Plot Window ['light']

    Returns:
        diplay, a wxmplot PlotFrame.

    Notes:
        this will either return the existing PlotFrame for the
        window index or create a new one.

    """
    win = max(1, min(MAX_WINDOWS, int(abs(win))))
    if win in PLOT_DISPLAYS:
        display = PLOT_DISPLAYS[win]
    else:
        display = PlotDisplay(window=win, size=size, theme=theme,
                              wintitle=wintitle)
    return display

def get_image_window(win=1, size=None, wintitle=None):
    """return an image display

    Args:
        win (int): index of Image Window (1 to 100)
        size (tuple): width, height in pixels of Image Window
        wintitle(str): text for Window title [Image Window N]

    Returns:
        diplay, a wxmplot ImageFrame.

    Notes:
        this will either return the existing ImageFrame for the
        window index or create a new one.
    """
    win = max(1, min(MAX_WINDOWS, int(abs(win))))
    if win in IMG_DISPLAYS:
        display = IMG_DISPLAYS[win]
    else:
        display = ImageDisplay(window=win, size=size,
                               wintitle=wintitle)

    return display

def plot(x,y, win=1, new=False, size=None, wintitle=None, theme=None, **kws):
    """plot(x, y, win=1, new=False, ...)

    Plot trace of x, y arrays in a PlotFrame

    Args:
        x (array-like):  ordinate values
        y (array-like):  abscissa values (x and y must be same size!)
        dy (array-like): array for error bars in y (must be same size as y!)
        new (bool): whether to start a new plot [False]
        win (int): index of Plot Window [1]
        label (str or None): label for this trace
        linewidth (float):  width of line joining points [from theme]
        color (str or None): color for trace (see note 1) [from theme]
        style (str or None): line style for joining points (see note 2)
        marker (str on None):  symbol to draw at each point (see note 3)
        markersize (float): size of marker
        zorder (float or None): zorder (depth) of this trace
        drawstyle (str or None): style for joining line segments (see note 4)
        xmin (float or None): minimum x value for plot range
        xmax (float or None): maximum x value for plot range
        ymin (float or None): minimum y value for plot range
        ymax (float or None): maximum y value for plot range
        use_dates (bool): whether to interpret x data as dates [False]
        side (str): side for y-axis ('left' or 'right') ['left']
        size (tuple or None): width, height in pixels of Plot Window
        wintitle (str or None): title for window frame
        theme (str on None): plotting theme to use
        title (str or None):  plot title
        xlabel (str or None): label for x-axis
        ylabel (str or None): label for y-axis
        y2label (str or None): label for y2-axis (that is, right-side axis)

        xlog_scale (bool): whether to show x-axis as log-scale [False]
        ylog_scale (bool): whether to show y-axis as log-scale [False]
        grid (bool): whether to draw background grid [True]
        show_legend (bool or None): whether to show legend [False]
        legend_loc (str): location for legend (see note 5) ['best']
        legend_on  (bool): whether legend is within the main axes [True]
        bgcolor (str on None): color of background plot area (from theme)
        framecolor (str on None): color of outer frame area (from theme)
        gridcolor (str or None):  color of grid (from theme)
        labelfontsize (float): size (pixels) of font for Labels (from theme)
        legendfontsize (float): size (pixels) of font for Legend (from theme)
        titlefontsize (float): size (pixels) of font for Title (from theme)
        axes_style (str): control what parts of axes are shown (see note 6)
        viewpad (float or None): percent of data range to expand view ranges
        delay_draw (boole): whether to delay drawing [False]

    Returns:
        plotter, a PlotFrame

    Notes:
        1. colors can be names such as 'red' or hex strings '#RRGGBB'.
           by default, they are set by the theme
        2. styles can be one of 'solid', 'short dashed', 'dash-dot',
           'dashed', 'dotted', 'long-dashed'.
        3. markers can be one of  'no symbol', 'o', '+', 'x', 'square',
           'diamond', 'thin diamond', '^', 'v', '>', '<', '|', '_',
           'hexagon', 'pentagon', 'tripod 1', or 'tripod 2'
        4. drawstyle can be one of 'default', 'steps-pre','steps-mid',
           or 'steps-post'.
        5. legend_loc can be one of 'best', 'upper right' , 'lower right',
           'center right', 'upper left', 'lower left',  'center left',
           'upper center', 'lower center', 'center'
        6. axis_style can be one of 'open', 'box', 'bottom'.

    """
    plotter = get_plot_window(win=win, size=size, wintitle=wintitle,
                             theme=theme)
    if plotter is None:
        return
    plotter.Raise()
    if new or plotter.panel.conf.ntrace == 0:
        plotter.plot(x, y, **kws)
    else:
        plotter.oplot(x, y, **kws)
    return plotter

def newplot(x, y, win=1, wintitle=None, **kws):
    """newplot(x, y, ...)

    Plot trace of x, y arrays in a PlotFrame, clearing any
    data currently shown in the PlotFrame.

    Notes:
        This is equivalent to
        plot(x, y, ...., new=True)

    """
    kws['new'] = True
    return plot(x, y, win=win, wintitle=wintitle, **kws)


def update_trace(x, y, trace=1, win=1, **kws):
    """
    update a plot trace with new data, avoiding complete redraw
    This can significantly descrease drawing time:

    Args:
        x (array-like):  ordinate values
        y (array-like):  abscissa values (x and y must be same size)
        trace (int): which plot trace to update [1]
        win (int): index of Plot Window [1]
        side (str): side for y-axis ('left' or 'right') ['left']

    """
    plotter = get_plot_window(win=win)
    if plotter is None:
        return
    plotter.Raise()
    trace -= 1 # wxmplot counts traces from 0
    plotter.panel.update_line(trace, x, y, draw=True, **kws)

def plot_setlimits(xmin=None, xmax=None, ymin=None, ymax=None, win=1):
    """set plot view limits for plot in window `win`

    Args:
        xmin (float): minimum x value
        ymax (float): maximum x value
        ymin (float): minimum y value
        ymax (float): maximum y value
        win (int): index of plot window
    """
    plotter = get_plot_window(win=win)
    if plotter is None:
        return
    plotter.panel.set_xylims((xmin, xmax, ymin, ymax))

def plot_text(text, x, y, win=1, rotation=None, ha='left', va='center',
              side='left', size=None, **kws):

    """plot_text(x, y, text, win=1, options)

    add text at x, y coordinates of a plot

    Args:
        text (str): text to draw
        x (float): x position of text
        y (float): y position of text
        win (int): index of plot window
        rotation (str or float):  text rotation. angle in degrees or 'vertical' or 'horizontal'
        ha (str):    horizontal alignment ('left', 'center', 'right')
        va (str)    vertical alignment ('top', 'center', 'bottom', 'baseline')
        side (str): which axis to use ('left' or 'right') for coordinates.


    """
    plotter = get_plot_window(win=win, size=size)
    if plotter is None:
        return
    plotter.Raise()
    plotter.add_text(text, x, y, rotation=rotation, ha=ha, va=va, **kws)

def plot_arrow(x1, y1, x2, y2, win=1, side='left',
               shape='full', color='black',
               width=0.00, head_width=0.05, head_length=0.25,
               size=None, **kws):
    """plot_arrow(x1, y1, x2, y2, win=1, **kws)

    draw arrow from x1, y1 to x2, y2.

    Args:
        x1 (float): starting x coordinate
        y1 (float): starting y coordinate
        x2 (float): ending x coordinate
        y2 (float): ending y coordinate
        side (str): which axis to use ('left' or 'right') for coordinates.
        shape (str):  arrow head shape ('full', 'left', 'right')
        color (str):  arrow color ('black')
        width (float):  width of arrow line (in points. default=0.0)
        head_width (float):  width of arrow head (in points. default=0.05)
        head_length (float):  length of arrow head (in points. default=0.25)
        overhang (float):   amount the arrow is swept back (in points. default=0)
        win (int): index of plot window

    """
    plotter = get_plot_window(win=win, size=size)
    if plotter is None:
        return
    plotter.Raise()
    plotter.add_arrow(x1, y1, x2, y2, side=side, shape=shape,
                      color=color, width=width, head_length=head_length,
                      head_width=head_width, **kws)

def plot_marker(x, y, marker='o', size=4, color='black', label='_nolegend_',
                win=1,  **kws):

    """plot_marker(x, y, marker='o', size=4, color='black')

    draw a marker at x, y

    Args:
        x (float): x coordinate for marker
        y float):  y coordinate
        marker (str): symbol to draw at each point (see Note 1)
        size (float): marker size [4]
        color (str): marker color  ['black']
        win (int): index of plot window

    Notes:
        1. marker can be one of ('+', 'o', 'x', 'square',
           'diamond', 'thin diamond', '^', 'v', '>', '<', '|', '_',
           'hexagon', 'pentagon', 'tripod 1', or 'tripod 2')

    """
    plotter = get_plot_window(win=win, size=None)
    if plotter is None:
        return
    plotter.Raise()
    plotter.oplot([x], [y], marker=marker, markersize=size, label=label,
                 color=color,  **kws)

def plot_axhline(y, xmin=0, xmax=1, win=1,
                  size=None, delay_draw=False,  **kws):
    """plot_axhline(y, xmin=None, ymin=None, **kws)

    plot a horizontal line spanning the plot axes

    Args:
        y (float):  y position of line
        xmin (float): starting x fraction (window units -- not user units!)
        xmax (float): ending x fraction (window units -- not user units!)
        win (int): index of plot window

    """
    plotter = get_plot_window(win=win, size=size)
    if plotter is None:
        return
    plotter.Raise()
    if 'label' not in kws:
        kws['label'] = '_nolegend_'
    plotter.panel.axes.axhline(y, xmin=xmin, xmax=xmax, **kws)
    if delay_draw:
        plotter.panel.canvas.draw()

def plot_axvline(x, ymin=0, ymax=1, win=1, size=None,
                 delay_draw=False, **kws):
    """plot_axvline(y, xmin=None, ymin=None, **kws)

    plot a vertical line spanning the plot axes

    Args:
        x (float):   x position of line
        ymin (float): starting y fraction (window units -- not user units!)
        ymax (float): ending y fraction (window units -- not user units!)
        win (int): index of plot window

    """
    plotter = get_plot_window(win=win, size=size)
    if plotter is None:
        return
    plotter.Raise()
    if 'label' not in kws:
        kws['label'] = '_nolegend_'
    plotter.panel.axes.axvline(x, ymin=ymin, ymax=ymax, **kws)
    if not delay_draw:
        plotter.panel.canvas.draw()


def hist(x, bins=10, win=1, new=False, size=None,
         force_draw=True, title=None, *args, **kws):
    """display a histogram

    Args:
        x (array-like): array of values
        bins (int): number of bins to show
        win (int): index of plot window

    """

    plotter = get_plot_window(win=win, size=size)
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

def imshow(map, y=None, x=None, colormap=None, win=1,
           wintitle=None, size=None, **kws):
    """imshow(map, ...)

    Display an 2-D array of intensities as a false-color map

    Args:
        map(ndarray):  map array data (see Note 1)
        y (array-like): values for pixels along vertical direction
        x (array-like): values for pixels along horizontal direction
        colormap (str): name of colormap to apply
        win (int): index of Image Window (1 to %d)
        size (tuple): width, height in pixels of Image Window
        wintitle(str): text for Window title [Image Window N]
        xlabel (str): label for horizontal axis ['X']
        ylabel (str): label for horizontal axis ['Y']
        style (str): display style ('image' or 'contour') ['image']
        nlevels (int): number of levels for contour
        contour_labels (bool): whether to show contour labels [True]
        show_axis (bool): whether to shos Axis [False]
        contrast_level (float): percent level for contrast [0]

    Returns:
        img, an ImageFrame

    Notes:
        1. the map data can either be a 2d array (shape NY, NX) for
           single-color map or (NY, NX, 3) array for an RGB map


    """
    img = get_image_window(win=win, size=size,
                          wintitle=wintitle)
    if img is not None:
        img.display(map, x=x, y=y, colormap=colormap, **kws)
    return img

def contour(map, x=None, y=None, **kws):
    """contour(map, ...)

    Display an 2-D array of intensities as a contour plot

    Notes:
        This is equivalent to
        imshow(map, ..., style='contour')
    """
    kws.update(dict(style='contour'))
    imshow(map, x=x, y=y, **kws)
