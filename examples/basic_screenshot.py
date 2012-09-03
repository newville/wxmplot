#!/usr/bin/env python
# simple wxmplot example

from numpy import linspace, sin, cos, random
from wxmplot import PlotApp

app = PlotApp()

x = linspace(0.0, 10.0, 101)
y = 5*sin(4*x)/(x+6)
z = cos(0.7*(x+0.3)) + random.normal(size=len(x), scale=0.2)

app.plot(x, y, title='WXMPlot Demo', label='decaying sine',
         ylabel=r'$\chi(x)$', xlabel='$x \ (\AA)$')
app.oplot(x, z, label='noisy cosine', marker='+')

app.write_message('Try Help->Quick Reference')
app.run()

