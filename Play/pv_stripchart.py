#!/usr/bin/python
import sys
import time
import numpy
import wx

import epics
import epics.wx
import  MPlot

class EpicsStripChart(wx.Frame):
    def __init__(self, parent=None, pvname=None):
        self.pvs = []
        
        wx.Frame.__init__(self, parent, -1, 'Strip Chart')
        self.pvdata = {}
        if pvname is not None:
            self.pv = epics.PV(pvname)
            self.pv.add_callback(self.onPVChange)
            self.pvdata[pvname] = []
        self.time0 = time.time()
        self.plotframe = MPlot.PlotFrame()
        
    @epics.wx.DelayedEpicsCallback
    def onPVChange(self, pvname=None, value=None,**kw):
        self.pvdata[pvname].append((time.time(),value))
        wx.CallAfter(self.UpdatePlot)

    def UpdatePlot(self):
        tnow = time.time()
        etime = tnow - self.time0

        self.tmin = -20
        for pvname, data in self.pvdata.items():
            tdat = numpy.array([i[0] for i in data]) - tnow

            mask = numpy.where(tdat>self.tmin)
            tdat = tdat[mask]
            ydat = numpy.array([i[1] for i in data])[mask]
            
            if len(tdat) <= 1:
                self.plotframe.plot(tdat, ydat, 
                                    drawstyle='steps-post',
                                    xlabel='Elapsed Time (s)',
                                    ylabel=pvname)
                
            else:
                self.plotframe.update_line(0, tdat, ydat)
                xylims = (min(tdat), max(tdat), min(ydat),max(ydat))
                print xylims
                
                self.plotframe.panel.set_xylims(xylims, autoscale=True)
                

#                       ydat[mask].max())
#             print len(tdat), xylims ,  min(tdat), max(tdat)
#             n = len(ydat)

            #elif n > 3:
            #    self.plotframe.update_line(tdat, ydat)
            #s = " %i points in %8.4f s" % (n,etime)
            #self.plotframe.write_message(s)
            # self.plotframe.panel.set_xylims(xylims)


if __name__ == '__main__':
    app = wx.PySimpleApp()
    #f = EpicsStripChart(pvname='13IDA:DMM1Ch2_calc.VAL')
    f = EpicsStripChart(pvname='Py:ao3')
    f.plotframe.Show(True)
    app.MainLoop()

