#!/usr/bin/python
"""
wxmplot PlotPanel: a wx.Panel for 2D line plotting, using matplotlib
"""
import os
import sys
import wx
is_wxPhoenix = 'phoenix' in wx.PlatformInfo
if is_wxPhoenix:
    wxCursor = wx.Cursor
else:
    wxCursor = wx.StockCursor

from numpy import nonzero, where, ma, nan
import matplotlib

from datetime import datetime
from matplotlib import dates
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.gridspec import GridSpec
from matplotlib.colors import colorConverter
from matplotlib.collections import CircleCollection

from .plotconfigframe import PlotConfigFrame
from .basepanel import BasePanel
from .config import PlotConfig
from .utils import inside_poly

to_rgba = colorConverter.to_rgba


def gformat(val, length=14):
    """format a number with '%g'-like format, except that
    the return will be length ``length`` (default=12)
    and have at least length-6 significant digits
    """
    length = max(length, 7)
    fmt = '{: .%ig}' % (length-6)
    if isinstance(val, int):
        out = ('{: .%ig}' % (length-2)).format(val)
        if len(out) > length:
            out = fmt.format(val)
    else:
        out = fmt.format(val)
    if len(out) < length:
        if 'e' in out:
            ie = out.find('e')
            if '.' not in out[:ie]:
                out = out[:ie] + '.' + out[ie:]
            out = out.replace('e', '0'*(length-len(out))+'e')
        else:
            fmt = '{: .%ig}' % (length-1)
            out = fmt.format(val)[:length]
            if len(out) < length:
                pad = '0' if '.' in  out else ' '
                out += pad*(length-len(out))
    return out

