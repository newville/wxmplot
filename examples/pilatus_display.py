#
# read Pilatus image into numpy array

import wx
import Image
import numpy
import mplot

def getPilatusImage(filename):
    img = Image.open(filename)
    dat = numpy.array(img.getdata()).reshape((195,487))
    return img, dat

img, dat = getPilatusImage('Pilatus.tiff')

app = wx.PySimpleApp()
frame = mplot.ImageFrame()
frame.display(dat)
frame.Show()
app.MainLoop()
