#!/usr/bin/python
"""
wxmplot ImageFrame: a wx.Frame for image display, using matplotlib
"""
import os
import wx
import numpy
from   matplotlib.cm import get_cmap
import matplotlib.cm as colormap
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg

from imagepanel import ImagePanel
from imageconf import ColorMap_List, Interp_List
from baseframe import BaseFrame
from colors import rgb2hex
from utils import Closure, LabelEntry

CURSOR_MENULABELS = {'zoom':  ('Zoom to Rectangle\tCtrl+B',
                               'Left-Drag to zoom to rectangular box'),
                     'lasso': ('Select Points\tCtrl+X',
                               'Left-Drag to select points freehand'),
                     'prof':  ('Select Line Profile\tCtrl+K',
                               'Left-Drag to select like for profile')}

class ImageFrame(BaseFrame):
    """
    MatPlotlib Image Display ons a wx.Frame, using ImagePanel
    """

    def __init__(self, parent=None, size=None,
                 config_on_frame=True, lasso_callback=None,
                 show_xsections=True, cursor_labels=None,
                 output_title='Image',   **kws):
        if size is None: size = (550, 450)
        self.config_on_frame = config_on_frame
        self.lasso_callback = lasso_callback
        self.cursor_menulabels =  {}
        self.cursor_menulabels.update(CURSOR_MENULABELS)
        if cursor_labels is not None:
            self.cursor_menulabels.update(cursor_labels)

        BaseFrame.__init__(self, parent=parent,
                           title  = 'Image Display Frame',
                           output_title=output_title,
                           size=size, **kws)
        self.BuildFrame(show_xsections=show_xsections)

    def display(self, img, title=None, colormap=None, style='image', **kw):
        """plot after clearing current plot """
        if title is not None:
            self.SetTitle(title)
        if self.config_on_frame:
            if len(img.shape) == 3:
                for comp in self.config_panel.Children:
                    comp.Disable()
            else:
                for comp in self.config_panel.Children:
                    comp.Enable()
        self.panel.display(img, style=style, **kw)
        self.panel.conf.title = title
        if colormap is not None:
            self.set_colormap(name=colormap)
        contour_value = 0
        if style == 'contour':
            contour_value = 1
        if self.config_on_frame:
            self.contour_toggle.SetValue(contour_value)
        self.panel.redraw()


    def BuildMenu(self):
        mids = self.menuIDs
        m0 = wx.Menu()
        mids.EXPORT = wx.NewId()
        m0.Append(mids.SAVE,   "&Save Image\tCtrl+S",  "Save PNG Image of Plot")
        m0.Append(mids.CLIPB,  "&Copy Image\tCtrl+C",  "Copy Image to Clipboard")
        m0.Append(mids.EXPORT, "Export Data",   "Export to ASCII file")
        m0.AppendSeparator()
        m0.Append(mids.PSETUP, 'Page Setup...', 'Printer Setup')
        m0.Append(mids.PREVIEW, 'Print Preview...', 'Print Preview')
        m0.Append(mids.PRINT, "&Print\tCtrl+P", "Print Plot")
        m0.AppendSeparator()
        m0.Append(mids.EXIT, "E&xit\tCtrl+Q", "Exit the 2D Plot Window")

        self.top_menus['File'] = m0

        mhelp = wx.Menu()
        mhelp.Append(mids.HELP, "Quick Reference",  "Quick Reference for WXMPlot")
        mhelp.Append(mids.ABOUT, "About", "About WXMPlot")
        self.top_menus['Help'] = mhelp

        mbar = wx.MenuBar()

        mbar.Append(self.top_menus['File'], "File")
        for m in self.user_menus:
            title,menu = m
            mbar.Append(menu, title)
        mbar.Append(self.top_menus['Help'], "&Help")


        self.SetMenuBar(mbar)
        self.Bind(wx.EVT_MENU, self.onHelp,            id=mids.HELP)
        self.Bind(wx.EVT_MENU, self.onAbout,           id=mids.ABOUT)
        self.Bind(wx.EVT_MENU, self.onExit ,           id=mids.EXIT)
        self.Bind(wx.EVT_CLOSE,self.onExit)

    def BuildCustomMenus(self):
        "build menus"
        mids = self.menuIDs
        mids.SAVE_CMAP = wx.NewId()
        mids.LOG_SCALE = wx.NewId()
        mids.FLIP_H    = wx.NewId()
        mids.FLIP_V    = wx.NewId()
        mids.FLIP_O    = wx.NewId()
        mids.ROT_CW    = wx.NewId()
        mids.CUR_ZOOM  = wx.NewId()
        mids.CUR_LASSO = wx.NewId()
        mids.CUR_PROF  = wx.NewId()
        m = wx.Menu()
        m.Append(mids.UNZOOM, "Zoom Out\tCtrl+Z",
                 "Zoom out to full data range")
        m.Append(mids.SAVE_CMAP, "Save Image of Colormap")
        m.AppendSeparator()
        m.Append(mids.LOG_SCALE, "Log Scale Intensity\tCtrl+L", "", wx.ITEM_CHECK)
        m.Append(mids.ROT_CW, 'Rotate clockwise\tCtrl+R', '')
        m.Append(mids.FLIP_V, 'Flip Top/Bottom\tCtrl+T', '')
        m.Append(mids.FLIP_H, 'Flip Left/Right\tCtrl+F', '')
        # m.Append(mids.FLIP_O, 'Flip to Original', '')
        m.AppendSeparator()
        m.Append(wx.NewId(), 'Cursor Modes : ',
                 'Action taken on with Left-Click and Left-Drag')

        clabs = self.cursor_menulabels
        m.AppendRadioItem(mids.CUR_ZOOM,  clabs['zoom'][0],  clabs['zoom'][1])
        m.AppendRadioItem(mids.CUR_LASSO, clabs['lasso'][0], clabs['lasso'][1])
        m.AppendRadioItem(mids.CUR_PROF,  clabs['prof'][0],  clabs['prof'][1])
        m.AppendSeparator()
        self.Bind(wx.EVT_MENU, self.onFlip,       id=mids.FLIP_H)
        self.Bind(wx.EVT_MENU, self.onFlip,       id=mids.FLIP_V)
        self.Bind(wx.EVT_MENU, self.onFlip,       id=mids.FLIP_O)
        self.Bind(wx.EVT_MENU, self.onFlip,       id=mids.ROT_CW)
        self.Bind(wx.EVT_MENU, self.onCursorMode, id=mids.CUR_ZOOM)
        self.Bind(wx.EVT_MENU, self.onCursorMode, id=mids.CUR_PROF)
        self.Bind(wx.EVT_MENU, self.onCursorMode, id=mids.CUR_LASSO)

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

    def onCursorMode(self, event=None):
        wid = event.GetId()
        self.panel.cursor_mode = 'zoom'
        if wid == self.menuIDs.CUR_PROF:
            self.panel.cursor_mode = 'profile'
        elif wid == self.menuIDs.CUR_LASSO:
            self.panel.cursor_mode = 'lasso'

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

    def BuildFrame(self, show_xsections=True):
        sbar = self.CreateStatusBar(2, wx.CAPTION|wx.THICK_FRAME)
        sfont = sbar.GetFont()
        sfont.SetWeight(wx.BOLD)
        sfont.SetPointSize(10)
        sbar.SetFont(sfont)

        self.SetStatusWidths([-2, -1])
        self.SetStatusText('', 0)

        self.BuildCustomMenus()
        self.BuildMenu()
        mainsizer = wx.BoxSizer(wx.HORIZONTAL)


        self.bgcol = rgb2hex(self.GetBackgroundColour()[:3])
        self.panel = ImagePanel(self, data_callback=self.onDataChange,
                                lasso_callback=self.onLasso,
                                output_title=self.output_title)

        if self.config_on_frame:
            lpanel = self.BuildConfigPanel()
            mainsizer.Add(lpanel, 0,
                          wx.LEFT|wx.ALIGN_LEFT|wx.TOP|wx.ALIGN_TOP|wx.EXPAND)

        mids = self.menuIDs
        self.Bind(wx.EVT_MENU, self.panel.exportASCII, id=mids.EXPORT)

        # show_config_popup=(not self.config_on_frame),
        img_panel_extent = (2, 2)
        img_panel_locale = (0, 1)

        if not show_xsections:
            img_panel_extent = (1, 1)
            img_panel_locale = (1, 1)
            xtop = wx.StaticText(self, label='Top')
            xside = wx.StaticText(self, label='Side')
            xinfo = wx.StaticText(self, label='Info')
            mainsizer.Add(xtop,  (0, 1), (1, 1), wx.EXPAND)
            mainsizer.Add(xinfo, (0, 2), (1, 1), wx.EXPAND)
            mainsizer.Add(xside, (1, 2), (1, 1), wx.EXPAND)

        self.panel.messenger = self.write_message
        self.panel.fig.set_facecolor(self.bgcol)

        mainsizer.Add(self.panel, 1,  wx.EXPAND)

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

        self.config_panel = lpanel
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
        self.cmap_choice = cmap_choice

        cmap_reverse = wx.CheckBox(lpanel, label='Reverse Table',
                                  size=(140, -1))
        cmap_reverse.Bind(wx.EVT_CHECKBOX, self.onCMapReverse)
        cmap_reverse.SetValue(conf.cmap_reverse)
        self.cmap_reverse = cmap_reverse

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

        lsizer.Add(self.cmap_choice,  (1, 0), (1, 4), labstyle, 2)
        lsizer.Add(self.cmap_reverse, (2, 0), (1, 4), labstyle, 5)
        lsizer.Add(self.cmap_lo_val,  (3, 0), (1, 1), labstyle, 5)
        lsizer.Add(self.cmap_canvas,  (3, 1), (1, 2), wx.ALIGN_CENTER|labstyle)
        lsizer.Add(self.cmap_hi_val,  (3, 3), (1, 1), labstyle, 5)
        lsizer.Add(iauto_toggle,      (4, 0), (1, 4), labstyle)

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

        contour_toggle = wx.CheckBox(lpanel, label='As Contour Plot?',
                                  size=(160, -1))
        contour_toggle.Bind(wx.EVT_CHECKBOX, self.onContourToggle)
        self.contour_toggle = contour_toggle
        contour_value = 0
        if conf.style == 'contour':
            contour_value = 1
        contour_toggle.SetValue(contour_value)
        contour_labels = wx.CheckBox(lpanel, label='Label Contours?',
                                  size=(160, -1))
        contour_labels.SetValue(1)
        contour_labels.Bind(wx.EVT_CHECKBOX, self.onContourLabels)
        self.contour_labels = contour_labels
        self.ncontours = LabelEntry(lpanel, 10, size=40, labeltext='N levels:',
                                   action = Closure(self.onContourLevels))

        lsizer.Add(self.contour_toggle,  (7, 0), (1, 4), labstyle, 5)
        lsizer.Add(self.ncontours.label, (8, 0), (1, 1), labstyle, 5)
        lsizer.Add(self.ncontours,       (8, 1), (1, 2), labstyle, 5)
        lsizer.Add(self.contour_labels,  (9, 0), (1, 4), labstyle, 5)

        lpanel.SetSizer(lsizer)
        lpanel.Fit()
        return lpanel

    def onContourLevels(self, event=None):
        try:
            nlevels = int(event.GetString())
        except:
            return
        panel = self.panel
        conf  = panel.conf
        if conf.style == 'image':
            return
        self.set_colormap()
        panel.axes.cla()
        panel.display(conf.data, x=panel.xdata, y = panel.ydata,
                      xlabel=panel.xlab, ylabel=panel.ylab,
                      nlevels=nlevels, style='contour')
        panel.redraw()

    def onContourToggle(self, event=None):
        panel = self.panel
        conf  = panel.conf
        conf.style = 'image'
        if event.IsChecked():
            conf.style = 'contour'
        try:
            nlevels = int(self.ncontours.GetValue())
        except:
            nlevels = None
        self.set_colormap()
        panel.axes.cla()
        panel.display(conf.data, x=panel.xdata, y = panel.ydata, nlevels=nlevels,
                      xlabel=panel.xlab, ylabel=panel.ylab, style=conf.style)
        panel.redraw()

    def onContourLabels(self, event=None):
        panel = self.panel
        conf  = panel.conf
        conf.contour_labels = event.IsChecked()
        try:
            nlevels = int(self.ncontours.GetValue())
        except:
            nlevels = None

        panel.axes.cla()
        self.set_colormap()
        panel.display(conf.data, x=panel.xdata, y = panel.ydata, nlevels=nlevels,
                      xlabel=panel.xlab, ylabel=panel.ylab, style=conf.style)
        panel.redraw()

    def onCMap(self, event=None):
        self.set_colormap(name=event.GetString())
        self.panel.redraw()

    def onLasso(self, data=None, selected=None, mask=None, **kws):
        if hasattr(self.lasso_callback , '__call__'):
            self.lasso_callback(data=data, selected=selected, mask=mask, **kws)

    def onDataChange(self, data, x=None, y=None, **kw):
        imin, imax = data.min(), data.max()
        if self.config_on_frame:
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

    def onCMapReverse(self, event=None):
        self.set_colormap()
        self.panel.redraw()

    def set_colormap(self, name=None):
        conf = self.panel.conf
        if name is None:
            name = self.cmap_choice.GetStringSelection()

        conf.cmap_reverse = (1 == int(self.cmap_reverse.GetValue()))
        if conf.cmap_reverse and not name.endswith('_r'):
            name = name + '_r'
        elif not conf.cmap_reverse and name.endswith('_r'):
            name = name[:-2]
        cmap_name = name
        try:
            conf.cmap = getattr(colormap, name)
        except:
            conf.cmap = get_cmap(name)
        if hasattr(conf, 'contour'):
            xname = 'gray'
            if cmap_name == 'gray_r':
                xname = 'Reds_r'
            elif cmap_name == 'gray':
                xname = 'Reds'
            elif cmap_name.endswith('_r'):
                xname = 'gray_r'
            conf.contour.set_cmap(getattr(colormap, xname))
        if hasattr(conf, 'image'):
            conf.image.set_cmap(conf.cmap)
        self.redraw_cmap()

        if hasattr(conf, 'highlight_areas'):
            if hasattr(conf.cmap, '_lut'):
                rgb  = (int(i*240)^255 for i in conf.cmap._lut[0][:3])
                col  = '#%02x%02x%02x' % tuple(rgb)
                for area in conf.highlight_areas:
                    for w in area.collections + area.labelTexts:
                        w.set_color(col)

    def redraw_cmap(self):
        conf = self.panel.conf
        if not hasattr(conf, 'image'): return
        # conf.image.set_cmap(conf.cmap)
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
        self.panel.redraw()

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
