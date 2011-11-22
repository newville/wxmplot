#!/usr/bin/python
#
#  compare, for reference:
#   http://www.mps.mpg.de/dislin/exa_curv.html
#   http://www.mps.mpg.de/dislin/exa_python.html#section_1

from wxmplot import PlotApp
import numpy as np

x  = 3.6*np.arange(101)
y1 = np.cos(np.pi*x/180)
y2 = np.sin(np.pi*x/180)

app = PlotApp()
app.plot(x, y1, color='red',
         xlabel='x', ylabel='y',
         title='DISLIN Comparison\nsin(x) and cos(x)',
         xmin=0, xmax=360.0)
app.oplot(x, y2, color='green3', marker='+')


app.run()
