import sys
import wx
from tifffile import imread
from wxmplot import ImageFrame

img = imread('ceo2.tiff')

app = wx.App()
frame = ImageFrame()
frame.display(img, auto_contrast=True, colormap='plasma')
frame.Show()
app.MainLoop()
