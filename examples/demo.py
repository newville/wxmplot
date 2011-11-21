import wx
import time, os, sys
from numpy import arange, sin, cos, exp, pi, linspace

from wxmplot.plotframe import PlotFrame

class TestFrame(wx.Frame):
    def __init__(self, parent, ID, *args,**kwds):

        kwds["style"] = wx.DEFAULT_FRAME_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL

        wx.Frame.__init__(self, parent, ID, '',
                         wx.DefaultPosition, wx.Size(-1,-1),**kwds)
        self.SetTitle(" WXMPlot Plotting Demo")


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

        panelsizer.Add( wx.StaticText(panel, -1, 'wxmplot 2D PlotPanel examples '),
                        0, wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.LEFT|wx.EXPAND, 10)

        b10 = wx.Button(panel, -1, 'Example #1',    size=(-1,-1))
        b20 = wx.Button(panel, -1, 'Example #2',    size=(-1,-1))
        b22 = wx.Button(panel, -1, 'Plot with 2 axes',    size=(-1,-1))
        b31 = wx.Button(panel, -1, 'Exponential Plot',    size=(-1,-1))
        b32 = wx.Button(panel, -1, 'SemiLog Plot',    size=(-1,-1))
        b40 = wx.Button(panel, -1, 'Start Timed Plot',   size=(-1,-1))
        b50 = wx.Button(panel, -1, 'Stop Timed Plot',    size=(-1,-1))
        b60 = wx.Button(panel, -1, 'Plot 100,000 points',  size=(-1,-1))

        b10.Bind(wx.EVT_BUTTON,self.onPlot1)
        b20.Bind(wx.EVT_BUTTON,self.onPlot2)
        b22.Bind(wx.EVT_BUTTON,self.onPlot4)
        b31.Bind(wx.EVT_BUTTON,self.onPlot3)
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
        self.y5 =  3000 * self.y3
        self.npts = len(self.x)
        self.bigx   = linspace(0, 100, 100000)
        self.bigy   = sin(pi*self.bigx/28.0)


    def ShowPlotFrame(self, do_raise=True):
        "make sure plot frame is enabled, and visible"
        if self.plotframe == None:  self.plotframe = PlotFrame(self)
        try:
            self.plotframe.Show()
        except wx.PyDeadObjectError:
            self.plotframe = PlotFrame(self)
            self.plotframe.Show()

        if do_raise:    self.plotframe.Raise()


    def onPlot1(self,event=None):
        self.ShowPlotFrame()
        self.plotframe.plot(self.x,self.y1)
        self.plotframe.oplot(self.x,self.y2)
        self.plotframe.write_message("Plot 1")

    def onPlot2(self,event=None):
        self.ShowPlotFrame()
        self.plotframe.plot( self.x,self.y2,color='black',style='dashed')
        self.plotframe.oplot(self.x,self.y3,color='green',marker='+',markersize=14)
        self.plotframe.write_message("Plot 2")


    def onPlot3(self,event=None):
        self.ShowPlotFrame()
        self.plotframe.plot( self.x,self.y4,ylog_scale=False,
                             color='black',style='dashed')
        self.plotframe.write_message("Exponential Plot")


    def onPlot4(self,event=None):
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
        self.time0    = time.time()
        self.start_mem= self.report_memory()
        self.timer.Start(25)

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
        self.ShowPlotFrame(do_raise=False)
        n = self.count
        if n >= self.npts:
            self.timer.Stop()
            self.timer_results()
        elif n <= 1:
            self.plotframe.plot(self.x[:n], self.y1[:n])# , grid=False)
        else:
            self.plotframe.update_line(0,self.x[:n], self.y1[:n])

            etime = time.time() - self.time0
            s = " %i / %i points in %8.4f s" % (n,self.npts,etime)
            self.plotframe.write_message(s)

        xr    = (min(self.x[:n]),max(self.x[:n]))
        yr    = (min(self.y1[:n]),max(self.y1[:n]))
        xv,yv = self.plotframe.get_xylims()
        if ((n > self.n_update-1) or
            (xr[0] < xv[0]) or (xr[1] > xv[1]) or
            (yr[0] < yv[0]) or (yr[1] > yv[1])):
            nx = self.n_update = min(self.npts,3+int(self.n_update*1.25))
            if nx > int(0.85*self.npts):
                nx = self.n_update = self.npts
                xylims = ((min(self.x),max(self.x)),
                          (min(self.y1),max(self.y1)))
            else:
                xylims = ((min(self.x[0:nx]),max(self.x[0:nx])),
                          (min(self.y1[0:nx]),max(self.y1[0:nx])))
            self.up_count = self.up_count + 1
            self.plotframe.panel.set_xylims(xylims,autoscale=False)

    def XonTimer(self, event):
        # print 'timer ', self.count
        self.count += 1
        self.ShowPlotFrame(do_raise=False)

        if self.count >= self.npts:
            self.timer.Stop()
            self.timer_results()
        else:
            self.plotframe.plot(self.x[:self.count],
                                self.y1[:self.count],refresh=False)

            etime = time.time() - self.time0
            s = " %i / %i   elapsed time= %8.2f s" % (self.count,self.npts,etime)
            self.plotframe.write_message(s)

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
