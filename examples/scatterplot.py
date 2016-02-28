#!/usr/bin/python
#
# scatterplot example, with lassoing and
# a user-level lasso-callback
import sys
import wx
import wxmplot
import numpy

x   = numpy.arange(100)/20.0 + numpy.random.random(size=100)
y   = numpy.random.random(size=len(x))
def onlasso(data=None, selected=None, mask=None):
    print( ':: lasso ', selected)

app = wx.App()

pframe = wxmplot.PlotFrame()
pframe.scatterplot(x, y, title='Scatter Plot', size=15,
                   xlabel='$ x\, \mathrm{(\AA)}$',
                   ylabel='$ y\, \mathrm{(\AA^{-1})}$')
pframe.panel.lasso_callback = onlasso
pframe.write_message('WXMPlot PlotFrame example: Try Help->Quick Reference')
pframe.Show()
#
app.MainLoop()
