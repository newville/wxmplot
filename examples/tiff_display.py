import sys
if not hasattr(sys, 'frozen'):
    import wxversion
    wxversion.ensureMinimal('2.8')

import wx
import numpy
import Image
from wxmplot import ImageFrame

img = Image.open("ceo2.tiff")
h, v = img.size

app = wx.App()
frame = ImageFrame()
frame.display(numpy.array(img.getdata()).reshape(h, v)[::-1])
frame.Show()
app.MainLoop()
