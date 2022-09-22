#!/usr/bin/python
##
## wxmplot ImagePanel: a wx.Panel for image display, using matplotlib
##

import time
import wx
from threading import Thread

import numpy as np
import matplotlib
import matplotlib.cm as cmap
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.patches import Rectangle

from .imageconf import ImageConfig, RGB_COLORS
from .basepanel import BasePanel
from .utils import inside_poly, MenuItem
from .plotframe import PlotFrame

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
                 redraw_callback=None, zoom_callback=None,
                 contour_callback=None, size=(525, 450), dpi=100,
                 output_title='Image', **kws):

        matplotlib.rc('lines', linewidth=2)
        BasePanel.__init__(self, parent,
                           output_title=output_title,
                           messenger=messenger,
                           zoom_callback=zoom_callback, **kws)

        self.conf = ImageConfig()
        self.conf.title = output_title
        self.cursor_mode = 'zoom'
        self.data_callback = data_callback
        self.cursor_callback = cursor_callback
        self.lasso_callback = lasso_callback
        self.contour_callback = contour_callback
        self.redraw_callback = redraw_callback
        self.slice_plotframe = None
        self.win_config = None
        self.size = size
        self.dpi  = dpi
        self.user_limits = {}
        self.scalebar_rect = self.scalerbar_text = None
        self.BuildPanel()

    @property
    def xdata(self):
        return self.conf.xdata

    @xdata.setter
    def xdata(self, value):
        self.conf.xdata = value

    @property
    def ydata(self):
        return self.conf.ydata

    @ydata.setter
    def ydata(self, value):
        self.conf.ydata = value


    def display(self, data, x=None, y=None, xlabel=None, ylabel=None,
                style=None, nlevels=None, levels=None, contour_labels=None,
                store_data=True, col=0, unzoom=True, show_axis=False,
                auto_contrast=False, contrast_level=0, colormap=None, **kws):
        """
        generic display, using imshow (default) or contour
        """
        if style is not None:
            self.conf.style = style
        self.axes.cla()
        conf = self.conf
        conf.log_scale = False
        conf.show_axis = show_axis
        conf.highlight_areas = []
        if 1 in data.shape:
            data = data.squeeze()
        self.data_range = [0, data.shape[1], 0, data.shape[0]]
        if contrast_level not in (0, None):
            conf.contrast_level = contrast_level
        if auto_contrast:
            conf.contrast_level = 1
        if x is not None:
            conf.xdata = np.array(x)
            if conf.xdata.shape[0] != data.shape[1]:
                conf.xdata = None
        if y is not None:
            conf.ydata = np.array(y)
            if conf.ydata.shape[0] != data.shape[0]:
                conf.ydata = None

        if xlabel is not None:
            conf.xlab = xlabel
        if ylabel is not None:
            conf.ylab = ylabel
        if store_data:
            conf.data = data

        if self.conf.style == 'contour':
            if levels is None:
                levels = self.conf.ncontour_levels
            else:
                self.conf.ncontour_levels = levels
            if nlevels is None:
                nlevels = self.conf.ncontour_levels = 9
            nlevels = max(2, nlevels)

            if conf.contrast_level is not None:
                contrast = [conf.contrast_level, 100.0-conf.contrast_level]
                imin, imax = np.percentile(conf.data, contrast)
                data = np.clip(conf.data, imin, imax)

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
            self.conf.contour.set_cmap(getattr(cmap, xname))

            if contour_labels is None:
                contour_labels = self.conf.contour_labels
            if contour_labels:
                nlog = np.log10(abs(clevels[1]-clevels[0]))
                fmt = "%.4f"
                if nlog < -2:
                    fmt = "%%.%df" % (1-nlog)
                elif nlog > 2:
                    fmt = "%.1f"
                self.axes.clabel(self.conf.contour, fontsize=10, inline=1, fmt=fmt)
            if hasattr(self.contour_callback , '__call__'):
                self.contour_callback(levels=clevels)
        else:
            if data.max() == data.min():
                img = data
            else:
                img = (data - data.min()) /(1.0*data.max() - data.min())
            if colormap is not None:
                self.conf.set_colormap(colormap, icol=col)
            self.conf.image = self.axes.imshow(img, cmap=self.conf.cmap[col],
                                               interpolation=self.conf.interp)

        self.autoset_margins()

        if unzoom:
            self.unzoom_all()

        if hasattr(self.data_callback, '__call__'):
            self.data_callback(data, x=x, y=y, **kws)

        self.conf.indices = None
        self.indices_thread = Thread(target=self.calc_indices, args=(data.shape, ))
        self.indices_thread.start()


    def update_image(self, data):
        """
        update image on panel, as quickly as possible
        """
        if 1 in data.shape:
            data = data.squeeze()
        if self.conf.contrast_level is not None:
            clevels = [self.conf.contrast_level, 100.0-self.conf.contrast_level]
            imin, imax = np.percentile(data, clevels)
            data = np.clip((data - imin)/(imax - imin + 1.e-8), 0, 1)
        self.axes.images[0].set_data(data)
        self.canvas.draw()


    def autoset_margins(self):
        """auto-set margins  left, bottom, right, top
        according to the specified margins (in pixels)
        and axes extent (taking into account labels,
        title, axis)
        """
        if self.conf.show_axis:
            self.axes.set_axis_on()
            if self.conf.show_grid:
                self.axes.grid(True,
                               alpha=self.conf.grid_alpha,
                               color=self.conf.grid_color)
            else:
                self.axes.grid(False)
            self.conf.set_formatters()

            l, t, r, b = 0.08, 0.96, 0.96, 0.08
            if self.conf.xlab is not None:
                self.axes.set_xlabel(self.conf.xlab)
                b, t = 0.11, 0.96
            if self.conf.ylab is not None:
                self.axes.set_ylabel(self.conf.ylab)
                l, r = 0.11, 0.96
        else:
            self.axes.set_axis_off()
            l, t, r, b = 0.01, 0.99, 0.99, 0.01
        self.gridspec.update(left=l, top=t, right=r, bottom=b)

        for ax in self.fig.get_axes():
            figpos = ax.get_subplotspec().get_position(self.canvas.figure)
            ax.set_position(figpos)

    def add_highlight_area(self, mask, label=None, col=0):
        """add a highlighted area -- outline an arbitrarily shape --
        as if drawn from a Lasso event.
        This takes a mask, which should be a boolean array of the
        same shape as the image.
        """
        patch = mask * np.ones(mask.shape) * 0.9
        cmap = self.conf.cmap[col]
        area = self.axes.contour(patch, cmap=cmap, levels=[0, 1])
        self.conf.highlight_areas.append(area)
        if not hasattr(cmap, '_lut'):
            try:
                cmap._init()
            except:
                pass

        if hasattr(cmap, '_lut'):
            rgb  = [int(i*240)^255 for i in cmap._lut[0][:3]]
            col  = '#%02x%02x%02x' % (rgb[0], rgb[1], rgb[2])
        if label is not None:
            def fmt(*args, **kws): return label
            self.axes.clabel(area, fontsize=9, fmt=fmt,
                             colors=col, rightside_up=True)

        if col is not None:
            for l in area.collections:
                l.set_edgecolor(col)
        self.canvas.draw()

    def set_viewlimits(self, axes=None):
        """ update xy limits of a plot"""
        if axes is None:
            axes = self.axes

        xmin, xmax, ymin, ymax = self.data_range
        if len(self.conf.zoom_lims) >1:
            zlims = self.conf.zoom_lims[-1]
            if axes in zlims:
                xmin, xmax, ymin, ymax = zlims[axes]

        xmin = max(self.data_range[0], xmin)
        xmax = min(self.data_range[1], xmax)
        ymin = max(self.data_range[2], ymin)
        ymax = min(self.data_range[3], ymax)
        if (xmax < self.data_range[0] or
            xmin > self.data_range[1] or
            ymax < self.data_range[2] or
            ymin > self.data_range[3] ):
            self.conf.zoom_lims.pop()
            return

        if abs(xmax-xmin) < 2:
            xmin = int(0.5*(xmax+xmin) - 1)
            xmax = xmin + 2

        if abs(ymax-ymin) < 2:
            ymin = int(0.5*(ymax+xmin) - 1)
            ymax = ymin + 2

        self.axes.set_xlim((xmin, xmax),emit=True)
        self.axes.set_ylim((ymin, ymax),emit=True)
        self.axes.update_datalim(((xmin, ymin), (xmax, ymax)))

        self.conf.datalimits = [xmin, xmax, ymin, ymax]
        self.conf.reset_formats()
        self.redraw()

    def clear(self):
        """ clear plot """
        self.axes.cla()
        self.conf.title  = ''


    ####
    ## create GUI
    ####
    def BuildPanel(self):
        """ builds basic GUI panel and popup menu"""
        figsize = (1.0*self.size[0]/self.dpi, 1.0*self.size[1]/self.dpi)
        self.fig   = Figure(figsize, dpi=self.dpi)
        self.gridspec = GridSpec(1,1)
        self.axes  = self.fig.add_subplot(self.gridspec[0],
                                          facecolor='#FFFFFD')
        self.canvas = FigureCanvasWxAgg(self, -1, self.fig)
        self.canvas.gui_repaint = self.gui_repaint
        self.conf.axes  = self.axes
        self.conf.fig   = self.fig
        self.conf.canvas= self.canvas

        # self.canvas.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        # This way of adding to sizer allows resizing
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.canvas, 1, wx.ALL|wx.GROW)
        self.SetSizer(sizer)
        self.SetSize(self.GetBestVirtualSize())
        self.addCanvasEvents()

    def BuildPopup(self):
        # build pop-up menu for right-click display
        self.popup_menu = popup = wx.Menu()
        MenuItem(self, popup, 'Zoom out', '',   self.unzoom)
        MenuItem(self, popup, 'Zoom all the way out', '',   self.unzoom_all)

        self.popup_menu.AppendSeparator()

        MenuItem(self, popup, 'Rotate 90deg  (CW)', '', self.rotate90)
        MenuItem(self, popup, 'Save Image', '', self.save_figure)

    def rotate90(self, event=None, display=True):
        "rotate 90 degrees, CW"
        self.conf.rotate90()
        if display:
            conf = self.conf
            self.display(conf.data, x=conf.xdata, y=conf.ydata,
                         xlabel=conf.xlab, ylabel=conf.ylab,
                         show_axis=conf.show_axis,
                         levels=conf.ncontour_levels)

    def flip_horiz(self):
        self.conf.flip_horiz()

    def flip_vert(self):
        self.conf.flip_vert()

    def restore_flips_rotations(self):
        "restore flips and rotations"
        conf = self.conf
        if conf.flip_lr:
            self.flip_horiz()
        if conf.flip_ud:
            self.flip_vert()
        if conf.rot_level != 0:
            for i in range(4-conf.rot_level):
                self.rotate90(display=False)
            self.display(conf.data, x=conf.xdata, y=conf.ydata,
                         xlabel=conf.xlab, ylabel=conf.ylab,
                         show_axis=conf.show_axis)




    def toggle_curmode(self, event=None):
        "toggle cursor mode"
        if self.cursor_mode == 'zoom':
            self.cursor_mode = 'lasso'
        else:
            self.cursor_mode = 'zoom'

    ####
    ## GUI events, overriding BasePanel components
    ####
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
        if len(self.conf.zoom_lims) > 1:
            lims = self.conf.zoom_lims.pop()
        ax = self.axes
        if lims is None: # auto scale
            self.conf.zoom_lims = [None]
            xmin, xmax, ymin, ymax = self.data_range
            lims = {self.axes: [xmin, xmax, ymin, ymax]}
        self.set_viewlimits()
        self.canvas.draw()

    def zoom_leftup(self, event=None):
        """leftup event handler for zoom mode  in images"""
        if self.zoom_ini is None:
            return

        ini_x, ini_y, ini_xd, ini_yd = self.zoom_ini
        try:
            dx = abs(ini_x - event.x)
            dy = abs(ini_y - event.y)
        except:
            dx, dy = 0, 0
        t0 = time.time()
        self.rbbox = None
        self.zoom_ini = None
        if (dx > 3) and (dy > 3) and (t0-self.mouse_uptime)>0.1:
            self.mouse_uptime = t0
            zlims, tlims = {}, {}
            ax =  self.axes
            xmin, xmax = ax.get_xlim()
            ymin, ymax = ax.get_ylim()

            zlims[ax] = [xmin, xmax, ymin, ymax]

            if len(self.conf.zoom_lims) == 0:
                self.conf.zoom_lims.append(zlims)


            ax_inv = ax.transData.inverted
            try:
                x1, y1 = ax_inv().transform((event.x, event.y))
            except:
                x1, y1 = self.x_lastmove, self.y_lastmove
            try:
                x0, y0 = ax_inv().transform((ini_x, ini_y))
            except:
                x0, y0 = ini_xd, ini_yd

            tlims[ax] = [int(round(min(x0, x1))), int(round(max(x0, x1))),
                         int(round(min(y0, y1))), int(round(max(y0, y1)))]
            self.conf.zoom_lims.append(tlims)
            # now apply limits:
            self.set_viewlimits()
            if callable(self.zoom_callback):
                self.zoom_callback(wid=self.GetId(), limits=tlims[ax])


    def unzoom_all(self, event=None):
        """ zoom out full data range """
        self.conf.zoom_lims = [None]
        self.unzoom(event)

    def redraw(self, col=0):
        """redraw image, applying
        - log scaling,
        - max/min values from sliders or explicit intensity ranges
        - color map
        - interpolation
        """
        conf = self.conf
        img = conf.data
        if img is None: return
        if len(img.shape) == 2:
            col = 0
        if self.conf.style == 'image':
            if conf.log_scale:
                img = np.log10(1 + 9.0*img)

        # apply intensity scale for current limited (zoomed) image
        if len(img.shape) == 2:
            # apply clipped color scale, as from sliders

            imin = float(conf.int_lo[col])
            imax = float(conf.int_hi[col])
            if conf.log_scale:
                imin = np.log10(1 + 9.0*imin)
                imax = np.log10(1 + 9.0*imax)

            (xmin, xmax, ymin, ymax) = self.conf.datalimits
            if xmin is None:  xmin = 0
            if xmax is None:  xmax = img.shape[1]
            if ymin is None:  ymin = 0
            if ymax is None:  ymax = img.shape[0]


            img = (img - imin)/(imax - imin + 1.e-8)
            mlo = conf.cmap_lo[0]/(1.0*conf.cmap_range)
            mhi = conf.cmap_hi[0]/(1.0*conf.cmap_range)
            if self.conf.style == 'image':
                conf.image.set_data(np.clip((img - mlo)/(mhi - mlo + 1.e-8), 0, 1))
                conf.image.set_interpolation(conf.interp)
        else:
            r, g, b = img[:,:,0], img[:,:,1], img[:,:,2]

            rmin = float(conf.int_lo[0])
            rmax = float(conf.int_hi[0])
            gmin = float(conf.int_lo[1])
            gmax = float(conf.int_hi[1])
            bmin = float(conf.int_lo[2])
            bmax = float(conf.int_hi[2])
            if conf.log_scale:
                rmin = np.log10(1 + 9.0*rmin)
                rmax = np.log10(1 + 9.0*rmax)
                gmin = np.log10(1 + 9.0*gmin)
                gmax = np.log10(1 + 9.0*gmax)
                bmin = np.log10(1 + 9.0*bmin)
                bmax = np.log10(1 + 9.0*bmax)

            rlo = conf.cmap_lo[0]/(1.0*conf.cmap_range)
            rhi = conf.cmap_hi[0]/(1.0*conf.cmap_range)
            glo = conf.cmap_lo[1]/(1.0*conf.cmap_range)
            ghi = conf.cmap_hi[1]/(1.0*conf.cmap_range)
            blo = conf.cmap_lo[2]/(1.0*conf.cmap_range)
            bhi = conf.cmap_hi[2]/(1.0*conf.cmap_range)
            r = (r - rmin)/(rmax - rmin + 1.e-8)
            g = (g - gmin)/(gmax - gmin + 1.e-8)
            b = (b - bmin)/(bmax - bmin + 1.e-8)

            inew = img*1.0
            inew[:,:,0] = np.clip((r - rlo)/(rhi - rlo + 1.e-8), 0, 1)
            inew[:,:,1] = np.clip((g - glo)/(ghi - glo + 1.e-8), 0, 1)
            inew[:,:,2] = np.clip((b - blo)/(bhi - blo + 1.e-8), 0, 1)

            whitebg = conf.tricolor_bg.startswith('wh')

            if whitebg:
                inew = conf.tricolor_white_bg(inew)

            if self.conf.style == 'image':
                conf.image.set_data(inew)
                conf.image.set_interpolation(conf.interp)


        try:
            self.scalebar_rect.remove()
        except:
            pass
        try:
            self.scalebar_text.remove()
        except:
            pass

        if conf.scalebar_show:
            ystep, xstep = conf.scalebar_pixelsize
            if xstep is None or ystep is None:
                ystep, xstep = 1, 1
                if conf.xdata is not None:
                    xstep = abs(np.diff(conf.xdata).mean())
                if conf.ydata is not None:
                    ystep = abs(np.diff(conf.ydata).mean())
                self.scalebar_pixelsize = ystep, xstep
            y, x = conf.scalebar_pos
            y, x = int(y), int(x)
            h, w = conf.scalebar_size
            h, w = int(h), int(w/xstep)
            col =  conf.scalebar_color

            self.scalebar_rect = Rectangle((x, y), w, h,linewidth=1, edgecolor=col,
                                 facecolor=col)
            self.axes.add_patch(self.scalebar_rect)
            if conf.scalebar_showlabel:
                yoff, xoff = conf.scalebar_textoffset
                self.scalebar_text = self.axes.text(x+xoff, y+yoff, conf.scalebar_label,
                                                    color=col)
        self.canvas.draw()
        if callable(self.redraw_callback):
            self.redraw_callback(wid=self.GetId())


    def report_motion(self, event=None):
        if event.inaxes is None:
            return
        fmt = "X,Y= %g, %g"
        x, y  = event.xdata, event.ydata
        if len(self.fig.get_axes()) > 1:
            try:
                x, y = self.axes.transData.inverted().transform((x, y))
            except:
                pass
        if self.motion_sbar is None:
            try:
                self.motion_sbar = self.nstatusbar-1
            except AttributeError:
                self.motion_sbar = 1
        self.write_message(fmt % (x, y), panel=self.motion_sbar)
        conf = self.conf
        if conf.slice_onmotion:
            ix, iy = int(round(x)), int(round(y))
            if (ix >= 0 and ix < conf.data.shape[1] and
                iy >= 0 and iy < conf.data.shape[0]):
                conf.slice_xy = ix, iy
                self.update_slices()

    def report_leftdown(self,event=None):
        if event == None:
            return
        if event.xdata is None or event.ydata is None:
            return

        ix, iy = int(round(event.xdata)), int(round(event.ydata))

        conf = self.conf
        if (ix >= 0 and ix < conf.data.shape[1] and
            iy >= 0 and iy < conf.data.shape[0]):
            pos = ''
            if conf.xdata is not None:
                pos = ' %s=%.4g,' % (conf.xlab, conf.xdata[ix])
            if conf.ydata is not None:
                pos = '%s %s=%.4g,' % (pos, conf.ylab, conf.ydata[iy])
            dval = conf.data[iy, ix]
            if len(conf.data.shape) == 3:
                dval = "%.4g, %.4g, %.4g" % tuple(dval)
            else:
                dval = "%.4g" % dval
            msg = "Pixel [%i, %i], %s Intensity=%s " % (ix, iy, pos, dval)

            self.write_message(msg, panel=0)
            conf.slice_xy = ix, iy
            self.update_slices()
            if hasattr(self.cursor_callback , '__call__'):
                self.cursor_callback(x=event.xdata, y=event.ydata)

    def get_slice_plotframe(self):
        shown = False
        new_plotter = False
        if self.slice_plotframe is not None:
            try:
                self.slice_plotframe.Raise()
                shown = True
            except:
                pass
        if not shown:
            self.slice_plotframe = pf = PlotFrame(self)
            new_plotter = True
            try:
                xpos, ypos = self.parent.GetPosition()
                xsiz, ysiz = self.parent.GetSize()
                pf.SetPosition((xpos+xsiz+10, ypos))
            except:
                pass

        return new_plotter, self.slice_plotframe

    def update_slices(self):
        if self.conf.slices in ('None', None, 0):
            return
        x, y = -1, -1
        try:
            x, y = [int(a) for a in self.conf.slice_xy]
        except:
            return
        if len(self.conf.data.shape) == 3:
            ymax, xmax, _nc = self.conf.data.shape
        elif len(self.conf.data.shape) == 2:
            ymax, xmax = self.conf.data.shape
            _nc = 0
        else:
            return
        if x < 0 or y < 0 or x > xmax or y > ymax:
            return

        wid = int(self.conf.slice_width)
        new_plotter, pf = self.get_slice_plotframe()

        popts = {'ylabel': 'Intensity', 'linewidth': 3}

        if self.conf.slices.lower() == 'x':
            y1 = int(y - wid/2. + 1)
            y2 = int(y + wid/2.) + 1
            if y1 < 0: y1 = 0
            if y2 > ymax: y2 = ymax
            _x = self.conf.xdata
            if _x is None:
                _x = np.arange(self.conf.data.shape[1])
            _y = self.conf.data[y1:y2].sum(axis=0)
            popts['xlabel'] = 'X'
            popts['title'] = 'X Slice: Y=%d:%d' % (y1, y2)
            if y2 == y1+1:
                popts['title'] = 'X Slice: Y=%d' % y1

        else:
            x1 = int(x - wid/2.0 + 1)
            x2 = int(x + wid/2.0) + 1
            if x1 < 0: x1 = 0
            if x2 > xmax: x2 = xmax
            _x = self.conf.ydata
            if _x is None:
                _x = np.arange(self.conf.data.shape[0])
            _y = self.conf.data[:,x1:x2].sum(axis=1)
            popts['xlabel'] = 'Y'
            popts['title'] = 'Y Slice: X=%d:%d' % (x1, x2)
            if x2 == x1+1:
                popts['title'] = 'Y Slice: X=%d' % x1

        if new_plotter:
            if len(_y.shape) == 2 and _y.shape[1] == 3:
                pf.plot(_x,  _y[:, 0], color=RGB_COLORS[0], delay_draw=True, **popts)
                pf.oplot(_x, _y[:, 1], color=RGB_COLORS[1], delay_draw=True, **popts)
                pf.oplot(_x, _y[:, 2], color=RGB_COLORS[2], **popts)
            else:
                pf.plot(_x, _y, **popts)
        else:
            pf.panel.set_title(popts['title'], delay_draw=True)
            pf.panel.set_xlabel(popts['xlabel'], delay_draw=True)
            if len(_y.shape) == 2 and _y.shape[1] == 3:
                pf.update_line(0, _x,  _y[:, 0], update_limits=True, draw=False)
                pf.update_line(1, _x,  _y[:, 1], update_limits=True, draw=False)
                pf.update_line(2, _x,  _y[:, 2], update_limits=True, draw=True)
            else:
                pf.update_line(0, _x, _y, update_limits=True, draw=True)


        pf.Show()
        self.SetFocus()
        try:
            self.parent.Raise()
        except:
            pass
