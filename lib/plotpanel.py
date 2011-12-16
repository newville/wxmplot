#!/usr/bin/python
"""
wxmplot PlotPanel: a wx.Panel for 2D line plotting, using matplotlib
"""
import wx
from numpy import nonzero
import matplotlib
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

from matplotlib.colors import colorConverter
from matplotlib.collections import CircleCollection
from matplotlib.nxutils import points_inside_poly

from plotconfigframe import PlotConfigFrame
from basepanel import BasePanel
from config import PlotConfig

to_rgba = colorConverter.to_rgba
class PlotPanel(BasePanel):
    """
    MatPlotlib 2D plot as a wx.Panel, suitable for embedding
    in any wx.Frame.   This does provide a right-click popup
    menu for configuration, zooming, saving an image of the
    figure, and Ctrl-C for copy-image-to-clipboard.

    For more features, see PlotFrame, which embeds a PlotPanel
    and also provides, a Menu, StatusBar, and Printing support.
    """
    def __init__(self, parent, size=(4.00, 2.48), dpi=144,
                 trace_color_callback=None, **kws):

        self.trace_color_callback = trace_color_callback
        matplotlib.rc('axes', axisbelow=True)
        matplotlib.rc('lines', linewidth=2)
        matplotlib.rc('xtick', labelsize=10, color='k')
        matplotlib.rc('ytick', labelsize=10, color='k')
        matplotlib.rc('legend', fontsize=10)
        matplotlib.rc('grid',  linewidth=0.5, linestyle='-')

        BasePanel.__init__(self, parent, **kws)

        self.conf = PlotConfig()
        self.data_range = {}
        self.win_config = None
        self.cursor_callback = None
        self.lasso_callback = None
        self.parent    = parent
        self.figsize = size
        self.dpi     = dpi
        self.BuildPanel()
        self.user_limits = [None, None, None, None]

    def plot(self, xdata, ydata, side='left', title=None,
             xlabel=None, ylabel=None, y2label=None,
             use_dates=False, grid=None,  **kw):
        """
        plot (that is, create a new plot: clear, then oplot)
        """
        allaxes = self.fig.get_axes()
        if len(allaxes) > 1:
            for ax in allaxes[1:]:
                if ax in self.data_range:
                    self.data_range.pop(ax)
                self.fig.delaxes(ax)

        self.data_range = {}
        self.zoom_lims = []
        self.clear()
        axes = self.axes
        if side == 'right':
            axes = self.get_right_axes()
        self.conf.ntrace  = 0
        self.conf.cursor_mode = 'zoom'
        self.conf.plot_type = 'lineplot'
        self.user_limits = [None, None, None, None]

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
        if grid is not None:
            self.conf.show_grid = grid

        return self.oplot(xdata, ydata, side=side, **kw)

    def oplot(self, xdata, ydata, side='left', label=None,
              xlabel=None, ylabel=None, dy=None, ylog_scale=False,
              xmin=None, xmax=None, ymin=None, ymax=None,
              color=None, style=None, drawstyle=None,
              linewidth=2, marker=None, markersize=None,
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
        if linewidth is None:
            linewidth = 2

        # set data range for this axes, and the view limits
        datrange = [min(xdata), max(xdata), min(ydata), max(ydata)]
        if axes not in self.data_range:
            self.data_range[axes] = datrange
        else:
            dr = self.data_range[axes][:]
            self.data_range[axes][0] = min(dr[0], datrange[0])
            self.data_range[axes][1] = max(dr[1], datrange[1])
            self.data_range[axes][2] = min(dr[2], datrange[2])
            self.data_range[axes][3] = max(dr[3], datrange[3])

        if xmin is not None: self.user_limits[0] = xmin
        if xmax is not None: self.user_limits[1] = xmax
        if ymin is not None: self.user_limits[2] = ymin
        if ymax is not None: self.user_limits[3] = ymax

        xylims = self.calc_xylims(axes)
        if axes == self.axes:
            axes.yaxis.set_major_formatter(FuncFormatter(self.yformatter))
        else:
            axes.yaxis.set_major_formatter(FuncFormatter(self.y2formatter))

        axes.xaxis.set_major_formatter(FuncFormatter(self.xformatter))

        conf  = self.conf
        n    = conf.ntrace



        scalex = self.user_limits[0] is None and self.user_limits[1] is None
        scaley = self.user_limits[2] is None and self.user_limits[3] is None

        print 'autoscale ', autoscale, scalex, scaley
        if autoscale and scalex and scaley:
            axes.autoscale(enable=True, axis='both')
        else:
            self.set_xylims(xylims, axes=axes)

            axes.autoscale_view(scalex=scalex, scaley=scaley)

        if conf.show_grid and axes == self.axes:
            # I'm sure there's a better way...
            for i in axes.get_xgridlines()+axes.get_ygridlines():
                i.set_color(self.conf.grid_color)
            axes.grid(True)
        else:
            axes.grid(False)

        if dy is None:
            _lines = axes.plot(xdata, ydata, drawstyle=drawstyle)
        else:
            _lines = axes.errorbar(xdata, ydata, yerr=dy)

        if label is None:
            label = 'trace %i' % (conf.ntrace+1)
        conf.set_trace_label(label)

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
        if drawstyle is not None:
            conf.set_trace_drawstyle(drawstyle)

        conf.lines[n] = _lines

        if refresh:
            conf.refresh_trace(conf.ntrace)
            conf.relabel()

        self.canvas.draw()
        self.canvas.Refresh()
        conf.ntrace = conf.ntrace + 1
        return _lines

    def calc_xylims(self, axes):
        xylims = self.user_limits[:]
        for i in range(4):
            if xylims[i] is None:
                xylims[i] = self.data_range[axes][i]
        return xylims

    def scatterplot(self, xdata, ydata, label=None, size=10,
                    color=None, edgecolor=None,
                    selectcolor=None, selectedge=None,
                    xlabel=None, ylabel=None, y2label=None,
                    xmin=None, xmax=None, ymin=None, ymax=None,
                    title=None, grid=None, callback=None, **kw):

        if xlabel is not None:
            self.set_xlabel(xlabel)
        if ylabel is not None:
            self.set_ylabel(ylabel)
        if y2label is not None:
            self.set_y2label(y2label)
        if title  is not None:
            self.set_title(title)
        if grid is not None:
            self.conf.show_grid = grid
        if callback is not None:
            self.lasso_callback = callback

        self.conf.plot_type = 'scatter'
        self.conf.cursor_mode = 'lasso'
        if color is not None:
            self.conf.scatter_normalcolor = color
        if edgecolor is not None:
            self.conf.scatter_normaledge  = edgecolor
        if selectcolor is not None:
            self.conf.scatter_selectcolor = selectcolor
        if selectedge is not None:
            self.conf.scatter_selectedge = selectedge

        axes = self.axes
        self.data_range[axes] = [min(xdata), max(xdata),
                                 min(ydata), max(ydata)]

        if xmin is not None: self.user_limits[0] = xmin
        if xmax is not None: self.user_limits[1] = xmax
        if ymin is not None: self.user_limits[2] = ymin
        if ymax is not None: self.user_limits[3] = ymax
        xylims = self.calc_xylims(axes)

        fcols = [to_rgba(self.conf.scatter_normalcolor) for x in xdata]
        ecols = [self.conf.scatter_normaledge]*len(xdata)

        self.conf.scatter_data = [(x, y) for x, y in zip(xdata, ydata)]
        self.conf.scatter_size = size
        self.conf.scatter_coll = CircleCollection(
            sizes=(size, ), facecolors=fcols, edgecolors=ecols,
            offsets=self.conf.scatter_data,
            transOffset= self.axes.transData)
        self.axes.add_collection(self.conf.scatter_coll)

        if xylims is not None:
            self.set_xylims(xylims, axes=axes)

        if self.conf.show_grid:
            for i in axes.get_xgridlines()+axes.get_ygridlines():
                i.set_color(self.conf.grid_color)
            axes.grid(True)
        else:
            axes.grid(False)
        axes.autoscale_view()

        self.canvas.draw()

    def lassoHandler(self, vertices):
        conf = self.conf
        fcols = conf.scatter_coll.get_facecolors()
        ecols = conf.scatter_coll.get_edgecolors()
        mask = points_inside_poly(conf.scatter_data, vertices)
        pts = nonzero(mask)[0]
        self.conf.scatter_mask = mask
        for i in range(len(conf.scatter_data)):
            if i in pts:
                ecols[i] = to_rgba(conf.scatter_selectedge)
                fcols[i] = to_rgba(conf.scatter_selectcolor)
                fcols[i][3] = 0.5
            else:
                fcols[i] = to_rgba(conf.scatter_normalcolor)
                ecols[i] = to_rgba(conf.scatter_normaledge)

        self.lasso = None
        self.canvas.draw_idle()
        if (self.lasso_callback is not None and
            hasattr(self.lasso_callback , '__call__')):
            self.lasso_callback(data = conf.scatter_coll.get_offsets(),
                                selected = pts, mask=mask)

    def set_xylims(self, lims, axes=None, side=None, autoscale=False):
        """ update xy limits of a plot, as used with .update_line() """
        if axes is None:
            axes = self.axes
        if side == 'right' and len(self.fig.get_axes()) == 2:
            axes = self.fig.get_axes()[1]

        xmin, xmax, ymin, ymax = lims

        #axes.set_xbound(axes.xaxis.get_major_locator().view_limits(xmin, xmax))
        #axes.set_ybound(axes.yaxis.get_major_locator().view_limits(ymin, ymax))
        axes.set_xlim((xmin, xmax), emit=True)
        axes.set_ylim((ymin, ymax), emit=True)
        #axes.autoscale_view()

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
            self.axes.autoscale_view()
            return
        else:
            for ax, lims in self.zoom_lims.pop().items():
                self.set_xylims(lims=lims, axes=ax)

        self.canvas.draw()

    def configure(self, event=None):
        """show configuration frame"""
        try:
            self.win_config.Raise()
        except:
            self.win_config = PlotConfigFrame(parent=self,
                                              config=self.conf,
                                              trace_color_callback=self.trace_color_callback)


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

    def update_line(self, trace, xdata, ydata, side='left', draw=False):
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
        self.cursor_state = None
        if draw:
            self.canvas.draw()

    def draw(self):
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

