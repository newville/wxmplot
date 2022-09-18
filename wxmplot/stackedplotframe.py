#!/usr/bin/python
##
## StackedPlotFrame: a wx.Frame for 2 PlotPanels, top and bottom
##   with the top panel being the main panel and the lower panel
##   being 1/4 the height (configurable) and the dependent panel

from tempfile import NamedTemporaryFile
import os
import wx
import numpy as np
import matplotlib
from matplotlib.ticker import NullFormatter, NullLocator

from wxutils import get_cwd
from PIL import Image

from functools import partial
from .utils import pack, MenuItem, Printer
from .plotpanel import PlotPanel
from .baseframe import BaseFrame

class StackedPlotFrame(BaseFrame):
    """
    Top/Bottom MatPlotlib panels in a single frame
    """
    def __init__(self, parent=None, title ='Stacked Plot Frame',
                 framesize=(550,650), panelsize=(550,350),
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

    def unzoom_all(self, event=None):
        """ zoom out full data range """
        for p in (self.panel, self.panel_bot):
            p.conf.zoom_lims = []
            p.conf.unzoom(full=True)
        # self.panel.set_viewlimits()

    def unzoom(self, event=None, panel='top'):
        """zoom out 1 level, or to full data range """
        panel = self.get_panel(panel)
        panel.conf.unzoom(event=event)
        self.panel.set_viewlimits()

    def update_line(self, t, x, y, panel='top', **kws):
        """overwrite data for trace t """
        panel = self.get_panel(panel)
        panel.update_line(t, x, y, **kws)

    def set_xylims(self, lims, axes=None, panel='top', **kws):
        """set xy limits"""
        panel = self.get_panel(panel)
        # print("Stacked set_xylims ", panel, self.panel)
        panel.set_xylims(lims, axes=axes, **kws)

    def clear(self, panel='top'):
        """clear plot """
        panel = self.get_panel(panel)
        panel.clear()

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
        transparent = False
        dpi = 600
        file_choices = "PNG (*.png)|*.png|SVG (*.svg)|*.svg|PDF (*.pdf)|*.pdf"

        tpanel = self.get_panel('top')
        bpanel = self.get_panel('bottom')

        tfile = NamedTemporaryFile(suffix='top.png', delete=False)
        bfile = NamedTemporaryFile(suffix='bot.png', delete=False)

        tpanel.canvas.print_figure(tfile, transparent=False, dpi=600)
        bpanel.canvas.print_figure(bfile, transparent=False, dpi=600)

        timg = Image.open(tfile.name)
        bimg = Image.open(bfile.name)


        nimg = Image.new(size=(timg.size[0],
                               timg.size[1]+bimg.size[1]),
                         mode=timg.mode)
        nimg.paste(timg, (0, 0))
        nimg.paste(bimg, (0, timg.size[1]))
        os.unlink(tfile.name)
        os.unlink(bfile.name)

        try:
            ofile = tpanel.conf.title.strip()
        except:
            ofile = 'Image'
        if len(ofile) > 64:
            ofile = ofile[:63].strip()
        if len(ofile) < 1:
            ofile = 'plot'

        for c in ' :";|/\\': # "
            ofile = ofile.replace(c, '_')

        ofile = ofile + '.png'
        orig_dir = os.path.abspath(get_cwd())
        dlg = wx.FileDialog(self, message='Save Plot Figure as...',
                            defaultDir=orig_dir,
                            defaultFile=ofile,
                            wildcard=file_choices,
                            style=wx.FD_SAVE|wx.FD_CHANGE_DIR)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if nimg is not None:
                nimg.save(path)
            elif hasattr(self, 'fig'):
                tpanel.fig.savefig(path, transparent=transparent, dpi=dpi)
            else:
                tpanel.canvas.print_figure(path, transparent=transparent, dpi=dpi)

            self.write_message('Saved plot to %s' % path)
        os.chdir(orig_dir)


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
        margins = {'top': dict(left=0.15, bottom=0.01, top=0.10, right=0.05),
                   'bot': dict(left=0.15, bottom=0.300, top=0.02, right=0.05)}

        self.panel     = PlotPanel(self, size=self.panelsize)
        self.panel_bot = PlotPanel(self, size=botsize)
        self.panel.xformatter = self.null_formatter
        lsize = self.panel.conf.labelfont.get_size()
        # self.panel_bot.conf = self.panel.conf
        # self.panel_bot.conf.labelfont.set_size(lsize-2)
        self.panel_bot.yformatter = self.bot_yformatter

        self.panel.conf.theme_color_callback = self.onThemeColor
        self.panel.conf.margin_callback = self.onMargins

        for pan, pname in ((self.panel, 'top'), (self.panel_bot, 'bot')):
            pan.messenger = self.write_message
            pan.conf.auto_margins = False
            pan.conf.set_margins(**margins[pname])
            # pan.axes.update_params()
            # pan.axes.set_position(pan.axes.figbox)
            # ax.update_params()
            # ax.set_position(ax.figbox)
            figpos = pan.axes.get_subplotspec().get_position(pan.canvas.figure)
            pan.axes.set_position(figpos)

            pan.set_viewlimits = partial(self.set_viewlimits, panel=pname)
            pan.unzoom_all = self.unzoom_all
            pan.unzoom = self.unzoom
            pan.canvas.figure.set_facecolor('#F4F4EC')

        # suppress mouse events on the bottom panel
        null_events = {'leftdown': None, 'leftup': None, 'rightdown': None,
                       'rightup': None, 'motion': None, 'keyevent': None}
        self.panel_bot.cursor_modes = {'zoom': null_events}


        sizer.Add(self.panel,     round(0.75*self.ratio), wx.GROW|wx.EXPAND, 2)
        sizer.Add(self.panel_bot, 1, wx.GROW, 2)
        pack(self, sizer)
        self.SetSize(self.GetBestVirtualSize())
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
                 self.unzoom_all)

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

    def onThemeColor(self, color, item):
        """pass theme colors to bottom panel"""
        bconf = self.panel_bot.conf
        if item == 'grid':
            bconf.set_gridcolor(color)
        elif item == 'bg':
            bconf.set_facecolor(color)
        elif item == 'frame':
            bconf.set_framecolor(color)
        elif item == 'text':
            bconf.set_textcolor(color)
        bconf.canvas.draw()

    def onMargins(self, left=0.1, top=0.1, right=0.1, bottom=0.1):
        """ pass left/right margins on to bottom panel"""
        bconf = self.panel_bot.conf
        l, t, r, b = bconf.margins
        bconf.set_margins(left=left, top=t, right=right, bottom=b)
        bconf.canvas.draw()

    def set_viewlimits(self, panel='top'):
        """update xy limits of a plot, as used with .update_line() """
        this_panel = self.get_panel(panel)

        xmin, xmax, ymin, ymax = this_panel.conf.set_viewlimits()[0]
        # print("Set ViewLimits ", xmin, xmax, ymin, ymax)
        # make top/bottom panel follow xlimits
        if this_panel == self.panel:
            other = self.panel_bot
            for _ax in other.fig.get_axes():
                _ax.set_xlim((xmin, xmax), emit=True)
            other.draw()

    def null_formatter(self, x, pos, type='x'):
        return ''

    def bot_yformatter(self, val, type=''):
        """custom formatter for FuncFormatter() and bottom panel"""
        fmt = '%1.5g'

        ax = self.panel_bot.axes.yaxis

        ticks = ax.get_major_locator()()
        dtick = ticks[1] - ticks[0]

        if   dtick > 29999:
            fmt = '%1.5g'
        elif dtick > 1.99:
            fmt = '%1.0f'
        elif dtick > 0.099:
            fmt = '%1.1f'
        elif dtick > 0.0099:
            fmt = '%1.2f'
        elif dtick > 0.00099:
            fmt = '%1.3f'
        elif dtick > 0.000099:
            fmt = '%1.4f'
        elif dtick > 0.0000099:
            fmt = '%1.5f'

        s =  fmt % val
        s.strip()
        s = s.replace('+', '')
        while s.find('e0')>0:
            s = s.replace('e0','e')
        while s.find('-0')>0:
            s = s.replace('-0','-')
        return s
