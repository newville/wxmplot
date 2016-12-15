#!/usr/bin/python
##
## Image Matrix Frame:  2 correlated images in a 2x2 grid:
#
#     +-------------+--------------+
#     |             |              |
#     |   mage1     |  image 1+2   |
#     |             |              |
#     +-------------+--------------+
#     |             |              |
#     | correlation |   image2     |
#     | plot        |              |
#     +-------------+--------------+
##

import wx
import numpy as np
import matplotlib

from functools import partial

from .baseframe  import BaseFrame
from .plotpanel  import PlotPanel
from .imagepanel import ImagePanel
from .imageframe import ColorMapPanel
from .colors import rgb2hex
from .utils import LabelEntry, MenuItem, pack


class ImageMatrixFrame(BaseFrame):
    """
    wx.Frame, with 3 ImagePanels and correlation plot for 2 map arrays
    """
    def __init__(self, parent=None, size=(900,600),
                 subtitles=None, **kws):

        self.sel_mask = None

        BaseFrame.__init__(self, parent=parent,
                           title  = 'Image Matrix', size=size, **kws)
        self.cmap_panels= {}
        self.subtitles = {}
        if subtitles is not None:
            self.subtitles = subtitles

        sbar = self.CreateStatusBar(2, wx.CAPTION)
        sfont = sbar.GetFont()
        sfont.SetWeight(wx.BOLD)
        sfont.SetPointSize(10)
        sbar.SetFont(sfont)

        self.SetStatusWidths([-2, -1])
        self.SetStatusText('', 0)

        self.optional_menus = []

        self.bgcol = rgb2hex(self.GetBackgroundColour()[:3])


        self.SetBackgroundColour('#F8F8F4')

        splitter  = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        splitter.SetMinimumPaneSize(200)

        conf_panel = wx.Panel(splitter)
        main_panel = wx.Panel(splitter)

        # main panel
        self.plot_panel = PlotPanel(main_panel, size=(400, 325))
        self.plot_panel.axesmargins = (15, 15, 15, 15)
        self.plot_panel.conf.set_axes_style(style='open')
        self.plot_panel.cursor_mode = 'lasso'
        self.plot_panel.plot_type = 'scatter'
        self.plot_panel.lass_callback = self.on_corplot_lasso

        img_opts = dict(size=(400, 300),
                        redraw_callback=self.on_imageredraw,
                        zoom_callback=self.on_imagezoom)
        self.img1_panel = ImagePanel(main_panel, **img_opts)
        self.img2_panel = ImagePanel(main_panel, **img_opts)
        self.dual_panel = ImagePanel(main_panel, **img_opts)

        self.imgpanels = [self.img1_panel,
                          self.img2_panel,
                          self.dual_panel]

        lsty = wx.ALIGN_LEFT|wx.LEFT|wx.TOP|wx.EXPAND

        ir = 0
        self.wids = {}
        cmap_colors = ('blue', 'red', 'green', 'magenta', 'cyan', 'yellow')
        self.cmap_panels = [None, None]
        csizer = wx.BoxSizer(wx.VERTICAL)
        for i, imgpanel in enumerate((self.img1_panel, self.img2_panel)):
            self.cmap_panels[i] =  ColorMapPanel(conf_panel, imgpanel,
                                                 title='Map %i: ' % (i+1),
                                                 color=0,
                                                 default=cmap_colors[i],
                                                 colormap_list=cmap_colors)

            csizer.Add(self.cmap_panels[i], 0, lsty, 2)
            csizer.Add(wx.StaticLine(conf_panel, size=(100, 2),
                                    style=wx.LI_HORIZONTAL), 0, lsty, 2)

        pack(conf_panel, csizer)


        for name, panel in (('corplot', self.plot_panel),
                            ('map1',    self.img1_panel),
                            ('map2',    self.img2_panel),
                            ('dual',    self.dual_panel)):

            panel.report_leftdown = partial(self.report_leftdown, name=name)
            panel.messenger = self.write_message

        sizer = wx.GridSizer(2, 2, 3, 3)
        lsty |= wx.GROW|wx.ALL|wx.EXPAND|wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL
        sizer.Add(self.img1_panel, 1, lsty, 5)
        sizer.Add(self.dual_panel, 1, lsty, 5)
        sizer.Add(self.plot_panel, 1, lsty, 5)
        sizer.Add(self.img2_panel, 1, lsty, 5)

        pack(main_panel, sizer)
        splitter.SplitVertically(conf_panel, main_panel, 1)

        self.BuildMenu()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(splitter, 1, wx.GROW|wx.ALL, 5)
        pack(self, sizer)

    def unzoom(self, event=None):
        self.update_scatterplot(self.map1, self.map2)
        for p in self.imgpanels:
            p.unzoom_all()
        self.plot_panel.unzoom_all()

    def save_figure(self, event=None):
        print(" Save Figure ??")


    def BuildMenu(self):
        # file menu
        mfile = wx.Menu()
        MenuItem(self, mfile, "&Save Image\tCtrl+S",
                 "Save Image of Plot (PNG, SVG, JPG)",
                 action=self.save_figure)

        MenuItem(self, mfile, "E&xit\tCtrl+Q", "Exit", self.onExit)

        # options menu
        mview =  wx.Menu()
        MenuItem(self, mview, "Zoom Out\tCtrl+Z",
                 "Zoom out to full data range",
                 self.unzoom)

        mbar = wx.MenuBar()
        mbar.Append(mfile, 'File')
        mbar.Append(mview, 'Options')

        self.SetMenuBar(mbar)
        self.Bind(wx.EVT_CLOSE,self.onExit)

    def report_leftdown(self, event=None, name=None):
        print("report leftdown, ", name, event)


    def on_corplot_lasso(self, data=None, selected=None, mask=None):
        self.sel_mask = mask
        try:
            self.sel_mask.shape = self.zoom_map1.shape
            self.update_dualimage()
        except:
            pass

    def on_imagezoom(self, event=None, wid=0, limits=None):
        if wid in [w.GetId() for w in self.imgpanels]:
            lims = [int(round(x)) for x in limits]
            for ipanel in self.imgpanels:
                ax = ipanel.fig.axes[0]
                axlims = {ax: lims}
                ipanel.conf.zoom_lims.append(axlims)
                ipanel.set_viewlimits()

        m1  = self.map1[lims[2]:lims[3], lims[0]:lims[1]]
        m2  = self.map2[lims[2]:lims[3], lims[0]:lims[1]]
        self.update_scatterplot(m1, m2)

    def on_imageredraw(self, event=None, wid=0):
        if wid in (self.img1_panel.GetId(), self.img2_panel.GetId()):
            self.update_dualimage()

    def display(self, map1, map2, title=None, x=None, y=None, xoff=None, yoff=None,
                subtitles=None, xrmfile=None, det=None):

        self.map1 = map1
        self.map2 = map2
        self.img1_panel.display(map1)
        self.img2_panel.display(map2)
        self.update_scatterplot(map1, map2)

        self.set_contrast_levels()
        self.update_dualimage()


    def update_scatterplot(self, x, y):
        self.zoom_map1 = x
        self.zoom_map2 = y
        _x = x.flatten()
        _y = y.flatten()
        xmax = max(_x) * 1.2
        xmin = min(_x) * 0.8
        ymax = max(_y) * 1.2
        ymin = min(_y) * 0.8
        self.plot_panel.clear()
        self.plot_panel.scatterplot(_x, _y,
                                    min=xmin, xmax=xmax,
                                    ymin=ymin, ymax=ymax,
                                    callback=self.on_corplot_lasso)

    def onEnhanceContrast(self, event=None):
        """change image contrast, using scikit-image exposure routines"""
        self.panel.conf.auto_contrast = event.IsChecked()
        self.set_contrast_levels()
        self.panel.redraw()

    def set_contrast_levels(self):
        """enhance contrast levels, or use full data range
        according to value of self.panel.conf.auto_contrast
        """
        for cmap_panel, img_panel in zip((self.cmap_panels[0], self.cmap_panels[1]),
                                         (self.img1_panel, self.img2_panel)):
            conf = img_panel.conf
            img  = img_panel.conf.data
            enhance = conf.auto_contrast
            clevel = conf.auto_contrast_level
            jmin = imin = img.min()
            jmax = imax = img.max()
            cmap_panel.imin_val.SetValue('%.4g' % imin)
            cmap_panel.imax_val.SetValue('%.4g' % imax)
            if enhance:
                jmin, jmax = np.percentile(img, [clevel, 100.0-clevel])

            conf.int_lo[0]  = imin
            conf.int_hi[0]  = imax
            conf.cmap_lo[0] = xlo = (jmin-imin)*conf.cmap_range/(imax-imin)
            conf.cmap_hi[0] = xhi = (jmax-imin)*conf.cmap_range/(imax-imin)

            cmap_panel.cmap_hi.SetValue(xhi)
            cmap_panel.cmap_lo.SetValue(xlo)
            cmap_panel.islider_range.SetLabel('Shown: [ %.4g :  %.4g ]' % (jmin, jmax))
            cmap_panel.redraw_cmap()
            img_panel.redraw()


    def update_dualimage(self):
        try:
            col1 = self.img1_panel.conf.cmap[0].name
            dat1 = self.zoom_map1
            conf = self.img1_panel.conf
            ilo1 = float(conf.int_lo[0])
            ihi1 = float(conf.int_hi[0])
            mlo1 = float(conf.cmap_lo[0])/(1.0*conf.cmap_range)
            mhi1 = float(conf.cmap_hi[0])/(1.0*conf.cmap_range)


            col2 = self.img2_panel.conf.cmap[0].name
            dat2 = self.zoom_map2
            conf = self.img2_panel.conf
            ilo2 = float(conf.int_lo[0])
            ihi2 = float(conf.int_hi[0])
            mlo2 = float(conf.cmap_lo[0])/(1.0*conf.cmap_range)
            mhi2 = float(conf.cmap_hi[0])/(1.0*conf.cmap_range)
            ihi2 = float(self.img2_panel.conf.int_hi[0])
        except:
            return

        dat1 = (dat1 - ilo1) / (ihi1 - ilo1 + 1.e-8)
        dat2 = (dat2 - ilo2) / (ihi2 - ilo2 + 1.e-8)

        dat1 = (dat1 - mlo1) / (mhi1 - mlo1 + 1.e-8)
        dat2 = (dat2 - mlo2) / (mhi2 - mlo2 + 1.e-8)

        mr, mg, mb =(1, 1, 1)
        for col in (col1, col2):
            if col.startswith('red'):
                mr = 0
            elif col.startswith('green'):
                mg = 0
            elif col.startswith('blue'):
                mb = 0
            elif col.startswith('cyan'):
                mg, mb = 0, 0
            elif col.startswith('yellow'):
                mr, mg  = 0, 0
            elif col.startswith('magenta'):
                mr, mb = 0, 0
        maskcolor = {(1, 0, 0): 'red',
                     (0, 1, 0): 'green',
                     (0, 0, 1): 'blue',
                     (0, 0, 0): 'white',
                     (0, 1, 1): 'cyan',
                     (1, 1, 0): 'yellow',
                     (0, 1, 1): 'cyan',
                     (1, 0, 1): 'magenta'}.get((mr, mg, mb), 'white')

        ctabs = [col1, col2]
        dimgs = [dat1, dat2]
        if self.sel_mask is not None:
            ctabs.append(maskcolor)
            dimgs.append(self.sel_mask)

        w, h = dat1.shape
        img = np.zeros(3*w*h).reshape(w, h, 3)

        for col, dimg in zip(ctabs, dimgs):
            if col.endswith('_r'):
                col = col[:-2]
                dimg = 1.0 - dimg
            if col == 'red':
                img[:, :, 0] += dimg
            elif col == 'green':
                img[:, :, 1] += dimg
            elif col == 'blue':
                img[:, :, 2] += dimg
            elif col == 'cyan':
                img[:, :, 1] += dimg/2.
                img[:, :, 2] += dimg/2.
            elif col == 'yellow':
                img[:, :, 0] += dimg/2.
                img[:, :, 1] += dimg/2.
            elif col == 'magenta':
                img[:, :, 0] += dimg/2.
                img[:, :, 2] += dimg/2.
            elif col == 'white':
                img[:, :, 0] += dimg
                img[:, :, 1] += dimg
                img[:, :, 2] += dimg

        self.dual_panel.display(img)
        self.sel_mask = None
