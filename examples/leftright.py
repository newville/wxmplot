#!/usr/bin/python
#
#  example plot with left and right axes with different scales

import wx
import numpy
import wxmplot

x   = numpy.linspace(0,100,201)
y1  = numpy.sin(x/3.4)/(0.2*x+2) + numpy.random.normal(size=len(x), scale=0.1)
y2  = 62 + 25 * numpy.cos(x/47.) * numpy.exp(-x*x/3e3) + + numpy.random.normal(size=len(x), scale=0.2)

app = wx.App()
pframe = wxmplot.PlotFrame(output_title='simple')
pframe.plot(x, y1, title='Test 2 Axes with different y scales', xlabel='x (mm)',
            ylabel='y1', ymin=-0.75, ymax=0.75)
pframe.oplot(x, y2, y2label='y2', side='right', ymin=0, ymax=100)

pframe.Show()
app.MainLoop()


