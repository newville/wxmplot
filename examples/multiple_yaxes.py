#!/usr/bin/python
#
#  example plot with 3 different right-hand axes with different y scales
import numpy as np
import wxmplot.interactive as wi

noise = np.random.normal
n = 201
x  = np.linspace(0, 100, n)
y1 = np.sin(x/3.4)/(0.2*x+2) + noise(size=n, scale=0.1)
y2 = 92.2 + 26.5*np.cos(x/16.) * np.exp(-x*x/7e3) + noise(size=n, scale=0.3)
y3 = 0.04 + 0.07*np.sin(x/46.) * np.exp(-x*x/7e3) + noise(size=n, scale=0.0003)
y4 = -210. + 0.6*x * np.exp(-x*x/7e3) + noise(size=n, scale=0.3)


disp = wi.plot(x, y1, title='Test 4 Axes with different y scales',
               show_legend=True, yaxes_tracecolor=True,
               xlabel='x (mm)', label='signal 1', ylabel='ylabel')

wi.plot(x, y2, y2label='y2label', label='signal 2', yaxes=2)
wi.plot(x, y3, y3label='y3label', label='signal 3', yaxes=3)
wi.plot(x, y4, y4label='y4label', label='signal 4', yaxes=4)
