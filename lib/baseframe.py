#!/usr/bin/python
##
## MPlot PlotFrame: a wx.Frame for 2D line plotting, using matplotlib
##

from . import __version__
import os
import time
import wx
import matplotlib
from .plotpanel import PlotPanel
from .utils import MenuItem

class Menu_IDs:
    def __init__(self):
        pass

class BaseFrame(wx.Frame):
    """
    MatPlotlib 2DRadio plot as a wx.Frame, using PlotPanel
    """
    help_msg =  """Quick help:

 Left-Click:   to display X,Y coordinates
 Left-Drag:    to zoom in on plot region
 Right-Click:  display popup menu with choices:
                Zoom out 1 level
                Zoom all the way out
                --------------------
                Configure
                Save Image

Also, these key bindings can be used
(For Mac OSX, replace 'Ctrl' with 'Apple'):

  Ctrl-S:     save plot image to file
  Ctrl-C:     copy plot image to clipboard
  Ctrl-K:     Configure Plot
  Ctrl-Q:     quit

"""

    about_msg =  """WXMPlot  version %s
Matt Newville <newville@cars.uchicago.edu>""" % __version__

    def __init__(self, parent=None, panel=None, title='', size=None,
                 axisbg=None, exit_callback=None, user_menus=None,
                 output_title='Plot', dpi=150, **kws):
        if size is None: size = (700,450)
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
        self.size = size
        self.axisbg = axisbg

    def write_message(self,s,panel=0):
        """write a message to the Status Bar"""
        self.SetStatusText(s, panel)

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
        # Python3 note: wxPython has no THICK_FRAME
        sbar = self.CreateStatusBar(2, wx.CAPTION)
        sfont = sbar.GetFont()
        sfont.SetWeight(wx.BOLD)
        sfont.SetPointSize(10)
        sbar.SetFont(sfont)

        self.SetStatusWidths([-3,-1])
        self.SetStatusText('',0)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel = PlotPanel(self, size=self.size,
                               axisbg=self.axisbg,
                               output_title=self.output_title)
        self.panel.messenger = self.write_message
        sizer.Add(self.panel, 1, wx.EXPAND)
        self.BuildMenu()

        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Fit()


    def Build_FileMenu(self, extras=None):
        mfile = wx.Menu()
        MenuItem(self, mfile, "&Save Image\tCtrl+S",
                 "Save Image of Plot (PNG, SVG, JPG)",
                 action=self.save_figure)
        MenuItem(self, mfile, "&Copy\tCtrl+C",
                 "Copy Plot Image to Clipboard",
                 self.Copy_to_Clipboard)

        MenuItem(self, mfile, "Export Data",
                "Export Data to ASCII Column file",
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
        MenuItem(self, mopts, "Zoom Out\tCtrl+Z",
                 "Zoom out to full data range",
                 self.panel.unzoom)

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
        if self.panel is not None:
            self.panel.onExport(event=event)
        else:
            dlg = wx.MessageDialog(self, "Export Data not available",
                                   "Export Data to ASCII",
                                   wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()

    def onHelp(self, event=None):
        dlg = wx.MessageDialog(self, self.help_msg, "WXMPlot Quick Reference",
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def onExit(self, event=None):
        try:
            if hasattr(self.exit_callback, '__call__'):
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
