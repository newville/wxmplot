#!/usr/bin/python

import numpy as np
from  wxmplot.interactive import plot, wxloop

x = np.arange(0.0,10.0,0.1)
y = np.sin(2*x)/(x+2)

plot(x, y, title='Test Plot', xlabel=r'${ R \mathrm{(\AA)}}$')
wxloop()
