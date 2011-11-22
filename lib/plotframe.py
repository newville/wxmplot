#!/usr/bin/python
"""
 MPlot PlotFrame: a wx.Frame for 2D line plotting, using matplotlib
"""
from plotpanel import PlotPanel
from baseframe import BaseFrame

class PlotFrame(BaseFrame):
    """
    MatPlotlib 2D plot as a wx.Frame, using PlotPanel
    """
    def __init__(self, parent=None, size=(700, 450),
                 title=None, **kws):
        if title is None:
            title = '2D Plot Frame'
        BaseFrame.__init__(self, parent=parent,
                           title  = title,
                           size=size, **kws)
        self.BuildFrame()

    def plot(self, x, y, **kw):
        """plot after clearing current plot """
        self.panel.plot(x, y, **kw)

    def oplot(self, x, y, **kw):
        """generic plotting method, overplotting any existing plot """
        self.panel.oplot(x, y, **kw)

    def clear(self):
        "clear plot"
        self.panel.clear()

    def clear(self):
        "clear plot"
        self.panel.clear()

    def reset_config(self):        
        self.panel.reset_config()
        
    def update_line(self, t, x, y, **kw):
        """overwrite data for trace t """
        self.panel.update_line(t, x, y, **kw)
