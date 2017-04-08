#!/usr/bin/python
#
# simple example of MPlot

import wx
import wxmplot
import numpy

x   = numpy.linspace(0.0, 10.0, 201)
y1  = numpy.sin(3*x)/(x+2)
y2  = numpy.cos(2*x)*numpy.sin(2*x)
y3  = numpy.cos(2*x) + x/3
y4  = numpy.cos(2*x)*numpy.exp(-x/10.)
y5  = y4 + y2
y6  = 10*y1 +  y3
app = wx.App()

pframe = wxmplot.MultiPlotFrame(rows=2, cols=3, panelsize=(350, 275))


pframe.plot(x, y1, panel=(0, 0), labelfontsize=6)
pframe.plot(x, y2, panel=(0, 1), color='red',  labelfontsize=6)
pframe.plot(x, y3, panel=(0, 2), color='black', labelfontsize=5)
pframe.plot(x, y4, panel=(1, 0), fullbox=False)
pframe.plot(x, y5, panel=(1, 1), show_grid=False)
pframe.plot(x, y6, panel=(1, 2))
pframe.set_title('Test Plot', panel=(0, 0))
pframe.set_title('Plot2',panel=(1,0))
pframe.set_xlabel(r' $ R  (\AA) $ ')
pframe.Show()
pframe.Raise()

app.MainLoop()
