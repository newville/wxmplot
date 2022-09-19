#!/usr/bin/python
##
## wxmplot PlotFrame: a wx.Frame for line plotting, using matplotlib
##

from . import __version__
import os
import time
import wx
import matplotlib
from functools import partial

from wxutils import get_cwd

from .plotpanel import PlotPanel
from .utils import MenuItem, fix_filename

class BaseFrame(wx.Frame):
    """
    wx.Frame with PlotPanel
    """
    help_msg =  """
Left-Click:   to display X,Y coordinates
Left-Drag:    to zoom in on plot region
Right-Click:  display popup menu with choices:
           Zoom out 1 level
           Zoom all the way out
           Configure
           Save Image

With a Plot Legend displayed, click on each label to toggle the display of that trace.

Key bindings (use 'Apple' for 'Ctrl' on MacOSX):

Ctrl-S:     Save plot image to PNG file
Ctrl-C:     Copy plot image to system clipboard
Ctrl-P:     Print plot image

Ctrl-D:     Export data to plain text file

Ctrl-L:     Toggle Display of Plot Legend
Ctrl-G:     Toggle Display of Grid

Ctrl-K:     Show Plot Configure Frame

Ctrl-Q:     Quit
"""

    about_msg =  """WXMPlot  version %s
Matt Newville <newville@cars.uchicago.edu>""" % __version__


    def __init__(self, parent=None, panel=None, title='', size=None,
                 exit_callback=None, user_menus=None, panelkws=None,
                 axisbg=None, output_title='Plot', dpi=150,
                 with_data_process=True, theme=None, **kws):
        if size is None:
            size = (700, 500)
        kws['style'] = wx.DEFAULT_FRAME_STYLE
        kws['size']  = size
        wx.Frame.__init__(self, parent, -1, title, **kws)

        self.SetMinSize((250, 250))
        self.output_title = output_title
        self.exit_callback = exit_callback
        self.parent = parent
        self.panel  = panel
        self.dpi    = dpi
        self.user_menus = user_menus
        self.with_data_process = with_data_process
        self.size = size
        self.panelkws = panelkws or {}
        self.theme = theme
        if axisbg is not None:
            self.panelkws['axisbg'] = axisbg

    def write_message(self, txt, panel=0):
        """write a message to the Status Bar"""
        self.SetStatusText(txt, panel)

    def set_xylims(self, limits, axes=None):
        """overwrite data for trace t """
        if self.panel is not None:
            self.panel.set_xylims(limits, axes=axes)

    def clear(self):
        """clear plot """
        if self.panel is not None:
            self.panel.clear()

    def unzoom_all(self,event=None):
        """zoom out full data range """
        if self.panel is not None:
            self.panel.unzoom_all(event=event)

    def unzoom(self,event=None):
        """zoom out 1 level, or to full data range """
        if self.panel is not None: self.panel.unzoom(event=event)

    def set_title(self,s):
        "set plot title"
        if self.panel is not None:
            self.panel.set_title(s)

    def set_xlabel(self,s):
        "set plot xlabel"
        if self.panel is not None: self.panel.set_xlabel(s)
        self.panel.canvas.draw()

    def set_ylabel(self,s):
        "set plot xlabel"
        if self.panel is not None: self.panel.set_ylabel(s)
        self.panel.canvas.draw()

    def save_figure(self,event=None, transparent=False, dpi=600):
        """ save figure image to file"""
        if self.panel is not None:
            self.panel.save_figure(event=event,
                                   transparent=transparent, dpi=dpi)

    def configure(self,event=None):
        if self.panel is not None: self.panel.configure(event=event)

    ####
    ## create GUI
    ####
    def BuildFrame(self):
        sbar_widths = [-2, -1, -1]
        sbar = self.CreateStatusBar(len(sbar_widths), wx.CAPTION)
        sfont = sbar.GetFont()
        sfont.SetWeight(wx.BOLD)
        sfont.SetPointSize(10)
        sbar.SetFont(sfont)
        self.SetStatusWidths(sbar_widths)

        sizer = wx.BoxSizer(wx.VERTICAL)
        panelkws = self.panelkws
        if self.size is not None:
            panelkws.update({'size': self.size})
        panelkws.update({'output_title': self.output_title,
                         'with_data_process': self.with_data_process,
                         'theme': self.theme})

        self.panel = PlotPanel(self, **panelkws)
        # self.toolbar = NavigationToolbar(self.panel.canvas)
        self.panel.messenger = self.write_message
        self.panel.nstatusbar = sbar.GetFieldsCount()
        sizer.Add(self.panel, 1, wx.EXPAND)
        self.BuildMenu()

        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.SetSize(self.GetBestVirtualSize())


    def Build_FileMenu(self, extras=None):
        mfile = wx.Menu()
        MenuItem(self, mfile, "&Save Image\tCtrl+S",
                 "Save Image of Plot (PNG, SVG, JPG)",
                 action=self.save_figure)
        MenuItem(self, mfile, "&Copy\tCtrl+C",
                 "Copy Plot Image to Clipboard",
                 self.Copy_to_Clipboard)
        MenuItem(self, mfile, "Export Data\tCtrl+D",
                 "Export Data to Text File",
                 self.onExport)

        if extras is not None:
            for text, helptext, callback in extras:
                MenuItem(self, mfile, text, helptext, callback)

        mfile.AppendSeparator()
        MenuItem(self, mfile, 'Page Setup...', 'Printer Setup',
                 self.PrintSetup)

        MenuItem(self, mfile, 'Print Preview...', 'Print Preview',
                 self.PrintPreview)

        MenuItem(self, mfile, "&Print\tCtrl+P", "Print Plot",
                 self.Print)

        mfile.AppendSeparator()
        MenuItem(self, mfile, "E&xit\tCtrl+Q", "Exit", self.onExit)
        return mfile

    def Copy_to_Clipboard(self, event=None):
        self.panel.canvas.Copy_to_Clipboard(event=event)

    def PrintSetup(self, event=None):
        self.panel.PrintSetup(event=event)

    def PrintPreview(self, event=None):
        self.panel.PrintPreview(event=event)

    def Print(self, event=None):
        self.panel.Print(event=event)

    def onZoomStyle(self, event=None, style='both x and y'):
        self.panel.conf.zoom_style = style

    def BuildMenu(self):
        mfile = self.Build_FileMenu()
        mopts = wx.Menu()
        MenuItem(self, mopts, "Configure Plot\tCtrl+K",
                 "Configure Plot styles, colors, labels, etc",
                 self.panel.configure)

        MenuItem(self, mopts, "Toggle Legend\tCtrl+L",
                 "Toggle Legend Display",
                 self.panel.toggle_legend)
        MenuItem(self, mopts, "Toggle Grid\tCtrl+G",
                 "Toggle Grid Display",
                 self.panel.toggle_grid)

        mopts.AppendSeparator()

        MenuItem(self, mopts, "Zoom X and Y\tCtrl+W",
                 "Zoom on both X and Y",
                 partial(self.onZoomStyle, style='both x and y'),
                 kind=wx.ITEM_RADIO, checked=True)
        MenuItem(self, mopts, "Zoom X Only\tCtrl+X",
                 "Zoom X only",
                 partial(self.onZoomStyle, style='x only'),
                 kind=wx.ITEM_RADIO)

        MenuItem(self, mopts, "Zoom Y Only\tCtrl+Y",
                 "Zoom Y only",
                 partial(self.onZoomStyle, style='y only'),
                 kind=wx.ITEM_RADIO)

        MenuItem(self, mopts, "Undo Zoom/Pan\tCtrl+Z",
                 "Zoom out / Pan out to previous view",
                 self.panel.unzoom)
        MenuItem(self, mopts, "Zoom all the way out",
                 "Zoom out to full data range",
                 self.panel.unzoom_all)

        mopts.AppendSeparator()

        logmenu = wx.Menu()
        for label in self.panel.conf.log_choices:
            xword, yword = label.split(' / ')
            xscale = xword.replace('x', '').strip()
            yscale = yword.replace('y', '').strip()
            MenuItem(self, logmenu, label, label,
                     partial(self.panel.set_logscale, xscale=xscale, yscale=yscale),
                     kind=wx.ITEM_RADIO)

        mopts.AppendSubMenu(logmenu, "Linear/Log Scale ")

        transmenu = None
        if self.panel.conf.with_data_process:
            transmenu = wx.Menu()
            MenuItem(self, transmenu, "Toggle Derivative", "Toggle Derivative",
                     self.panel.toggle_deriv, kind=wx.ITEM_CHECK)

            for expr in self.panel.conf.data_expressions:
                label = expr
                if label is None:
                    label = 'original Y(X)'
                MenuItem(self, transmenu, label, label,
                         partial(self.panel.process_data, expr=expr),
                         kind=wx.ITEM_RADIO)

        if transmenu is not None:
            mopts.AppendSubMenu(transmenu, "Transform Y(X)")

        mhelp = wx.Menu()
        MenuItem(self, mhelp, "Quick Reference",
                 "Quick Reference for WXMPlot", self.onHelp)
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

    def BindMenuToPanel(self, panel=None):
        pass

    def onAbout(self, event=None):
        dlg = wx.MessageDialog(self, self.about_msg, "About WXMPlot",
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def onExport(self, event=None):
        if (self.panel is None or
            not callable(getattr(self, 'ExportTextFile', None))):
            return

        try:
            title = self.panel.conf.title
        except AttributeError:
            title = None

        if title is None:
            title = self.output_title
        if title is None:
            title = self.GetTitle()

        title = title.strip()
        if title is None:
            title = 'wxmplot'

        fname = fix_filename(title + '.dat')

        origdir = get_cwd()
        file_choices = "DAT (*.dat)|*.dat|ALL FILES (*.*)|*.*"
        dlg = wx.FileDialog(self, message='Export Data to Text File',
                            defaultDir=origdir,
                            defaultFile=fname,
                            wildcard=file_choices,
                            style=wx.FD_SAVE|wx.FD_CHANGE_DIR)

        if dlg.ShowModal() == wx.ID_OK:
            self.ExportTextFile(dlg.GetPath(), title=title)
        os.chdir(origdir)

    def onHelp(self, event=None):
        dlg = wx.MessageDialog(self, self.help_msg, "WXMPlot Quick Reference",
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def onExit(self, event=None):
        try:
            if callable(self.exit_callback):
                self.exit_callback()
        except:
            pass
        try:
            if self.panel is not None:
                self.panel.win_config.Close(True)
            if self.panel is not None:
                self.panel.win_config.Destroy()
        except:
            pass

        try:
            self.Destroy()
        except:
            pass
