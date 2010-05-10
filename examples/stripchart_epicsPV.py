#!/usr/bin/python
import sys
import time
import numpy
import wx

import epics
import epics.wx
import MPlot

class EpicsStripChart:
    def __init__(self, pvname=None):
        self.pv = None
        self.pvname = pvname
        if pvname is not None:
            self.pv = epics.PV(pvname)
            self.pv.add_callback(self.onPVChange)
        self.pvlist = []
        self.tlist = []
        self.time0 = time.time()
        self.plotframe = MPlot.PlotFrame()
        
    @epics.wx.DelayedEpicsCallback
    def onPVChange(self,pvname=None,value=None,**kw):
        t0 = time.time()
        self.tlist.append(t0)
        self.pvlist.append(value)
        self.UpdatePlot()
        
    def UpdatePlot(self):
        etime = time.time() - self.time0

        self.tmin = -30
        tdat = numpy.array(self.tlist) -self.tlist[-1]
        tmin = max(self.tmin, tdat.min())
        mask = numpy.where(tdat>self.tmin)
        ydat = numpy.array(self.pvlist)
        xylims = (tmin, 0,
                  ydat[mask].min(),
                  ydat[mask].max())
        n = len(ydat)
        if n <= 1:
            return
        elif n == 2:
            self.plotframe.plot(tdat, ydat,
                                drawstyle='steps-post',
                                xlabel='T (s)',
                                ylabel=self.pvname)
        else:
            self.plotframe.update_line(0,tdat, ydat)
            s = " %i points in %8.4f s" % (n,etime)
            self.plotframe.write_message(s)
        self.plotframe.panel.set_xylims(xylims,
                                        autoscale=True, scalex=False)
        

if __name__ == '__main__':
    app = wx.PySimpleApp()
    f = EpicsStripChart(pvname='13IDA:DMM1Ch2_calc.VAL')
    f.plotframe.Show(True)
    app.MainLoop()

