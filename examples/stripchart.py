#!/usr/bin/python
import time
import numpy
import wx

from mplot import PlotFrame

def next_data():
    t0 = time.time()
    lt = time.localtime(t0)
    tmin,tsec = lt[4],lt[5]
    x = numpy.sin(tmin/5.0) + tsec/30. + numpy.random.random()/5.0    
    return t0, x

import time, os, sys
from numpy import arange, sin, cos, exp, pi

class TestFrame(wx.Frame):
    def __init__(self, parent, ID, *args,**kwds):

        kwds["style"] = wx.DEFAULT_FRAME_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL
            
        wx.Frame.__init__(self, parent, ID, '',
                         wx.DefaultPosition, wx.Size(-1,-1),**kwds)
        self.SetTitle(" MPlot Test ")


        self.SetFont(wx.Font(12,wx.SWISS,wx.NORMAL,wx.BOLD,False))
        menu = wx.Menu()
        ID_EXIT  = wx.NewId()
        ID_TIMER = wx.NewId()

        menu.Append(ID_EXIT, "E&xit", "Terminate the program")

        menuBar = wx.MenuBar()
        menuBar.Append(menu, "&File");
        self.SetMenuBar(menuBar)

        wx.EVT_MENU(self, ID_EXIT,  self.OnExit)

        self.Bind(wx.EVT_CLOSE,self.OnExit) # CloseEvent)

        self.plotframe  = None

        self.create_data()
        framesizer = wx.BoxSizer(wx.VERTICAL)

        panel      = wx.Panel(self, -1, size=(-1, -1))
        panelsizer = wx.BoxSizer(wx.VERTICAL)        
        
        
        b40 = wx.Button(panel, -1, 'Start Timed Plot',   size=(-1,-1))
        b50 = wx.Button(panel, -1, 'Stop Timed Plot',    size=(-1,-1))

        b40.Bind(wx.EVT_BUTTON,self.onStartTimer)
        b50.Bind(wx.EVT_BUTTON,self.onStopTimer)


        panelsizer.Add( wx.StaticText(panel, -1, 'MPlot Examples '),
                        0, wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.LEFT|wx.EXPAND, 10)
        panelsizer.Add(b40, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.LEFT, 5)
        panelsizer.Add(b50, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.LEFT, 5)
        

        panel.SetSizer(panelsizer)
        panelsizer.Fit(panel)

        framesizer.Add(panel, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.EXPAND,2)
        self.SetSizer(framesizer)
        framesizer.Fit(self)

        wx.EVT_TIMER(self, ID_TIMER, self.onTimer)
        self.timer = wx.Timer(self, ID_TIMER)
        self.Refresh()

    def create_data(self):
        self.count = 0
        self.x  = x = arange(0.0,20.0,0.1)
        self.y1 = 4*cos(2*pi*(x-1)/5.7)/(6+x) + 2*sin(2*pi*(x-1)/2.2)/(10)
        self.y2 = sin(2*pi*x/30.0)
        self.y3 =  -pi + 2*(x/10. + exp(-(x-3)/5.0))
        self.y4 =  exp(0.01 + 0.5*x ) / (x+2)
        self.npts = len(self.x)

        self.bigx   = arange(0,250,0.01)
        self.bigy   = sin(pi*self.bigx/80)

    def ShowPlotFrame(self, do_raise=True):
        "make sure plot frame is enabled, and visible"
        if self.plotframe == None:
            self.plotframe = PlotFrame(self)
        try:
            self.plotframe.Show()
        except wx.PyDeadObjectError:
            self.plotframe = PlotFrame(self)            
            self.plotframe.Show()

        if do_raise:
            self.plotframe.Raise()
            
    def onStartTimer(self,event=None):
        self.count    = 0
        self.up_count = 0
        self.n_update = 1
        t0,y0 = next_data()
        self.ylist = [y0]
        self.tlist = [t0]
        self.time0    = time.time()
        self.timer.Start(10)
        
    def timer_results(self):
        if (self.count < 2): return
        etime = time.time() - self.time0
        tpp   = etime/max(1,self.count)
        s = "drew %i points in %8.3f s: time/point= %8.4f s" % (self.count,etime,tpp)
        self.plotframe.write_message(s)
        self.time0 = 0
        self.count = 0
        
    def onStopTimer(self,event=None):
        self.timer.Stop()
        try:
            self.timer_results()
        except:
            pass

    def onTimer(self, event):
        # print 'timer ', self.count, time.time()
        self.count += 1
        self.tmin = -5
        self.ShowPlotFrame(do_raise=False)        
        etime = time.time() - self.time0
        if etime > 70:
            self.timer.Stop()
            self.timer_results()

        t1,y1 = next_data()
        self.ylist.append(y1)
        self.tlist.append(t1)
        tdat = numpy.array(self.tlist) -t1
        mask = numpy.where(tdat>self.tmin)
        ydat = numpy.array(self.ylist)

        n = len(self.ylist)
        if n <= 2:
            self.plotframe.plot(tdat, ydat)
        else:
            self.plotframe.update_line(0,tdat, ydat)
            s = " %i points in %8.4f s" % (n,etime)
            self.plotframe.write_message(s)

        xr    = tdat.min(), tdat.max()
        yr    = ydat.min(), ydat.max()
        xv,yv = self.plotframe.get_xylims()
        xylims = (self.tmin, 0, ydat[mask].min(), ydat[mask].max())
        self.plotframe.panel.set_xylims(xylims,autoscale=False)
# 
#         if ((n > self.n_update-1) or
#             (xr[0] < xv[0]) or (xr[1] > xv[1]) or
#             (yr[0] < yv[0]) or (yr[1] > yv[1])):
#             nx = self.n_update = min(self.npts,3+int(self.n_update*1.25))
#             if nx > int(0.85*self.npts):
#                 nx = self.n_update = self.npts
#                 xylims = (min(self.x),max(self.x),
#                           min(self.y1),max(self.y1))
#             else:
#                 xylims = (min(self.x[0:nx]),max(self.x[0:nx]),
#                           min(self.y1[0:nx]),max(self.y1[0:nx]))
#             self.up_count = self.up_count + 1
#             self.plotframe.panel.set_xylims(xylims,autoscale=False)
            
    def OnAbout(self, event):
        dlg = wx.MessageDialog(self, "This sample program shows some\n"
                              "examples of MPlot PlotFrame.\n"
                              "message dialog.",
                              "About MPlot test", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def OnExit(self, event):
        try:
            if self.plotframe != None:  self.plotframe.onExit()
        except:
            pass
        self.Destroy()

def main():
    app = wx.PySimpleApp()
    f = TestFrame(None,-1)
    f.Show(True)
    app.MainLoop()

#profile.run('main()')
main()


# 
