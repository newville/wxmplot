#!/usr/bin/python
"""
wxmplot PlotPanel: a wx.Panel for line plotting, using matplotlib
"""
import os
import sys
from functools import partial
from datetime import datetime

import wx

from numpy import nonzero, where
import matplotlib
from matplotlib import dates
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.gridspec import GridSpec
from matplotlib.colors import colorConverter
from matplotlib.collections import CircleCollection

from .basepanel import BasePanel
from .config import PlotConfig, ifnot_none
from .utils import inside_poly, fix_filename, gformat, MenuItem
from .plotconfigframe import PlotConfigFrame

to_rgba = colorConverter.to_rgba

class PlotPanel(BasePanel):
    """
    MatPlotlib line plot as a wx.Panel, suitable for embedding
    in any wx.Frame.   This does provide a right-click popup
    menu for configuration, zooming, saving an image of the
    figure, and Ctrl-C for copy-image-to-clipboard.

    For more features, see PlotFrame, which embeds a PlotPanel
    and also provides, a Menu, StatusBar, and Printing support.
    """

    def __init__(self, parent, size=(700, 450), dpi=150, axisbg=None,
                 facecolor=None, fontsize=9, trace_color_callback=None,
                 output_title='plot', with_data_process=True, theme=None,
                 **kws):

        self.trace_color_callback = trace_color_callback
        BasePanel.__init__(self, parent,
                           output_title=output_title, size=size, **kws)

        self.conf = PlotConfig(panel=self, theme=theme,
                               with_data_process=with_data_process)
        self.data_range = {}
        self.win_config = None
        self.cursor_callback = None
        self.lasso_callback = None
        self.cursor_mode = 'zoom'
        self.parent  = parent
        self.figsize = (size[0]*1.0/dpi, size[1]*1.0/dpi)
        self.dpi  = dpi
        self.conf.facecolor = ifnot_none(axisbg, self.conf.facecolor)
        self.conf.facecolor = ifnot_none(facecolor, self.conf.facecolor)

        # axesmargins : margins in px left/top/right/bottom
        self.axesmargins = (30, 30, 30, 30)

        self.BuildPanel()
        self.conf.user_limits = {} # [None, None, None, None]
        self.data_range = {}
        self.conf.zoom_lims = []
        self.conf.axes_traces = {}
        self.use_dates = False
        self.dates_style = None

    def plot(self, xdata, ydata, side='left', title=None,
             xlabel=None, ylabel=None, y2label=None,
             use_dates=False, dates_style=None, **kws):
        """
        create a new plot of x/y data, clearing any existing plot on the panel

        """
        allaxes = self.fig.get_axes()
        if len(allaxes) > 1:
            for ax in allaxes[1:]:
                if ax in self.data_range:
                    self.data_range.pop(ax)
                self.fig.delaxes(ax)

        self.data_range = {}
        self.conf.zoom_lims = []
        self.conf.axes_traces = {}
        self.clear()
        axes = self.axes
        if side == 'right':
            axes = self.get_right_axes()
        self.conf.reset_lines()
        self.conf.yscale = 'linear'
        self.conf.user_limits[axes] = 4*[None]

        if xlabel is not None:
            self.set_xlabel(xlabel, delay_draw=True)
        if ylabel is not None:
            self.set_ylabel(ylabel, delay_draw=True)
        if y2label is not None:
            self.set_y2label(y2label, delay_draw=True)
        if title is not None:
            self.set_title(title, delay_draw=True)
        self.dates_style = ifnot_none(dates_style, self.dates_style)
        self.use_dates = ifnot_none(use_dates, self.use_dates)
        return self.oplot(xdata, ydata, side=side, **kws)


    def oplot(self, xdata, ydata, side='left', label=None, xlabel=None,
              ylabel=None, y2label=None, title=None, dy=None,
              ylog_scale=None, xlog_scale=None, grid=None, xmin=None,
              xmax=None, ymin=None, ymax=None, color=None, style=None, alpha=None,
              fill=False, drawstyle=None, linewidth=2,
              marker=None, markersize=None, refresh=True, show_legend=None,
              legend_loc='best', legend_on=True, delay_draw=False,
              bgcolor=None, framecolor=None, gridcolor=None, textcolor=None,
              labelfontsize=None, titlefontsize=None, legendfontsize=None,
              fullbox=None, axes_style=None, zorder=None, viewpad=None,
              theme=None, use_dates=None, dates_style=None, **kws):
        """
        basic plot method, adding to an existing display

        """
        self.cursor_mode = 'zoom'
        conf = self.conf
        conf.plot_type = 'lineplot'
        axes = self.axes
        if theme is not None:
            conf.set_theme(theme=theme)
        if side == 'right':
            axes = self.get_right_axes()
        # set y scale to log/linear
        if ylog_scale is not None:
            conf.yscale = {False:'linear', True:'log'}[ylog_scale]

        if xlog_scale is not None:
            conf.xscale = {False:'linear', True:'log'}[xlog_scale]

        axes.xaxis.set_major_formatter(FuncFormatter(self.xformatter))
        self.dates_style = ifnot_none(dates_style, self.dates_style)
        self.use_dates = ifnot_none(use_dates, self.use_dates)
        if isinstance(xdata[0], datetime):
            self.use_dates = True

        if self.use_dates:
            # date handling options to get xdate to mpl dates
            #   1. xdate are in datetime: convert to mpl dates
            #   2. xdata are strings: parse with datestr2num
            #   3. xdata are floats:
            #        a) dates_styles=='dates': use directly
            #        b) else: convert as unix timestamp to mpl dates
            x0 = xdata[0]
            dstyle = self.dates_style
            if dstyle is None: dstyle = ''
            if isinstance(x0, datetime):
                xdata = dates.date2num(xdata)
            elif isinstance(x0, str) or dstyle.lower().startswith('str'):
                xdata = dates.datestr2num(xdata)
            elif not dstyle.lower().startswith('dates'):
                xdata = dates.epoch2num(xdata)
        linewidth = ifnot_none(linewidth, 2)
        conf.viewpad = ifnot_none(viewpad, conf.viewpad)

        if xlabel is not None:
            self.set_xlabel(xlabel, delay_draw=delay_draw)
        if ylabel is not None:
            self.set_ylabel(ylabel, delay_draw=delay_draw)
        if y2label is not None:
            self.set_y2label(y2label, delay_draw=delay_draw)
        if title  is not None:
            self.set_title(title, delay_draw=delay_draw)
        if show_legend is not None:
            conf.set_legend_location(legend_loc, legend_on)
            conf.show_legend = show_legend

        conf.show_grid = ifnot_none(grid, conf.show_grid)

        # set data range for this trace
        # datarange = [min(xdata), max(xdata), min(ydata), max(ydata)]

        if axes not in conf.user_limits:
            conf.user_limits[axes] = [None, None, None, None]

        conf.user_limits[axes][0] = ifnot_none(xmin, conf.user_limits[axes][0])
        conf.user_limits[axes][1] = ifnot_none(xmax, conf.user_limits[axes][1])
        conf.user_limits[axes][2] = ifnot_none(ymin, conf.user_limits[axes][2])
        conf.user_limits[axes][3] = ifnot_none(ymax, conf.user_limits[axes][3])

        if axes == self.axes:
            axes.yaxis.set_major_formatter(FuncFormatter(self.yformatter))
        else:
            axes.yaxis.set_major_formatter(FuncFormatter(self.y2formatter))

        zorder = ifnot_none(zorder, 5*(conf.ntrace+1))

        if axes not in conf.axes_traces:
            conf.axes_traces[axes] = []
        conf.axes_traces[axes].append(conf.ntrace)

        conf.gridcolor = ifnot_none(gridcolor, conf.gridcolor)
        conf.set_gridcolor(conf.gridcolor)

        conf.facecolor = ifnot_none(bgcolor, conf.facecolor)
        conf.set_facecolor(conf.facecolor)

        conf.textcolor = ifnot_none(textcolor, conf.textcolor)
        conf.set_textcolor(conf.textcolor)

        if framecolor is not None:
            conf.set_framecolor(framecolor)

        conf.set_trace_zorder(zorder, delay_draw=True)
        if color:
            conf.set_trace_color(color, delay_draw=True)
        if style:
            conf.set_trace_style(style, delay_draw=True)
        if marker:
            conf.set_trace_marker(marker, delay_draw=True)
        if linewidth is not None:
            conf.set_trace_linewidth(linewidth, delay_draw=True)
        if markersize is not None:
            conf.set_trace_markersize(markersize, delay_draw=True)
        if drawstyle is not None:
            conf.set_trace_drawstyle(drawstyle, delay_draw=True)
        if alpha is not None:
            conf.set_trace_alpha(alpha, delay_draw=True)

        conf.dy[conf.ntrace] = dy
        if fill:
            fkws = dict(step=None, zorder=zorder, color=color)
            if drawstyle != 'default':
                fkws['step'] = drawstyle
            if dy is None:
                _fill = axes.fill_between(xdata, ydata, y2=0, **fkws)
            else:
                _fill = axes.fill_between(xdata, ydata-dy, y2=ydata+dy, **fkws)
        else: # not filling -- most plots here
            _fill = None
            if dy is not None:
                ebar = axes.errorbar(xdata, ydata, yerr=dy, zorder=zorder)
                _lines = [ebar.lines[0], ebar.lines[2]]
            else:
                _lines = axes.plot(xdata, ydata, drawstyle=drawstyle, zorder=zorder)
        conf.traces[conf.ntrace].fill = fill

        if axes not in conf.data_save:
            conf.data_save[axes] = []
        conf.data_save[axes].append((xdata, ydata))

        if conf.show_grid and axes == self.axes:
            # I'm sure there's a better way...
            for i in axes.get_xgridlines() + axes.get_ygridlines():
                i.set_color(conf.gridcolor)
                i.set_zorder(-100)
            axes.grid(True)
        else:
            axes.grid(False)

        if (self.conf.xscale == 'log' or self.conf.yscale == 'log'):
            self.set_logscale(xscale=self.conf.xscale,
                              yscale=self.conf.yscale,
                              delay_draw=delay_draw)

        if label is None:
            label = 'trace %i' % (conf.ntrace+1)
        conf.set_trace_label(label, delay_draw=True)
        needs_relabel = False
        if labelfontsize is not None:
            conf.labelfont.set_size(labelfontsize)
            needs_relabel = True
        if titlefontsize is not None:
            conf.titlefont.set_size(titlefontsize)
            needs_relabel = True

        if legendfontsize is not None:
            conf.legendfont.set_size(legendfontsize)
            needs_relabel = True

        if conf.ntrace < len(conf.lines):
            conf.lines[conf.ntrace] = _lines
            conf.fills[conf.ntrace] = _fill
        else:
            conf.init_trace(conf.ntrace, 'black', 'solid')
            conf.lines.append(_lines)
            conf.fills.append(_fill)

        # now set plot limits:
        if not delay_draw:
            self.set_viewlimits()

        if refresh:
            conf.refresh_trace(conf.ntrace)
            needs_relabel = True

        if conf.show_legend and not delay_draw:
            conf.draw_legend()

        if needs_relabel and not delay_draw:
            conf.relabel()


        # axes style ('box' or 'open')
        conf.axes_style = 'box'
        if fullbox is not None and not fullbox:
            conf.axes_style = 'open'
        if axes_style in ('open', 'box', 'bottom'):
            conf.axes_style = axes_style
        conf.set_axes_style(delay_draw=delay_draw)
        if not delay_draw:
            self.draw()
            self.canvas.Refresh()
        conf.ntrace = conf.ntrace + 1
        return _lines

    def plot_many(self, datalist, side='left', title=None,
                  xlabel=None, ylabel=None, **kws):
        """
        plot many traces at once, taking a list of (x, y) pairs
        """
        def unpack_tracedata(tdat, **kws):
            if (isinstance(tdat, dict) and
                'xdata' in tdat and 'ydata' in tdat):
                xdata = tdat.pop('xdata')
                ydata = tdat.pop('ydata')
                out = kws
                out.update(tdat)
            elif isinstance(tdat, (list, tuple)):
                out = kws
                xdata = tdat[0]
                ydata = tdat[1]
            return (xdata, ydata, out)

        conf = self.conf
        opts = dict(side=side, title=title, xlabel=xlabel, ylabel=ylabel,
                    delay_draw=True)
        opts.update(kws)
        x0, y0, opts = unpack_tracedata(datalist[0], **opts)

        nplot_traces = len(conf.traces)
        nplot_request = len(datalist)
        if nplot_request > nplot_traces:
            linecolors = conf.linecolors
            ncols = len(linecolors)
            for i in range(nplot_traces, nplot_request+5):
                conf.init_trace(i,  linecolors[i%ncols], 'dashed')


        self.plot(x0, y0, **opts)


        for dat in datalist[1:]:
            x, y, opts = unpack_tracedata(dat, delay_draw=True)
            self.oplot(x, y, **opts)

        self.reset_formats()

        if conf.show_legend:
            conf.draw_legend()
        conf.relabel()
        self.draw()
        self.canvas.Refresh()

    def add_text(self, text, x, y, side='left', size=None,
                 rotation=None, ha='left', va='center',
                 family=None, **kws):
        """add text at supplied x, y position
        """
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
                    viewpad=None, title=None, grid=None, callback=None, **kw):

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
        if viewpad is not None:
            self.conf.viewpad = viewpad

        axes = self.axes
        self.conf.user_limits[axes] = [xmin, xmax, ymin, ymax]

        self.conf.axes_traces = {axes: [0]}
        self.conf.set_trace_label('scatterplot')
        # self.conf.set_trace_datarange((min(xdata), max(xdata),
        #                                min(ydata), max(ydata)))

        self.conf.scatter_xdata = xdata
        self.conf.scatter_ydata = ydata
        self.axes.scatter(xdata, ydata, c=self.conf.scatter_normalcolor,
                          edgecolors=self.conf.scatter_normaledge)

        if self.conf.show_grid:
            for i in axes.get_xgridlines()+axes.get_ygridlines():
                i.set_color(self.conf.gridcolor)
                i.set_zorder(-30)
            axes.grid(True)
        else:
            axes.grid(False)
        xrange = max(xdata) - min(xdata)
        yrange = max(ydata) - min(ydata)

        xmin = min(xdata) - xrange/25.0
        xmax = max(xdata) + xrange/25.0
        ymin = min(ydata) - yrange/25.0
        ymax = max(ydata) + yrange/25.0

        axes.set_xlim((xmin, xmax), emit=True)
        axes.set_ylim((ymin, ymax), emit=True)
        self.set_viewlimits()
        self.draw()

    def lassoHandler(self, vertices):
        conf = self.conf
        if self.conf.plot_type == 'scatter':
            xd, yd = conf.scatter_xdata, conf.scatter_ydata
            sdat = list(zip(xd, yd))
            oldmask = conf.scatter_mask
            try:
                self.axes.scatter(xd[where(oldmask)], yd[where(oldmask)],
                                  s=conf.scatter_size,
                                  c=conf.scatter_normalcolor,
                                  edgecolors=conf.scatter_normaledge)
            except IndexError:
                self.axes.scatter(xd, yd, s=conf.scatter_size,
                                  c=conf.scatter_normalcolor,
                                  edgecolors=conf.scatter_normaledge)

            mask = conf.scatter_mask = inside_poly(vertices, sdat)
            pts = nonzero(mask)[0]
            self.axes.scatter(xd[where(mask)], yd[where(mask)],
                              s=conf.scatter_size,
                              c=conf.scatter_selectcolor,
                              edgecolors=conf.scatter_selectedge)

        else:
            xdata = self.axes.lines[0].get_xdata()
            ydata = self.axes.lines[0].get_ydata()
            sdat = [(x, y) for x, y in zip(xdata, ydata)]
            mask = inside_poly(vertices,sdat)
            pts = nonzero(mask)[0]

        self.lasso = None
        self.draw()
        # self.canvas.draw_idle()
        if (self.lasso_callback is not None and
            hasattr(self.lasso_callback , '__call__')):
            self.lasso_callback(data = sdat,
                                selected=pts, mask=mask)

    def set_xylims(self, limits, axes=None, side='left'):
        "set user-defined limits and apply them"
        if axes is None:
            axes = self.axes
            if side == 'right':
                axes = self.get_right_axes()
        self.conf.user_limits[axes] = list(limits)
        self.unzoom_all()

    def set_viewlimits(self):
        """updates xy limits of a plot based on current data,
        user defined limits, and any zoom level

        """
        self.reset_formats()
        self.conf.set_viewlimits()

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
        self.conf.data_save = {}

    def reset_config(self):
        """reset configuration to defaults."""
        self.conf.set_defaults()

    def unzoom(self, event=None, **kws):
        """ zoom out 1 level, or to full data range """
        self.reset_formats()
        self.conf.unzoom(full=False)

    def unzoom_all(self, event=None):
        """ zoom out full data range """
        self.reset_formats()
        self.conf.unzoom(full=True)

    def process_data(self, event=None, expr=None):
        if expr in self.conf.data_expressions:
            self.conf.data_expr = expr
            self.conf.process_data()
            self.draw()
        if expr is None:
            expr = ''
        if self.conf.data_deriv:
            if expr is None:
                expr = 'y'
            expr = "deriv(%s)" % expr
        self.write_message("plotting %s" % expr, panel=0)

    def toggle_deriv(self, event=None, value=None):
        "toggle derivative of data"
        if value is None:
            self.conf.data_deriv = not self.conf.data_deriv

            expr = self.conf.data_expr or ''
            if self.conf.data_deriv:
                expr = "deriv(%s)" % expr
            self.write_message("plotting %s" % expr, panel=0)

            self.conf.process_data()

    def set_logscale(self, event=None, xscale='linear', yscale='linear',
                     delay_draw=False):
        "set log or linear scale for x, y axis"
        self.conf.set_logscale(xscale=xscale, yscale=yscale,
                               delay_draw=delay_draw)

    def toggle_legend(self, evt=None, show=None):
        "toggle legend display"
        if show is None:
            show = not self.conf.show_legend
            self.conf.show_legend = show
        self.conf.draw_legend()

    def toggle_grid(self, event=None, show=None):
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
    ####x
    def BuildPanel(self):
        """ builds basic GUI panel and popup menu"""
        self.fig   = Figure(self.figsize, dpi=self.dpi)
        # 1 axes for now
        self.gridspec = GridSpec(1,1)
        self.axes  = self.fig.add_subplot(self.gridspec[0],
                                          facecolor=self.conf.facecolor)
        self.canvas = FigureCanvas(self, -1, self.fig)
        self.canvas.SetClientSize((self.figsize[0]*self.dpi, self.figsize[1]*self.dpi))
        self.canvas.SetMinSize((100, 100))
        self.canvas.gui_repaint = self.gui_repaint

        self.printer.canvas = self.canvas
        self.set_bg(self.conf.framecolor)
        self.conf.canvas = self.canvas
        self.canvas.SetCursor(wx.Cursor(wx.CURSOR_CROSS))
        self.canvas.mpl_connect("pick_event", self.__onPickEvent)

        # overwrite ScalarFormatter from ticker.py here:
        self.axes.xaxis.set_major_formatter(FuncFormatter(self.xformatter))
        self.axes.yaxis.set_major_formatter(FuncFormatter(self.yformatter))

        # This way of adding to sizer allows resizing
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 2, wx.LEFT|wx.TOP|wx.BOTTOM|wx.EXPAND, 0)
        # self.SetAutoLayout(True)
        self.autoset_margins()
        self.SetSizer(sizer)
        self.SetSize(self.GetBestVirtualSize())

        canvas_draw = self.canvas.draw
        def draw(*args, **kws):
            self.autoset_margins()
            canvas_draw(*args, **kws)
        self.canvas.draw = draw
        self.addCanvasEvents()

    def BuildPopup(self):
        # build pop-up menu for right-click display
        self.popup_menu = popup = wx.Menu()
        MenuItem(self, popup, 'Configure', '',   self.configure)

        MenuItem(self, popup, 'Save Image', '',   self.save_figure)
        popup.AppendSeparator()

        MenuItem(self, popup, 'Undo Zoom/Pan', '',   self.unzoom)
        MenuItem(self, popup, 'Zoom all the way out', '', self.unzoom_all)

        popup.AppendSeparator()
        MenuItem(self, popup, 'Zoom X and Y', '',
                 partial(self.onZoomStyle, style='both x and y'),
                 kind=wx.ITEM_RADIO, checked=True)
        MenuItem(self, popup, 'Zoom X Only', '',
                 partial(self.onZoomStyle, style='x only'),
                 kind=wx.ITEM_RADIO)
        MenuItem(self, popup, 'Zoom Y Only', '',
                 partial(self.onZoomStyle, style='y only'),
                 kind=wx.ITEM_RADIO)

    def onZoomStyle(self, event=None, style='both x and y'):
        self.conf.zoom_style = style

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

        # Extent
        dl, dt, dr, db = 0, 0, 0, 0
        for ax in self.fig.get_axes():
            (x0, y0),(x1, y1) = ax.get_position().get_points()
            try:
                (ox0, oy0), (ox1, oy1) = ax.get_tightbbox(self.canvas.get_renderer()).get_points()
                (ox0, oy0), (ox1, oy1) = trans(((ox0 ,oy0),(ox1 ,oy1)))
                dl = min(0.2, max(dl, (x0 - ox0)))
                dt = min(0.2, max(dt, (oy1 - y1)))
                dr = min(0.2, max(dr, (ox1 - x1)))
                db = min(0.2, max(db, (y0 - oy0)))
            except:
                pass

        return (l + dl, t + dt, r + dr, b + db)

    def autoset_margins(self):
        """auto-set margins  left, bottom, right, top
        according to the specified margins (in pixels)
        and axes extent (taking into account labels,
        title, axis)
        """
        if not self.conf.auto_margins:
            return

        self.conf.margins = l, t, r, b = self.get_default_margins()
        self.gridspec.update(left=l, top=1-t, right=1-r, bottom=b)
        # Axes positions update
        for ax in self.fig.get_axes():
            figpos = ax.get_subplotspec().get_position(self.canvas.figure)
            ax.set_position(figpos)

    def draw(self):
        self.canvas.draw()

    def update_line(self, trace, xdata, ydata, side='left', draw=False,
                    update_limits=True):
        """ update a single trace, for faster redraw """

        x = self.conf.get_mpl_line(trace)
        x.set_data(xdata, ydata)
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
        legtrace = self.conf.legend_map.get(legline, None)
        visible = True
        if legtrace is not None and self.conf.hidewith_legend:
            line, trace, legline, legtext = legtrace
            visible = not line.get_visible()
            line.set_visible(visible)
            if self.conf.fills[trace] is not None:
                self.conf.fills[trace].set_visible(visible)

            if visible:
                legline.set_zorder(10.00)
                legline.set_alpha(1.00)
                legtext.set_zorder(10.00)
                legtext.set_alpha(1.00)
            else:
                legline.set_alpha(0.50)
                legtext.set_alpha(0.50)


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
            msg = "X,Y= %g, %g" % (x, y)
        if len(self.fig.get_axes()) > 1:
            ax2 = self.fig.get_axes()[1]
            try:
                x2, y2 = ax2.transData.inverted().transform((ex, ey))
                msg = "X,Y,Y2= %g, %g, %g" % (x, y, y2)
            except:
                pass

        nsbar = getattr(self, 'nstatusbar', 1)
        self.write_message(msg,  panel=max(0, nsbar - 2))
        if (self.cursor_callback is not None and
            hasattr(self.cursor_callback , '__call__')):
            self.cursor_callback(x=event.xdata, y=event.ydata)
