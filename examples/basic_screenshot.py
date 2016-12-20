#!/usr/bin/env python
# simple wxmplot example

from numpy import linspace, sin, cos, random
from wxmplot import PlotApp

app = PlotApp()

random.seed(1)

x = linspace(0.0, 10.0, 101)
y = 5*sin(4*x)/(x*x+6)
z = cos(0.7*(x+0.3)) + random.normal(size=len(x), scale=0.11)

app.plot(x, y, title='WXMPlot example', 
         label='decaying sine',
         ylabel=r'$\phi(x)$', 
         xlabel=r'$x \> \rm (\AA)$')
app.oplot(x, z, label='noisy cosine', marker='+', show_legend=True)

app.write_message('Try Help->Quick Reference')
app.run()

