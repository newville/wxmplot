#!/usr/bin/python
#
# Stacked Plot shows two related plots stacked top and bottom that are
# expected to share an X axis.

# The upper panel is a standard PlotPanel. The bottom panel is compressed
# in height, and follows the X-range when zooming the top panel, and does
# not respond to most other mouse events.

import wx
import numpy
from wxmplot import StackedPlotFrame

x = numpy.arange(0.0, 30.0, 0.1)
noise = numpy.random.normal(size=len(x), scale=0.096)

y1 = numpy.sin(2*x)/(x+2)
y2 = y1 + noise

app = wx.App()

pframe = StackedPlotFrame(title='Stacked Example', ratio=3.000)

pframe.plot(x, y2, label='data(fake)', ylabel='signal', xlabel='x', title='some fit')

pframe.oplot(x, y1, label='simple theory', show_legend=True)
pframe.plot(x, noise, panel='bottom', ylabel='residual')


pframe.Show()
pframe.Raise()

app.MainLoop()
