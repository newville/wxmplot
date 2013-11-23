#
# read Pilatus image into numpy array
import sys
if not hasattr(sys, 'frozen'):
    import wxversion
    wxversion.ensureMinimal('2.8')

import wx
import Image
import numpy
from wxmplot import ImageFrame

def getPilatusImage(filename):
    return numpy.array(Image.open(filename))

dat = getPilatusImage('Pilatus.tiff')

app = wx.App()
frame = ImageFrame()
frame.display(dat)
frame.Show()
app.MainLoop()
