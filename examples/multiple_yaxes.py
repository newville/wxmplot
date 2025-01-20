#!/usr/bin/python
#
#  example plot with 3 different right-hand axes with different y scales
import numpy as np
import wxmplot.interactive as wi

noise = np.random.normal
n = 201
x  = np.linspace(0, 100, n)
y1 = np.sin(x/3.4)/(0.2*x+2) + noise(size=n, scale=0.1)
y2 = (x * 0.041 + noise(size=n, scale=0.1)).astype(int)
y3 = 0.04 + 0.07*np.sin(x/46.) * np.exp(-x*x/7e3) + noise(size=n, scale=0.0003)
y4 = -210. + 0.6*x * np.exp(-x*x/7e3) + noise(size=n, scale=0.3)


disp = wi.plot(x, y1, title='Test 4 Axes with different y scales',
               show_legend=True, yaxes_tracecolor=True,
               xlabel='x (mm)', label='signal 1', ylabel='ylabel',
               size=(1000, 600))

wi.plot(x, y2, y2label='y2label', label='state', yaxes=2,
                  drawstyle='steps-post')

disp.panel.set_ytick_labels({0: 'off', 1: 'staged',
                            2: 'ready', 3: 'running', 4: 'finished'},
                            yaxes=2)

wi.plot(x, y3, y3label='y3label', label='signal 3', yaxes=3)
wi.plot(x, y4, y4label='y4label', label='signal 4', yaxes=4)
