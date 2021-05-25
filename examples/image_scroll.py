import time, os, sys
from random import shuffle

import numpy as np

import wx
from wxmplot import ImageFrame

class TestFrame(wx.Frame):
    def __init__(self, parent=None, *args,**kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL

        wx.Frame.__init__(self, parent, -1, '',
                         wx.DefaultPosition, wx.Size(-1,-1), **kwds)
        self.SetTitle(" WXMPlot Image Scroll")

        self.SetFont(wx.Font(12,wx.SWISS,wx.NORMAL,wx.BOLD,False))
        menu = wx.Menu()

        self.arrays = []
        self.imageframe  = None

        framesizer = wx.BoxSizer(wx.VERTICAL)

        panel      = wx.Panel(self, -1, size=(-1, -1))
        panelsizer = wx.BoxSizer(wx.VERTICAL)

        panelsizer.Add( wx.StaticText(panel, -1, 'Show Images'),
                        0, wx.LEFT|wx.EXPAND, 10)

        btn = wx.Button(panel, -1, 'start scrolling', size=(-1,-1))
        btn.Bind(wx.EVT_BUTTON,self.onScrollImages)

        btn2 = wx.Button(panel, -1, 'stop scrolling', size=(-1,-1))
        btn2.Bind(wx.EVT_BUTTON,self.onStop)

        self.msg = wx.StaticText(panel, label='000 images in 00.0000 seconds ',  size=(500, -1))

        panelsizer.Add(btn, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.LEFT, 5)
        panelsizer.Add(btn2, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.LEFT, 5)
        panelsizer.Add(self.msg, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.LEFT, 5)

        panel.SetSizer(panelsizer)
        panelsizer.Fit(panel)

        framesizer.Add(panel, 0, wx.EXPAND, 2)
        self.SetSizer(framesizer)
        framesizer.Fit(self)
        self.create_data()
        self.ShowImageFrame()
        self.count    = 0
        self.Bind(wx.EVT_TIMER, self.onTimer)
        self.timer = wx.Timer(self)
        self.Refresh()

    def create_data(self):
        nx = ny = 1001
        print("Creating 240 images..")
        for xoff in np.linspace(-2.5, 2.5, 20):
            y, x = np.mgrid[-10+xoff:10+xoff:nx*1j, -10:10:nx*1j]
            for xscale in (4.5, 5.0, 6.0):
                for yscale in (0.8, 1.0, 1.1, 1.2):
                    dat = np.sin(x*x/xscale + y*y/yscale)/(1 + (x+y)*(x+y))
                    dat += np.random.normal(scale=0.12, size=(nx, ny))
                    self.arrays.append(dat)
        shuffle(self.arrays)
        print("Built %d arrays, shape=%s" % (len(self.arrays), repr(dat.shape)))

    def ShowImageFrame(self):
        if self.imageframe is None:
            self.imageframe = ImageFrame(self)
        try:
            self.imageframe.Show()
        except RuntimeError:
            self.imageframe = Imageframe(self)
            self.imageframe.Show()

        self.imageframe.display(self.arrays[0])
        self.imageframe.Raise()

    def onTimer(self, event):
        self.count += 1
        message = " %d images in %.3f sec" % (self.count,
                                              time.time()-self.t0)
        self.msg.SetLabel(message)
        wx.CallAfter(self.imageframe.panel.update_image,
                     self.arrays[self.count % len(self.arrays)])

    def onScrollImages(self,event=None):
        self.ShowImageFrame()
        self.count = 0
        self.t0 = time.time()
        self.timer.Start(10)

    def onStop(self,event=None):
        self.timer.Stop()

if __name__ == '__main__':
    app = wx.App()
    f = TestFrame(None,-1)
    f.Show(True)
    app.MainLoop()
