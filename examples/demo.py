import sys
import wx
is_wxPhoenix = 'phoenix' in wx.PlatformInfo
if is_wxPhoenix:
    PyDeadObjectError = RuntimeError
else:
    from wx._core import PyDeadObjectError

import time, os, sys

from numpy import arange, sin, cos, exp, pi, linspace, ones, random

from wxmplot.plotframe import PlotFrame

class TestFrame(wx.Frame):
    def __init__(self, parent=None, *args,**kwds):

        kwds["style"] = wx.DEFAULT_FRAME_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL

        wx.Frame.__init__(self, parent, wx.NewId(), '',
                         wx.DefaultPosition, wx.Size(-1,-1), **kwds)
        self.SetTitle(" WXMPlot Plotting Demo")

        self.SetFont(wx.Font(12,wx.SWISS,wx.NORMAL,wx.BOLD,False))
        menu = wx.Menu()
        ID_EXIT  = wx.NewId()

        menu_exit = menu.Append(ID_EXIT, "E&xit", "Terminate the program")

        menuBar = wx.MenuBar()
        menuBar.Append(menu, "&File");
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.OnExit, menu_exit)

        self.Bind(wx.EVT_CLOSE, self.OnExit) # CloseEvent)

        self.plotframe  = None

        self.create_data()
        framesizer = wx.BoxSizer(wx.VERTICAL)

        panel      = wx.Panel(self, -1, size=(-1, -1))
        panelsizer = wx.BoxSizer(wx.VERTICAL)

        panelsizer.Add( wx.StaticText(panel, -1, 'wxmplot 2D PlotPanel examples '),
                        0, wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.LEFT|wx.EXPAND, 10)

        b10 = wx.Button(panel, -1, 'Example #1',          size=(-1,-1))
        b20 = wx.Button(panel, -1, 'Example #2',          size=(-1,-1))
        b22 = wx.Button(panel, -1, 'Plot with 2 axes',    size=(-1,-1))
        b31 = wx.Button(panel, -1, 'Plot with Errorbars', size=(-1,-1))
        b32 = wx.Button(panel, -1, 'SemiLog Plot',        size=(-1,-1))
        b40 = wx.Button(panel, -1, 'Start Timed Plot',    size=(-1,-1))
        b50 = wx.Button(panel, -1, 'Stop Timed Plot',     size=(-1,-1))
        b60 = wx.Button(panel, -1, 'Plot 500,000 points',  size=(-1,-1))

        b10.Bind(wx.EVT_BUTTON,self.onPlot1)
        b20.Bind(wx.EVT_BUTTON,self.onPlot2)
        b22.Bind(wx.EVT_BUTTON,self.onPlot2Axes)
        b31.Bind(wx.EVT_BUTTON,self.onPlotErr)
        b32.Bind(wx.EVT_BUTTON,self.onPlotSLog)
        b40.Bind(wx.EVT_BUTTON,self.onStartTimer)
        b50.Bind(wx.EVT_BUTTON,self.onStopTimer)
        b60.Bind(wx.EVT_BUTTON,self.onPlotBig)

        panelsizer.Add(b10, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.LEFT, 5)
        panelsizer.Add(b20, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.LEFT, 5)
        panelsizer.Add(b22, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.LEFT, 5)
        panelsizer.Add(b31, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.LEFT, 5)
        panelsizer.Add(b32, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.LEFT, 5)
        panelsizer.Add(b40, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.LEFT, 5)
        panelsizer.Add(b50, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.LEFT, 5)
        panelsizer.Add(b60, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.LEFT, 5)

        panel.SetSizer(panelsizer)
        panelsizer.Fit(panel)

        framesizer.Add(panel, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.EXPAND,2)
        self.SetSizer(framesizer)
        framesizer.Fit(self)

        self.Bind(wx.EVT_TIMER, self.onTimer)
        self.timer = wx.Timer(self)
        self.Refresh()

    def create_data(self):
        self.count = 0
        self.x  = x = arange(0.0,25.0,0.1)
        self.y1 = 4*cos(2*pi*(x-1)/5.7)/(6+x) + 2*sin(2*pi*(x-1)/2.2)/(10)
        self.y2 = sin(2*pi*x/30.0)
        self.y3 =  -pi + 2*(x/10. + exp(-(x-3)/5.0))
        self.y4 =  exp(0.01 + 0.5*x ) / (x+2)
        self.y5 =  3000 * self.y3
        self.npts = len(self.x)
        self.bigx   = linspace(0, 2500, 500000)
        self.bigy   = (sin(pi*self.bigx/140.0) +
                       cos(pi*self.bigx/277.0) +
                       cos(pi*self.bigx/820.0))


    def ShowPlotFrame(self, do_raise=True, clear=True):
        "make sure plot frame is enabled, and visible"
        if self.plotframe is None:
            self.plotframe = PlotFrame(self)
            self.has_plot = False
        try:
            self.plotframe.Show()
        except PyDeadObjectError:
            self.plotframe = PlotFrame(self)
            self.plotframe.Show()

        if do_raise:
            self.plotframe.Raise()
        if clear:
            self.plotframe.panel.clear()
            self.plotframe.reset_config()


    def onPlot1(self,event=None):
        self.ShowPlotFrame()
        self.plotframe.plot(self.x,self.y1)
        self.plotframe.oplot(self.x,self.y2)
        self.plotframe.write_message("Plot 1")

    def onPlot2(self,event=None):
        self.ShowPlotFrame()
        x  = arange(100)
        y1 = cos(pi*x/72)
        y2 = sin(pi*x/23)
        self.plotframe.plot(x, y1, color='red')
        self.plotframe.oplot(x, y2, color='green3', marker='+')
        self.plotframe.write_message("Plot 2")


    def onPlotErr(self,event=None):
        self.ShowPlotFrame()
        npts = 81
        x  = linspace(0, 40.0, npts)
        y  = 0.4 * cos(x/2.0) + random.normal(scale=0.03, size=npts)
        dy = 0.03 * (ones(npts) + random.normal(scale=0.2, size=npts))

        self.plotframe.plot(x, y, dy=dy, color='red', linewidth=0,
                            xlabel='x', ylabel='y', marker='o',
                            title='Plot with error bars')
        self.plotframe.write_message("Errorbars!")


    def onPlot2Axes(self,event=None):
        self.ShowPlotFrame()

        self.plotframe.plot( self.x,self.y2, color='black',style='dashed')
        self.plotframe.oplot(self.x,self.y5, color='red', side='right')
        self.plotframe.write_message("Plot with 2 axes")


    def onPlotSLog(self,event=None):
        self.ShowPlotFrame()

        self.plotframe.plot( self.x,self.y4,ylog_scale=True,
                             color='black',style='dashed')
        self.plotframe.write_message("Semi Log Plot")

    def onPlotBig(self,event=None):
        self.ShowPlotFrame()

        t0 = time.time()
        self.plotframe.plot(self.bigx, self.bigy, marker='+', linewidth=0)
        dt = time.time()-t0
        self.plotframe.write_message(
            "Plot array with npts=%i, elapsed time=%8.3f s" % (len(self.bigx),dt))

    def report_memory(i):
        pid = os.getpid()
        if os.name == 'posix':
            mem = os.popen("ps -o rss -p %i" % pid).readlines()[1].split()[0]
        else:
            mem = 0
        return int(mem)

    def onStartTimer(self,event=None):
        self.count    = 0
        self.up_count = 0
        self.n_update = 1
        self.datrange = None
        self.time0    = time.time()
        self.start_mem= self.report_memory()
        self.timer.Start(10)

    def timer_results(self):
        if (self.count < 2): return
        etime = time.time() - self.time0
        tpp   = etime/max(1,self.count)
        s = "drew %i points in %8.3f s: time/point= %8.4f s" % (self.count,etime,tpp)
        self.plotframe.write_message(s)
        self.time0 = 0
        self.count = 0
        self.datrange = None

    def onStopTimer(self,event=None):
        self.timer.Stop()
        try:
            self.timer_results()
        except:
            pass

    def onTimer(self, event):
        # print 'timer ', self.count, time.time()
        self.count += 1
        self.ShowPlotFrame(do_raise=False, clear=False)
        n = self.count
        if n < 2:
            return
        if n >= self.npts:
            self.timer.Stop()
            self.timer_results()
        elif n <= 3:
            self.plotframe.plot(self.x[:n], self.y1[:n])# , grid=False)

        else:
            self.plotframe.update_line(0, self.x[:n], self.y1[:n], update_limits=n<10, draw=True)

            etime = time.time() - self.time0
            s = " %i / %i points in %8.4f s" % (n,self.npts,etime)
            self.plotframe.write_message(s)

        if self.datrange is None:
            self.datrange = [min(self.x[:n]), max(self.x[:n]),
                             min(self.y1[:n]),max(self.y1[:n])]

        dr = [min(self.x[:n]), max(self.x[:n]), min(self.y1[:n]),max(self.y1[:n])]
        lims = self.plotframe.panel.get_viewlimits()
        if dr[0] < lims[0] or dr[1] > lims[1] or dr[2] < lims[2] or dr[3] > lims[3]:
            self.datrange = dr
            if n < len(self.x):
                nmax = min(int(n*1.6), len(self.x)-1)
                self.datrange[1] = self.x[nmax]
            self.plotframe.panel.set_xylims(self.datrange)

#        if (n > self.n_update-1) or
#             (xr[0] < xv[0]) or (xr[1] > xv[1]) or
#             (yr[0] < yv[0]) or (yr[1] > yv[1])):
#             nx = self.n_update = min(self.npts,3+int(self.n_update*2.0))
#             if nx > int(0.92*self.npts):
#                 nx = self.n_update = self.npts
#                 xylims = (min(self.x),max(self.x),
#                           min(self.y1),max(self.y1))
#             else:
#                 xylims = (min(self.x[0:nx]),max(self.x[0:nx]),
#                           min(self.y1[0:nx]),max(self.y1[0:nx]))
#             self.up_count = self.up_count + 1
#             self.plotframe.panel.set_xylims(xylims)

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

if __name__ == '__main__':
    app = wx.App()
    f = TestFrame(None,-1)
    f.Show(True)
    app.MainLoop()
