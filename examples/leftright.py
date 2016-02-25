#!/usr/bin/python
#
#  example plot with left and right axes with different scales

import sys

import wx
import numpy as np
import wxmplot

noise = np.random.normal
n = 201
x  = np.linspace(0, 100, n)
y1 = np.sin(x/3.4)/(0.2*x+2) + noise(size=n, scale=0.1)
y2 = 92 + 65*np.cos(x/16.) * np.exp(-x*x/7e3) + noise(size=n, scale=0.3)

app = wx.App()
pframe = wxmplot.PlotFrame()

pframe.plot(x, y1, title='Test 2 Axes with different y scales',
            xlabel='x (mm)', ylabel='y1', ymin=-0.75, ymax=0.75)
pframe.oplot(x, y2, y2label='y2', side='right', ymin=0)
pframe.Show()
app.MainLoop()


