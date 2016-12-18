#!/usr/bin/python
"""
wxmplot ImageFrame: a wx.Frame for image display, using matplotlib
"""
import os
import wx
is_wxPhoenix = 'phoenix' in wx.PlatformInfo
if is_wxPhoenix:
    PyDeadObjectError = RuntimeError
else:
    from wx._core import PyDeadObjectError

from functools import partial
import numpy as np
from   matplotlib.cm import get_cmap
import matplotlib.cm as mpl_colormap
from matplotlib.figure import Figure
from matplotlib.ticker import NullFormatter
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

from .imagepanel import ImagePanel
from .imageconf import ColorMap_List, Interp_List
from .baseframe import BaseFrame
from .plotframe import PlotFrame
from .colors import rgb2hex
from .utils import LabelEntry, MenuItem, pack
from .contourdialog import ContourDialog

CURSOR_MENULABELS = {'zoom':  ('Zoom to Rectangle\tCtrl+B',
                               'Left-Drag to zoom to rectangular box'),
                     'lasso': ('Select Points\tCtrl+V',
                               'Left-Drag to select points freehand'),
                     'prof':  ('Select Line Profile\tCtrl+K',
                               'Left-Drag to select like for profile')}

RGB_COLORS = ('red', 'green', 'blue')
CMY_COLORS = ('cyan', 'magenta', 'yellow')

