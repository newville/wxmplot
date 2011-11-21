import wx
import numpy
import Image
from wxmplot import ImageFrame

img = Image.open("test.tiff")
h, v = img.size

app = wx.PySimpleApp()
frame = ImageFrame()
frame.display(numpy.array(img.getdata()).reshape(h, v)[::-1])
frame.Show()
app.MainLoop()
