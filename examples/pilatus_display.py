#
# read Pilatus image into numpy array
import sys
if not hasattr(sys, 'frozen'):
    import wxversion
    wxversion.ensureMinimal('2.8')

import wx
from tifffile import imread
from wxmplot import ImageFrame

dat = imread('Pilatus.tiff')

app = wx.App()
frame = ImageFrame()
frame.display(dat)
frame.Show()
app.MainLoop()
