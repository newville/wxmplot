import wx
import numpy
import Image
import mplot

img = Image.open("test.tiff")
h, v = img.size

app = wx.PySimpleApp()
frame = mplot.ImageFrame()
frame.display(numpy.array(img.getdata()).reshape(h, v)[::-1])
frame.Show()
app.MainLoop()
