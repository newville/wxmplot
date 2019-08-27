#!/usr/bin/python
from os import path
import numpy as np
import wxmplot.interactive as wi

fname = 'xafs.dat'
thisdir, _ = path.split(__file__)
dat = np.loadtxt(path.join(thisdir, fname))

x = dat[:, 0]
y = dat[:, 1]

wi.plot(x, y, xlabel='E (eV)', ylabel=r'$\mu(E)$',
        label='As K edge', title='Data from %s' % fname)
