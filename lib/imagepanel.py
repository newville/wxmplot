#!/usr/bin/python
##
## MPlot PlotPanel: a wx.Panel for 2D line plotting, using matplotlib
##

import sys
import time
import os
import wx
import numpy as np
import matplotlib
import matplotlib.cm as colormap
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg

from imageconf import ImageConfig, ImageConfigFrame
from basepanel import BasePanel

class ImagePanel(BasePanel):
    """
    MatPlotlib Image as a wx.Panel, suitable for embedding
    in any wx.Frame.   This provides a right-click popup
    menu for configuration, zoom by dragging, saving an image
    figure, and Ctrl-C for copy-image-to-clipboard, customizations
    of colormap, interpolation, and intesity scaling

    For more features, see PlotFrame, which embeds a PlotPanel
    and also provides, a Menu, StatusBar, and Printing support.
    """

    def __init__(self, parent, messenger=None, data_callback=None,
                 size=(4.50,4.00), dpi=96, **kws):
        matplotlib.rc('lines', linewidth=2)
        BasePanel.__init__(self, parent, messenger=messenger, **kws)
        self.data_callback = data_callback
        self.conf = ImageConfig()
        self.win_config = None
        self.cursor_callback = None
        self.figsize = size
        self.dpi     = dpi
        self.xlab    = 'X'
        self.ylab    = 'Y'
        self.xdata   = None
        self.ydata   = None
        self.BuildPanel()

    def display(self, data, x=None, y=None, xlabel=None, ylabel=None, **kw):
        """
        display a new image display on the current panel
        """
        self.axes.cla()
        self.conf.rot = False
        self.data_range = [0, data.shape[1], 0, data.shape[0]]
        if x is not None:
            self.xdata = np.array(x)
            if self.xdata.shape[0] != data.shape[1]:
                print 'Warning X array wrong size!'
        if y is not None:
            self.ydata = np.array(y)
            if self.ydata.shape[0] != data.shape[0]:
                print 'Warning Y array wrong size!'

        if xlabel is not None:
            self.xlab = xlabel
        if ylabel is not None:
            self.ylab = ylabel
        self.conf.data = data
        cmap = self.conf.cmap
        img = (data -data.min()) /(1.0*data.max() - data.min())
        self.conf.image = self.axes.imshow(img, cmap=self.conf.cmap,
                                           interpolation=self.conf.interp)
        self.axes.set_axis_off()
        self.unzoom_all()
        if hasattr(self.data_callback, '__call__'):
            self.data_callback(data, x=x, y=y, **kw)

    def set_xylims(self, lims, axes=None, autoscale=True):
        """ update xy limits of a plot"""
        if axes is None:
            axes = self.axes

        if autoscale:
            xmin, xmax, ymin, ymax = self.data_range
        else:
            xmin, xmax, ymin, ymax = lims

        xmin = int(max(self.data_range[0], xmin) + 0.5)
        xmax = int(min(self.data_range[1], xmax) + 0.5)
        ymin = int(max(self.data_range[2], ymin) + 0.5)
        ymax = int(min(self.data_range[3], ymax) + 0.5)

        if abs(xmax-xmin) < 2:
            xmin = int(0.5*(xmax+xmin) - 1)
            xmax = xmin + 2

        if abs(ymax-ymin) < 2:
            ymin = int(0.5*(ymax+xmin) - 1)
            ymax = ymin + 2

        self.axes.set_xlim((xmin,xmax),emit=True)
        self.axes.set_ylim((ymin,ymax),emit=True)
        self.axes.update_datalim(((xmin,ymin),(xmax,ymax)))
        if autoscale:
            self.axes.set_xbound(self.axes.xaxis.get_major_locator().view_limits(xmin,xmax))
            self.axes.set_ybound(self.axes.yaxis.get_major_locator().view_limits(ymin,ymax))

        self.conf.xylims = [[xmin, xmax], [ymin, ymax]]
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
        self.axes  = self.fig.add_axes([0.02, 0.02, 0.96, 0.96])

        self.canvas = FigureCanvasWxAgg(self, -1, self.fig)
        self.fig.set_facecolor('#FBABA8')

        self.conf.axes  = self.axes
        self.conf.fig   = self.fig
        self.conf.canvas= self.canvas

        self.canvas.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

        # This way of adding to sizer allows resizing
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 2, wx.LEFT|wx.TOP|wx.BOTTOM|wx.EXPAND|wx.ALL, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Fit()
        self.addCanvasEvents()

    def BuildPopup(self):
        # build pop-up menu for right-click display
        pass

    ####
    ## GUI events, overriding BasePanel components
    ####
    def reportMotion(self,event=None):
        pass

    def unzoom(self, event=None, set_bounds=True):
        """ zoom out 1 level, or to full data range """
        lims = None
        if len(self.zoom_lims) > 1:
            lims = self.zoom_lims.pop()
        ax = self.axes
        if lims is None: # auto scale
            self.zoom_lims = [None]
            xmin, xmax, ymin, ymax = self.data_range
            lims = {self.axes: [xmin, xmax, ymin, ymax]}
        self.set_xylims(lims=lims[self.axes], axes=self.axes, autoscale=False)

    def unzoom_all(self, event=None):
        """ zoom out full data range """
        self.zoom_lims = [None]
        self.unzoom(event)

    def redraw(self):
        """redraw image, applying the following:
        rotation, flips, log scale
        max/min values from sliders or explicit intensity ranges
        color map
        interpolation
        """
        conf = self.conf
        # note: rotation re-calls display(), to reset the image
        # other transformations will just do .set_data() on image
        if conf.rot:
            if self.xdata is not None:
                self.xdata = self.xdata[::-1]
            self.display(np.rot90(conf.data),
                         x=self.ydata, xlabel=self.ylab,
                         y=self.xdata, ylabel=self.xlab)
        # flips, log scales
        img = conf.data
        if conf.flip_ud:   img = np.flipud(img)
        if conf.flip_lr:   img = np.fliplr(img)
        if conf.log_scale: img = np.log10(1.0+ 9.0 * img)

        # apply intensity scale for current limited (zoomed) image
        imin = conf.int_lo
        imax = conf.int_hi
        if conf.auto_intensity:
            ((xmin, xmax), (ymin, ymax)) = self.conf.xylims
            if xmin is None:  xmin = 0
            if xmax is None:  xmax = img.shape[1]
            if ymin is None:  ymin = 0
            if ymax is None:  ymax = img.shape[0]
            imin = np.min(img[ymin:ymax, xmin:xmax])
            imax = np.max(img[ymin:ymax, xmin:xmax])
        img = (img - imin)/(imax - imin + 1.e-8)

        # apply clipped color scale, as from sliders
        mlo = conf.cmap_lo/(1.0*conf.cmap_range)
        mhi = conf.cmap_hi/(1.0*conf.cmap_range)
        conf.image.set_data(np.clip((img - mlo)/(mhi - mlo + 1.e-8), 0, 1))

        conf.image.set_interpolation(conf.interp)
        self.canvas.draw()

    def reportLeftDown(self,event=None):
        if event == None:
            return
        ix, iy = round(event.xdata), round(event.ydata)
        if self.conf.flip_ud:  iy = self.conf.data.shape[0] - iy
        if self.conf.flip_lr:  ix = self.conf.data.shape[1] - ix

        if (ix >= 0 and ix < self.conf.data.shape[1] and
            iy >= 0 and iy < self.conf.data.shape[0]):
            pos = ''
            if self.xdata is not None:
                pos = ' %s=%.4g,' % (self.xlab, self.xdata[ix])
            if self.ydata is not None:
                pos = '%s %s=%.4g,' % (pos, self.ylab, self.ydata[iy])
            msg = "Pixel [%i, %i],%s Intensity=%.4g " % (ix, iy, pos,
                                                         self.conf.data[iy, ix])
            self.write_message(msg, panel=0)
            if hasattr(self.cursor_callback , '__call__'):
                self.cursor_callback(x=event.xdata, y=event.ydata)
