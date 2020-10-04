#!/usr/bin/env python
from numpy import linspace, sin, random
import wxmplot.interactive as wi

x = linspace(0.0, 15.0, 151)
y = 5*sin(4*x)/(x*x+6)
z = 4.8*sin(4.3*x)/(x*x+8) + random.normal(size=len(x), scale=0.05)

for ix, theme in enumerate(('light', 'dark', 'matplotlib', 'seaborn',
                            'ggplot', 'bmh', 'tableau-colorblind10')):
    this = wi.plot(x, y, wintitle='%s theme' % theme,   win=ix+1,
                   title=theme,
                   ylabel=r'$\phi(\tau)$', xlabel=r'$\tau \> \rm (ms)$',
                   label='reference', show_legend=True, theme=theme, size=(600,450))
    wi.plot(x, z, label='signal', marker='+', win=ix+1)
    siz = this.GetSize()
    this.SetPosition((25 + int(ix*siz[0]/4), 25 + int(ix*siz[1]/12)))
