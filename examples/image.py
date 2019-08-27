#!/usr/bin/python
import numpy as np
import wxmplot.interactive as wi

y, x = np.mgrid[-5:5:101j, -4:6:101j]
dat = np.sin(x*x/3.0 + y*y)/(1 + (x+y)*(x+y))

wi.imshow(dat, x=x[0,:], y=y[:,0], colormap='viridis',
          wintitle='wxmplot imshow')
