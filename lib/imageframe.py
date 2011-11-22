#!/usr/bin/python
"""
wxmplot ImageFrame: a wx.Frame for image display, using matplotlib
"""
import os
import wx
import numpy
import matplotlib.cm as colormap
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg

from imagepanel import ImagePanel
from imageconf import ColorMap_List, Interp_List
from baseframe import BaseFrame
from colors import rgb2hex
from utils import Closure, LabelEntry

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

    def display(self, img, title=None, **kw):
        """plot after clearing current plot """
        if title is not None:
            self.SetTitle(title)
        self.panel.display(img, **kw)

    def BuildCustomMenus(self):
        "build menus"
        mids = self.menuIDs
        mids.SAVE_CMAP = wx.NewId()
        mids.LOG_SCALE = wx.NewId()
        mids.FLIP_H    = wx.NewId()
        mids.FLIP_V    = wx.NewId()
        mids.FLIP_O    = wx.NewId()
        mids.ROT_CW    = wx.NewId()
        m = wx.Menu()
        m.Append(mids.UNZOOM, "Zoom Out\tCtrl+Z",
                 "Zoom out to full data range")
        m.Append(mids.LOG_SCALE, "Log Scale Intensity\tCtrl+L", "", wx.ITEM_CHECK)
        m.AppendSeparator()
        m.Append(mids.ROT_CW, 'Rotate clockwise\tCtrl+R', '')
        m.AppendSeparator()
        m.Append(mids.FLIP_V, 'Flip Top/Bottom\tCtrl+T', '')
        m.Append(mids.FLIP_H, 'Flip Left/Right\tCtrl+F', '')
        m.Append(mids.FLIP_O, 'Flip to Original', '')
        m.AppendSeparator()
        m.Append(mids.SAVE_CMAP, "Save Image of Colormap")
        self.Bind(wx.EVT_MENU, self.onFlip,       id=mids.FLIP_H)
        self.Bind(wx.EVT_MENU, self.onFlip,       id=mids.FLIP_V)
        self.Bind(wx.EVT_MENU, self.onFlip,       id=mids.FLIP_O)
        self.Bind(wx.EVT_MENU, self.onFlip,       id=mids.ROT_CW)

        sm = wx.Menu()
        for itype in Interp_List:
            wid = wx.NewId()
            sm.AppendRadioItem(wid, itype, itype)
            self.Bind(wx.EVT_MENU, Closure(self.onInterp, name=itype), id=wid)
        self.user_menus  = [('&Options', m), ('Smoothing', sm)]

    def onInterp(self, evt=None, name=None):
        if name not in Interp_List:
            name = Interp_List[0]
        self.panel.conf.interp = name
        self.panel.redraw()

    def onFlip(self, event=None):
        conf = self.panel.conf
        wid = event.GetId()
        mids = self.menuIDs

        if wid == mids.FLIP_H:
            conf.flip_lr = not conf.flip_lr
        elif wid == mids.FLIP_V:
            conf.flip_ud = not conf.flip_ud
        elif wid == mids.FLIP_O:
            conf.flip_lr, conf.flip_ud = False, False
        elif wid == mids.ROT_CW:
            conf.rot = True
        self.panel.unzoom_all()

    def BuildFrame(self):
        sbar = self.CreateStatusBar(2, wx.CAPTION|wx.THICK_FRAME)
        sfont = sbar.GetFont()
        sfont.SetWeight(wx.BOLD)
        sfont.SetPointSize(12)
        sbar.SetFont(sfont)

        self.SetStatusWidths([-3, -1])
        self.SetStatusText('', 0)

        self.BuildCustomMenus()
        self.BuildMenu()
        mainsizer = wx.BoxSizer(wx.HORIZONTAL)

        self.bgcol = rgb2hex(self.GetBackgroundColour()[:3])
        self.panel = ImagePanel(self, data_callback=self.onDataChange)
                                # show_config_popup=(not self.config_on_frame),


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
        self.Bind(wx.EVT_MENU, self.onLogScale, id=mids.LOG_SCALE)

        self.SetAutoLayout(True)
        self.SetSizer(mainsizer)
        self.Fit()

    def BuildConfigPanel(self):
        """config panel for left-hand-side of frame"""
        conf = self.panel.conf
        lpanel = wx.Panel(self)
        lsizer = wx.GridBagSizer(7, 4)

        labstyle = wx.ALIGN_LEFT|wx.LEFT|wx.TOP|wx.EXPAND

        # interp_choice =  wx.Choice(lpanel, choices=Interp_List)
        # interp_choice.Bind(wx.EVT_CHOICE,  self.onInterp)

        s = wx.StaticText(lpanel, label=' Color Table:', size=(100, -1))
        s.SetForegroundColour('Blue')
        lsizer.Add(s, (0, 0), (1, 3), labstyle, 5)

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
                                       numpy.ones(cmax/4))

        self.cmap_fig   = Figure((0.80, 1.0), dpi=100)
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
                                     conf.cmap_range, size=(-1, 180),
                                     style=wx.SL_INVERSE|wx.SL_VERTICAL)

        self.cmap_hi_val = wx.Slider(lpanel, -1, conf.cmap_hi, 0,
                                     conf.cmap_range, size=(-1, 180),
                                     style=wx.SL_INVERSE|wx.SL_VERTICAL)

        self.cmap_lo_val.Bind(wx.EVT_SCROLL,  self.onStretchLow)
        self.cmap_hi_val.Bind(wx.EVT_SCROLL,  self.onStretchHigh)

        iauto_toggle = wx.CheckBox(lpanel, label='Autoscale Intensity?',
                                  size=(160, -1))
        iauto_toggle.Bind(wx.EVT_CHECKBOX, self.onInt_Autoscale)
        iauto_toggle.SetValue(conf.auto_intensity)

        lsizer.Add(cmap_choice,      (1, 0), (1, 4), labstyle, 2)
        lsizer.Add(cmap_toggle,      (2, 0), (1, 4), labstyle, 5)
        lsizer.Add(self.cmap_lo_val, (3, 0), (1, 1), labstyle, 5)
        lsizer.Add(self.cmap_canvas, (3, 1), (1, 2), wx.ALIGN_CENTER|labstyle)
        lsizer.Add(self.cmap_hi_val, (3, 3), (1, 1), labstyle, 5)
        lsizer.Add(iauto_toggle,     (4,0), (1,4), labstyle)

        self.imin_val = LabelEntry(lpanel, conf.int_lo,  size=40, labeltext='I min:',
                                   action = Closure(self.onThreshold, argu='lo'))
        self.imax_val = LabelEntry(lpanel, conf.int_hi,  size=40, labeltext='I max:',
                                   action = Closure(self.onThreshold, argu='hi'))
        self.imax_val.Disable()
        self.imin_val.Disable()

        lsizer.Add(self.imin_val.label, (5, 0), (1, 1), labstyle, 5)
        lsizer.Add(self.imax_val.label, (6, 0), (1, 1), labstyle, 5)
        lsizer.Add(self.imin_val, (5, 1), (1, 2), labstyle, 5)
        lsizer.Add(self.imax_val, (6, 1), (1, 2), labstyle, 5)

        lpanel.SetSizer(lsizer)
        lpanel.Fit()
        return lpanel

    def onCMap(self, event=None):
        self.update_cmap(event.GetString())

    def onDataChange(self, data, x=None, y=None, **kw):
        imin, imax = data.min(), data.max()
        self.imin_val.SetValue("%.4g" % imin)
        self.imax_val.SetValue("%.4g" % imax)
        self.panel.conf.int_lo = imin
        self.panel.conf.int_hi = imax

    def onThreshold(self, event=None, argu='hi'):
        if (wx.EVT_TEXT_ENTER.evtType[0] == event.GetEventType()):
            try:
                val =  float(str(event.GetString()).strip())
            except:
                return
        elif (wx.EVT_KILL_FOCUS.evtType[0] == event.GetEventType()):
            val = float(self.imax_val.GetValue())
            if argu == 'lo':
                val = float(self.imin_val.GetValue())
        if argu == 'lo':
            self.panel.conf.int_lo = val
        else:
            self.panel.conf.int_hi = val
        self.panel.redraw()

    def onInt_Autoscale(self, event=None):
        val = self.panel.conf.auto_intensity = event.IsChecked()
        if val:
            try:
                self.onDataChange(self.panel.conf.data)
            except:
                pass
            self.imax_val.Disable()
            self.imin_val.Disable()
        else:
            self.imax_val.Enable()
            self.imin_val.Enable()
        self.panel.redraw()


#
#         if isinstance(cmap_name, tuple):
#             return
#         if cmap_name.endswith('_r'):
#             cmap_name = cmap_name[:-2]
#         self.update_cmap(cmap_name)

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
        wid = numpy.ones(cmax/4)
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

    def onLogScale(self, event=None):
        self.panel.conf.log_scale = not self.panel.conf.log_scale
        self.panel.redraw()

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
