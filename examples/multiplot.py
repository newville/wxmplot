#!/usr/bin/python
#
# simple example of MPlot

import wx
import wxmplot
import numpy

x   = numpy.arange(0.0,10.0,0.1)
y1  = numpy.sin(2*x)/(x+2)
y2  = numpy.cos(2*x)*numpy.sin(2*x)
y3  = numpy.cos(2*x) + x/3
y4  = numpy.cos(2*x)*numpy.exp(-x/10.)
app = wx.App()

pframe = wxmplot.MultiPlotFrame(rows=2,cols=3,panelsize=(2.5,1.75))


pframe.plot(x,y1,panel=(0,0))
pframe.plot(x,y2,panel=(0,1))
pframe.plot(x,y3,panel=(1,1))
pframe.plot(x,y4,panel=(1,2))
pframe.set_title('Test Plot',panel=(0,0))
pframe.set_title('Plot2',panel=(1,0))
pframe.set_xlabel(r' $ R  (\AA) $ ')
pframe.write_message('MPlot PlotFrame example: Try Help->Quick Reference')
pframe.Show()
pframe.Raise()

app.MainLoop()
