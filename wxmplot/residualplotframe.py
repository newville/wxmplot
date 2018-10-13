#!/usr/bin/python
##
## ResidualPlotFrame: a wx.Frame for 2 PlotPanels, top and bottom
##   with the top panel being the main panel and the lower panel
##   being 1/4 the height (configurable) and the dependent panel

from .stackedplotframe import StackedPlotFrame

class ResidualPlotFrame(StackedPlotFrame):
    """
    Top/Bottom MatPlotlib panels in a single frame
    """
    def __init__(self, parent=None, title ='Residual Plot Frame',
                 framesize=(850,450), panelsize=(550,450),
                 ratio=3.0, **kws):

        StackedPlotFrame.__init__(self, parent=parent, title=title,
                           framesize=framesize, **kws)
       

    def plot_residual(self, x, y1, y2, label1='Raw data', label2='Fit/theory', 
             xlabel=None, ylabel=None, show_legend=True,
             **kws):
        """plot after clearing current plot """

        panel = self.get_panel('top')
        panel.plot(x, y1, label=label1, **kws)
        panel = self.get_panel('top')
        panel.oplot(x, y2, label=label2, ylabel=ylabel, show_legend=show_legend, **kws)
        panel = self.get_panel('bottom')
        panel.plot(x, (y2-y1), ylabel='residual', show_legend=False, **kws)
        
        if xlabel is not None:
            self.xlabel = xlabel
        if self.xlabel is not None:
            self.panel_bot.set_xlabel(self.xlabel)