class ColorMapPanel(wx.Panel):
    """color map interface"""
    def __init__(self, parent, imgpanel, color=0,
                 colormap_list=None, default=None,
                 cmap_callback=None, title='Color Table',  **kws):
        wx.Panel.__init__(self, parent, -1,  **kws)

        self.imgpanel = imgpanel
        self.icol = color
        self.cmap_callback = cmap_callback

        labstyle = wx.ALIGN_LEFT|wx.LEFT|wx.TOP|wx.EXPAND
        sizer = wx.GridBagSizer(2, 2)

        self.title = wx.StaticText(self, label=title, size=(120, -1))
        sizer.Add(self.title, (0, 0), (1, 4), labstyle, 2)

        self.cmap_choice = None
        reverse = False
        cmap = default
        if colormap_list is not None:
            cmap_choice =  wx.Choice(self, size=(90, -1), choices=colormap_list)
            cmap_choice.Bind(wx.EVT_CHOICE,  self.onCMap)
            self.cmap_choice = cmap_choice

            if cmap is None:
                cmap = colormap_list[0]

            if cmap.endswith('_r'):
                reverse = True
                cmap = cmap[:-2]
            cmap_choice.SetStringSelection(cmap)

            cmap_reverse = wx.CheckBox(self, label='Reverse', size=(60, -1))
            cmap_reverse.Bind(wx.EVT_CHECKBOX, self.onCMapReverse)
            cmap_reverse.SetValue(reverse)
            self.cmap_reverse = cmap_reverse

        if cmap is None:
            cmap = 'gray'
        self.imgpanel.conf.cmap[color] = get_cmap(cmap)

        maxval = self.imgpanel.conf.cmap_range
        wd, ht = 1.00, 0.125

        self.cmap_dat = np.outer(np.ones(int(maxval*ht)),
                                 np.linspace(0, 1, maxval))

        fig = Figure((wd, ht), dpi=150)

        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_axis_off()
        self.cmap_canvas = FigureCanvas(self, -1, figure=fig)

        self.cmap_img = ax.imshow(self.cmap_dat, cmap=cmap,
                                  interpolation='bilinear')
        self.cmap_lo = wx.Slider(self, -1, 0, 0, maxval,
                                 style=wx.SL_HORIZONTAL)

        self.cmap_hi = wx.Slider(self, -1, maxval, 0, maxval,
                                 style=wx.SL_HORIZONTAL)


        self.cmap_lo.Bind(wx.EVT_SCROLL,  self.onStretchLow)
        self.cmap_hi.Bind(wx.EVT_SCROLL,  self.onStretchHigh)

        irow = 0
        if self.cmap_choice is not None:
            irow += 1
            sizer.Add(self.cmap_choice,  (irow, 0), (1, 2), labstyle, 2)
            sizer.Add(self.cmap_reverse, (irow, 2), (1, 2), labstyle, 2)

        irow += 1
        sizer.Add(self.cmap_hi,      (irow, 0), (1, 4), labstyle, 2)
        irow += 1
        sizer.Add(self.cmap_canvas,  (irow, 0), (1, 4), wx.ALIGN_CENTER, 0)
        irow += 1
        sizer.Add(self.cmap_lo,      (irow, 0), (1, 4), labstyle, 2)

        self.imin_val = LabelEntry(self, 0, size=80,
                                   labeltext='Range:',
                                   action=partial(self.onThreshold, argu='lo'))
        self.imax_val = LabelEntry(self, maxval, size=80, labeltext=':',
                                   action=partial(self.onThreshold, argu='hi'))
        self.islider_range = wx.StaticText(self, label='Shown: ',
                                                size=(90, -1))
        irow += 1
        sizer.Add(self.imin_val.label, (irow, 0), (1, 1), labstyle, 1)
        sizer.Add(self.imin_val,       (irow, 1), (1, 1), labstyle, 0)
        sizer.Add(self.imax_val.label, (irow, 2), (1, 1), labstyle, 0)
        sizer.Add(self.imax_val,       (irow, 3), (1, 1), labstyle, 0)
        irow += 1
        sizer.Add(self.islider_range,  (irow, 0), (1, 4), labstyle, 0)
        pack(self, sizer)
        self.set_colormap(default)


    def onCMap(self, event=None):
        self.set_colormap(name=event.GetString())
        self.imgpanel.redraw()
        if callable(self.cmap_callback):
            self.cmap_callback(name=event.GetString())


    def onCMapReverse(self, event=None):
        self.set_colormap()
        self.imgpanel.redraw()

    def set_colormap(self, name=None):
        conf = self.imgpanel.conf
        col = self.icol
        try:
            if name is None:
                name = self.cmap_choice.GetStringSelection()
        except:
            return
        conf.cmap_reverse = False
        try:
            conf.cmap_reverse = (1 == int(self.cmap_reverse.GetValue()))
        except:
            pass
        if conf.cmap_reverse and not name.endswith('_r'):
            name = name + '_r'
        elif not conf.cmap_reverse and name.endswith('_r'):
            name = name[:-2]
        cmap_name = name
        conf.cmap[col] = get_cmap(name)

        if hasattr(conf, 'contour'):
            xname = 'gray'
            if cmap_name == 'gray_r':
                xname = 'Reds_r'
            elif cmap_name == 'gray':
                xname = 'Reds'
            elif cmap_name.endswith('_r'):
                xname = 'gray_r'
            conf.contour.set_cmap(getattr(mpl_colormap, xname))
        if hasattr(conf, 'image'):
            conf.image.set_cmap(conf.cmap[col])
        self.redraw_cmap()

        if hasattr(conf, 'highlight_areas'):
            if hasattr(conf.cmap[col], '_lut'):
                rgb  = [int(i*240)^255 for i in conf.cmap[col]._lut[0][:3]]
                col  = '#%02x%02x%02x' % (rgb[0], rgb[1], rgb[2])
                for area in conf.highlight_areas:
                    for w in area.collections + area.labelTexts:
                        w.set_color(col)

    def onThreshold(self, event=None, argu='hi'):
        col = self.icol
        conf = self.imgpanel.conf
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
            conf.int_lo[col] = val
        else:
            conf.int_hi[col] = val
        lo = conf.int_lo[col]
        hi = conf.int_hi[col]
        self.islider_range.SetLabel('Shown: [ %.4g :  %.4g ]' % (lo, hi))
        self.imgpanel.redraw()

    def redraw_cmap(self):
        col = self.icol
        conf = self.imgpanel.conf
        self.cmap_img.set_cmap(conf.cmap[col])
        lo = int(conf.cmap_lo[col])
        hi = int(conf.cmap_hi[col])
        self.cmap_dat[:, :lo] = 0
        self.cmap_dat[:, lo:hi]  = np.linspace(0., 1., hi-lo)
        self.cmap_dat[:, hi:] = 1
        self.cmap_img.set_data(self.cmap_dat)
        self.cmap_canvas.draw()

    def onStretchLow(self, event=None):
        high = self.cmap_hi.GetValue()
        self.StretchCMap(event.GetInt(), high)

    def onStretchHigh(self, event=None):
        low = self.cmap_lo.GetValue()
        self.StretchCMap(low, event.GetInt())

    def StretchCMap(self, low, high):
        col = self.icol
        conf = self.imgpanel.conf
        lo, hi = min(low, high), max(low, high)
        if (hi-lo)<2:
            hi = min(hi, conf.cmap_range)
            lo = max(lo, 0)
        self.cmap_lo.SetValue(lo)
        self.cmap_hi.SetValue(hi)
        conf.cmap_lo[col] = lo
        conf.cmap_hi[col] = hi
        imin = float(self.imin_val.GetValue())
        imax = float(self.imax_val.GetValue())
        xlo = imin + (imax-imin)*lo/conf.cmap_range
        xhi = imin + (imax-imin)*hi/conf.cmap_range
        self.islider_range.SetLabel('Shown: [%.4g: %.4g]' % (xlo, xhi))
        self.redraw_cmap()
        self.imgpanel.redraw()



