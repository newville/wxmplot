#!/usr/bin/python
##
## MPlot PlotPanel: a wx.Panel for 2D line plotting, using matplotlib
##

import sys
import time
import os
import wx
import numpy
import matplotlib
import matplotlib.cm as colormap
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg

from imageconf import ImageConfig, ImageConfigFrame
from basepanel import BasePanel

class ImagePanel(BasePanel):
    """
    MatPlotlib Image as a wx.Panel, suitable for embedding
    in any wx.Frame.   This does provide a right-click popup
    menu for configuration, zooming, saving an image of the
    figure, and Ctrl-C for copy-image-to-clipboard.

    For more features, see PlotFrame, which embeds a PlotPanel
    and also provides, a Menu, StatusBar, and Printing support.
    """

    def __init__(self, parent, messenger=None,
                 size=(4.50,4.00), dpi=96, **kws):
        matplotlib.rc('lines', linewidth=2)
        BasePanel.__init__(self, parent, messenger=messenger, **kws)

        self.conf = ImageConfig()
        self.win_config = None
        self.cursor_callback = None
        self.figsize = size
        self.dpi     = dpi
        self.BuildPanel()

    def display(self,data,x=None,y=None,**kw):
        """
        display (that is, create a new image display on the current frame
        """
        self.axes.cla()
        self.conf.ntraces  = 0
        self.data_range = [0,data.shape[1], 0, data.shape[0]]
        if x is not None: self.data_range[:1] = [min(x),max(x)]
        if y is not None: self.data_range[2:] = [min(y),max(y)]

        self.conf.data = data
        img = (data -data.min()) /(1.0*data.max() - data.min())
        self.conf.image = self.axes.imshow(img, cmap=colormap.gray,
                                           interpolation='nearest')
        self.axes.set_axis_off()
        self.unzoom(set_bounds=False)

    def set_xylims(self, lims, axes=None, autoscale=True):
        """ update xy limits of a plot"""
        if axes is None:
            axes = self.axes

        if autoscale:
            (xmin, xmax), (ymin, ymax) = self.data_range
        else:
            (xmin, xmax), (ymin, ymax) = lims

        if abs(xmax-xmin) < 1.90:
            xmin = 0.5*(xmax+xmin) - 1
            xmax = 0.5*(xmax+xmin) + 1

        if abs(ymax-ymin) < 1.90:
            ymin = 0.5*(ymax+xmin) - 1
            ymax = 0.5*(ymax+xmin) + 1

        self.axes.set_xlim((xmin,xmax),emit=True)
        self.axes.set_ylim((ymin,ymax),emit=True)
        self.axes.update_datalim(((xmin,ymin),(xmax,ymax)))
        if autoscale:
            self.axes.set_xbound(self.axes.xaxis.get_major_locator().view_limits(xmin,xmax))
            self.axes.set_ybound(self.axes.yaxis.get_major_locator().view_limits(ymin,ymax))

        self.conf.xylims = [[int(xmin+0.5), int(xmax+0.5)], [int(ymin+0.5), int(ymax+0.5)]]
        self.redraw()

    def clear(self):
        """ clear plot """
        self.axes.cla()
        self.conf.title  = ''

    def configure(self,event=None):
        try:
            self.win_config.Raise()
        except:
            self.win_config = ImageConfigFrame(parent=self, conf=self.conf)
    ####
    ## create GUI
    ####
    def BuildPanel(self):
        """ builds basic GUI panel and popup menu"""

        self.fig   = Figure(self.figsize,dpi=self.dpi)
        self.axes  = self.fig.add_axes([0.08,0.08,0.90,0.90],
                                       axisbg='#FEFEFE')

        self.canvas = FigureCanvasWxAgg(self, -1, self.fig)
        self.fig.set_facecolor('#FBFBF8')

        self.conf.axes  = self.axes
        self.conf.fig   = self.fig
        self.conf.canvas= self.canvas

        self.canvas.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

        # This way of adding to sizer allows resizing
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 2, wx.LEFT|wx.TOP|wx.BOTTOM|wx.EXPAND,0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Fit()
        self.addCanvasEvents()

    def BuildPopup(self):
        # build pop-up menu for right-click display
        self.popup_unzoom_all = wx.NewId()
        self.popup_unzoom_one = wx.NewId()
        self.popup_save   = wx.NewId()
        self.popup_flipv  = wx.NewId()
        self.popup_fliph  = wx.NewId()
        self.popup_flipo  = wx.NewId()
        self.popup_menu = wx.Menu()
        self.popup_menu.Append(self.popup_unzoom_one, 'Zoom out')
        self.popup_menu.Append(self.popup_unzoom_all, 'Zoom all the way out')
        self.popup_menu.AppendSeparator()
        self.popup_menu.Append(self.popup_flipv, 'Flip Top/Bottom')
        self.popup_menu.Append(self.popup_fliph, 'Flip Left/Right')
        self.popup_menu.Append(self.popup_flipo, 'Flip to Original')
        self.popup_menu.AppendSeparator()
        self.popup_menu.Append(self.popup_save,  'Save Image')
        self.Bind(wx.EVT_MENU, self.unzoom,    id=self.popup_unzoom_one)
        self.Bind(wx.EVT_MENU, self.unzoom_all,   id=self.popup_unzoom_all)
        self.Bind(wx.EVT_MENU, self.save_figure,  id=self.popup_save)
        self.Bind(wx.EVT_MENU, self.onFlip,       id=self.popup_fliph)
        self.Bind(wx.EVT_MENU, self.onFlip,       id=self.popup_flipv)
        self.Bind(wx.EVT_MENU, self.onFlip,       id=self.popup_flipo)

    ####
    ## GUI events, overriding BasePanel components
    ####
    def reportMotion(self,event=None):
        pass

    def onFlip(self, event=None):
        oldflip = self.conf.flip
        wid = event.GetId()
        if wid == self.popup_fliph:
            self.conf.flip = (oldflip[0], not oldflip[1])
        elif wid == self.popup_flipv:
            self.conf.flip = (not oldflip[0], oldflip[1])
        elif wid == self.popup_flipo:
            self.conf.flip = (False, False)
        self.unzoom_all()

    def unzoom(self, event=None, set_bounds=True):
        """ zoom out 1 level, or to full data range """
        lims = None
        if len(self.zoom_lims) > 1:
            lims = self.zoom_lims.pop()
        ax = self.axes
        if lims is None: # auto scale
            self.zoom_lims = [None]
            xmin, xmax, ymin, ymax = self.data_range
            lims = {self.axes: ((xmin, xmax), (ymin, ymax))}

        self.set_xylims(lims=lims[self.axes], axes=self.axes,
                        autoscale=False)
        txt = ''
        if len(self.zoom_lims) > 1:
            txt = 'zoom level %i' % (len(self.zoom_lims))
        self.write_message(txt)
        self.redraw()

    def unzoom_all(self, event=None):
        """ zoom out full data range """
        self.zoom_lims = [None]
        self.unzoom(event)

    def redraw(self):
        """redraw image, applying the following:
           flip state
           interpolation
           color map
           max/min values from sliders or
           intensity ranges
        """
        conf = self.conf
        lo, hi = conf.cmap_lo, conf.cmap_hi
        cmax = 1.0*conf.cmap_range

        ((xmin, xmax), (ymin, ymax)) = self.conf.xylims

        data = conf.data
        if xmin is None: xmin = 0
        if xmax is None: xmax = data.shape[1]
        if ymin is None: ymin = 0
        if ymax is None: ymax = data.shape[0]

        dmin = numpy.min(data[ymin:ymax, xmin:xmax]) #
        dmax = numpy.max(data[ymin:ymax, xmin:xmax]) #

        img = cmax*(data -dmin) /(1.0*dmax- dmin + 1.e-5)
        img = numpy.clip((cmax*(img-lo)/(hi-lo+1.e-5)), 0, int(cmax))/cmax

        if conf.flip[0]:
            img = img[::-1]
        if conf.flip[1]:
            img = img.transpose()[::-1].transpose()

        conf.image.set_data(img)
        conf.image.set_interpolation(conf.interp)
        self.canvas.draw()

    def reportLeftDown(self,event=None):
        if event == None:
            return
        ix, iy = round(event.xdata), round(event.ydata)
        if self.conf.flip[1]:
            ix = self.conf.data.shape[1] - ix
        if self.conf.flip[0]:
            iy = self.conf.data.shape[0] - iy

        if (ix > 0 and ix < self.conf.data.shape[1] and
            iy > 0 and iy < self.conf.data.shape[0]):
            msg = "Pixel[%i, %i], Intensity=%.4g " %(ix,iy,
                                                     self.conf.data[iy,ix])
            self.write_message(msg, panel=0)
            if hasattr(self.cursor_callback , '__call__'):
                self.cursor_callback(x=event.xdata, y=event.ydata)

