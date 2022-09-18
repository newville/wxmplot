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
from functools import partial

import wx
from wxutils import get_cwd
import numpy as np
import matplotlib

from PIL import Image

from .baseframe  import BaseFrame
from .plotpanel  import PlotPanel
from .imagepanel import ImagePanel
from .imageframe import ColorMapPanel, InterpPanel, ContrastPanel
from .imageconf import ColorMap_List, Interp_List
from .colors import rgb2hex
from .utils import MenuItem, pack, fix_filename, gformat

COLORMAPS = ('blue', 'red', 'green', 'yellow', 'cyan', 'magenta')
CM_DEFS = ('blue', 'yellow')

###, 'Reds', 'Greens', 'Blues')

def color_complements(color):
    colors = list(COLORMAPS)
    colors.remove(color)
    return colors

def image2wxbitmap(img):
    "PIL image 2 wx bitmap"
    wximg = wx.Image(*img.size)
    wximg.SetData(img.tobytes())
    return wximg.ConvertToBitmap()

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
        splitter  = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        splitter.SetMinimumPaneSize(225)

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


        lsty = wx.LEFT|wx.TOP|wx.EXPAND

        ir = 0
        self.wids = {}
        self.cmap_panels = [None, None]
        csizer = wx.BoxSizer(wx.VERTICAL)
        for i, imgpanel in enumerate((self.img1_panel, self.img2_panel)):
            self.cmap_panels[i] =  ColorMapPanel(conf_panel, imgpanel,
                                                 title='Map %i: ' % (i+1),
                                                 color=0,
                                                 default=CM_DEFS[i],
                                                 colormap_list=COLORMAPS,
                                                 cmap_callback=partial(self.onColorMap, index=i))

            csizer.Add(self.cmap_panels[i], 0, lsty, 2)
            csizer.Add(wx.StaticLine(conf_panel, size=(200, 2),
                                    style=wx.LI_HORIZONTAL), 0, lsty, 2)


        self.interp_panel = InterpPanel(self.config_panel, self.img1_panel, default=0,
                                        callback=self.onInterp)
        self.contrast_panel = ContrastPanel(self.config_panel,
                                            callback=self.set_contrast_levels)

        csizer.Add(self.interp_panel, 0, lsty, 2)
        csizer.Add(self.contrast_panel, 0, lsty, 2)

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
        lsty |= wx.GROW|wx.ALL|wx.EXPAND
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


        ic1 = (COLORMAPS.index(name) + 3) % 6
        if COLORMAPS[ic1] in colors:
            c1 = COLORMAPS[ic1]
        if c1  not in colors:
            c1 = colors[0]
        opanel.cmap_choice.SetStringSelection(c1)
        opanel.set_colormap(name=c1)
        opanel.imgpanel.redraw()

    def unzoom_all(self, event=None):
        self.unzoom(event=event)

    def unzoom(self, event=None):
        self.xzoom = slice(0, self.map1.shape[1]+1)
        self.yzoom = slice(0, self.map1.shape[0]+1)

        self.update_scatterplot(self.map1, self.map2)
        self.plot_panel.unzoom_all()
        for p in self.imgpanels:
            p.unzoom_all()

    def BuildMenu(self):
        # file menu
        mfile = self.Build_FileMenu()

        mview =  wx.Menu()

        MenuItem(self, mview, "Zoom Out\tCtrl+Z",
                 "Zoom out to full data range",
                 self.unzoom)

        MenuItem(self, mview, 'Enhance Contrast Cycle\tCtrl++',
                 'Cycle Through Contrast Choices',
                 self.cycle_contrast)
        MenuItem(self, mview, 'Reduce Contrast Cycle\tCtrl+-',
                 'Cycle Through Contrast Choices',
                 partial(self.cycle_contrast, dir='back'))

        mbar = wx.MenuBar()
        mbar.Append(mfile, 'File')
        mbar.Append(mview, 'Image')

        self.SetMenuBar(mbar)
        self.Bind(wx.EVT_CLOSE,self.onExit)


    def save_figure(self, event=None):
        file_choices = "PNG (*.png)|*.png|SVG (*.svg)|*.svg|PDF (*.pdf)|*.pdf"
        ofile = "%s.png" % self.title
        dlg = wx.FileDialog(self, message='Save Figure as...',
                            defaultDir=get_cwd(),
                            defaultFile=ofile,
                            wildcard=file_choices,
                            style=wx.FD_SAVE|wx.FD_CHANGE_DIR)

        if dlg.ShowModal() != wx.ID_OK:
            return

        path = dlg.GetPath()
        img = self.make_composite_image()
        img.save(path)
        self.write_message('Saved plot to %s' % path)

    def make_composite_image(self):
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

        img = Image.new('RGB', (2*w+2, 2*h+2))
        img.paste(img1, (0,   0))
        img.paste(img2, (1+w, 1+h))
        img.paste(dual, (1+w, 0))
        img.paste(plot, (0,   1+h))
        return img

    def Copy_to_Clipboard(self, event=None):
        img = self.make_composite_image()
        bmp_obj = wx.BitmapDataObject()
        bmp_obj.SetBitmap(image2wxbitmap(img))

        if not wx.TheClipboard.IsOpened():
            open_success = wx.TheClipboard.Open()
            if open_success:
                wx.TheClipboard.SetData(bmp_obj)
                wx.TheClipboard.Close()
                wx.TheClipboard.Flush()

    def PrintSetup(self, event=None):
        dlg = wx.MessageDialog(self, "Printing not Available",
                               "Save Image or Copy to Clipboard",
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def PrintPreview(self, event=None):
        dlg = wx.MessageDialog(self, "Printing not Available",
                               "Save Image or Copy to Clipboard",
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def Print(self, event=None):
        dlg = wx.MessageDialog(self, "Printing not Available",
                               "Save Image or Copy to Clipboard",
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def onInterp(self, event=None, name=None):
        if name not in Interp_List:
            name = Interp_List[0]
        for ipanel in self.imgpanels:
            ipanel.conf.interp = name
            ipanel.redraw()

    def onExit(self, event=None):
        self.dualimage_timer.Stop()
        self.Destroy()

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
                pos = ' %s=%.4g,' % (self.xlabel, self.xdata[ix])
            if self.ydata is not None:
                pos = '%s %s=%.4g,' % (pos, self.ylabel, self.ydata[iy])

            d1, d2 = (self.map1[iy, ix], self.map2[iy, ix])
            msg = "Pixel [%i, %i],%s %s=%.4g, %s=%.4g" % (ix, iy, pos,
                                                          self.name1, d1,
                                                          self.name2, d2)
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

    def display(self, map1, map2, title=None, name1='Map1', name2='Map2',
                xlabel='x', ylabel='y', x=None, y=None):
        self.map1 = map1
        self.map2 = map2
        self.name1 = name1
        self.name2 = name2
        self.xdata = x
        self.ydata = y
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.xzoom = slice(0, map1.shape[1]+1)
        self.yzoom = slice(0, map1.shape[0]+1)

        self.img1_panel.display(map1, x=x, y=y)
        self.img2_panel.display(map2, x=x, y=y)

        self.cmap_panels[0].title.SetLabel(name1)
        self.cmap_panels[1].title.SetLabel(name2)
        self.update_scatterplot(map1, map2)

        self.set_contrast_levels()
        self.dualimage_needs_update = True
        self.panel = self.img1_panel

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
                                    xlabel=self.name1, ylabel=self.name2,
                                    callback=self.on_corplot_lasso)

    def cycle_contrast(self, event=None, dir='fore'):
        if dir.startswith('f'):
            self.contrast_panel.advance()
        else:
            self.contrast_panel.retreat()

    def set_contrast_levels(self, contrast_level=0):
        """enhance contrast levels, or use full data range
        according to value of self.panel.conf.contrast_level
        """
        for cmap_panel, img_panel in zip((self.cmap_panels[0], self.cmap_panels[1]),
                                         (self.img1_panel, self.img2_panel)):
            conf = img_panel.conf
            img  = img_panel.conf.data
            if contrast_level is None:
                contrast_level = 0
            conf.contrast_level = contrast_level
            clevels = [contrast_level, 100.0-contrast_level]

            jmin = imin = img.min()
            jmax = imax = img.max()
            cmap_panel.imin_val.SetValue('%.4g' % imin)
            cmap_panel.imax_val.SetValue('%.4g' % imax)
            jmin, jmax = np.percentile(img, clevels)

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

        ctabs = [] # [col1, col2]
        dimgs = [] # [dat1, dat2]

        for panel, dmap in zip((self.img1_panel, self.img2_panel),
                               (self.map1, self.map2)):
            try:
                col = panel.conf.cmap[0].name
                dat = dmap
                conf = panel.conf
                ilo = float(conf.int_lo[0])
                ihi = float(conf.int_hi[0])
                mlo = float(conf.cmap_lo[0])/(1.0*conf.cmap_range)
                mhi = float(conf.cmap_hi[0])/(1.0*conf.cmap_range)

                dat = (dat - ilo) / (ihi - ilo)
                dat = (dat - mlo) / (mhi - mlo)
                dat[np.where(dat<0)] = 0.0
                dat[np.where(dat>1)] = 1.0
                ctabs.append(col)
                dimgs.append(dat)
            except:
                return

        mr, mg, mb =(1, 1, 1)
        for col in ctabs:
            if col.startswith('red'):
                mr = 0
            elif col.startswith('green'):
                mg = 0
            elif col.startswith('blue'):
                mb = 0
            elif col.startswith('cyan'):
                mb = mg = 0
            elif col.startswith('yellow'):
                mr = mg = 0
            elif col.startswith('magenta'):
                mr = mb = 0

        maskcolor = {(1, 0, 0): 'red',
                     (0, 1, 0): 'green',
                     (0, 0, 1): 'blue',
                     (0, 0, 0): 'white',
                     (0, 1, 1): 'cyan',
                     (1, 1, 0): 'yellow',
                     (0, 1, 1): 'cyan',
                     (1, 0, 1): 'magenta'}.get((mr, mg, mb), 'white')

        if self.sel_mask is not None:
            ctabs.append(maskcolor)
            dimgs.append(self.sel_mask)

        w, h = dimgs[0].shape
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
            dp.conf.zoom_lims.append({dp.axes:list(im1_zoom.values())[0]})
            dp.set_viewlimits()
            if self.sel_mask is not None:
                dp.conf.image = dp.axes.imshow(img, cmap=dp.conf.cmap[0],
                                               interpolation=dp.conf.interp)
            dp.canvas.draw()
        else:
            self.dual_panel.display(img)
        self.sel_mask = None


    def ExportTextFile(self, fname, title='unknown map'):
        buff = ["# Correlation Map Data for %s" % title,
                "#-------------------------------------"]

        labels = ['  Y', '  X', self.name1, self.name2]
        labels = [(' '*(11-len(l)) + l + ' ') for l in labels]

        buff.append("#%s" % ('  '.join(labels)))

        ny, nx = self.map1.shape
        xdat = np.arange(nx)
        ydat = np.arange(ny)
        if self.xdata is not None:
            xdat = self.xdata
        if self.ydata is not None:
            ydat = self.ydata

        for iy in range(ny):
            for ix in range(nx):
                d = [ydat[iy], xdat[ix], self.map1[iy, ix], self.map2[iy, ix]]
                buff.append("  ".join([gformat(a, 12) for a in d]))

        fout = open(fname, 'w')
        fout.write("%s\n" % "\n".join(buff))
        fout.close()
