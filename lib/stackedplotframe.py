#!/usr/bin/python
##
## StackedPlotFrame: a wx.Frame for 2 PlotPanels, top and bottom
##   with the top panel being the main panel and the lower panel
##   being 1/4 the height (configurable) and the dependent panel

import wx
import numpy as np
import matplotlib
from matplotlib.ticker import NullFormatter, NullLocator
from functools import partial
from .utils import pack, MenuItem
from .plotpanel import PlotPanel
from .baseframe import BaseFrame

class StackedPlotFrame(BaseFrame):
    """
    Top/Bottom MatPlotlib panels in a single frame
    """
    def __init__(self, parent=None, title ='Stacked Plot Frame',
                 framesize=(850,450), panelsize=(550,450),
                 ratio=3.0, **kws):

        BaseFrame.__init__(self, parent=parent, title=title,
                           size=framesize, **kws)
        self.ratio = ratio
        self.panelsize = panelsize
        self.panel = None
        self.panel_bot = None
        self.xlabel = None
        self.BuildFrame()

    def get_panel(self, panelname):
        if panelname.lower().startswith('bot'):
            return self.panel_bot
        return self.panel

    def plot(self, x, y, panel='top', xlabel=None, **kws):
        """plot after clearing current plot """
        panel = self.get_panel(panel)
        panel.plot(x, y, **kws)
        if xlabel is not None:
            self.xlabel = xlabel
        if self.xlabel is not None:
            self.panel_bot.set_xlabel(self.xlabel)

    def oplot(self, x, y, panel='top', xlabel=None, **kws):
        """plot method, overplotting any existing plot """
        panel = self.get_panel(panel)
        panel.oplot(x, y, **kws)
        if xlabel is not None:
            self.xlabel = xlabel
        if self.xlabel is not None:
            self.panel_bot.set_xlabel(self.xlabel)


    def update_line(self, t, x, y, panel='top', **kws):
        """overwrite data for trace t """
        panel = self.get_panel(panel)
        panel.update_line(t, x, y, **kws)

    def set_xylims(self, lims, axes=None, panel='top', **kws):
        """set xy limits"""
        panel = self.get_panel(panel)
        print("Stacked set_xylims ", panel, self.panel)
        panel.set_xylims(lims, axes=axes, **kws)

    def clear(self, panel='top'):
        """clear plot """
        panel = self.get_panel(panel)
        panel.clear()

    def unzoom_all(self, event=None, panel='top'):
        """zoom out full data range """
        panel = self.get_panel(panel)
        panel.unzoom_all(event=event)

    def unzoom(self, event=None, panel='top'):
        """zoom out 1 level, or to full data range """
        panel = self.get_panel(panel)
        panel.unzoom(event=event)

    def set_title(self,s, panel='top'):
        "set plot title"
        panel = self.get_panel(panel)
        panel.set_title(s)

    def set_xlabel(self,s, panel='top'):
        "set plot xlabel"
        self.panel_bot.set_xlabel(s)

    def set_ylabel(self,s, panel='top'):
        "set plot xlabel"
        panel = self.get_panel(panel)
        panel.set_ylabel(s)

    def save_figure(self, event=None, panel='top'):
        """ save figure image to file"""
        panel = self.get_panel(panel)
        panel.save_figure(event=event)

    def configure(self, event=None, panel='top'):
        panel = self.get_panel(panel)
        panel.configure(event=event)

    ####
    ## create GUI
    ####
    def BuildFrame(self):
        sbar = self.CreateStatusBar(2, wx.CAPTION)
        sfont = sbar.GetFont()
        sfont.SetWeight(wx.BOLD)
        sfont.SetPointSize(10)
        sbar.SetFont(sfont)

        self.SetStatusWidths([-3,-1])
        self.SetStatusText('',0)

        sizer = wx.BoxSizer(wx.VERTICAL)

        botsize = self.panelsize[0], self.panelsize[1]/self.ratio
        margins = {'top': dict(left=0.15, bottom=0.01, top=0.90, right=0.95),
                   'bot': dict(left=0.15, bottom=0.40, top=0.99, right=0.95)}

        self.panel     = PlotPanel(self, size=self.panelsize)
        self.panel_bot = PlotPanel(self, size=botsize)
        self.panel.xformatter = self.null_formatter
        self.panel_bot.yformatter = self.bot_yformatter

        for pan, pname in ((self.panel, 'top'), (self.panel_bot, 'bot')):
            pan.messenger = self.write_message
            pan.conf.auto_margins = False
            pan.gridspec.update(**margins[pname])
            pan.axes.update_params()
            pan.axes.set_position(pan.axes.figbox)
            pan.set_viewlimits = partial(self.set_viewlimits, panel=pname)
            pan.unzoom_all = self.unzoom_all
            pan.canvas.figure.set_facecolor('#F4F4EC')

        # suppress mouse events on the bottom panel
        null_events = {'leftdown': None, 'leftup': None, 'rightdown': None,
                       'rightup': None, 'motion': None, 'keyevent': None}
        self.panel_bot.cursor_modes = {'zoom': null_events}
        self.panel_bot.axes.xaxis.set_major_formatter(NullFormatter())
        self.panel_bot.axes.tick_params(axis='y', labelsize=8)

        sizer.Add(self.panel,self.ratio, wx.GROW|wx.EXPAND|wx.ALIGN_CENTER, 2)
        sizer.Add(self.panel_bot, 1,     wx.GROW|wx.EXPAND|wx.ALIGN_CENTER, 2)

        pack(self, sizer)

        self.SetAutoLayout(True)
        self.SetSizerAndFit(sizer)
        self.BuildMenu()

    def BuildMenu(self):
        mfile = self.Build_FileMenu()

        mopts = wx.Menu()
        MenuItem(self, mopts, "Configure Plot\tCtrl+K",
                 "Configure Plot styles, colors, labels, etc",
                 self.panel.configure)
        MenuItem(self, mopts, "Configure Lower Plot",
                 "Configure Plot styles, colors, labels, etc",
                 self.panel_bot.configure)
        MenuItem(self, mopts, "Toggle Legend\tCtrl+L",
                 "Toggle Legend Display",
                 self.panel.toggle_legend)
        MenuItem(self, mopts, "Toggle Grid\tCtrl+G",
                 "Toggle Grid Display",
                 self.toggle_grid)


        mopts.AppendSeparator()

        MenuItem(self, mopts, "Zoom Out\tCtrl+Z",
                 "Zoom out to full data range",
                 self.panel.unzoom)

        mhelp = wx.Menu()
        MenuItem(self, mhelp, "Quick Reference",  "Quick Reference for WXMPlot", self.onHelp)
        MenuItem(self, mhelp, "About", "About WXMPlot", self.onAbout)

        mbar = wx.MenuBar()
        mbar.Append(mfile, 'File')
        mbar.Append(mopts, '&Options')
        if self.user_menus is not None:
            for title, menu in self.user_menus:
                mbar.Append(menu, title)

        mbar.Append(mhelp, '&Help')

        self.SetMenuBar(mbar)
        self.Bind(wx.EVT_CLOSE,self.onExit)

    def toggle_grid(self, event=None, show=None):
        "toggle grid on top/bottom panels"
        if show is None:
            show = not self.panel.conf.show_grid
        for p in (self.panel, self.panel_bot):
            p.conf.enable_grid(show)



    def set_viewlimits(self, autoscale=False, panel='top'):
        """update xy limits of a plot, as used with .update_line() """
        panel = self.get_panel(panel)

        trace0 = None
        while trace0 is None:
            for axes in panel.fig.get_axes():
                if (axes in panel.axes_traces and
                   len(panel.axes_traces[axes]) > 0):
                    trace0 = panel.axes_traces[axes][0]
                    break

        for axes in panel.fig.get_axes():
            datlim = panel.conf.get_trace_datarange(trace=trace0)
            if axes in panel.axes_traces:
                for i in panel.axes_traces[axes]:
                    l =  panel.conf.get_trace_datarange(trace=i)
                    datlim = [min(datlim[0], l[0]), max(datlim[1], l[1]),
                              min(datlim[2], l[2]), max(datlim[3], l[3])]

            xmin, xmax = axes.get_xlim()
            ymin, ymax = axes.get_ylim()
            limits = [min(datlim[0], xmin),
                      max(datlim[1], xmax),
                      min(datlim[2], ymin),
                      max(datlim[3], ymax)]

            if (axes in panel.user_limits and
                (panel.user_limits[axes] != 4*[None] or
                len(panel.conf.zoom_lims) > 0)):

                for i, val in enumerate(panel.user_limits[axes]):
                    if val is not None:
                        limits[i] = val
                xmin, xmax, ymin, ymax = limits
                if len(panel.conf.zoom_lims) > 0:
                    limits_set = True
                    xmin, xmax, ymin, ymax = panel.conf.zoom_lims[-1][axes]
                axes.set_xlim((xmin, xmax), emit=True)
                axes.set_ylim((ymin, ymax), emit=True)

            # make top/bottom panel follow xlimits
            other = self.panel
            if panel == self.panel:
                other = self.panel_bot

            for _ax in other.fig.get_axes():
                _ax.set_xlim((xmin, xmax), emit=True)
            other.draw()

    def unzoom_all(self, event=None):
        """ zoom out full data range """
        for p in (self.panel, self.panel_bot):
            p.conf.zoom_lims = None

            p.unzoom(event)

    def null_formatter(self, x, pos, type='x'):
        return ''


    def bot_yformatter(self, val, type=''):
        """custom formatter for FuncFormatter() and bottom panel"""
        fmt, v = '%1.5g','%1.5g'

        ax = self.panel_bot.axes.yaxis
        try:
            dtick = 0.1 * ax.get_view_interval().span()
        except:
            dtick = 0.2

        try:
            ticks = ax.get_major_locator()()
            dtick = abs(ticks[1] - ticks[0])
        except:
            pass

        ival = 0
        if val > ticks[0]:
            ival = max(np.where(ticks <= val)[0])

        if len(ticks) > 4 and ival % 2 == 1 or ival > len(ticks)-2:
            return ''
        if   dtick > 29999:
            fmt, v = ('%1.5g', '%1.6g')
        elif dtick > 1.99:
            fmt, v = ('%1.0f', '%1.2f')
        elif dtick > 0.099:
            fmt, v = ('%1.1f', '%1.3f')
        elif dtick > 0.0099:
            fmt, v = ('%1.2f', '%1.4f')
        elif dtick > 0.00099:
            fmt, v = ('%1.3f', '%1.5f')
        elif dtick > 0.000099:
            fmt, v = ('%1.4f', '%1.6e')
        elif dtick > 0.0000099:
            fmt, v = ('%1.5f', '%1.6e')

        s =  fmt % val
        s.strip()
        s = s.replace('+', '')
        while s.find('e0')>0:
            s = s.replace('e0','e')
        while s.find('-0')>0:
            s = s.replace('-0','-')
        if type == 'y':
            self._yfmt = v
        if type == 'y2':
            self._y2fmt = v
        if type == 'x':
            self._xfmt = v
        return s
