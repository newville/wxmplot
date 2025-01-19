#
# read Pilatus image into numpy array
import sys
import wx
from tifffile import imread
from wxmplot import ImageFrame

dat = imread('Pilatus.tiff')

app = wx.App()
frame = ImageFrame()
frame.display(dat, contrast_level='0.005', auto_contrast=False)
frame.Show()
app.MainLoop()
