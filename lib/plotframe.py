#!/usr/bin/python
"""
 MPlot PlotFrame: a wx.Frame for 2D line plotting, using matplotlib
"""
from .plotpanel import PlotPanel
from .baseframe import BaseFrame

class PlotFrame(BaseFrame):
    """
    MatPlotlib 2D plot as a wx.Frame, using PlotPanel
    """
    def __init__(self, parent=None, size=None, axisbg=None, title=None, **kws):
        if title is None:
            title = '2D Plot Frame'

        BaseFrame.__init__(self, parent=parent, title=title, size=size,
                           axisbg=axisbg, **kws)

        self.BuildFrame()

    def get_figure(self):
        """return MPL plot figure"""
        return self.panel.fig
        
    def add_text(self, text, x, y, **kws):
        """add text to plot"""
        self.panel.add_text(text, x, y, **kws)

    def add_arrow(self, x1, y1, x2, y2, **kws):
        """add arrow to plot"""
        self.panel.add_arrow(x1, y1, x2, y2, **kws)

    def plot(self, x, y, **kw):
        """plot after clearing current plot """
        self.panel.plot(x, y, **kw)

    def oplot(self, x, y, **kw):
        """generic plotting method, overplotting any existing plot """
        self.panel.oplot(x, y, **kw)

    def scatterplot(self, x, y, **kw):
        """plot after clearing current plot """
        self.panel.scatterplot(x, y, **kw)

    def draw(self):
        "explicit draw of underlying canvas"
        self.panel.canvas.draw()

    def clear(self):
        "clear plot"
        self.panel.clear()

    def reset_config(self):
        self.panel.reset_config()

    def update_line(self, t, x, y, **kw):
        """overwrite data for trace t """
        self.panel.update_line(t, x, y, **kw)
