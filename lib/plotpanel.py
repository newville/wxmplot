#!/usr/bin/python
"""
wxmplot PlotPanel: a wx.Panel for 2D line plotting, using matplotlib
"""
import wx
from numpy import nonzero, where, ma
import matplotlib
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

from matplotlib.colors import colorConverter
from matplotlib.collections import CircleCollection

from .plotconfigframe import PlotConfigFrame
from .basepanel import BasePanel
from .config import PlotConfig
from .utils import inside_poly

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
    def __init__(self, parent, size=None, dpi=150,
                 axissize=None, axisbg=None, fontsize=9,
                 trace_color_callback=None,
                 output_title='plot', **kws):

        if size is None: size=(700, 450)

        self.trace_color_callback = trace_color_callback
        matplotlib.rc('axes', axisbelow=True)
        matplotlib.rc('lines', linewidth=2)
        matplotlib.rc('xtick', labelsize=fontsize, color='k')
        matplotlib.rc('ytick', labelsize=fontsize, color='k')
        matplotlib.rc('legend', fontsize=fontsize)
        matplotlib.rc('grid',  linewidth=0.5, linestyle='-')


        BasePanel.__init__(self, parent,
                           output_title=output_title, **kws)

        self.conf = PlotConfig()
        self.data_range = {}
        self.win_config = None
        self.cursor_callback = None
        self.lasso_callback = None
        self.parent    = parent
        self.figsize = (size[0]*1.0/dpi, size[1]*1.0/dpi)
        self.dpi     = dpi

        if axissize is None:  axissize = [0.16, 0.16, 0.72, 0.75]
        if axisbg is None:     axisbg='#FEFFFE'
        self.axisbg = axisbg
        self.axissize = axissize
        self.BuildPanel()
        self.user_limits = {} # [None, None, None, None]
        self.data_range = {}
        self.zoom_lims = []
        self.axes_traces = {}

    def plot(self, xdata, ydata, side='left', title=None,
             xlabel=None, ylabel=None, y2label=None,
             use_dates=False, **kws):
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
        self.axes_traces = {}
        self.clear()
        axes = self.axes
        if side == 'right':
            axes = self.get_right_axes()
        self.conf.ntrace  = 0
        self.cursor_mode = 'zoom'
        self.conf.plot_type = 'lineplot'
        self.user_limits[axes] = [None, None, None, None]

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

        return self.oplot(xdata, ydata, side=side, **kws)

    def oplot(self, xdata, ydata, side='left', label=None,
              xlabel=None, ylabel=None, y2label=None, title=None,
              dy=None, ylog_scale=False, grid=None,
              xmin=None, xmax=None, ymin=None, ymax=None,
              color=None, style=None, drawstyle=None,
              linewidth=2, marker=None, markersize=None,
              autoscale=True, refresh=True, show_legend=None,
              legend_loc='ur', legend_on=True, delay_draw=False,
              bgcolor=None, framecolor=None, gridcolor=None,
              labelfontsize=None, legendfontsize=None,
              fullbox=True, zorder=None, **kws):
        """ basic plot method, overplotting any existing plot """
        axes = self.axes
        if side == 'right':
            axes = self.get_right_axes()
        # set y scale to log/linear
        yscale = 'linear'
        if ylog_scale:
            yscale = 'log'
            # ydata = ma.masked_where(ydata<=0, 1.0*ydata)
            # ymin = min(ydata[where(ydata>0)])
            ydata[where(ydata<=0)] = None

        axes.set_yscale(yscale, basey=10)
        if linewidth is None:
            linewidth = 2

        if xlabel is not None:
            self.set_xlabel(xlabel)
        if ylabel is not None:
            self.set_ylabel(ylabel)
        if y2label is not None:
            self.set_y2label(y2label)
        if title  is not None:
            self.set_title(title)
        if show_legend is not None:
            self.conf.set_legend_location(legend_loc, legend_on)
            self.conf.show_legend = show_legend

        if grid is not None:
            self.conf.show_grid = grid

        # set data range for this trace
        datarange = [min(xdata), max(xdata), min(ydata), max(ydata)]

        if axes not in self.user_limits:
            self.user_limits[axes] = [None, None, None, None]

        if xmin is not None: self.user_limits[axes][0] = xmin
        if xmax is not None: self.user_limits[axes][1] = xmax
        if ymin is not None: self.user_limits[axes][2] = ymin
        if ymax is not None: self.user_limits[axes][3] = ymax

        if axes == self.axes:
            axes.yaxis.set_major_formatter(FuncFormatter(self.yformatter))
        else:
            axes.yaxis.set_major_formatter(FuncFormatter(self.y2formatter))

        axes.xaxis.set_major_formatter(FuncFormatter(self.xformatter))

        conf  = self.conf
        n    = conf.ntrace
        if zorder is None:
            zorder = 10*(n+1)
        if axes not in self.axes_traces:
            self.axes_traces[axes] = []
        self.axes_traces[axes].append(n)

        if conf.show_grid and axes == self.axes:
            # I'm sure there's a better way...
            for i in axes.get_xgridlines()+axes.get_ygridlines():
                i.set_color(conf.grid_color)
                i.set_zorder(0)
            axes.grid(True)
        else:
            axes.grid(False)
        if dy is None:
            _lines = axes.plot(xdata, ydata, drawstyle=drawstyle, zorder=zorder)
        else:
            _lines = axes.errorbar(xdata, ydata, yerr=dy, zorder=zorder)

        if label is None:
            label = 'trace %i' % (conf.ntrace+1)
        conf.set_trace_label(label)
        conf.set_trace_datarange(datarange)

        if bgcolor is not None:
            axes.set_axis_bgcolor(bgcolor)
        if framecolor is not None:
            self.canvas.figure.set_facecolor(framecolor)

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

        if gridcolor is not None:
            conf.grid_color = gridcolor
        if labelfontsize is not None:
            conf.labelfont.set_size(labelfontsize)
        if legendfontsize is not None:
            conf.legendfont.set_size(legendfontsize)

        if n < len(conf.lines):
            conf.lines[n] = _lines
        else:
            conf._init_trace(n, 'black', solid)
            conf.lines[n] = _lines

        # now set plot limits:
        self.set_viewlimits()
        if refresh:
            conf.refresh_trace(conf.ntrace)
            conf.relabel()

        if self.conf.show_legend:
            conf.draw_legend()

        # axes style ('box' or 'open')
        conf.axes_style = 'box'
        if not fullbox:  # show only left and bottom lines
            conf.axes_style = 'open'
        conf.set_axes_style()

        if not delay_draw:
            self.canvas.draw()
            self.canvas.Refresh()

        conf.ntrace = conf.ntrace + 1
        return _lines

    def add_text(self, text, x, y, side='left', size=None,
                 rotation=None, ha='left', va='center',
                 family=None, **kws):
        """add text at supplied x, y position"""
        axes = self.axes
        if side == 'right':
            axes = self.get_right_axes()
        dynamic_size = False
        if size is None:
            size = self.conf.legendfont.get_size()
            dynamic_size = True
        t = axes.text(x, y, text, ha=ha, va=va, size=size,
                      rotation=rotation, family=family, **kws)
        self.conf.added_texts.append((dynamic_size, t))
        self.canvas.draw()

    def add_arrow(self, x1, y1, x2, y2,  side='left',
                  shape='full', color='black',
                  width=0.01, head_width=0.03, overhang=0, **kws):
        """add arrow supplied x, y position"""
        dx, dy = x2-x1, y2-y1

        axes = self.axes
        if side == 'right':
            axes = self.get_right_axes()
        axes.arrow(x1, y1, dx, dy, shape=shape,
                   length_includes_head=True,
                   fc=color, edgecolor=color,
                   width=width, head_width=head_width,
                   overhang=overhang, **kws)
        self.canvas.draw()

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
        self.cursor_mode = 'lasso'
        if color is not None:
            self.conf.scatter_normalcolor = color
        if edgecolor is not None:
            self.conf.scatter_normaledge  = edgecolor
        if selectcolor is not None:
            self.conf.scatter_selectcolor = selectcolor
        if selectedge is not None:
            self.conf.scatter_selectedge = selectedge

        axes = self.axes
        self.user_limits[axes] = (xmin, xmax, ymin, ymax)

        self.axes_traces = {axes: [0]}
        self.conf.set_trace_label('scatterplot')
        self.conf.set_trace_datarange((min(xdata), max(xdata),
                                       min(ydata), max(ydata)))

        fcols = [to_rgba(self.conf.scatter_normalcolor) for x in xdata]
        ecols = [self.conf.scatter_normaledge]*len(xdata)

        self.conf.scatter_data = [(x, y) for x, y in zip(xdata, ydata)]
        self.conf.scatter_size = size
        self.conf.scatter_coll = CircleCollection(
            sizes=(size, ), facecolors=fcols, edgecolors=ecols,
            offsets=self.conf.scatter_data,
            transOffset= self.axes.transData)
        self.axes.add_collection(self.conf.scatter_coll)
        # self.set_viewlimits(axes=axes)

        if self.conf.show_grid:
            for i in axes.get_xgridlines()+axes.get_ygridlines():
                i.set_color(self.conf.grid_color)
                i.set_zorder(-100)
            axes.grid(True)
        else:
            axes.grid(False)
        self.set_viewlimits()
        self.canvas.draw()

    def lassoHandler(self, vertices):
        conf = self.conf
       
        if self.conf.plot_type == 'scatter':
            fcols = conf.scatter_coll.get_facecolors()
            ecols = conf.scatter_coll.get_edgecolors()
            sdat = conf.scatter_data
            mask = inside_poly(vertices,sdat)
            pts = nonzero(mask)[0]
            self.conf.scatter_mask = mask
            for i in range(len(sdat)):
                if i in pts:
                    ecols[i] = to_rgba(conf.scatter_selectedge)
                    fcols[i] = to_rgba(conf.scatter_selectcolor)
                    fcols[i][3] = 0.3
                    ecols[i][3] = 0.8
                else:
                    fcols[i] = to_rgba(conf.scatter_normalcolor)
                    ecols[i] = to_rgba(conf.scatter_normaledge)
        else:
            xdata = self.axes.lines[0].get_xdata()
            ydata = self.axes.lines[0].get_ydata()
            sdat = [(x, y) for x, y in zip(xdata, ydata)]
            mask = inside_poly(vertices,sdat)
            #print  len(xdata), sdat[:20]
            # print mask
            pts = nonzero(mask)[0]
            #print 'Points selected = ', pts
            
        self.lasso = None
        self.canvas.draw()
        # self.canvas.draw_idle()
        if (self.lasso_callback is not None and
            hasattr(self.lasso_callback , '__call__')):
            self.lasso_callback(data = sdat,
                                selected = pts, mask=mask)

    def set_xylims(self, limits, axes=None):
        "set user-defined limits and apply them"
        if axes not in self.user_limits:
            axes = self.axes
        self.user_limits[axes] = limits
        self.unzoom_all()


    def set_viewlimits(self, autoscale=False):
        """ update xy limits of a plot, as used with .update_line() """

        trace0 = None
        while trace0 is None:
            for axes in self.fig.get_axes():
                if (axes in self.axes_traces and
                   len(self.axes_traces[axes]) > 0):
                    trace0 = self.axes_traces[axes][0]
                    break

        for axes in self.fig.get_axes():
            datlim = self.conf.get_trace_datarange(trace=trace0)
            if axes in self.axes_traces:
                for i in self.axes_traces[axes]:
                    l =  self.conf.get_trace_datarange(trace=i)
                    datlim = [min(datlim[0], l[0]), max(datlim[1], l[1]),
                              min(datlim[2], l[2]), max(datlim[3], l[3])]

            xmin, xmax = axes.get_xlim()
            ymin, ymax = axes.get_ylim()
            limits = [min(datlim[0], xmin),
                      max(datlim[1], xmax),
                      min(datlim[2], ymin),
                      max(datlim[3], ymax)]

            if (axes in self.user_limits and
                (self.user_limits[axes] != 4*[None] or
                len(self.zoom_lims) > 0)):

                for i, val in enumerate(self.user_limits[axes]):
                    if val is not None:
                        limits[i] = val
                xmin, xmax, ymin, ymax = limits
                if len(self.zoom_lims) > 0:
                    limits_set = True
                    xmin, xmax, ymin, ymax = self.zoom_lims[-1][axes]
                axes.set_xlim((xmin, xmax), emit=True)
                axes.set_ylim((ymin, ymax), emit=True)

    def get_viewlimits(self, axes=None):
        if axes is None: axes = self.axes
        xmin, xmax = axes.get_xlim()
        ymin, ymax = axes.get_ylim()
        return (xmin, xmax, ymin, ymax)

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
        if len(self.zoom_lims) > 1:
            self.zoom_lims.pop()
        self.set_viewlimits()
        self.canvas.draw()

    def toggle_legend(self, evt=None, show=None):
        "toggle legend display"
        if show is None:
            show = not self.conf.show_legend
        self.conf.show_legend = show
        self.conf.draw_legend()

    def toggle_grid(self, evt=None, show=None):
        "toggle grid display"
        if show is None:
            show = not self.conf.show_grid
        self.conf.enable_grid(show)

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
        self.axes  = self.fig.add_axes(self.axissize, axisbg=self.axisbg)

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

    def update_line(self, trace, xdata, ydata, side='left', draw=False,
                    update_limits=True):
        """ update a single trace, for faster redraw """

        x = self.conf.get_mpl_line(trace)
        x.set_data(xdata, ydata)
        datarange = [xdata.min(), xdata.max(), ydata.min(), ydata.max()]
        self.conf.set_trace_datarange(datarange, trace=trace)
        axes = self.axes
        if side == 'right':
            axes = self.get_right_axes()
        # print 'update line ', trace, datarange
        # dr = self.data_range[axes]
        #
        #         self.data_range[axes] = [min(dr[0], xdata.min()),
        #                                  max(dr[1], xdata.max()),
        #                                  min(dr[2], ydata.min()),
        #                                  max(dr[3], ydata.max())]
        # print 'Update ', trace, side, axes == self.get_right_axes(), dr
        # this defeats zooming, which gets ugly in this fast-mode anyway.
        if update_limits:
            self.set_viewlimits()
        if draw:
            self.canvas.draw()

    def draw(self):
        self.canvas.draw()

    ####
    ## GUI events
    ####
    def report_leftdown(self, event=None):
        if event is None:
            return
        ex, ey = event.x, event.y
        msg = ''
        try:
            x, y = self.axes.transData.inverted().transform((ex, ey))
        except:
            x, y = event.xdata, event.ydata

        if x is not None and y is not None:
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
