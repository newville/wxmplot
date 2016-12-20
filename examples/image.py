import sys
import wx
import numpy as np
from wxmplot import ImageFrame

y, x = np.mgrid[-5:5:101j, -4:6:101j]
dat = np.sin(x*x/3.0 + y*y)/(1 + (x+y)*(x+y))

x0 = x[0,:]
y0 = y[:,0]


app = wx.App()
frame = ImageFrame(mode='intensity')
frame.display(dat, x=x0, y=y0)
frame.Show()
app.MainLoop()
