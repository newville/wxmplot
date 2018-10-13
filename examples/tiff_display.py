import sys
import wx
from tifffile import imread
from wxmplot import ImageFrame

img = imread('ceo2.tiff')

app = wx.App()
frame = ImageFrame()
frame.display(img, contrast_level=0.1, colormap='plasma')
frame.Show()
app.MainLoop()
