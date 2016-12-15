#!/usr/bin/python
##
## Image Matrix Frame:  2 correlated images in a 2x2 grid:
#
#     +-------------+--------------+
#     |             |              |
#     |   mage1     |  image 1+2   |
#     |             |              |
#     +-------------+--------------+
#     |             |              |
#     | correlation |   image2     |
#     | plot        |              |
#     +-------------+--------------+
##

import wx
import matplotlib

from functools import partial

from .baseframe  import BaseFrame
from .plotpanel  import PlotPanel
from .imagepanel import ImagePanel
from .imageframe import ColorMapPanel
from .colors import rgb2hex
from .utils import LabelEntry, MenuItem, pack


class ImageMatrixFrame(BaseFrame):
    """
    wx.Frame, with 3 ImagePanels and correlation plot for 2 map arrays
    """
    def __init__(self, parent=None, size=(900,600),
                 subtitles=None, **kws):

        BaseFrame.__init__(self, parent=parent,
                           title  = 'Image Matrix', size=size, **kws)
        self.cmap_panels= {}
        self.subtitles = {}
        if subtitles is not None:
            self.subtitles = subtitles

        sbar = self.CreateStatusBar(2, wx.CAPTION)
        sfont = sbar.GetFont()
        sfont.SetWeight(wx.BOLD)
        sfont.SetPointSize(10)
        sbar.SetFont(sfont)

        self.SetStatusWidths([-2, -1])
        self.SetStatusText('', 0)

        self.optional_menus = []

        self.bgcol = rgb2hex(self.GetBackgroundColour()[:3])


        self.SetBackgroundColour('#F8F8F4')

        splitter  = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        splitter.SetMinimumPaneSize(200)

        conf_panel = wx.Panel(splitter)
        main_panel = wx.Panel(splitter)

        # main panel
        self.plot_panel = PlotPanel(main_panel, size=(400, 325))
        self.plot_panel.axesmargins = (15, 15, 15, 15)
        self.plot_panel.conf.set_axes_style(style='open')

        self.img1_panel = ImagePanel(main_panel, size=(360, 270))
        self.img2_panel = ImagePanel(main_panel, size=(360, 270))
        self.dual_panel = ImagePanel(main_panel, size=(360, 270))


        lsty = wx.ALIGN_LEFT|wx.LEFT|wx.TOP|wx.EXPAND

        ir = 0
        self.wids = {}
        cmap_colors = ('blue', 'red', 'green', 'magenta', 'cyan', 'yellow')
        self.cmap_panels = [None, None]
        csizer = wx.BoxSizer(wx.VERTICAL)
        for i, imgpanel in enumerate((self.img1_panel, self.img2_panel)):
            print i, imgpanel, cmap_colors[i]
            self.cmap_panels[i] =  ColorMapPanel(conf_panel, imgpanel,
                                                 title='Map %i: ' % (i+1),
                                                 color=0,
                                                 default=cmap_colors[i],
                                                 colormap_list=cmap_colors)

            csizer.Add(self.cmap_panels[i], 0, lsty, 2)
            csizer.Add(wx.StaticLine(conf_panel, size=(100, 2),
                                    style=wx.LI_HORIZONTAL), 0, lsty, 2)

        pack(conf_panel, csizer)


        for name, panel in (('corplot', self.plot_panel),
                            ('map1',    self.img1_panel),
                            ('map2',    self.img2_panel),
                            ('dual',    self.dual_panel)):

            panel.add_cursor_mode('prof',
                                  motion = partial(self.prof_motion, name=name),
                                  leftdown = partial(self.prof_leftdown, name=name),
                                  leftup   = partial(self.prof_leftup, name=name))
            panel.report_leftdown = partial(self.report_leftdown, name=name)
            panel.report_motion   = partial(self.report_motion, name=name)
            panel.messenger = self.write_message

        sizer = wx.GridBagSizer(3, 3)

        lsty |= wx.GROW|wx.ALL
        sizer.Add(self.img1_panel, (0, 0), (1, 1), lsty, 2)
        sizer.Add(self.dual_panel, (0, 1), (1, 1), lsty, 2)
        sizer.Add(self.plot_panel, (1, 0), (1, 1), lsty, 2)
        sizer.Add(self.img2_panel, (1, 1), (1, 1), lsty, 2)


        for i in range(2):
            sizer.AddGrowableRow(i)
            sizer.AddGrowableCol(i)


        pack(main_panel, sizer)
        splitter.SplitVertically(conf_panel, main_panel, 1)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(splitter, 1, wx.GROW|wx.ALL, 5)
        pack(self, sizer)


    def prof_motion(self, event=None, name=None):
        print("prof motion, ", name, event)

    def prof_leftdown(self, event=None, name=None):
        print("prof leftdown, ", name, event)

    def prof_leftup(self, event=None, name=None):
        print("prof leftup, ", name, event)

    def report_motion(self, event=None, name=None):
        print("report motion, ", name, event)

    def report_leftdown(self, event=None, name=None):
        print("report leftdown, ", name, event)

    def report_leftup(self, event=None, name=None):
        print("report leftup, ", name, event)

    def on_colormap(self, event=None, index=0):
        print("on colormap ", index)

    def on_mapsel(self, event=None, index=0):
        print("on mapsel ", index)

    def display(self, map1, map2, title=None, x=None, y=None, xoff=None, yoff=None,
                subtitles=None, xrmfile=None, det=None):

        self.img1_panel.display(map1)
        self.img2_panel.display(map2)

        self.plot_panel.plot(map1.flatten(), map2.flatten())
