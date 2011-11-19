#!/usr/bin/python
"""
 mplot ImageFrame: a wx.Frame for image display, using matplotlib
"""

import os
import wx
import numpy
import matplotlib.cm as colormap
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg

from imagepanel import ImagePanel
from baseframe import BaseFrame
from colors import rgb2hex
ColorMap_List = []

for cm in ('gray', 'coolwarm', 'cool', 'Spectral', 'gist_earth',
           'gist_yarg', 'gist_rainbow', 'gist_heat', 'gist_stern', 'ocean',
           'copper', 'jet', 'hsv', 'Reds', 'Greens', 'Blues', 'hot',
           'cool', 'copper', 'spring', 'summer', 'autumn', 'winter', 'PiYG', 'PRGn',
           'Spectral', 'Accent', 'YlGn', 'YlGnBu', 'RdBu', 'RdPu', 'RdYlBu', 'RdYlGn'):
    if hasattr(colormap, cm):
        ColorMap_List.append(cm)

Interp_List = ('nearest', 'bilinear', 'bicubic', 'spline16', 'spline36',
               'hanning', 'hamming', 'hermite', 'kaiser', 'quadric',
               'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc',
               'lanczos')

class ImageFrame(BaseFrame):
    """
    MatPlotlib Image Display ons a wx.Frame, using ImagePanel
    """
    def __init__(self, parent=None, size=(550, 450),
                 config_on_frame=True, **kws):

        self.config_on_frame = config_on_frame
        BaseFrame.__init__(self, parent=parent,
                           title  = 'Image Display Frame',
                           size=size, **kws)
        self.BuildFrame()

    def display(self, img, **kw):
        """plot after clearing current plot """
        self.panel.display(img, **kw)

    def BuildCustomMenus(self):
        "build menus"
        mids = self.menuIDs
        mids.SAVE_CMAP = wx.NewId()
        m = wx.Menu()
        m.Append(mids.UNZOOM, "Zoom Out\tCtrl+Z",
                 "Zoom out to full data range")
        m.AppendSeparator()
        m.Append(mids.SAVE_CMAP, "Save Colormap Image")

        self.user_menus  = [('&Options', m)]

    def BuildFrame(self):
        sbar = self.CreateStatusBar(2, wx.CAPTION|wx.THICK_FRAME)
        sfont = sbar.GetFont()
        sfont.SetWeight(wx.BOLD)
        sfont.SetPointSize(10)
        sbar.SetFont(sfont)

        self.SetStatusWidths([-3, -1])
        self.SetStatusText('', 0)

        self.BuildCustomMenus()
        self.BuildMenu()
        mainsizer = wx.BoxSizer(wx.HORIZONTAL)

        self.bgcol = rgb2hex(self.GetBackgroundColour()[:3])
        self.panel = ImagePanel(self,
                                show_config_popup=(not self.config_on_frame))

        self.panel.messenger = self.write_message

        if self.config_on_frame:
            lpanel = self.BuildConfigPanel()
            mainsizer.Add(lpanel, 0,
                          wx.LEFT|wx.ALIGN_LEFT|wx.TOP|wx.ALIGN_TOP|wx.EXPAND)

        self.panel.fig.set_facecolor(self.bgcol)

        mainsizer.Add(self.panel, 1, wx.EXPAND)

        self.BindMenuToPanel()
        mids = self.menuIDs
        self.Bind(wx.EVT_MENU, self.onCMapSave, id=mids.SAVE_CMAP)

        self.SetAutoLayout(True)
        self.SetSizer(mainsizer)
        self.Fit()

    def BuildConfigPanel(self):
        """config panel for left-hand-side of frame"""
        conf = self.panel.conf
        lpanel = wx.Panel(self)
        lsizer = wx.GridBagSizer(7, 4)

        labstyle = wx.ALIGN_LEFT|wx.LEFT|wx.TOP|wx.EXPAND

        interp_choice =  wx.Choice(lpanel, choices=Interp_List)
        interp_choice.Bind(wx.EVT_CHOICE,  self.onInterp)

        interp_choice.SetStringSelection(conf.interp)
        s = wx.StaticText(lpanel, label=' Smoothing:')
        s.SetForegroundColour('Blue')
        lsizer.Add(s,               (0, 0), (1, 3), labstyle, 5)
        lsizer.Add(interp_choice,   (1, 0), (1, 3), labstyle, 2)

        s = wx.StaticText(lpanel, label=' Color Table:')
        s.SetForegroundColour('Blue')
        lsizer.Add(s, (2, 0), (1, 3), labstyle, 5)

        cmap_choice =  wx.Choice(lpanel, choices=ColorMap_List)
        cmap_choice.Bind(wx.EVT_CHOICE,  self.onCMap)
        cmap_name = conf.cmap.name
        if cmap_name.endswith('_r'):
            cmap_name = cmap_name[:-2]
        cmap_choice.SetStringSelection(cmap_name)

        cmap_toggle = wx.CheckBox(lpanel, label='Reverse Table',
                                  size=(140, -1))
        cmap_toggle.Bind(wx.EVT_CHECKBOX, self.onCMapReverse)
        cmap_toggle.SetValue(conf.cmap_reverse)

        cmax = conf.cmap_range
        self.cmap_data   = numpy.outer(numpy.linspace(0, 1, cmax),
                                       numpy.ones(cmax/8))

        self.cmap_fig   = Figure((0.350, 1.75), dpi=100)
        self.cmap_axes  = self.cmap_fig.add_axes([0, 0, 1, 1])
        self.cmap_axes.set_axis_off()

        self.cmap_canvas = FigureCanvasWxAgg(lpanel, -1,
                                             figure=self.cmap_fig)

        self.bgcol = rgb2hex(lpanel.GetBackgroundColour()[:3])
        self.cmap_fig.set_facecolor(self.bgcol)

        self.cmap_image = self.cmap_axes.imshow(self.cmap_data,
                                                cmap=conf.cmap,
                                                interpolation='bilinear')

        self.cmap_axes.set_ylim((0, cmax), emit=True)

        self.cmap_lo_val = wx.Slider(lpanel, -1, conf.cmap_lo, 0,
                                     conf.cmap_range, size=(-1, 200),
                                     style=wx.SL_INVERSE|wx.SL_VERTICAL)

        self.cmap_hi_val = wx.Slider(lpanel, -1, conf.cmap_hi, 0,
                                     conf.cmap_range, size=(-1, 200),
                                     style=wx.SL_INVERSE|wx.SL_VERTICAL)

        self.cmap_lo_val.Bind(wx.EVT_SCROLL,  self.onStretchLow)
        self.cmap_hi_val.Bind(wx.EVT_SCROLL,  self.onStretchHigh)


        lsizer.Add(cmap_choice,      (3, 0), (1, 4), labstyle, 2)
        lsizer.Add(cmap_toggle,      (4, 0), (1, 4), labstyle, 5)
        lsizer.Add(self.cmap_lo_val, (5, 0), (1, 1), labstyle, 5)
        lsizer.Add(self.cmap_canvas, (5, 1), (1, 2), wx.ALIGN_CENTER|labstyle)
        lsizer.Add(self.cmap_hi_val, (5, 3), (1, 1), labstyle, 5)
        # lsizer.Add(log_toggle,       (6,0), (1,4), labstyle)

        lpanel.SetSizer(lsizer)
        lpanel.Fit()
        return lpanel

    def onInterp(self, event=None):
        self.panel.conf.interp =  event.GetString()
        self.panel.redraw()

    def onCMap(self, event=None):
        self.update_cmap(event.GetString())

    def onCMapReverse(self, event=None):
        self.panel.conf.cmap_reverse = event.IsChecked()
        cmap_name = self.panel.conf.cmap.name
        if isinstance(cmap_name, tuple):
            return
        if cmap_name.endswith('_r'):
            cmap_name = cmap_name[:-2]
        self.update_cmap(cmap_name)

    def update_cmap(self, cmap_name):
        conf = self.panel.conf
        if  conf.cmap_reverse:
            cmap_name = cmap_name + '_r'

        conf.cmap = getattr(colormap, cmap_name)
        self.redraw_cmap()

    def redraw_cmap(self):
        conf = self.panel.conf
        conf.image.set_cmap(conf.cmap)
        self.cmap_image.set_cmap(conf.cmap)

        lo = conf.cmap_lo
        hi = conf.cmap_hi
        cmax = 1.0 * conf.cmap_range
        wid = numpy.ones(cmax/8)
        self.cmap_data[:lo, :] = 0
        self.cmap_data[lo:hi] = numpy.outer(numpy.linspace(0., 1., hi-lo), wid)
        self.cmap_data[hi:, :] = 1
        self.cmap_image.set_data(self.cmap_data)
        self.cmap_canvas.draw()
        self.panel.redraw()

    def onStretchLow(self, event=None):
        self.StretchCMap(event.GetInt(), self.cmap_hi_val.GetValue())

    def onStretchHigh(self, event=None):
        self.StretchCMap(self.cmap_lo_val.GetValue(), event.GetInt())

    def StretchCMap(self, low, high):
        lo, hi = min(low, high), max(low, high)
        if (hi-lo)<2:
            hi = min(hi, self.panel.conf.cmap_range)
            lo = max(lo, 0)

        self.cmap_lo_val.SetValue(lo)
        self.cmap_hi_val.SetValue(hi)
        self.panel.conf.cmap_lo = lo
        self.panel.conf.cmap_hi = hi
        self.redraw_cmap()

    def onCMapSave(self, event=None):
        """save color table image"""
        file_choices = "PNG (*.png)|*.png"
        ofile = 'Colormap.png'

        dlg = wx.FileDialog(self, message='Save Colormap as...',
                            defaultDir = os.getcwd(),
                            defaultFile=ofile,
                            wildcard=file_choices,
                            style=wx.SAVE|wx.CHANGE_DIR)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.cmap_canvas.print_figure(path, dpi=300)
