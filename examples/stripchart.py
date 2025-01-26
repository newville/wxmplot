#!/usr/bin/python
"""
2-axes strip chart
"""
import os
import time
import numpy as np
import sys
import wx
from wx.lib import masked
from floatcontrol import FloatCtrl
from wxmplot import PlotPanel
from matplotlib.dates import date2num
import pytz

tzname = os.environ.get('TZ', 'US/Central')
TZONE = pytz.timezone(tzname)

def next_data():
    "simulated data"
    t0 = time.time()
    lt = time.localtime(t0)

    tmin, tsec = lt[4], lt[5]
    u = np.random.random()
    v = np.random.random()
    x = np.sin( (u + tsec)/3.0) + tmin/30. + v/5.0
    y = 4*np.cos( (v + tsec)/3.0) + tmin/30. + u*3
    return t0, x, y

class StripChartFrame(wx.Frame):
    def __init__(self, parent, ID, **kws):
        kws["style"] = wx.DEFAULT_FRAME_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL

        wx.Frame.__init__(self, parent, ID, '',
                         wx.DefaultPosition, wx.Size(-1,-1), **kws)
        self.SetTitle("wxmplot StripChart Demo")

        self.tmin = 30.0

        self.SetFont(wx.Font(12,wx.SWISS,wx.NORMAL,wx.BOLD,False))
        menu = wx.Menu()
        menu_exit = menu.Append(-1, "E&xit", "Terminate the program")

        menuBar = wx.MenuBar()
        menuBar.Append(menu, "&File");
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU,  self.OnExit, menu_exit)
        self.Bind(wx.EVT_CLOSE, self.OnExit)

        sbar = self.CreateStatusBar(2,wx.CAPTION)
        sfont = sbar.GetFont()
        sfont.SetWeight(wx.BOLD)
        sfont.SetPointSize(11)
        sbar.SetFont(sfont)
        self.SetStatusWidths([-3,-1])
        self.SetStatusText('',0)

        mainsizer = wx.BoxSizer(wx.VERTICAL)

        btnpanel = wx.Panel(self, -1)
        btnsizer = wx.BoxSizer(wx.HORIZONTAL)

        b_on  = wx.Button(btnpanel, -1, 'Start',   size=(-1,-1))
        b_off = wx.Button(btnpanel, -1, 'Stop',    size=(-1,-1))

        b_on.Bind(wx.EVT_BUTTON, self.onStartTimer)
        b_off.Bind(wx.EVT_BUTTON, self.onStopTimer)

        tlabel = wx.StaticText(btnpanel, -1, '  Time range (seconds from present):')
        self.time_range = FloatCtrl(btnpanel,  size=(100, -1),
                                    value=abs(self.tmin), precision=1)

        btnsizer.Add(b_on,   0, wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.LEFT, 0)
        btnsizer.Add(b_off,  0, wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.LEFT, 0)
        btnsizer.Add(tlabel, 1, wx.GROW|wx.ALL|wx.ALIGN_LEFT|wx.LEFT, 0)
        btnsizer.Add(self.time_range, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.LEFT, 0)

        btnpanel.SetSizer(btnsizer)
        btnsizer.Fit(btnpanel)

        self.plotpanel = PlotPanel(self, messenger=self.write_message)
        self.plotpanel.BuildPanel()
        self.plotpanel.set_xlabel('Time from Present (s)')
        mainsizer.Add(btnpanel, 0,  wx.GROW|wx.ALIGN_LEFT|wx.LEFT, 0)
        mainsizer.Add(self.plotpanel, 1, wx.GROW|wx.ALL|wx.ALIGN_LEFT|wx.LEFT, 0)
        self.SetSizer(mainsizer)
        mainsizer.Fit(self)

        self.Bind(wx.EVT_TIMER, self.onTimer)
        self.timer = wx.Timer(self)
        self.count = 0
        self.Refresh()
        self.SetSize(self.GetBestVirtualSize())

        wx.CallAfter(self.onStartTimer)

    def write_message(self, msg, panel=0):
        """write a message to the Status Bar"""
        self.SetStatusText(msg, panel)

    def onStartTimer(self,event=None):
        self.count    = 0
        t0, y0, y1 = next_data()
        self.y2list = [y0]
        self.y1list = [y0]
        self.y2list = [y1]
        self.tlist = [t0]
        self.tmin_last = -10000
        self.time0    = time.time()
        self.timer.Start(50)

    def onStopTimer(self,event=None):
        self.timer.Stop()

    def onTimer(self, event):
        self.count += 1
        now = time.time()
        tmin = now - float(self.time_range.GetValue())
        t1, y1, y2 = next_data()
        self.tlist.append(t1)
        self.y1list.append(y1)
        self.y2list.append(y2)
        t0 = self.tlist[0]
        tdat = np.array(self.tlist)
        mask = np.where(tdat > tmin)

        y1dat = np.array(self.y1list)[mask]
        y2dat = np.array(self.y2list)[mask]
        tdat = np.array(self.tlist)[mask]
        tdat /= 86400.  # convert timestamps to matplotlib date, need TimeZone!!
        n = len(self.y1list)

        if n <= 2:
            self.plotpanel.plot(tdat, y1dat, use_date=True, timezone=TZONE,
                                xlabel='time', ylabel='Val 1', yaxes_tracecolor=True)
            self.plotpanel.oplot(tdat, y2dat, yaxes=2, y2label='Value 2',
                                 use_dates=True, timezone=TZONE)
        else:
            self.plotpanel.update_line(0, tdat, y1dat, draw=True)
            self.plotpanel.update_line(1, tdat, y2dat, draw=True, yaxes=2)
            # self.write_message(f"update {n} points in {(now-self.time0):.2f} sec")

    def OnAbout(self, event):
        dlg = wx.MessageDialog(self, "wxmplot example: stripchart app",
                              "About WXMPlot test", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def OnExit(self, event):
        self.Destroy()

app = wx.App()
f = StripChartFrame(None,-1)
f.Show(True)
app.MainLoop()
#
