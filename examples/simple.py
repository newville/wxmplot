#!/usr/bin/python
import numpy as np
import wxmplot.interactive as wi

x = np.linspace(0.0, 20.0, 201)
wi.plot(x, np.sin(x)/(x+1),
        title='Titles can include latex: $\\chi^2/\\epsilon $ \n and newlines',
        ylabel='unicde can also be used [\u03c7] (\u212B)',  xlabel='T (sec)')