class AutoContrastDialog(wx.Dialog):
    """Configure Auto-Contrast Level"""
    msg = '''Configure Auto-Contrast'''
    def __init__(self, parent=None, conf=None,
                 title='Auto-Contrast Configuration',
                 size=wx.DefaultSize, pos=wx.DefaultPosition,
                 style=wx.DEFAULT_DIALOG_STYLE):
        self.conf = conf
        if conf is None:
            return
        wid = -1
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title=title)

        sizer = wx.GridBagSizer(4, 4)
        clevel = float(conf.auto_contrast_level)

        label = wx.StaticText(self, -1, "Contrast Percent Level:")
        self.level = wx.TextCtrl(self, -1, "%.2f" % clevel, size=(100,-1))

        sizer.Add(label,        (0, 0), (1, 1), wx.ALIGN_LEFT|wx.ALL, 2)
        sizer.Add(self.level,   (0, 1), (1, 1), wx.ALIGN_LEFT|wx.ALL, 2)

        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, (2, 0), (1, 2),
                  wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 2)

        btnsizer = wx.StdDialogButtonSizer()

        btn1 = wx.Button(self, wx.ID_OK)
        btn2 = wx.Button(self, wx.ID_CANCEL)
        btn1.Bind(wx.EVT_BUTTON, self.onOK)
        btn1.SetDefault()
        btnsizer.AddButton(btn1)
        btnsizer.AddButton(btn2)
        btnsizer.Realize()

        sizer.Add(btnsizer, (3, 0), (1, 2), wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)

    def onOK(self, evt=None):
        try:
            val = float(self.level.GetValue())
        except:
            val = 1.0
        self.conf.auto_contrast_level = val
        evt.Skip()
        return wx.ID_OK

