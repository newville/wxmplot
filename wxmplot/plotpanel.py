#!/usr/bin/python
"""
wxmplot PlotPanel: a wx.Panel for line plotting, using matplotlib
"""
from functools import partial
from datetime import datetime
import wx

from numpy import nonzero, where
import matplotlib as mpl
from matplotlib.dates import date2num, datestr2num, num2date
from matplotlib.dates import AutoDateLocator

from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.gridspec import GridSpec
from matplotlib.colors import colorConverter

from .basepanel import BasePanel
from .config import PlotConfig, ifnot_none, SIDE_YAXES
from .utils import inside_poly, MenuItem
from .plotconfigframe import PlotConfigFrame

to_rgba = colorConverter.to_rgba

def format_date(x, xrange, tz=None):
    if xrange > 12: # 12 days
        dtformat = "%Y-%m-%d"
    elif xrange > 3: # 3 days
        dtformat = "%Y-%m-%d %H"
    elif xrange > 0.25: # 6 hours
        dtformat = "%m-%d %H:%M"
    elif xrange > 0.12: #
        dtformat = "%d %H:%M:%S"
    elif xrange > 0.01: # 4.4 seconds
        dtformat = "%H:%M:%S.%f"
    else:
        dtformat = "%M:%S.%f"
    return datetime.strftime(num2date(x, tz=tz), dtformat)


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

    def plot(self, xdata, ydata, title=None, xlabel=None, ylabel=None,
             y2label=None, y3label=None, y4label=None, use_dates=False,
             dates_style=None, yaxes=1, side=None, **kws):
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
        yaxes, axes = self.get_yaxes(yaxes, side=side)

        self.conf.reset_lines()
        self.conf.yscale = 'linear'
        self.conf.user_limits[axes] = 4*[None]

        if xlabel is not None:
            self.set_xlabel(xlabel, delay_draw=True)
        if ylabel is not None:
            self.set_ylabel(ylabel, delay_draw=True)
        if y2label is not None:
            self.set_y2label(y2label, delay_draw=True)
        if y3label is not None:
            self.set_y3label(y3label, delay_draw=True)
        if y4label is not None:
            self.set_y4label(y4label, delay_draw=True)
        if title is not None:
            self.set_title(title, delay_draw=True)
        self.dates_style = ifnot_none(dates_style, self.dates_style)
        self.use_dates = ifnot_none(use_dates, self.use_dates)
        return self.oplot(xdata, ydata, yaxes=yaxes, **kws)


    def oplot(self, xdata, ydata, label=None, xlabel=None, ylabel=None,
              y2label=None, y3label=None, y4label=None, title=None, dy=None,
              ylog_scale=None, xlog_scale=None, grid=None, xmin=None,
              xmax=None, ymin=None, ymax=None, color=None, style=None,
              alpha=None, fill=False, drawstyle=None, linewidth=2, marker=None,
              markersize=None, refresh=True, show_legend=None,
              legend_loc='best', legend_on=True, delay_draw=False,
              bgcolor=None, framecolor=None, gridcolor=None, textcolor=None,
              labelfontsize=None, titlefontsize=None, legendfontsize=None,
              fullbox=None, axes_style=None, zorder=None, viewpad=None,
              theme=None, use_dates=None, dates_style=None, timezone=None,
              yaxes=1, side=None, yaxes_tracecolor=None, **kws):

        """
        basic plot method, adding to an existing display
        """
        self.cursor_mode = 'zoom'
        conf = self.conf
        conf.plot_type = 'lineplot'

        if theme is not None:
            conf.set_theme(theme=theme)

        yaxes, axes = self.get_yaxes(yaxes, side=side)
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
            #   3. xdata are floats: convert as unix timestamp to mpl dates
            axes.xaxis.set_major_locator(AutoDateLocator())
            x0 = xdata[0]
            dstyle = self.dates_style
            if dstyle is None:
                dstyle = ''
            if isinstance(x0, datetime):
                self.dates_tzinfo = xdata[0].tzinfo
                xdata = date2num(xdata)
            elif isinstance(x0, str) or dstyle.lower().startswith('str'):
                xdata = datestr2num(xdata)
            if timezone is not None:
                self.dates_tzinfo = timezone

        linewidth = ifnot_none(linewidth, 2)
        conf.viewpad = ifnot_none(viewpad, conf.viewpad)

        if xlabel is not None:
            self.set_xlabel(xlabel, delay_draw=True)
        if ylabel is not None:
            self.set_ylabel(ylabel, delay_draw=True)
        if y2label is not None:
            self.set_y2label(y2label, delay_draw=True)
        if y3label is not None:
            self.set_y3label(y3label, delay_draw=True)
        if y4label is not None:
            self.set_y4label(y4label, delay_draw=True)
        if title  is not None:
            self.set_title(title, delay_draw=True)
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

        yformatter = {1: self.yformatter,
                      2: self.y2formatter,
                      3: self.y3formatter,
                      4: self.y4formatter}.get(yaxes, self.yformatter)

        axes.yaxis.set_major_formatter(FuncFormatter(yformatter))

        zorder = ifnot_none(zorder, 5*(conf.ntrace+1))

        if axes not in conf.axes_traces:
            conf.axes_traces[axes] = []
        conf.axes_traces[axes].append(conf.ntrace)

        conf.gridcolor = ifnot_none(gridcolor, conf.gridcolor)
        conf.set_gridcolor(conf.gridcolor)
        conf.facecolor = ifnot_none(bgcolor, conf.facecolor)
        conf.set_facecolor(conf.facecolor)
        conf.textcolor = ifnot_none(textcolor, conf.textcolor)
        conf.set_textcolor(conf.textcolor, delay_draw=True)
        if framecolor is not None:
            conf.set_framecolor(framecolor)

        conf.set_trace_zorder(zorder, delay_draw=True)
        conf.set_trace_yaxes(yaxes, delay_draw=True)
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
            _lines = axes.plot(xdata, ydata, drawstyle=drawstyle, zorder=zorder, color=color)
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
            # conf.set_gridcolor(conf.gridcolor)
            mpl.rcParams['grid.color'] = conf.gridcolor

            # grid_color = mpl.rcParams["grid.color"]
            # for i in axes.get_xgridlines() + axes.get_ygridlines():
            #     i.set_color(conf.gridcolor)
            #     i.set_zorder(-100)
            axes.grid(True)
        else:
            axes.grid(False)

        if (self.conf.xscale == 'log' or self.conf.yscale == 'log'):
            self.set_logscale(xscale=self.conf.xscale,
                              yscale=self.conf.yscale,
                              delay_draw=True)

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
        if conf.show_legend:
            conf.draw_legend(delay_draw=True)

        if needs_relabel:
            conf.relabel(delay_draw=True)

        # axes style ('box' or 'open')
        conf.axes_style = 'box'
        if fullbox is not None and not fullbox:
            conf.axes_style = 'open'
        if axes_style in ('open', 'box', 'bottom'):
            conf.axes_style = axes_style

        conf.set_axes_style(delay_draw=delay_draw)
        conf.set_yaxes_tracecolor(yaxes_tracecolor, delay_draw=True)

        if not delay_draw:
            self.draw()
            # self.canvas.Refresh()
        conf.ntrace = conf.ntrace + 1
        return _lines

    def plot_many(self, datalist, title=None, xlabel=None, ylabel=None,
                  show_legend=False, zoom_limits=None, yaxes=1, side=None,
                  **kws):
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
        opts = {'yaxes': yaxes, 'title': title, 'xlabel': xlabel,
               'ylabel': ylabel, 'delay_draw': True, 'show_legend': False}
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

        self.set_zoomlimits(zoom_limits)
        self.conf.show_legend = show_legend
        if show_legend:
            conf.draw_legend(delay_draw=True)
        conf.relabel(delay_draw=True)
        self.reset_formats()
        self.draw()
        # self.canvas.Refresh()

    def get_zoomlimits(self):
        return self.axes, self.get_viewlimits(), self.conf.zoom_lims

    def set_zoomlimits(self, limits):
        """set zoom limits returned from get_zoomlimits()"""
        if limits is None:
            # print("panel.set_zoom none")
            return False
        ax, vlims, zoom_lims = limits
        if ax == self.axes:
            try:
                ax.set_xlim((vlims[0], vlims[1]), emit=True)
                ax.set_ylim((vlims[2], vlims[3]), emit=True)
                if len(zoom_lims) > 0:
                    self.conf.zoom_lims = zoom_lims
            except:
                # print("panel.set_zoom error")
                return False
        return True

    def add_text(self, text, x, y, size=None, rotation=None, ha='left',
                 va='center', family=None, yaxes=1, side=None, **kws):
        """add text at supplied x, y position
        """
        yaxes, axes = self.get_yaxes(yaxes, side=side)
        dynamic_size = False
        if size is None:
            size = self.conf.legendfont.get_size()
            dynamic_size = True
        t = axes.text(x, y, text, ha=ha, va=va, size=size,
                      rotation=rotation, family=family, **kws)
        self.conf.added_texts.append((dynamic_size, t))
        self.draw()

    def add_arrow(self, x1, y1, x2, y2, shape='full', color='black',
                  width=0.01, head_width=0.03, overhang=0, yaxes=1, side=None,
                  delay_draw=False, **kws):
        """add arrow supplied x, y position"""
        dx, dy = x2-x1, y2-y1

        yaxes, axes = self.get_yaxes(yaxes, side=side)
        axes.arrow(x1, y1, dx, dy, shape=shape,
                   length_includes_head=True,
                   fc=color, edgecolor=color,
                   width=width, head_width=head_width,
                   overhang=overhang, **kws)
        if not delay_draw:
            self.draw()

    def add_vline(self, x, ymin=0, ymax=1, side=None, yaxes=1,
                      delay_draw=False, label='_nolegend_', report_data=None, **kws):
        """add a vertical line at x

        Args:
           x (float):      x position of line, in user coordinates
           ymin (float):   starting y fraction (window units -- not user units!)
           ymax (float):   ending y y fraction (window units -- not user units!)
           delay_draw (bool): whether to delay drawing
           label (str):    label to show in legend
           report_data (dict or None): data to report on mouse cursor (left-down)
        """
        yaxes, axes = self.get_yaxes(yaxes, side=side)
        vline = axes.axvline(x, ymin=ymin, ymax=ymax, label=label, **kws)
        if report_data is not None:
            self.conf.marker_report_data.append((x, None, label, report_data))
        if not delay_draw:
            self.draw()
        return vline

    def add_hline(self, y, xmin=0, xmax=1, side=None, yaxes=1,
                      delay_draw=False, label='_nolegend_', report_data=None, **kws):
        """add a horizontal line at y

        Args:
           y (float):      y position of line, in user coordinates
           xmin (float):   starting x fraction (window units -- not user units!)
           xmax (float):   ending y x fraction (window units -- not user units!)
           delay_draw (bool): whether to delay drawing
           label (str):    label to show in legend
           report_data (dict or None): data to report on mouse cursor (left-down)
        """
        yaxes, axes = self.get_yaxes(yaxes, side=side)
        hline = axes.axhline(y, xmin=xmin, xmax=xmax, label=label, **kws)
        if report_data is not None:
            self.conf.marker_report_data.append((None, y, label, report_data))
        if not delay_draw:
            self.draw()
        return hline

    def add_marker(self, x, y, marker='o', size=4, color='black', side=None, yaxes=1,
                      delay_draw=False, label='_nolegend_', report_data=None, **kws):
        """add a marker at x, y coordinates

        Args:
           x (float):      x position of line, in user coordinates
           y (float):      y position of line, in user coordinates
           marker (str):   marker type
           size (float):   marker size
           color (str):   marker color
           delay_draw (bool): whether to delay drawing
           label (str):    label to show in legend
           report_data (dict or None): data to report on mouse cursor (left-down)
        """
        yaxes, axes = self.get_yaxes(yaxes, side=side)
        mline = self.oplot([x], [y], yaxes=yaxes, marker=marker, markersizer=size,
                           color=color, label=label, *kws)
        if report_data is not None:
            self.conf.marker_report_data.append((x, y, label, report_data))
        if not delay_draw:
            self.draw()
        return mline

    def set_xtick_labels(self, xticks, yaxes=1, side=None):
        """
        set xtick labels from dict of {x: label} pairs
        """
        yaxes, axes = self.get_yaxes(yaxes, side=side)
        axes.set_xticks(list(xticks.keys()))
        axes.set_xticklabels(list(xticks.values()))

    def set_ytick_labels(self, yticks, yaxes=1, side=None):
        """
        set ytick labels from dict of {y: label} pairs
        """
        yaxes, axes = self.get_yaxes(yaxes, side=side)
        axes.set_yticks(list(yticks.keys()))
        axes.set_yticklabels(list(yticks.values()))


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

    def set_xylims(self, limits, axes=None, yaxes=1, side=None):
        "set user-defined limits and apply them"
        if axes is None:
            yaxes, axes = self.get_yaxes(yaxes, side=side)

        self.conf.user_limits[axes] = list(limits)
        self.unzoom_all()

    def set_viewlimits(self):
        """updates xy limits of a plot based on current data,
        user defined limits, and any zoom level

        """
        self.reset_formats()
        self.conf.set_viewlimits()

    def get_viewlimits(self, axes=None):
        if axes is None:
                axes = self.axes
        xmin, xmax = axes.get_xlim()
        ymin, ymax = axes.get_ylim()
        return (xmin, xmax, ymin, ymax)

    def get_yaxes(self, n, side=None):
        """get y axis number 1, 2, 3, or 4, where
        n=1 is the normal left-hand y-axis (aka "y"),
        n=2 is the right-hand y-axis (aka "y2"), and
        n=3 is a second right-hand y-axis (aka "y3"), and
        n=4 is a third right-hand y-axis (aka "y4")
        """
        if side is not None:
            _n = SIDE_YAXES.get(side, None)
            if _n in (1, 2, 3, 4):
                n = _n
        if n not in (1, 2, 3, 4):
            raise ValueError("get_yaxes() needs value 1, 2, 3, or 4")

        while len(self.fig.get_axes()) < n:
            self.axes.twinx()
        return (n, self.fig.get_axes()[n-1])

    def get_right_axes(self, side='right'):
        """
        return right-hand (y2, y3, or y4) axes, creating if needed)

        use side='right' or 'y2' [default], or side='right2', or 'y3', or
       'right3' or 'y4',   See also  get_yaxes()
        """
        if side in ('right3', 'y4'):
            return self.get_yaxes(4)[1]
        elif side in ('right2', 'y3'):
            return self.get_yaxes(3)[1]
        else:
            return self.get_yaxes(2)[1]

    def clear(self):
        """ clear plot """
        for ax in self.fig.get_axes():
            ax.cla()
        self.conf.ntrace = 0
        self.conf.xlabel = ''
        self.conf.ylabel = ''
        self.conf.y2label = ''
        self.conf.y3label = ''
        self.conf.y4label = ''
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
        left, top, right, bot = self.axesmargins
        (left, bot), (right, top) = trans(((left, bot), (right, top)))

        # Extent
        dl, dt, dr, db = 0, 0, 0, 0
        for i, ax in enumerate(self.fig.get_axes()):
            (x0, y0),(x1, y1) = ax.get_position().get_points()
            try:
                (ox0, oy0), (ox1, oy1) = ax.get_tightbbox(self.canvas.get_renderer()).get_points()
                (ox0, oy0), (ox1, oy1) = trans(((ox0 ,oy0),(ox1 ,oy1)))
                dl = min(0.2, max(dl, (x0 - ox0)))
                dt = min(0.2, max(dt, (oy1 - y1)))
                dr = min(0.2*(i+1), max(dr, (ox1 - x1)))
                db = min(0.2, max(db, (y0 - oy0)))
            except ValueError:
                pass
        return (left + dl, top + dt, right + dr, bot + db)

    def autoset_margins(self):
        """auto-set margins  left, bottom, right, top
        according to the specified margins (in pixels)
        and axes extent (taking into account labels,
        title, axis)
        """
        if not self.conf.auto_margins:
            return

        self.conf.margins = left, top, right, bot = self.get_default_margins()
        self.gridspec.update(left=left, top=1-top, right=1-right, bottom=bot)
        # Axes positions update
        for ax in self.fig.get_axes():
            figpos = ax.get_subplotspec().get_position(self.canvas.figure)
            ax.set_position(figpos)

    def draw(self):
        self.canvas.draw()

    def update_line(self, trace, xdata, ydata,draw=False,
                    update_limits=True, yaxes=1, side=None):
        """ update a single trace, for faster redraw """
        x = self.conf.get_mpl_line(trace)
        if trace >= self.conf.ntrace:
            self.oplot(xdata, ydata, yaxes=yaxes, side=side, delay_draw=True)
        x.set_data(xdata, ydata)

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

        ax  = self.canvas.figure.get_axes()[0]
        if x is not None and y is not None:
            if self.use_dates:
                xlims = ax.get_xlim()
                xrange = abs(xlims[1] - xlims[0])
                x = format_date(x, xrange, tz=self.dates_tzinfo)
            else:
                x = f"{x:g}"
            msg = f"X,Y= {x}, {y:g}"
        if len(self.fig.get_axes()) > 1:
            ax2 = self.fig.get_axes()[1]
            try:
                x2, y2 = ax2.transData.inverted().transform((ex, ey))
                msg = f"X,Y,Y2= {x}, {y:g}, {y2:g}"
            except:
                pass

        nsbar = getattr(self, 'nstatusbar', 1)
        self.write_message(msg,  panel=max(0, nsbar-2))
        if (self.cursor_callback is not None and
            hasattr(self.cursor_callback , '__call__')):
            marker_data = []
            if (len(self.conf.marker_report_data) > 0 and
                    event.xdata is not None and
                    event.ydata is not None):
                xlims = ax.get_xlim()
                ylims = ax.get_ylim()
                xrange = max(xlims[1] - xlims[0], 1.e-14)
                yrange = max(ylims[1] - ylims[0], 1.e-14)
                for mx, my, label, extra in self.conf.marker_report_data:
                    nearx, neary = True, True
                    if mx is not None:
                        nearx = (abs(event.xdata-mx) /xrange)  < 0.01
                    if my is not None:
                        neary = (abs(event.ydata-my) /yrange)  < 0.01
                    if nearx and neary:
                        marker_data.append((mx, my, label, extra))

            self.cursor_callback(x=event.xdata, y=event.ydata,
                                 message=msg, marker_data=marker_data)

    def report_motion(self, event=None):
        if event.inaxes is None:
            return
        x, y  = event.xdata, event.ydata
        if len(self.fig.get_axes()) > 1:
            try:
                x, y = self.axes.transData.inverted().transform((event.x, event.y))
            except:
                pass
        if x is not None and y is not None:
            if self.use_dates:
                ax  = self.canvas.figure.get_axes()[0]
                xlims = ax.get_xlim()
                xrange = abs(xlims[1] - xlims[0])
                x = format_date(x, xrange, tz=self.dates_tzinfo)
            else:
                x = f"{x:g}"
            msg = f"X,Y= {x}, {y:g}"

        nsbar = getattr(self, 'nstatusbar', 1)
        self.write_message(msg, panel=max(0, nsbar-1))
