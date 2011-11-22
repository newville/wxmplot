#!/usr/bin/python
#

from wxmplot import PlotApp
import numpy as np

npts = 41
x  = np.linspace(0, 10.0, npts)
y  = 0.4 * np.cos(x/2.0) + np.random.normal(scale=0.03, size=npts)
dy = 0.03 * np.ones(npts)

app = PlotApp()
app.plot(x, y, dy=dy, color='red', linewidth=0,
         xlabel='x', ylabel='y', title='Plot with error bars')

app.run()
