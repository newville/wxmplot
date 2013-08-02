#!/usr/bin/python
##
## MPlot PlotPanel: a wx.Panel for 2D line plotting, using matplotlib
##

import sys
import time
import os
import wx
from threading import Thread

import numpy as np
import matplotlib
import matplotlib.cm as colormap
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg

from .imageconf import ImageConfig
from .basepanel import BasePanel
from .utils import inside_poly

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
                 cursor_callback=None, lasso_callback=None,
                 contour_callback=None,
                 size=(5.25, 4.50), dpi=100,
                 output_title='Image', **kws):
        matplotlib.rc('lines', linewidth=2)
        BasePanel.__init__(self, parent,
                           output_title=output_title,
                           messenger=messenger, **kws)
        self.conf = ImageConfig()
        self.conf.title = output_title
        self.cursor_mode = 'zoom'

        self.data_callback = data_callback
        self.cursor_callback = cursor_callback
        self.lasso_callback = lasso_callback
        self.contour_callback = contour_callback

        self.win_config = None
        self.data_shape = None
        self.figsize = size
        self.dpi     = dpi
        self.xlab    = 'X'
        self.ylab    = 'Y'
        self.xdata   = None
        self.ydata   = None
        self.user_limits = {}
        self.BuildPanel()

    def display(self, data, x=None, y=None, xlabel=None, ylabel=None,
                style=None, nlevels=None, levels=None, contour_labels=None,
                col='int', **kws):
        """
        generic display, using imshow (default) or contour
        """
        if style is not None:
            self.conf.style = style
        self.axes.cla()
        conf = self.conf
        conf.rot, conf.log_scale   = False, False
        conf.flip_ud, conf.flip_lr = False, False
        conf.highlight_areas = []
        self.data_shape = data.shape
        self.data_range = [0, data.shape[1], 0, data.shape[0]]

        if x is not None:
            self.xdata = np.array(x)
            if self.xdata.shape[0] != data.shape[1]:
                self.xdata = None
        if y is not None:
            self.ydata = np.array(y)
            if self.ydata.shape[0] != data.shape[0]:
                self.ydata = None
        if xlabel is not None:
            self.xlab = xlabel
        if ylabel is not None:
            self.ylab = ylabel
        self.conf.data = data

        cmap = self.conf.cmap[col]
        if self.conf.style == 'contour':
            if levels is None:
                levels = self.conf.ncontour_levels
            else:
                self.conf.ncontour_levels = levels
            if nlevels is None:
                nlevels = self.conf.ncontour_levels = 9
            nlevels = max(2, nlevels)
            clevels  = np.linspace(data.min(), data.max(), nlevels+1)
            self.conf.contour_levels = clevels
            self.conf.image = self.axes.contourf(data, cmap=self.conf.cmap[col],
                                                 levels=clevels)

            self.conf.contour = self.axes.contour(data, cmap=self.conf.cmap[col],
                                                  levels=clevels)
            cmap_name = self.conf.cmap[col].name
            xname = 'gray'
            try:
                if cmap_name == 'gray_r':
                    xname = 'Reds_r'
                elif cmap_name == 'gray':
                    xname = 'Reds'
                elif cmap_name.endswith('_r'):
                    xname = 'gray_r'
            except:
                pass
            self.conf.contour.set_cmap(getattr(colormap, xname))

            if contour_labels is None:
                contour_labels = self.conf.contour_labels
            if contour_labels:
                self.axes.clabel(self.conf.contour, fontsize=10, inline=1)
            if hasattr(self.contour_callback , '__call__'):
                self.contour_callback(levels=clevels)
        else: # image
            img = (data -data.min()) /(1.0*data.max() - data.min())
            self.conf.image = self.axes.imshow(img, cmap=self.conf.cmap[col],
                                               interpolation=self.conf.interp)

        self.axes.set_axis_off()
        self.unzoom_all()
        if hasattr(self.data_callback, '__call__'):
            self.data_callback(data, x=x, y=y, **kws)

        self.conf.indices = None
        self.indices_thread = Thread(target=self.calc_indices, args=(data.shape, ))
        self.indices_thread.start()


    def add_highlight_area(self, mask, label=None, col='int'):
        """add a highlighted area -- outline an arbitrarily shape --
        as if drawn from a Lasso event.

        This takes a mask, which should be a boolean array of the
        same shape as the image.
        """
        patch = mask * np.ones(mask.shape) * 0.9
        cmap = self.conf.cmap[col]
        area = self.axes.contour(patch, cmap=cmap, levels=[0.8])
        self.conf.highlight_areas.append(area)
        col = None
        if hasattr(cmap, '_lut'):
            rgb  = [int(i*240)^255 for i in cmap._lut[0][:3]]
            col  = '#%02x%02x%02x' % (rgb[0], rgb[1], rgb[2])

        if label is not None:
            fmt = {0.8: label, 0.9: label}
            self.axes.clabel(area, fontsize=9, inline=1, fmt=fmt, colors=col)

        if col is not None:
            for l in area.collections:
                l.set_color(col)

        self.canvas.draw()

    def set_viewlimits(self, axes=None, autoscale=False):
        """ update xy limits of a plot"""
        if axes is None:
            axes = self.axes

        xmin, xmax, ymin, ymax = self.data_range
        if not autoscale and len(self.zoom_lims) >1:
            zlims = self.zoom_lims[-1]
            if axes in zlims:
                xmin, xmax, ymin, ymax = zlims[axes]

        xmin = int(max(self.data_range[0], xmin) + 0.5)
        xmax = int(min(self.data_range[1], xmax) + 0.5)
        ymin = int(max(self.data_range[2], ymin) + 0.5)
        ymax = int(min(self.data_range[3], ymax) + 0.5)
        if (xmax < self.data_range[0] or
            xmin > self.data_range[1] or
            ymax < self.data_range[2] or
            ymin > self.data_range[3] ):
            self.zoom_lims.pop()
            return

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
        self.conf.datalimits = [xmin, xmax, ymin, ymax]
        try:
            self.redraw()
        except ValueError:
            pass

    def clear(self):
        """ clear plot """
        self.axes.cla()
        self.conf.title  = ''


    ####
    ## create GUI
    ####
    def BuildPanel(self):
        """ builds basic GUI panel and popup menu"""

        self.fig   = Figure(self.figsize, dpi=self.dpi)
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
        self.popup_unzoom_all = wx.NewId()
        self.popup_unzoom_one = wx.NewId()
        self.popup_rot90     = wx.NewId()
        self.popup_curmode   = wx.NewId()
        self.popup_save   = wx.NewId()
        self.popup_menu = wx.Menu()
        self.popup_menu.Append(self.popup_unzoom_one, 'Zoom out')
        self.popup_menu.Append(self.popup_unzoom_all, 'Zoom all the way out')
        self.popup_menu.AppendSeparator()
        self.popup_menu.Append(self.popup_rot90,   'Rotate 90deg (CW)')

        self.popup_menu.Append(self.popup_save,  'Save Image')
        self.Bind(wx.EVT_MENU, self.unzoom,       id=self.popup_unzoom_one)
        self.Bind(wx.EVT_MENU, self.unzoom_all,   id=self.popup_unzoom_all)
        self.Bind(wx.EVT_MENU, self.save_figure,  id=self.popup_save)
        # self.popup_menu.Append(self.popup_curmode, 'Toggle Cursor Mode')
        # self.Bind(wx.EVT_MENU, self.toggle_curmode,  id=self.popup_curmode)
        self.Bind(wx.EVT_MENU, self.rotate90,  id=self.popup_rot90)

    def rotate90(self, event=None):
        "rotate 90 degrees, CW"
        self.conf.rot = True
        self.unzoom_all()

    def toggle_curmode(self, event=None):
        "toggle cursor mode"
        if self.cursor_mode == 'zoom':
            self.cursor_mode = 'lasso'
        else:
            self.cursor_mode = 'zoom'

    ####
    ## GUI events, overriding BasePanel components
    ####
    def exportASCII(self, event=None):
        ofile  = ''
        title = 'unknown map'
        if self.conf.title is not None:
            title = ofile = self.conf.title.strip()
        if len(ofile) > 64:
            ofile = ofile[:63].strip()
        if len(ofile) < 1:
            ofile = 'Image'

        for c in ' .:";|/\\(){}[]\'&^%*$+=-?!@#':
            ofile = ofile.replace(c, '_')

        while '__' in ofile:
            ofile = ofile.replace('__', '_')

        ofile = ofile + '.dat'
        orig_dir = os.path.abspath(os.curdir)

        dlg = wx.FileDialog(self, message='Export Map Data to ASCII...',
                            defaultDir = os.getcwd(),
                            defaultFile=ofile,
                            style=wx.SAVE|wx.CHANGE_DIR)

        if dlg.ShowModal() == wx.ID_OK:
            self.writeASCIIFile(dlg.GetPath(), title=title)

    def writeASCIIFile(self, fname, title='unknown map'):
        buff = ["# Map Data for %s" % title,
                "#------", "#   Y   X   Intensity"]
        ny, nx = self.conf.data.shape
        xdat = np.arange(nx)
        ydat = np.arange(ny)
        if self.xdata is not None: xdat = self.xdata
        if self.ydata is not None: ydat = self.ydata

        for iy in range(ny):
            for ix in range(nx):
                buff.append(" %.10g  %.10g  %.10g" % (
                    ydat[iy], xdat[ix], self.conf.data[iy, ix]))

        fout = open(fname, 'w')
        fout.write("%s\n" % "\n".join(buff))
        fout.close()

    def calc_indices(self, shape):
        """calculates and stores the set of indices
        ix=[0, nx-1], iy=[0, ny-1] for data of shape (nx, ny)"""
        if len(shape) == 2:
            ny, nx = shape
        elif len(shape) == 3:
            ny, nx, nchan = shape

        inds = []
        for iy in range(ny):
            inds.extend([(ix, iy) for ix in range(nx)])
        self.conf.indices = np.array(inds)

    def lassoHandler(self, vertices):
        if self.conf.indices is None or self.indices_thread.is_alive():
            self.indices_thread.join()
        ind = self.conf.indices
        mask = inside_poly(vertices,ind)
        mask.shape = (self.conf.data.shape[0], self.conf.data.shape[1])
        self.lasso = None
        self.canvas.draw()
        if hasattr(self.lasso_callback , '__call__'):
            self.lasso_callback(mask=mask)

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
        self.set_viewlimits()
        self.canvas.draw()

    def unzoom_all(self, event=None):
        """ zoom out full data range """
        self.zoom_lims = [None]
        self.unzoom(event)

    def redraw(self, col='int'):
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
        if len(img.shape) == 2:
            col = 'int'
        if self.conf.style == 'image':
            if conf.flip_ud:   img = np.flipud(img)
            if conf.flip_lr:   img = np.fliplr(img)
            if conf.log_scale:
                img = np.log10(1 + 9.0*img)

        # apply intensity scale for current limited (zoomed) image
        imin = float(conf.int_lo[col])
        imax = float(conf.int_hi[col])
        if conf.log_scale:
            imin = np.log10(1 + 9.0*imin)
            imax = np.log10(1 + 9.0*imax)
        if conf.auto_intensity:
            (xmin, xmax, ymin, ymax) = self.conf.datalimits
            if xmin is None:  xmin = 0
            if xmax is None:  xmax = img.shape[1]
            if ymin is None:  ymin = 0
            if ymax is None:  ymax = img.shape[0]
            imin = np.min(img[ymin:ymax, xmin:xmax])
            imax = np.max(img[ymin:ymax, xmin:xmax])
        # apply clipped color scale, as from sliders
        if len(img.shape) == 2:
            img = (img - imin)/(imax - imin + 1.e-8)
            mlo = conf.cmap_lo[col]/(1.0*conf.cmap_range)
            mhi = conf.cmap_hi[col]/(1.0*conf.cmap_range)
            if self.conf.style == 'image':
                conf.image.set_data(np.clip((img - mlo)/(mhi - mlo + 1.e-8), 0, 1))
                conf.image.set_interpolation(conf.interp)
        else:
            r, g, b = img[:,:,0], img[:,:,1], img[:,:,2]
            rmin = float(conf.int_lo['red'])
            rmax = float(conf.int_hi['red'])
            gmin = float(conf.int_lo['green'])
            gmax = float(conf.int_hi['green'])
            bmin = float(conf.int_lo['blue'])
            bmax = float(conf.int_hi['blue'])
            if conf.log_scale:
                rmin = np.log10(1 + 9.0*rmin)
                rmax = np.log10(1 + 9.0*rmax)
                gmin = np.log10(1 + 9.0*gmin)
                gmax = np.log10(1 + 9.0*gmax)
                bmin = np.log10(1 + 9.0*bmin)
                bmax = np.log10(1 + 9.0*bmax)

            rlo = conf.cmap_lo['red']/(1.0*conf.cmap_range)
            rhi = conf.cmap_hi['red']/(1.0*conf.cmap_range)
            glo = conf.cmap_lo['green']/(1.0*conf.cmap_range)
            ghi = conf.cmap_hi['green']/(1.0*conf.cmap_range)
            blo = conf.cmap_lo['blue']/(1.0*conf.cmap_range)
            bhi = conf.cmap_hi['blue']/(1.0*conf.cmap_range)
            r = (r - rmin)/(rmax - rmin + 1.e-8)
            g = (g - gmin)/(gmax - gmin + 1.e-8)
            b = (b - bmin)/(bmax - bmin + 1.e-8)
            inew = img*1.0
            inew[:,:,0] = np.clip((r - rlo)/(rhi - rlo + 1.e-8), 0, 1)
            inew[:,:,1] = np.clip((g - glo)/(ghi - glo + 1.e-8), 0, 1)
            inew[:,:,2] = np.clip((b - blo)/(bhi - blo + 1.e-8), 0, 1)

            if self.conf.style == 'image':
                conf.image.set_data(inew)
                conf.image.set_interpolation(conf.interp)
        self.canvas.draw()

    def report_leftdown(self,event=None):
        if event == None:
            return
        if event.xdata is None or event.ydata is None:
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
            dval = self.conf.data[iy, ix]
            if len(self.data_shape) == 3:
                dval = "%.4g, %.4g, %.4g" % tuple(dval)
            else:
                dval = "%.4g" % dval
            msg = "Pixel [%i, %i],%s Intensity=%s " % (ix, iy, pos, dval)

            self.write_message(msg, panel=0)
            if hasattr(self.cursor_callback , '__call__'):
                self.cursor_callback(x=event.xdata, y=event.ydata)
