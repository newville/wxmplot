#!/usr/bin/python
"""
example setting yticks for categorical data
"""
import numpy as np
import wxmplot.interactive as wi

x = np.arange(100)
y = (x * 0.06).astype(int)

y[84:86] -= 1
y[94:] -= 1
y[67:69] += 1
y[43:45] += 1


display = wi.plot(x, y, xlabel='t (s)', ylabel='Y label', title='discrete y data',
                  drawstyle='steps-post')

display.panel.set_ytick_labels({0: 'zero', 1: 'one', 2: 'two',
                           3: 'three', 4: 'four', 5: 'five', 6: 'six'})
display.draw()
