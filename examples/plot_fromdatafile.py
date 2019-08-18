#!/usr/bin/python

from os import path
import numpy as np
from wxmplot.interactive import plot, wxloop

thisdir, _ = path.split(__file__)
dat = np.loadtxt(path.join(thisdir, 'xafs.dat'))

x = dat[:, 0]
y = dat[:, 1]

plot(x, y, xlabel='E (eV)', label='As K edge', title='Test Plot')
wxloop()
