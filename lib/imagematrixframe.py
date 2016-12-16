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

import os
import wx
import numpy as np
import matplotlib

from functools import partial

HAS_IMAGE = False
try:
    from PIL import Image
    HAS_IMAGE = True
except ImportError:
    pass

from .baseframe  import BaseFrame
from .plotpanel  import PlotPanel
from .imagepanel import ImagePanel
from .imageframe import ColorMapPanel, AutoContrastDialog
from .colors import rgb2hex
from .utils import LabelEntry, MenuItem, pack

COLORMAPS = ('blue', 'red', 'green', 'magenta', 'cyan', 'yellow')

def color_complements(color):
    colors = list(COLORMAPS)
    colors.remove(color)
    return colors

class ImageMatrixFrame(BaseFrame):
    """
    wx.Frame, with 3 ImagePanels and correlation plot for 2 map arrays
    """
    def __init__(self, parent=None, size=(900,600),
                 cursor_callback=None, title='Image Matrix', **kws):

        self.sel_mask = None
        self.xdata = None
        self.ydata = None
        self.cursor_callback = cursor_callback
        BaseFrame.__init__(self, parent=parent,
                           title=title, size=size, **kws)
        self.title = title
        self.cmap_panels= {}
        sbar = self.CreateStatusBar(2, wx.CAPTION)
        sfont = sbar.GetFont()
        sfont.SetWeight(wx.BOLD)
        sfont.SetPointSize(10)
        sbar.SetFont(sfont)

        self.SetStatusWidths([-2, -1])
        self.SetStatusText('', 0)

        self.bgcol = rgb2hex(self.GetBackgroundColour()[:3])

        self.SetBackgroundColour('#F8F8F4')

        splitter  = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        splitter.SetMinimumPaneSize(200)

        conf_panel = wx.Panel(splitter)
        main_panel = wx.Panel(splitter)

        self.config_panel = conf_panel

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
        self.cmap_panels = [None, None]
        csizer = wx.BoxSizer(wx.VERTICAL)
        for i, imgpanel in enumerate((self.img1_panel, self.img2_panel)):
            self.cmap_panels[i] =  ColorMapPanel(conf_panel, imgpanel,
                                                 title='Map %i: ' % (i+1),
                                                 color=0,
                                                 default=COLORMAPS[i],
                                                 colormap_list=COLORMAPS,
                                                 cmap_callback=partial(self.onColorMap, index=i))

            csizer.Add(self.cmap_panels[i], 0, lsty, 2)
            csizer.Add(wx.StaticLine(conf_panel, size=(100, 2),
                                    style=wx.LI_HORIZONTAL), 0, lsty, 2)

        cust = self.CustomConfig(conf_panel)
        if cust is not None:
            sizer.Add(cust, 0, lsty, 1)
        pack(conf_panel, csizer)

        for name, panel in (('corplot', self.plot_panel),
                            ('map1',    self.img1_panel),
                            ('map2',    self.img2_panel),
                            ('dual',    self.dual_panel)):

            panel.report_leftdown = partial(self.report_leftdown, name=name)
            panel.messenger = self.write_message

        sizer = wx.GridSizer(2, 2, 2, 2)
        lsty |= wx.GROW|wx.ALL|wx.EXPAND|wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL
        sizer.Add(self.img1_panel, 1, lsty, 2)
        sizer.Add(self.dual_panel, 1, lsty, 2)
        sizer.Add(self.plot_panel, 1, lsty, 2)
        sizer.Add(self.img2_panel, 1, lsty, 2)

        pack(main_panel, sizer)
        splitter.SplitVertically(conf_panel, main_panel, 1)

        self.BuildMenu()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(splitter, 1, wx.GROW|wx.ALL, 5)
        pack(self, sizer)

        self.dualimage_needs_update = False
        self.dualimage_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onDualImageTimer, self.dualimage_timer)
        self.dualimage_timer.Start(150)


    def CustomConfig(self, parent):
        """
        override to add custom config panel items to bottom of config panel
        """
        pass

    def onColorMap(self, name=None, index=None):
        colors = color_complements(name)
        opanel = self.cmap_panels[0]
        if index == 0:
            opanel = self.cmap_panels[1]

        c1 = opanel.cmap_choice.GetStringSelection()
        opanel.cmap_choice.Clear()
        for c in colors:
            opanel.cmap_choice.Append(c)
        if c1 in colors:
            opanel.cmap_choice.SetStringSelection(c1)
        else:
            opanel.cmap_choice.SetStringSelection(colors[0])
            opanel.set_colormap(name=colors[0])
            opanel.imgpanel.redraw()


    def unzoom(self, event=None):
        self.xzoom = slice(0, self.map1.shape[1]+1)
        self.yzoom = slice(0, self.map1.shape[0]+1)

        self.update_scatterplot(self.map1, self.map2)
        self.plot_panel.unzoom_all()
        for p in self.imgpanels:
            p.unzoom_all()

    def save_figure(self, event=None):
        if not HAS_IMAGE:
            return

        file_choices = "PNG (*.png)|*.png|SVG (*.svg)|*.svg|PDF (*.pdf)|*.pdf"
        ofile = self.title + '.png'
        dlg = wx.FileDialog(self, message='Save Figure as...',
                            defaultDir = os.getcwd(),
                            defaultFile=ofile,
                            wildcard=file_choices,
                            style=wx.FD_SAVE|wx.FD_CHANGE_DIR)

        if dlg.ShowModal() != wx.ID_OK:
            return

        h, w = 0, 0
        def GetImage(panel):
            wximg = panel.canvas.bitmap.ConvertToImage()
            w, h = wximg.GetWidth(), wximg.GetHeight()
            img = Image.new( 'RGB', (w, h))
            img.frombytes(bytes(wximg.GetData()))
            return img, w, h

        img1, w1, h1 = GetImage(self.img1_panel)
        img2, w2, h2 = GetImage(self.img2_panel)
        dual, w3, h3 = GetImage(self.dual_panel)
        plot, w4, h4 = GetImage(self.plot_panel)

        w = (w1 + w2 + w3 + w4 ) / 4
        h = (h1 + h2 + h3 + h4 ) / 4

        out = Image.new('RGB', (2*w+2, 2*h+2))
        out.paste(img1, (0,   0))
        out.paste(img2, (1+w, 1+h))
        out.paste(dual, (1+w, 0))
        out.paste(plot, (0,   1+h))

        path = dlg.GetPath()
        out.save(path)
        self.write_message('Saved plot to %s' % path)



    def BuildMenu(self):
        # file menu
        mfile = wx.Menu()
        MenuItem(self, mfile, "&Save Image\tCtrl+S",
                 "Save Image of Plot (PNG, SVG, JPG)",
                 action=self.save_figure)

        MenuItem(self, mfile, "E&xit\tCtrl+Q", "Exit", self.onExit)

        mview =  wx.Menu()
        MenuItem(self, mview, "Zoom Out\tCtrl+Z",
                 "Zoom out to full data range",
                 self.unzoom)
        MenuItem(self, mview, 'Toggle Contrast Enhancement\tCtrl+E',
                 'Toggle contrast between auto-scale and full-scale',
                 self.onEnhanceContrast, kind=wx.ITEM_CHECK)

        MenuItem(self, mview, 'Set Auto-Contrast Level',
                 'Set auto-contrast scale',
                 self.onContrastConfig)

        mbar = wx.MenuBar()
        mbar.Append(mfile, 'File')
        mbar.Append(mview, 'Options')

        self.SetMenuBar(mbar)
        self.Bind(wx.EVT_CLOSE,self.onExit)

    def onEnhanceContrast(self, event=None):
        """change image contrast, using scikit-image exposure routines"""
        for ipanel in self.imgpanels:
            ipanel.conf.auto_contrast = event.IsChecked()
            ipanel.redraw()
        self.set_contrast_levels()


    def onContrastConfig(self, event=None):
        dlg = AutoContrastDialog(parent=self, conf=self.img1_panel.conf)
        dlg.CenterOnScreen()
        val = dlg.ShowModal()
        if val == wx.ID_OK:
            for ipanel in self.imgpanels:
                ipanel.conf.auto_contrast_level = self.img1_panel.conf.auto_contrast_level
        dlg.Destroy()
        self.set_contrast_levels()

    def report_leftdown(self,event=None, name=''):
        if event is None:
            return
        if event.xdata is None or event.ydata is None:
            return
        ix, iy = int(round(event.xdata)), int(round(event.ydata))
        if (ix >= 0 and ix < self.map1.shape[1] and
            iy >= 0 and iy < self.map1.shape[0]):
            pos = ''
            if self.xdata is not None:
                pos = ' %s=%.4g,' % (self.xlab, self.xdata[ix])
            if self.ydata is not None:
                pos = '%s %s=%.4g,' % (pos, self.ylab, self.ydata[iy])

            d1, d2 = (self.map1[iy, ix], self.map2[iy, ix])
            msg = "Pixel [%i, %i],%s Map1=%.4g, Map2=%.4g" % (ix, iy, pos, d1, d2)
            self.write_message(msg, panel=0)

            if callable(self.cursor_callback):
                self.cursor_callback(x=event.xdata, y=event.ydata)

    def on_corplot_lasso(self, data=None, selected=None, mask=None):
        self.sel_mask = mask
        try:
            mask.shape = self.zoom_map1.shape
            self.sel_mask = 0 * self.map1
            self.sel_mask[self.yzoom, self.xzoom] = mask
            self.dualimage_needs_update = True
        except:
            pass

    def on_imagezoom(self, event=None, wid=0, limits=None):
        if wid in [w.GetId() for w in self.imgpanels]:
            lims = [int(x) for x in limits]
            for ipanel in self.imgpanels:
                ax = ipanel.fig.axes[0]
                axlims = {ax: lims}
                ipanel.conf.zoom_lims.append(axlims)
                ipanel.set_viewlimits()

        m1 = self.map1[lims[2]:lims[3], lims[0]:lims[1]]
        m2 = self.map2[lims[2]:lims[3], lims[0]:lims[1]]
        self.xzoom = slice(lims[0], lims[1])
        self.yzoom = slice(lims[2], lims[3])
        self.update_scatterplot(m1, m2)

    def on_imageredraw(self, event=None, wid=0):
        if wid in (self.img1_panel.GetId(), self.img2_panel.GetId()):
            self.dualimage_needs_update = True

    def display(self, map1, map2, title=None, xlabel=None, ylabel=None,
                x=None, y=None, xoff=None, yoff=None, **kws):
        self.map1 = map1
        self.map2 = map2
        self.xdata = x
        self.ydata = y
        self.xzoom = slice(0, map1.shape[1]+1)
        self.yzoom = slice(0, map1.shape[0]+1)

        self.xlabel = xlabel
        self.ylabel = ylabel
        self.img1_panel.display(map1, x=x, y=y)
        self.img2_panel.display(map2, x=x, y=y)

        self.cmap_panels[0].title.SetLabel(xlabel)
        self.cmap_panels[1].title.SetLabel(ylabel)
        self.update_scatterplot(map1, map2)

        self.set_contrast_levels()
        self.dualimage_needs_update = True

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
        self.plot_panel.conf.labelfont.set_size(7)
        self.plot_panel.scatterplot(_x, _y, size=3,
                                    min=xmin, xmax=xmax,
                                    ymin=ymin, ymax=ymax,
                                    xlabel=self.xlabel, ylabel=self.ylabel,
                                    callback=self.on_corplot_lasso)

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

    def onDualImageTimer(self, event=None):
        if not self.dualimage_needs_update:
            return

        self.dualimage_needs_update = False
        try:
            col1 = self.img1_panel.conf.cmap[0].name
            dat1 = self.map1
            conf = self.img1_panel.conf
            ilo1 = float(conf.int_lo[0])
            ihi1 = float(conf.int_hi[0])
            mlo1 = float(conf.cmap_lo[0])/(1.0*conf.cmap_range)
            mhi1 = float(conf.cmap_hi[0])/(1.0*conf.cmap_range)

            col2 = self.img2_panel.conf.cmap[0].name
            dat2 = self.map2
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

        dp = self.dual_panel
        try:
            dp.conf.image.set_data(img)
        except:
            dp.conf.data = img
        im1_zoom = self.img1_panel.conf.zoom_lims[-1]
        if im1_zoom is not None:
            dp.conf.zoom_lims.append({dp.axes:im1_zoom.values()[0]})
            dp.set_viewlimits()
            if self.sel_mask is not None:
                dp.conf.image = dp.axes.imshow(img, cmap=dp.conf.cmap[0],
                                               interpolation=dp.conf.interp)
            dp.canvas.draw()
        else:
            self.dual_panel.display(img)
        self.sel_mask = None
