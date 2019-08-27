#!/usr/bin/python
import numpy as np
import wxmplot.interactive as wi

x = np.linspace(0.0, 20.0, 201)
wi.plot(x, np.sin(x)/(x+1), ylabel='response',  xlabel='T (sec)')
