#!/usr/bin/env python
from numpy import linspace, sin, random
import wxmplot.interactive as wi

x = linspace(0.0, 15.0, 151)
y = 5*sin(4*x)/(x*x+6)
z = 4.8*sin(4.3*x)/(x*x+8) + random.normal(size=len(x), scale=0.05)

wi.plot(x, y, wintitle='wxmplot example',  label='reference',
        ylabel=r'$\phi(\tau)$', xlabel=r'$\tau \> \rm (ms)$')

wi.plot(x, z, label='signal', marker='+', show_legend=True)
