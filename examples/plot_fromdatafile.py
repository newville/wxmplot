#!/usr/bin/python
from os import path
import numpy as np
import wxmplot.interactive as wi

thisdir, _ = path.split(__file__)
dat = np.loadtxt(path.join(thisdir, 'xafs.dat'))

x = dat[:, 0]
y = dat[:, 1]

wi.plot(x, y, xlabel='E (eV)', label='As K edge', title='Test Plot')
