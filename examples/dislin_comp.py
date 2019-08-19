#!/usr/bin/python
#
#  compare, for reference:
#   https://www2.mps.mpg.de/dislin/exa_curv.html
#   https://www2.mps.mpg.de/dislin/exa_python.html#section_1

import numpy as np
from wxmplot.interactive import plot, wxloop

x  = 3.6*np.arange(101)
y1 = np.cos(np.pi*x/180)
y2 = np.sin(np.pi*x/180)

plot(x, y1, title='DISLIN Comparison\nsin(x) and cos(x)',
     color='red', xlabel='x', ylabel='y')

plot(x, y2, color='green3', marker='+')
wxloop()
