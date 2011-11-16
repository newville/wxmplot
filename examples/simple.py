#!/usr/bin/python
#
# simple example of MPlot

import wx
import numpy 
import mplot  

x   = numpy.arange(0.0,10.0,0.1)
y   = numpy.sin(2*x)/(x+2)
app = wx.PySimpleApp()

pframe = mplot.PlotFrame()
pframe.plot(x,y)
pframe.set_title('Test Plot')
pframe.set_xlabel(r'  ${ R \mathrm{(\AA)}}$  ')
pframe.write_message('MPlot PlotFrame example: Try Help->Quick Reference')
pframe.Show()
# 
app.MainLoop()


