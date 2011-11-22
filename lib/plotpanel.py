#!/usr/bin/python
"""
wxmplot PlotPanel: a wx.Panel for 2D line plotting, using matplotlib
"""
import wx

import matplotlib
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

from plotconfigframe import PlotConfigFrame
from basepanel import BasePanel
from config import PlotConfig

class PlotPanel(BasePanel):
    """
    MatPlotlib 2D plot as a wx.Panel, suitable for embedding
    in any wx.Frame.   This does provide a right-click popup
    menu for configuration, zooming, saving an image of the
    figure, and Ctrl-C for copy-image-to-clipboard.

    For more features, see PlotFrame, which embeds a PlotPanel
    and also provides, a Menu, StatusBar, and Printing support.
    """
    def __init__(self, parent, size=(6.00, 3.70), dpi=96, **kws):

        matplotlib.rc('axes', axisbelow=True)
        matplotlib.rc('lines', linewidth=2)
        matplotlib.rc('xtick',  labelsize=11, color='k')
        matplotlib.rc('ytick',  labelsize=11, color='k')
        matplotlib.rc('grid',  linewidth=0.5, linestyle='-')

        BasePanel.__init__(self, parent, **kws)

        self.conf = PlotConfig()
        self.data_range = {}
        self.win_config = None
        self.cursor_callback = None
        self.parent    = parent
        self.figsize = size
        self.dpi     = dpi
        self.BuildPanel()

    def plot(self, xdata, ydata, side='left', title=None,
             xlabel=None, ylabel=None, y2label=None,
             use_dates=False, grid=None,  **kw):
        """
        plot (that is, create a new plot: clear, then oplot)
        """
        
        allaxes = self.fig.get_axes()
        if len(allaxes) > 1:
            for ax in allaxes[1:]:
                self.fig.delaxes(ax)

        axes = self.axes
        axes.cla()        
        if side == 'right':
            axes = self.get_right_axes()
            axes.cla()
        self.conf.ntrace  = 0
        self.data_range[axes] = [min(xdata), max(xdata),
                                 min(ydata), max(ydata)]

        if xlabel is not None:
            self.set_xlabel(xlabel)
        if ylabel is not None:
            self.set_ylabel(ylabel)
        if y2label is not None:
            self.set_y2label(y2label)
        if title  is not None:
            self.set_title(title)
        if use_dates is not None:
            self.use_dates  = use_dates

        if grid:
            self.conf.show_grid = grid

        return self.oplot(xdata, ydata, side=side, **kw)

    def oplot(self, xdata, ydata, side='left', label=None,
              dy=None, ylog_scale=False, 
              xmin=None, xmax=None, ymin=None, ymax=None,
              color=None, style=None, drawstyle=None,
              linewidth=None, marker=None, markersize=None,
              autoscale=True, refresh=True):
        """ basic plot method, overplotting any existing plot """
        axes = self.axes
        if side == 'right':
            axes = self.get_right_axes()

        # set y scale to log/linear
        yscale = 'linear'
        if ylog_scale and min(ydata) > 0:
            yscale = 'log'
        axes.set_yscale(yscale, basey=10)

        if dy is None:
            _lines = axes.plot(xdata, ydata, drawstyle=drawstyle)
        else:
            _lines = axes.errorbar(xdata, ydata, yerr=dy)

        if axes not in self.data_range:
            self.data_range[axes] = [min(xdata), max(xdata),
                                     min(ydata), max(ydata)]

        dr = self.data_range[axes]
        dr = self.data_range[axes] = [min(dr[0], min(xdata)),
                                      max(dr[1], max(xdata)),
                                      min(dr[2], min(ydata)),
                                      max(dr[3], max(ydata))]

        xylims = None
        if xmin is not None:
            self.data_range[axes][0] = max(xmin, dr[0])
            xylims = self.data_range[axes]
        if xmax is not None:
            self.data_range[axes][1] = min(xmax, dr[1])
            xylims = self.data_range[axes]
        if ymin is not None:
            self.data_range[axes][2] = max(ymin, dr[2])
            xylims = self.data_range[axes]
        if ymax is not None:
            self.data_range[axes][3] = min(ymax, dr[3])
            xylims = self.data_range[axes]
            
        conf  = self.conf
        n    = conf.ntrace

        if label is None:
            label = 'trace %i' % (n+1)
        conf.set_trace_label(label)
        conf.lines[n] = _lines

        if color:
            conf.set_trace_color(color)
        if style:
            conf.set_trace_style(style)
        if marker:
            conf.set_trace_marker(marker)
        if linewidth is not None:
            conf.set_trace_linewidth(linewidth)
        if markersize is not None:
            conf.set_trace_markersize(markersize)

        if axes == self.axes:
            axes.yaxis.set_major_formatter(FuncFormatter(self.yformatter))
        else:
            axes.yaxis.set_major_formatter(FuncFormatter(self.y2formatter))

        axes.xaxis.set_major_formatter(FuncFormatter(self.xformatter))

        if refresh:
            conf.refresh_trace(n)
            conf.relabel()

        if xylims is not None:
            self.set_xylims(xylims, autoscale=False)
        if autoscale:        
            axes.autoscale_view()
            self.unzoom_all()

        if self.conf.show_grid and axes == self.axes:
            # I'm sure there's a better way...
            for i in axes.get_xgridlines()+axes.get_ygridlines():
                i.set_color(self.conf.grid_color)
            axes.grid(True)
        else:
            axes.grid(False)

        self.canvas.draw()
        self.canvas.Refresh()
        conf.ntrace = conf.ntrace + 1
        
        return _lines

    def set_xylims(self, lims, axes=None, side=None, autoscale=True):
        """ update xy limits of a plot, as used with .update_line() """
        if axes is None:
            axes = self.axes
        if side == 'right' and len(self.fig.get_axes()) == 2:
            axes = self.fig.get_axes()[1]

        if autoscale:
            xmin, xmax, ymin, ymax = self.data_range[axes]
        else:
            xmin, xmax, ymin, ymax = lims

        axes.set_xbound(axes.xaxis.get_major_locator().view_limits(xmin, xmax))
        axes.set_ybound(axes.yaxis.get_major_locator().view_limits(ymin, ymax))
        axes.set_xlim((xmin, xmax), emit=True)
        axes.set_ylim((ymin, ymax), emit=True)

    def clear(self):
        """ clear plot """
        for ax in self.fig.get_axes():
            ax.cla()

        self.conf.ntrace = 0
        self.conf.xlabel = ''
        self.conf.ylabel = ''
        self.conf.y2label = ''
        self.conf.title  = ''

    def reset_config(self):
        """reset configuration to defaults."""
        self.conf.set_defaults()

    def unzoom(self, event=None, set_bounds=True):
        """ zoom out 1 level, or to full data range """
        if len(self.zoom_lims) < 1:
            return
        for ax, lims in self.zoom_lims.pop().items():
            self.set_xylims(lims=lims, axes=ax, autoscale=False)

        self.canvas.draw()

    def configure(self, event=None):
        """show configuration frame"""
        try:
            self.win_config.Raise()
        except:
            self.win_config = PlotConfigFrame(parent=self, config=self.conf)

    ####
    ## create GUI
    ####
    def BuildPanel(self):
        """ builds basic GUI panel and popup menu"""
        self.fig   = Figure(self.figsize, dpi=self.dpi)

        self.axes  = self.fig.add_axes([0.14, 0.14, 0.76, 0.72],
                                       axisbg='#FEFFFE')

        self.canvas = FigureCanvas(self, -1, self.fig)

        self.printer.canvas = self.canvas
        self.set_bg()
        self.conf.canvas = self.canvas
        self.canvas.SetCursor(wx.StockCursor(wx.CURSOR_CROSS))

        # overwrite ScalarFormatter from ticker.py here:
        self.axes.xaxis.set_major_formatter(FuncFormatter(self.xformatter))
        self.axes.yaxis.set_major_formatter(FuncFormatter(self.yformatter))

        # This way of adding to sizer allows resizing
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 2, wx.LEFT|wx.TOP|wx.BOTTOM|wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Fit()

        self.addCanvasEvents()

    def update_line(self, trace, xdata, ydata, side='left'):
        """ update a single trace, for faster redraw """

        x = self.conf.get_mpl_line(trace)
        x.set_data(xdata, ydata)
        axes = self.axes
        if side == 'right':
            axes = self.get_right_axes()
        dr = self.data_range[axes]
        self.data_range[axes] = [min(dr[0], xdata.min()),
                                 max(dr[1], xdata.max()),
                                 min(dr[2], ydata.min()),
                                 max(dr[3], ydata.max())]
        # this defeats zooming, which gets ugly in this fast-mode anyway.
        self.cursor_mode = 'cursor'
        self.canvas.draw()

    ####
    ## GUI events
    ####
    def reportLeftDown(self, event=None):
        if event is None:
            return
        ex, ey = event.x, event.y
        msg = ''
        try:
            x, y = self.axes.transData.inverted().transform((ex, ey))
        except:
            x, y = event.xdata, event.ydata

        msg = ("X,Y= %s, %s" % (self._xfmt, self._yfmt)) % (x, y)

        if len(self.fig.get_axes()) > 1:
            ax2 = self.fig.get_axes()[1]
            try:
                x2, y2 = ax2.transData.inverted().transform((ex, ey))
                msg = "X,Y,Y2= %s, %s, %s" % (self._xfmt, self._yfmt,
                                              self._y2fmt) % (x, y, y2)
            except:
                pass
        self.write_message(msg,  panel=0)
        if (self.cursor_callback is not None and
            hasattr(self.cursor_callback , '__call__')):
            self.cursor_callback(x=event.xdata, y=event.ydata)