class ImageFrame(BaseFrame):
    """
    MatPlotlib Image Display ons a wx.Frame, using ImagePanel
    """

    help_msg =  """Quick help:

Left-Click:   to display X,Y coordinates and Intensity
Left-Drag:    to zoom in on region
Right-Click:  display popup menu with choices:
               Zoom out 1 level
               Zoom all the way out
               --------------------
               Rotate Image
               Save Image

Keyboard Shortcuts:   (For Mac OSX, replace 'Ctrl' with 'Apple')
  Saving Images:
     Ctrl-S:     Save image to file
     Ctrl-C:     Copy image to clipboard
     Ctrl-P:     Print Image

  Zooming:
     Ctrl-Z:     Zoom all the way out

  Rotating/Flipping:
     Ctrl-R:     Rotate Clockwise
     Ctrl-T:     Flip Top/Bottom
     Ctrl-F:     Flip Left/Right

  Image Enhancement:
     Ctrl-L:     Log-Scale Intensity
     Ctrl-E:     Enhance Contrast


"""


    def __init__(self, parent=None, size=None,
                 lasso_callback=None, mode='intensity',
                 show_xsections=False, cursor_labels=None,
                 output_title='Image', subtitles=None,
                 user_menus=None, **kws):
        if size is None: size = (700, 525)
        self.lasso_callback = lasso_callback
        self.user_menus = user_menus
        self.cursor_menulabels =  {}
        self.cursor_menulabels.update(CURSOR_MENULABELS)
        if cursor_labels is not None:
            self.cursor_menulabels.update(cursor_labels)

        BaseFrame.__init__(self, parent=parent,
                           title  = 'Image Display Frame',
                           output_title=output_title,
                           size=size, **kws)

        self.cmap_panels = {}

        self.subtitles = {}
        self.config_mode = None
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

        self.panel = ImagePanel(self, data_callback=self.onDataChange,
                                size=(700, 525), dpi=100,
                                lasso_callback=self.onLasso,
                                output_title=self.output_title)


        self.BuildMenu()

        self.SetBackgroundColour('#F8F8F4')

        self.config_panel = wx.Panel(self)
        self.imin_val = {}
        self.imax_val = {}
        self.islider_range = {}

        self.config_mode = 'int'
        if mode.lower().startswith('rgb'):
            self.config_mode = 'rgb'
        elif mode.lower().startswith('cmy'):
            self.config_mode = 'cmy'
            self.panel.conf.tricolor_mode = 'cmy'

        self.Build_ConfigPanel()


        self.panel.messenger = self.write_message

        mainsizer = wx.BoxSizer(wx.HORIZONTAL)

        mainsizer.Add(self.config_panel, 0,
                      wx.LEFT|wx.ALIGN_LEFT|wx.TOP|wx.ALIGN_TOP|wx.EXPAND)

        mainsizer.Add(self.panel,    1, wx.ALL|wx.GROW)

        self.SetSizer(mainsizer)
        self.Fit()

    def display(self, img, title=None, colormap=None, style='image',
                subtitles=None, **kws):
        """plot after clearing current plot
        """
        if title is not None:
            self.SetTitle(title)
        if subtitles is not None:
            self.subtitles = subtitles
        cmode = self.config_mode.lower()[:3]

        if len(img.shape) == 3:
            if cmode not in ('rgb', 'cmy'):
                for comp in self.config_panel.Children:
                    comp.Destroy()
                self.config_mode = 'rgb'
                self.panel.conf.tricolor_mode = 'rgb'
                self.Build_ConfigPanel()
        else:
            if cmode != 'int':
                for comp in self.config_panel.Children:
                    comp.Destroy()
                self.config_mode = 'int'
                self.Build_ConfigPanel()
        self.panel.display(img, style=style, **kws)

        self.panel.conf.title = title
        if colormap is not None and self.config_mode == 'int':
            self.cmap_panels[0].set_colormap(name=colormap)

        if subtitles is not None:
            if isinstance(subtitles, dict):
                self.set_subtitles(**subtitles)
            elif self.config_mode == 'int':
                self.set_subtitles(red=subtitles)

        contour_value = 0
        if style == 'contour':
            contour_value = 1
        self.set_contrast_levels()
        self.panel.redraw()
        self.config_panel.Refresh()
        self.SendSizeEvent()
        wx.CallAfter(self.EnableMenus)

    def set_subtitles(self, red=None, green=None, blue=None):
        if self.config_mode.startswith('int') and red is not None:
            self.cmap_panels[0].title.SetLabel(red)

        if self.config_mode.startswith('rgb') and red is not None:
            self.cmap_panels[0].title.SetLabel(red)

        if self.config_mode.startswith('rgb') and green is not None:
            self.cmap_panels[1].title.SetLabel(green)

        if self.config_mode.startswith('rgb') and blue is not None:
            self.cmap_panels[2].title.SetLabel(blue)


    def EnableMenus(self, evt=None):
        is_3color = len(self.panel.conf.data.shape) > 2
        for menu, on_3color in self.optional_menus:
            menu.Enable(is_3color==on_3color)

    def BuildMenu(self):
        # file menu
        mfile = self.Build_FileMenu(extras=(('Save Image of Colormap',
                                     'Save Image of Colormap',
                                      self.onCMapSave),))

        # options menu
        mview = self.view_menu = wx.Menu()
        MenuItem(self, mview, "Zoom Out\tCtrl+Z",
                 "Zoom out to full data range",
                 self.panel.unzoom)

        m = MenuItem(self, mview, 'Toggle Background Color (Black/White)\tCtrl+W',
                     'Toggle background color for 3-color images',
                     self.onTriColorBG, kind=wx.ITEM_CHECK)

        self.optional_menus.append((m, True))

        mview.AppendSeparator()
        MenuItem(self, mview, 'Rotate clockwise\tCtrl+R', '',
                 partial(self.onFlip, mode='rot_cw'))
        MenuItem(self, mview,  'Flip Top/Bottom\tCtrl+T', '',
                 partial(self.onFlip, mode='flip_ud'))
        MenuItem(self, mview,  'Flip Left/Right\tCtrl+F', '',
                 partial(self.onFlip, mode='flip_lr'))

        mview.AppendSeparator()
        MenuItem(self, mview, 'Projet Horizontally\tCtrl+X', '',
                 partial(self.onProject, mode='x'))
        MenuItem(self, mview, 'Projet Vertically\tCtrl+Y', '',
                 partial(self.onProject, mode='y'))

        mview.AppendSeparator()
        m = MenuItem(self, mview, 'As Contour', 'Shown as contour map',
                     self.onContourToggle, kind=wx.ITEM_CHECK)
        m.Check(False)
        self.optional_menus.append((m, False))

        m = MenuItem(self, mview, 'Configure Contours', 'Configure Contours',
                     self.onContourConfig)
        self.optional_menus.append((m, False))

        # intensity contrast
        mint =self.intensity_menu = wx.Menu()
        MenuItem(self, mint,  'Log Scale Intensity\tCtrl+L',
                 'use logarithm to set intensity scale',
                 self.onLogScale, kind=wx.ITEM_CHECK)

        MenuItem(self, mint, 'Toggle Contrast Enhancement\tCtrl+E',
                 'Toggle contrast between auto-scale and full-scale',
                 self.onEnhanceContrast, kind=wx.ITEM_CHECK)


        MenuItem(self, mint, 'Set Auto-Contrast Level',
                 'Set auto-contrast scale',
                 self.onContrastConfig)

        # smoothing
        msmoo = wx.Menu()
        for itype in Interp_List:
            wid = wx.NewId()
            msmoo.AppendRadioItem(wid, itype, itype)
            self.Bind(wx.EVT_MENU, partial(self.onInterp, name=itype), id=wid)

        # help
        mhelp = wx.Menu()
        MenuItem(self, mhelp, 'Quick Reference',
                 'Quick Reference for WXMPlot', self.onHelp)
        MenuItem(self, mhelp, 'About', 'About WXMPlot', self.onAbout)

        # add all sub-menus, including user-added
        submenus = [('File', mfile),
                    ('Image', mview),
                    ('Contrast', mint),
                    ('Smoothing', msmoo)]
        if self.user_menus is not None:
            submenus.extend(self.user_menus)
        submenus.append(('&Help', mhelp))

        mbar = wx.MenuBar()
        for title, menu in submenus:
            mbar.Append(menu, title)

        self.SetMenuBar(mbar)
        self.Bind(wx.EVT_CLOSE,self.onExit)

    def onInterp(self, evt=None, name=None):
        if name not in Interp_List:
            name = Interp_List[0]
        self.panel.conf.interp = name
        self.panel.redraw()

    def onCursorMode(self, event=None, mode='zoom'):
        self.panel.cursor_mode = mode
        #if wid == self.menuIDs.CUR_PROF:
        #    self.panel.cursor_mode = 'profile'
        #elif wid == self.menuIDs.CUR_LASSO:
        #    self.panel.cursor_mode = 'lasso'

    def onProject(self, event=None, mode='y'):
        wid = event.GetId()
        if mode=='x':
            x = self.panel.ydata
            y = self.panel.conf.data.sum(axis=1)
            axname = 'horizontal'
            if x is None:
                x = np.arange(y.shape[0])

        else:
            x = self.panel.xdata
            y = self.panel.conf.data.sum(axis=0)
            if x is None:
                x = np.arange(y.shape[0])

            axname = 'vertical'
        title = '%s: sum along %s axis' % (self.GetTitle(), axname)

        pf = PlotFrame(title=title, parent=self, size=(500, 250))
        colors = RGB_COLORS
        if self.config_mode.lower()[:3] == 'cmy':
            colors = CMY_COLORS
        if len(y.shape) == 2 and y.shape[1] == 3:
            pf.plot(x, y[:,0], color=colors[0])
            pf.oplot(x, y[:,1], color=colors[1])
            pf.oplot(x, y[:,2], color=colors[2])
        else:
            pf.plot(x, y)
        pf.Raise()
        pf.Show()

    def onFlip(self, event=None, mode=None):
        conf = self.panel.conf
        if mode == 'flip_lr':
            conf.flip_lr = not conf.flip_lr
        elif mode == 'flip_ud':
            conf.flip_ud = not conf.flip_ud
        elif mode == 'flip_orig':
            conf.flip_lr, conf.flip_ud = False, False
        elif mode == 'rot_cw':
            conf.rot = True
        self.panel.unzoom_all()

    def Build_ConfigPanel(self):
        """config panel for left-hand-side of frame: RGB Maps"""
        panel = self.config_panel
        sizer = wx.BoxSizer(wx.VERTICAL)

        lsty = wx.ALIGN_LEFT|wx.LEFT|wx.TOP|wx.EXPAND

        if self.config_mode == 'rgb':
            for icol, col in enumerate(RGB_COLORS):
                self.cmap_panels[icol] =  ColorMapPanel(self.config_panel,
                                                       self.panel,
                                                       title='%s: ' % col.title(),
                                                       color=icol,
                                                       default=col,
                                                       colormap_list=None)

                sizer.Add(self.cmap_panels[icol], 0, lsty, 2)

                sizer.Add(wx.StaticLine(self.config_panel, size=(100, 2),
                                        style=wx.LI_HORIZONTAL), 0, lsty, 2)


        elif self.config_mode == 'cmy':
            for icol, col in enumerate(CMY_COLORS):
                self.cmap_panels[icol] =  ColorMapPanel(self.config_panel,
                                                        self.panel,
                                                        title='%s: ' % col.title(),
                                                        color=icol,
                                                        default=col,
                                                        colormap_list=None)

                sizer.Add(self.cmap_panels[icol], 0, lsty, 2)
                sizer.Add(wx.StaticLine(self.config_panel, size=(100, 2),
                                        style=wx.LI_HORIZONTAL), 0, lsty, 2)


        else:
            self.cmap_panels[0] =  ColorMapPanel(self.config_panel,
                                                 self.panel,
                                                 default='gray',
                                                 colormap_list=ColorMap_List)

            sizer.Add(self.cmap_panels[0],  0, lsty, 1)
            sizer.Add(wx.StaticLine(self.config_panel, size=(100, 2),
                                    style=wx.LI_HORIZONTAL), 0, lsty, 2)

        cust = self.CustomConfig(self.config_panel, None, 0)
        if cust is not None:
            sizer.Add(cust, 0, lsty, 1)
        pack(self.config_panel, sizer)


    def CustomConfig(self, lpanel, lsizer, irow):
        """ override to add custom config panel items
        to bottom of config panel
        """
        pass


    def onContrastConfig(self, event=None):
        dlg = AutoContrastDialog(parent=self, conf=self.panel.conf)
        dlg.CenterOnScreen()
        val = dlg.ShowModal()
        if val == wx.ID_OK:
            pass
        dlg.Destroy()


    def onContourConfig(self, event=None):
        panel = self.panel
        conf = panel.conf
        dlg = ContourDialog(parent=self, conf=conf)
        dlg.CenterOnScreen()
        val = dlg.ShowModal()
        if val == wx.ID_OK:
            pass
        dlg.Destroy()
        if conf.style != 'contour':
            return

        if self.config_mode == 'int':
            self.cmap_panels[0].set_colormap()

        panel.axes.cla()
        panel.display(conf.data, x=panel.xdata, y = panel.ydata,
                      xlabel=panel.xlab, ylabel=panel.ylab,
                      contour_labels=conf.contour_labels,
                      nlevels=conf.ncontour_levels, style='contour')
        panel.redraw()

    def onContourToggle(self, event=None):
        if len(self.panel.conf.data.shape) > 2:
            return
        panel = self.panel
        conf  = panel.conf
        conf.style = 'image'
        if event.IsChecked():
            conf.style = 'contour'
        nlevels = int(conf.ncontour_levels)
        if self.config_mode == 'int':
            self.cmap_panels[0].set_colormap()
        panel.axes.cla()
        panel.display(conf.data, x=panel.xdata, y = panel.ydata,
                      nlevels=nlevels, contour_labels=conf.contour_labels,
                      xlabel=panel.xlab, ylabel=panel.ylab,
                      style=conf.style)
        panel.redraw()

    def onTriColorBG(self, event=None):
        bgcol = {True:'white', False:'black'}[event.IsChecked()]
        conf = self.panel.conf
        if bgcol == conf.tricolor_bg:
            return

        conf.tricolor_bg = bgcol
        cmaps = colors = RGB_COLORS
        if bgcol.startswith('wh'):
            cmaps = ('Reds', 'Greens', 'Blues')

        if self.config_mode.lower()[:3] == 'cmy':
            cmaps = ('Reds', 'Greens', 'Blues')

        self.cmap_panels[0].set_colormap(name=cmaps[0])
        self.cmap_panels[1].set_colormap(name=cmaps[1])
        self.cmap_panels[2].set_colormap(name=cmaps[2])
        self.panel.redraw()

    def onLasso(self, data=None, selected=None, mask=None, **kws):
        if hasattr(self.lasso_callback , '__call__'):
            self.lasso_callback(data=data, selected=selected, mask=mask, **kws)

    def onDataChange(self, data, x=None, y=None, col='int', **kw):
        conf = self.panel.conf
        if len(data.shape) == 2: # intensity map
            imin, imax = data.min(), data.max()
            conf.int_lo[0] = imin
            conf.int_hi[0] = imax
            cpan = self.cmap_panels[0]

            cpan.cmap_lo.SetValue(imin)
            cpan.cmap_hi.SetValue(imax)

            cpan.imin_val.SetValue('%.4g' % imin)
            cpan.imax_val.SetValue('%.4g' % imax)
            cpan.imin_val.Enable()
            cpan.imax_val.Enable()

        else:
            for ix in range(3):
                imin, imax = data[:,:,ix].min(), data[:,:,ix].max()
                conf.int_lo[ix] = imin
                conf.int_hi[ix] = imax
                self.cmap_panels[ix].imin_val.SetValue('%.4g' % imin)
                self.cmap_panels[ix].imax_val.SetValue('%.4g' % imax)
                self.cmap_panels[ix].imin_val.Enable()
                self.cmap_panels[ix].imax_val.Enable()

    def onEnhanceContrast(self, event=None):
        """change image contrast, using scikit-image exposure routines"""
        self.panel.conf.auto_contrast = event.IsChecked()
        self.set_contrast_levels()
        self.panel.redraw()

    def set_contrast_levels(self):
        """enhance contrast levels, or use full data range
        according to value of self.panel.conf.auto_contrast
        """
        conf = self.panel.conf
        img  = self.panel.conf.data
        enhance = conf.auto_contrast
        clevel = conf.auto_contrast_level
        if len(img.shape) == 2: # intensity map
            col = 0
            jmin = imin = img.min()
            jmax = imax = img.max()
            self.cmap_panels[col].imin_val.SetValue('%.4g' % imin)
            self.cmap_panels[col].imax_val.SetValue('%.4g' % imax)
            if enhance:
                jmin, jmax = np.percentile(img, [clevel, 100.0-clevel])

            conf.cmap_lo[col] = xlo = (jmin-imin)*conf.cmap_range/(imax-imin)
            conf.cmap_hi[col] = xhi = (jmax-imin)*conf.cmap_range/(imax-imin)

            # print("Set contrast level =", conf.cmap_hi, conf.cmap_range)

            self.cmap_panels[col].cmap_hi.SetValue(xhi)
            self.cmap_panels[col].cmap_lo.SetValue(xlo)
            self.cmap_panels[col].islider_range.SetLabel('Shown: [ %.4g :  %.4g ]' % (jmin, jmax))
            self.cmap_panels[col].redraw_cmap()

        if len(img.shape) == 3: # rgb/cmy map
            for ix in range(3):
                jmin = imin = img[:,:,ix].min()
                jmax = imax = img[:,:,ix].max()
                self.cmap_panels[ix].imin_val.SetValue('%.4g' % imin)
                self.cmap_panels[ix].imax_val.SetValue('%.4g' % imax)
                if enhance:
                    jmin, jmax = np.percentile(img[:,:,ix], [1, 99])

                conf.cmap_lo[ix] = xlo = (jmin-imin)*conf.cmap_range/(imax-imin)
                conf.cmap_hi[ix] = xhi = (jmax-imin)*conf.cmap_range/(imax-imin)
                self.cmap_panels[ix].cmap_hi.SetValue(xhi)
                self.cmap_panels[ix].cmap_lo.SetValue(xlo)

                self.cmap_panels[ix].islider_range.SetLabel('Shown: [ %.4g :  %.4g ]' % (jmin, jmax))
                self.cmap_panels[ix].redraw_cmap()

    def onLogScale(self, event=None):
        self.panel.conf.log_scale = not self.panel.conf.log_scale
        self.panel.redraw()

    def onCMapSave(self, event=None, col='int'):
        """save color table image"""
        file_choices = 'PNG (*.png)|*.png'
        ofile = 'Colormap.png'

        dlg = wx.FileDialog(self, message='Save Colormap as...',
                            defaultDir=os.getcwd(),
                            defaultFile=ofile,
                            wildcard=file_choices,
                            style=wx.FD_SAVE|wx.FD_CHANGE_DIR)

        if dlg.ShowModal() == wx.ID_OK:
            self.cmap_panels[0].cmap_canvas.print_figure(dlg.GetPath(), dpi=600)

    def save_figure(self,event=None, transparent=True, dpi=600):
        """ save figure image to file"""
        if self.panel is not None:
            self.panel.save_figure(event=event,
                                   transparent=transparent, dpi=dpi)
