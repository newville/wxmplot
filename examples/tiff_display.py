import sys
import wx
from tifffile import imread
from wxmplot import ImageFrame

img = imread("ceo2.tiff")

app = wx.App()
frame = ImageFrame()
frame.display(img)
frame.Show()
app.MainLoop()
