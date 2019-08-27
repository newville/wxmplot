#!/usr/bin/python
import numpy as np
import wxmplot.interactive as wi

x = np.arange(0.0,10.0,0.1)
y = np.sin(2*x)/(x+2)

win1 = wi.plot(x, y, title='Window 1', xlabel='X (mm)', win=1)

win2 = wi.plot(x, np.cos(x-4), title='Window 2', xlabel='X (mm)', win=2)

pos = win2.GetPosition()
siz = win1.GetSize()
win2.SetPosition((pos[0]+int(siz[0]*0.8), pos[1]+10))
