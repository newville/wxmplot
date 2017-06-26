#!/usr/bin/python
#

import wx
import numpy as np
import wxmplot

x   = np.linspace(0, 5, 201)

traces = []

for i in range(20):
    traces.append((x, np.sqrt(x)*np.sin(0.25*(i+1)*x)*np.exp(-x/2)))


app = wx.App()

pframe = wxmplot.PlotFrame(output_title='Plot Multiple')
pframe.plot_many(traces, title='Test Plotting 20 traces with plot_many()',
                 xlabel=r'x (mm)')

pframe.write_message('WXMPlot PlotFrame example: Try Help->Quick Reference')
pframe.Show()
#
app.MainLoop()
