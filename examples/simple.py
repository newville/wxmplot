#!/usr/bin/python
import numpy as np
from wxmplot.interactive import plot

x = np.linspace(0.0, 20.0, 201)
plot(x, np.sin(x)/(x+1), ylabel='response',  xlabel='T (sec)')
