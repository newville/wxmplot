import numpy as np
from wxmplot.interactive import imshow

y, x = np.mgrid[-5:5:101j, -4:6:101j]
dat = np.sin(x*x/3.0 + y*y)/(1 + (x+y)*(x+y))

imshow(dat, x=x[0,:], y=y[:,0], colormap='viridis',
       wintitle='wxmplot imshow')