class PlotPanel(BasePanel):
    """
    MatPlotlib 2D plot as a wx.Panel, suitable for embedding
    in any wx.Frame.   This does provide a right-click popup
    menu for configuration, zooming, saving an image of the
    figure, and Ctrl-C for copy-image-to-clipboard.

    For more features, see PlotFrame, which embeds a PlotPanel
    and also provides, a Menu, StatusBar, and Printing support.
    """

    def __init__(self, parent, size=(700, 450), dpi=150, axisbg=None, fontsize=9,
                 trace_color_callback=None, output_title='plot', **kws):

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

        if axisbg is None:     axisbg='#FEFFFE'
        self.axisbg = axisbg
        # axesmargins : margins in px left/top/right/bottom
        self.axesmargins = (30, 30, 30, 30)

        self.BuildPanel()
        self.user_limits = {} # [None, None, None, None]
        self.data_range = {}
        self.conf.zoom_lims = []
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
        self.conf.zoom_lims = []
        self.axes_traces = {}
        self.clear()
        axes = self.axes
        if side == 'right':
            axes = self.get_right_axes()
        self.conf.ntrace  = 0
        self.conf.yscale = 'linear'
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
              dy=None, ylog_scale=None, grid=None,
              xmin=None, xmax=None, ymin=None, ymax=None,
              color=None, style=None, drawstyle=None,
              linewidth=2, marker=None, markersize=None,
              autoscale=True, refresh=True, show_legend=None,
              legend_loc='best', legend_on=True, delay_draw=False,
              bgcolor=None, framecolor=None, gridcolor=None,
              labelfontsize=None, legendfontsize=None,
              fullbox=None, axes_style=None, zorder=None, **kws):
        """ basic plot method, overplotting any existing plot """
        axes = self.axes
        if side == 'right':
            axes = self.get_right_axes()
        # set y scale to log/linear
        if ylog_scale is not None:
            self.conf.yscale = {False:'linear', True:'log'}[ylog_scale]

            # ydata = ma.masked_where(ydata<=0, 1.0*ydata)
            # ymin = min(ydata[where(ydata>0)])
            # ydata[where(ydata<=0)] = None

        try:
            axes.set_yscale(self.conf.yscale, basey=10)
        except:
            axes.set_yscale('linear')

        axes.xaxis.set_major_formatter(FuncFormatter(self.xformatter))
        if self.use_dates:
            x_dates = [datetime.fromtimestamp(i) for i in xdata]
            xdata = dates.date2num(x_dates)
            axes.xaxis.set_major_locator(dates.AutoDateLocator())

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

        conf  = self.conf
        n    = conf.ntrace
        if zorder is None:
            zorder = 5*(n+1)
        if axes not in self.axes_traces:
            self.axes_traces[axes] = []
        self.axes_traces[axes].append(n)
        if dy is None:
            _lines = axes.plot(xdata, ydata, drawstyle=drawstyle, zorder=zorder)
        else:
            _lines = axes.errorbar(xdata, ydata, yerr=dy, zorder=zorder)

        if conf.show_grid and axes == self.axes:
            # I'm sure there's a better way...
            for i in axes.get_xgridlines() + axes.get_ygridlines():
                i.set_color(conf.grid_color)
                i.set_zorder(-100)
            axes.grid(True)
        else:
            axes.grid(False)

        if label is None:
            label = 'trace %i' % (conf.ntrace+1)
        conf.set_trace_label(label)
        conf.set_trace_datarange(datarange)

        if bgcolor is not None:
            axes.set_axis_bgcolor(bgcolor)
        if framecolor is not None:
            self.canvas.figure.set_facecolor(framecolor)

        conf.set_trace_zorder(zorder)
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
        if fullbox is not None and not fullbox:
            conf.axes_style = 'open'
        if axes_style in ('open', 'box', 'bottom'):
            conf.axes_style = axes_style
        conf.set_axes_style()

        if not delay_draw:
            self.draw()
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
        self.draw()

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
        self.draw()

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
        self.set_viewlimits()

        if self.conf.show_grid:
            for i in axes.get_xgridlines()+axes.get_ygridlines():
                i.set_color(self.conf.grid_color)
                i.set_zorder(-30)
            axes.grid(True)
        else:
            axes.grid(False)
        self.set_viewlimits()
        self.draw()

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
            # print mask
            pts = nonzero(mask)[0]

        self.lasso = None
        self.draw()
        # self.canvas.draw_idle()
        if (self.lasso_callback is not None and
            hasattr(self.lasso_callback , '__call__')):
            self.lasso_callback(data = sdat,
                                selected = pts, mask=mask)

    def set_xylims(self, limits, axes=None, side='left'):
        "set user-defined limits and apply them"
        if axes is None:
            axes = self.axes
            if side == 'right':
                axes = self.get_right_axes()
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
                len(self.conf.zoom_lims) > 0)):

                for i, val in enumerate(self.user_limits[axes]):
                    if val is not None:
                        limits[i] = val
                xmin, xmax, ymin, ymax = limits
                if len(self.conf.zoom_lims) > 0:
                    limits_set = True
                    xmin, xmax, ymin, ymax = self.conf.zoom_lims[-1][axes]
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
        if len(self.conf.zoom_lims) > 1:
            self.conf.zoom_lims.pop()
        self.set_viewlimits()
        self.draw()

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
        if self.win_config is not None:
            try:
                self.win_config.Raise()
            except:
                self.win_config = None

        if self.win_config is None:
            self.win_config = PlotConfigFrame(parent=self,
                                              config=self.conf,
                                              trace_color_callback=self.trace_color_callback)
            self.win_config.Raise()


    ####
    ## create GUI
    ####
    def BuildPanel(self):
        """ builds basic GUI panel and popup menu"""
        self.fig   = Figure(self.figsize, dpi=self.dpi)
        # 1 axes for now
        self.gridspec = GridSpec(1,1)
        self.axes  = self.fig.add_subplot(self.gridspec[0], axisbg=self.axisbg)

        self.canvas = FigureCanvas(self, -1, self.fig)

        self.printer.canvas = self.canvas
        self.set_bg()
        self.conf.canvas = self.canvas
        self.canvas.SetCursor(wxCursor(wx.CURSOR_CROSS))
        self.canvas.mpl_connect("pick_event", self.__onPickEvent)

        # overwrite ScalarFormatter from ticker.py here:
        self.axes.xaxis.set_major_formatter(FuncFormatter(self.xformatter))
        self.axes.yaxis.set_major_formatter(FuncFormatter(self.yformatter))

        # This way of adding to sizer allows resizing
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 2, wx.LEFT|wx.TOP|wx.BOTTOM|wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.autoset_margins()
        self.SetSizer(sizer)
        self.Fit()

        canvas_draw = self.canvas.draw
        def draw(*args, **kws):
            self.autoset_margins()
            canvas_draw(*args, **kws)
        self.canvas.draw = draw
        self.addCanvasEvents()

    def _updateCanvasDraw(self):
        """ Overload of the draw function that update
        axes position before each draw"""
        fn = self.canvas.draw
        def draw2(*a,**k):
            self._updateGridSpec()
            return fn(*a,**k)
        self.canvas.draw = draw2

    def get_default_margins(self):
        """get default margins"""
        trans = self.fig.transFigure.inverted().transform

        # Static margins
        l, t, r, b = self.axesmargins
        (l, b), (r, t) = trans(((l, b), (r, t)))

        # print "AutoSet Margins 0b: (%.3f, %.3f, %.3f, %.3f)" %  (l, t, r, b)
        # Extent
        dl, dt, dr, db = 0, 0, 0, 0
        for i, ax in enumerate(self.fig.get_axes()):
            (x0, y0),(x1, y1) = ax.get_position().get_points()
            (ox0, oy0), (ox1, oy1) = ax.get_tightbbox(self.canvas.get_renderer()).get_points()
            (ox0, oy0), (ox1, oy1) = trans(((ox0 ,oy0),(ox1 ,oy1)))

            dl = max(dl, (x0 - ox0))
            dt = max(dt, (oy1 - y1))
            dr = max(dr, (ox1 - x1))
            db = max(db, (y0 - oy0))

        # print(" > %.3f %.3f %.3f %.3f " % (dl, dt, dr, db))
        return (l + dl, t + dt, r + dr, b + db)

    def autoset_margins(self):
        """auto-set margins  left, bottom, right, top
        according to the specified margins (in pixels)
        and axes extent (taking into account labels,
        title, axis)
        """
        if not self.conf.auto_margins:
            return
        # coordinates in px -> [0,1] in figure coordinates
        trans = self.fig.transFigure.inverted().transform

        # Static margins
        self.conf.margins = l, t, r, b = self.get_default_margins()
        self.gridspec.update(left=l, top=1-t, right=1-r, bottom=b)

        # Axes positions update
        for ax in self.fig.get_axes():
            try:
                ax.update_params()
            except ValueError:
                pass
            ax.set_position(ax.figbox)

    def draw(self):
        self.canvas.draw()

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

        if update_limits:
            self.set_viewlimits()
        if draw:
            self.draw()

    def get_figure(self):
        return self.fig

    def __onPickEvent(self, event=None):
        """pick events"""
        legline = event.artist
        trace = self.conf.legend_map.get(legline, None)
        visible = True
        if trace is not None and self.conf.hidewith_legend:
            line, legline, legtext = trace
            visible = not line.get_visible()
            line.set_visible(visible)
            if visible:
                legline.set_zorder(10.00)
                legline.set_alpha(1.00)
                legtext.set_zorder(10.00)
                legtext.set_alpha(1.00)
            else:
                legline.set_alpha(0.50)
                legtext.set_alpha(0.50)


    def onExport(self, event=None, **kws):
        ofile  = ''
        title = 'unknown plot'

        if self.conf.title is not None:
            title = ofile = self.conf.title.strip()
        if len(ofile) > 64:
            ofile = ofile[:63].strip()
        if len(ofile) < 1:
            ofile = 'plot'

        for c in ' .:";|/\\(){}[]\'&^%*$+=-?!@#':
            ofile = ofile.replace(c, '_')

        while '__' in ofile:
            ofile = ofile.replace('__', '_')

        ofile = ofile + '.dat'

        dlg = wx.FileDialog(self, message='Export Map Data to ASCII...',
                            defaultDir = os.getcwd(),
                            defaultFile=ofile,
                            style=wx.FD_SAVE|wx.FD_CHANGE_DIR)

        if dlg.ShowModal() == wx.ID_OK:
            self.writeASCIIFile(dlg.GetPath(), title=title)

    def writeASCIIFile(self, fname, title='unknown plot'):
        buff = ["# X,Y Data for %s" % title,
                "#------------", "#     X     Y"]
        lines= self.axes.get_lines()
        x0 = lines[0].get_xaxis()
        y0 = lines[0].get_yaxis()
        lab0 = lines[0].get_label().strip()
        if len(lab0) < 1: lab0 =  'Y'
        buff.append("#   X    %s" % lab0)
        outa = [x0, y0]
        npts = len(x0)
        if len(lines)  > 1:
            for ix, line in enumerate(lines[1:]):
                lab = ['#   ', '       ',
                       line.get_label().strip()]
                x = line.get_xdata()
                y = line.get_ydata()
                npts = max(npts, len(y))
                if not all(x==x0):
                    lab0[1]  = ' X%i ' % (ix+2)
                    out.append(x)
                out.append(line.get_ydata())

        fout = open(fname, 'w')
        fout.write("%s\n" % "\n".join(buff))
        fout.close()

        orig_dir = os.path.abspath(os.curdir)
        thisdir = os.getcwd()
        file_choices = "DAT (*.dat)|*.dat|ALL FILES (*.*)|*.*"
        dlg = wx.FileDialog(self,
                            message='Export Plot Data to ASCII...',
                            defaultDir=thisdir,
                            defaultFile=ofile,
                            wildcard=file_choices,
                            style=wx.FD_SAVE|wx.FD_CHANGE_DIR)

        if dlg.ShowModal() == wx.ID_OK:
            self.writeASCIIFile(dlg.GetPath(), title=title)
        os.chdir(orig_dir)

    def writeASCIIFile(self, fname, title='unknown plot'):
        "save plot data to external file"

        buff = ["# Plot Data for %s" % title, "#------"]

        out = []
        labs = []
        itrace = 0
        for ax in self.fig.get_axes():
            for line in ax.lines:
                itrace += 1
                x = line.get_xdata()
                y = line.get_ydata()
                ylab = line.get_label()

                if len(ylab) < 1: ylab = ' Y%i' % itrace
                if len(ylab) < 4: ylab = ' %s%s' % (' '*4, lab)
                for c in ' .:";|/\\(){}[]\'&^%*$+=-?!@#':
                    ylab = ylab.replace(c, '_')

                pad = max(1, 13-len(ylab))
                lab = '     X%i   %s%s  ' % (itrace, ' '*pad, ylab)
                out.extend([x, y])
                labs.append(lab)
        buff.append('# %s ' % (' '.join(labs)))

        npts = [len(a) for a in out]
        for i in range(max(npts)):
            oline = []
            for a in out:
                d = nan
                if i < len(a):  d = a[i]
                oline.append(gformat(d))
            buff.append(' '.join(oline))

        if itrace > 0:
            fout = open(fname, 'w')
            fout.write("%s\n" % "\n".join(buff))
            fout.close()
            self.write_message("Exported data to '%s'" % fname,
                               panel=0)

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
