#!/usr/bin/python
import numpy as np
import wxmplot.interactive as wi

x = np.concatenate((0.25 + np.random.normal(size=2000, scale=0.5),
                   np.random.random(size=600)*1.25,
                   -0.2+np.random.random(size=300)*0.7))

wi.hist(x, bins=51, rwidth=0.75, title='A Histogram')
