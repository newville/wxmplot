#!/usr/bin/python
##
## MPlot PlotFrame: a wx.Frame for 2D line plotting, using matplotlib
##

import wx
import matplotlib

from .utils import Closure

from .plotpanel import PlotPanel
from .baseframe import BaseFrame

class MultiPlotFrame(BaseFrame):
    """
    MatPlotlib Array of 2D plot as a wx.Frame, using PlotPanel
    """
    def __init__(self, parent=None, rows=1,cols=1,
                 framesize=(600,350),
                 panelsize=(4.0,3.20), **kws):

        BaseFrame.__init__(self, parent=parent,
                           title  = '2D Plot Array Frame',
                           size=framesize, **kws)
        self.panels = {}
        self.rows = rows
        self.cols = cols
        self.panelsize = panelsize
        self.current_panel = (0,0)
        self.BuildFrame()

    def set_panel(self,ix,iy):
        self.current_panel = (ix,iy)
        try:
            self.panel = self.panels[(ix,iy)]
        except KeyError:
            print( 'could not set self.panel')


    def plot(self,x,y,panel=None,**kw):
        """plot after clearing current plot """
        if panel is None: panel = self.current_panel
        self.panels[panel].plot(x,y,**kw)

    def oplot(self,x,y,panel=None,**kw):
        """generic plotting method, overplotting any existing plot """
        if panel is None: panel = self.current_panel
        self.panels[panel].oplot(x,y,**kw)

    def update_line(self, t, x, y, panel=None, **kw):
        """overwrite data for trace t """
        if panel is None:
            panel = self.current_panel
        self.panels[panel].update_line(t, x, y, **kw)

    def set_xylims(self, lims, axes=None, panel=None):
        """overwrite data for trace t """
        if panel is None: panel = self.current_panel
        self.panels[panel].set_xylims(lims, axes=axes, **kw)

    def clear(self,panel=None):
        """clear plot """
        if panel is None: panel = self.current_panel
        self.panels[panel].clear()

    def unzoom_all(self,event=None,panel=None):
        """zoom out full data range """
        if panel is None: panel = self.current_panel
        self.panels[panel].unzoom_all(event=event)

    def unzoom(self,event=None,panel=None):
        """zoom out 1 level, or to full data range """
        if panel is None: panel = self.current_panel
        self.panels[panel].unzoom(event=event)

    def set_title(self,s,panel=None):
        "set plot title"
        if panel is None: panel = self.current_panel
        self.panels[panel].set_title(s)

    def set_xlabel(self,s,panel=None):
        "set plot xlabel"
        if panel is None: panel = self.current_panel
        self.panels[panel].set_xlabel(s)

    def set_ylabel(self,s,panel=None):
        "set plot xlabel"
        if panel is None: panel = self.current_panel
        self.panels[panel].set_ylabel(s)

    def save_figure(self,event=None,panel=None):
        """ save figure image to file"""
        if panel is None: panel = self.current_panel
        self.panels[panel].save_figure(event=event)

    def configure(self,event=None,panel=None):
        if panel is None: panel = self.current_panel
        self.panels[panel].configure(event=event)

    ####
    ## create GUI
    ####
    def BuildFrame(self):
        sbar = self.CreateStatusBar(2,wx.CAPTION)
        sfont = sbar.GetFont()
        sfont.SetWeight(wx.BOLD)
        sfont.SetPointSize(10)
        sbar.SetFont(sfont)

        self.SetStatusWidths([-3,-1])
        self.SetStatusText('',0)

        self.BuildMenu()
        sizer = wx.GridBagSizer(self.rows,self.cols)


        for i in range(self.rows):
            for j in range(self.cols):
                self.panels[(i,j)] = PlotPanel(self, size=self.panelsize)
                self.panels[(i,j)].messenger = self.write_message
                panel = self.panels[(i,j)]

                sizer.Add(panel,(i,j),(1,1),flag=wx.EXPAND|wx.ALIGN_CENTER)
                panel.reportLeftDown = Closure(self.reportLeftDown,
                                               panelkey=(i,j))


        self.panel = self.panels[(0,0)]
        for i in range(self.rows): sizer.AddGrowableRow(i)
        for i in range(self.cols): sizer.AddGrowableCol(i)

        self.SetAutoLayout(True)
        self.SetSizerAndFit(sizer)

    def reportLeftDown(self, event=None, panelkey=None,**kw):
        try:
            self.panel.set_bg()
            self.panel.canvas.draw()
        except:
            pass

        if panelkey is not None:
            ix, iy = panelkey
            self.set_panel(ix,iy)
            self.panel.write_message("%f, %f" % (event.xdata,event.ydata), panel=1)

            self.BindMenuToPanel(panel=self.panel)
            self.panel.set_bg('#FEFEFA')
            self.panel.canvas.draw()
