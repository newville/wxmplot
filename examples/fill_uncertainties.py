#!/usr/bin/python
import numpy as np
import wxmplot.interactive as wi

x = np.linspace(0.0, 20.0, 201)
y1 = np.sin(x)/(x+1)
dy1 = 0.04 * np.ones(201)

y2 = np.cos(x*1.1)/(x+1)
dy2 = 0.07 * np.ones(201)

wi.plot(x, y1, dy=dy1, label='thing1', alpha=0.25, fill=True, xlabel='x (mm)')
wi.plot(x, y2, dy=dy2, label='thing2', alpha=0.40, fill=True, show_legend=True)
