#!/usr/bin/python
"""
wxmplot ImageFrame: a wx.Frame for image display, using matplotlib
"""
import os
from functools import partial

import wx
from wx.lib.agw.floatspin import FloatSpin, EVT_FLOATSPIN
import wx.lib.colourselect as csel

import numpy as np

import matplotlib.cm as cmap
from matplotlib.figure import Figure
from matplotlib.ticker import NullFormatter
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

from wxutils import get_cwd

from .imagepanel import ImagePanel
from .imageconf import (ColorMap_List, Interp_List, Contrast_List,
                        Contrast_NDArray, Slices_List, RGB_COLORS,
                        ImageConfigFrame)
from .baseframe import BaseFrame
from .plotframe import PlotFrame
from .colors import rgb2hex, mpl_color
from .utils import LabeledTextCtrl, MenuItem, pack, gformat


CURSOR_MENULABELS = {'zoom':  ('Zoom to Rectangle\tCtrl+B',
                               'Left-Drag to zoom to rectangular box'),
                     'lasso': ('Select Points\tCtrl+V',
                               'Left-Drag to select points freehand'),
                     'prof':  ('Select Line Profile\tCtrl+K',
                               'Left-Drag to select like for profile')}

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
        cmapname = default
        if colormap_list is not None:
            cmap_choice =  wx.Choice(self, size=(90, -1), choices=colormap_list)
            cmap_choice.Bind(wx.EVT_CHOICE,  self.onCMap)
            self.cmap_choice = cmap_choice

            if cmapname is None:
                cmapname = colormap_list[0]

            if cmapname.endswith('_r'):
                reverse = True
                cmapname = cmap[:-2]
            cmap_choice.SetStringSelection(cmapname)

            cmap_reverse = wx.CheckBox(self, label='Reverse', size=(60, -1))
            cmap_reverse.Bind(wx.EVT_CHECKBOX, self.onCMapReverse)
            cmap_reverse.SetValue(reverse)
            self.cmap_reverse = cmap_reverse

        if cmapname is None:
            cmapname = 'gray'
        self.imgpanel.conf.cmap[color] = cmap.get_cmap(cmapname)

        maxval = self.imgpanel.conf.cmap_range
        wd, ht = 1.00, 0.125

        self.cmap_dat = np.outer(np.ones(int(maxval*ht)),
                                 np.linspace(0, 1, maxval))

        fig = Figure((wd, ht), dpi=150)

        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_axis_off()
        self.cmap_canvas = FigureCanvas(self, -1, figure=fig)

        self.cmap_img = ax.imshow(self.cmap_dat, cmap=cmapname,
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

        self.imin_val = LabeledTextCtrl(self, 0, size=(80, -1),
                                        labeltext='Range:',
                                        action=partial(self.onThreshold, argu='lo'))
        self.imax_val = LabeledTextCtrl(self, maxval, size=(80, -1), labeltext=':',
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
        self.set_colormap(cmapname)


    def onCMap(self, event=None):
        if event is not None:
            self.set_colormap(name=event.GetString())
            self.imgpanel.redraw()
            if callable(self.cmap_callback):
                self.cmap_callback(name=event.GetString())


    def onCMapReverse(self, event=None):
        self.set_colormap()
        self.imgpanel.redraw()

    def set_colormap(self, name=None):
        conf = self.imgpanel.conf
        try:
            if name is None:
                name = self.cmap_choice.GetStringSelection()
        except:
            return

        try:
            reverse = (1 == int(self.cmap_reverse.GetValue()))
        except:
            reverse = False

        conf.set_colormap(name, reverse=reverse, icol=self.icol)
        self.redraw_cmap()


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
        self.cmap_lo.SetValue(float(lo))
        self.cmap_hi.SetValue(float(hi))
        conf.cmap_lo[col] = lo
        conf.cmap_hi[col] = hi
        imin = float(self.imin_val.GetValue())
        imax = float(self.imax_val.GetValue())
        xlo = imin + (imax-imin)*lo/conf.cmap_range
        xhi = imin + (imax-imin)*hi/conf.cmap_range
        self.islider_range.SetLabel('Shown: [%.4g: %.4g]' % (xlo, xhi))
        self.redraw_cmap()
        self.imgpanel.redraw()


class InterpPanel(wx.Panel):
    """interpoloation / smoothing panel"""
    def __init__(self, parent, imgpanel, default=0, callback=None, **kws):
        wx.Panel.__init__(self, parent, -1,  **kws)

        self.imgpanel = imgpanel
        self.callback = callback
        labstyle = wx.ALIGN_LEFT|wx.LEFT|wx.TOP|wx.EXPAND
        sizer = wx.GridBagSizer(2, 2)

        title = wx.StaticText(self, label='Smoothing:', size=(120, -1))
        sizer.Add(title, (0, 0), (1, 1), labstyle, 2)

        interp_choice =  wx.Choice(self, size=(100, -1), choices=Interp_List)
        interp_choice.Bind(wx.EVT_CHOICE,  self.onInterp)
        interp_choice.SetSelection(default)

        sizer.Add(interp_choice,  (0, 1), (1, 2), labstyle, 2)
        pack(self, sizer)

    def onInterp(self, event=None):
        name=event.GetString()
        if name not in Interp_List:
            name = Interp_List[0]
        self.imgpanel.conf.interp = name
        self.imgpanel.redraw()
        if callable(self.callback):
            self.callback(name=name)

class ContrastPanel(wx.Panel):
    """auto-contrast panel"""
    def __init__(self, parent, default=0, callback=None, **kws):
        wx.Panel.__init__(self, parent, -1,  **kws)

        self.callback = callback
        labstyle = wx.ALIGN_LEFT|wx.LEFT|wx.TOP|wx.EXPAND
        sizer = wx.GridBagSizer(2, 2)

        title = wx.StaticText(self, label='Auto-Contrast (%):', size=(120, -1))
        sizer.Add(title, (0, 0), (1, 1), labstyle, 2)

        self.choice = wx.Choice(self, size=(100, -1), choices=Contrast_List)
        self.choice.Bind(wx.EVT_CHOICE,  self.onChoice)
        self.choice.SetSelection(default)
        sizer.Add(self.choice, (0, 1), (1, 1), labstyle, 2)
        pack(self, sizer)

    def set(self, choice=None):
        if choice in Contrast_List:
            self.SetStringSelection(choice)

    def advance(self):
        clevel = 1 + self.choice.GetSelection()
        if clevel >= len(Contrast_List):
            clevel = 0
        self.choice.SetSelection(clevel)
        clevel = Contrast_List[clevel]
        if clevel == 'None':
            clevel = 0
        else:
            clevel = float(clevel)
        self.callback(contrast_level=clevel)

    def retreat(self):
        clevel = -1 + self.choice.GetSelection()
        if clevel < 0:
            clevel = len(Contrast_List) - 1
        self.choice.SetSelection(clevel)
        clevel = Contrast_List[clevel]
        if clevel == 'None':
            clevel = 0
        else:
            clevel = float(clevel)
        self.callback(contrast_level=clevel)


    def onChoice(self, event=None):
        if callable(self.callback):
            clevel = event.GetString()
            if clevel == 'None':
                clevel = 0
            else:
                clevel = float(clevel)
            self.callback(contrast_level=clevel)




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

"""

    def __init__(self, parent=None, size=(750, 625), lasso_callback=None,
                 mode='intensity', show_xsections=False,
                 cursor_labels=None, output_title='Image', subtitles=None,
                 user_menus=None, title='Image Display Frame', **kws):

        self.lasso_callback = lasso_callback
        self.user_menus = user_menus
        self.cursor_menulabels =  {}
        self.cursor_menulabels.update(CURSOR_MENULABELS)
        if cursor_labels is not None:
            self.cursor_menulabels.update(cursor_labels)

        BaseFrame.__init__(self, parent=parent, title=title,
                           output_title=output_title, size=size, **kws)

        self.cmap_panels = {}
        self.subtitles = {}
        self.config_mode = None
        if subtitles is not None:
            self.subtitles = subtitles
        sbar_widths = [-2, -1, -1]
        sbar = self.CreateStatusBar(len(sbar_widths), wx.CAPTION)
        sfont = sbar.GetFont()
        sfont.SetWeight(wx.BOLD)
        sfont.SetPointSize(10)
        sbar.SetFont(sfont)
        self.SetStatusWidths(sbar_widths)

        self.optional_menus = []
        self.win_config = None
        self.bgcol = rgb2hex(self.GetBackgroundColour()[:3])

        self.panel = ImagePanel(self, data_callback=self.onDataChange,
                                size=(650, 725), dpi=100,
                                lasso_callback=self.onLasso,
                                output_title=self.output_title)

        self.panel.nstatusbar = sbar.GetFieldsCount()
        self.BuildMenu()

        self.SetBackgroundColour('#F8F8F4')

        self.config_panel = wx.Panel(self)
        self.imin_val = {}
        self.imax_val = {}
        self.islider_range = {}

        self.config_mode = 'int'
        if mode.lower().startswith('rgb'):
            self.config_mode = 'rgb'

        self.Build_ConfigPanel()

        self.panel.messenger = self.write_message

        mainsizer = wx.BoxSizer(wx.HORIZONTAL)

        mainsizer.Add(self.config_panel, 0,
                      wx.LEFT|wx.ALIGN_LEFT|wx.TOP|wx.ALIGN_TOP|wx.EXPAND)

        mainsizer.Add(self.panel,  1, wx.ALL|wx.GROW)
        self.SetSizer(mainsizer)
        self.SetSize(self.GetBestVirtualSize())

    def display(self, img, title=None, colormap=None, style='image',
                subtitles=None, auto_contrast=False, contrast_level=None, **kws):
        """display image"""
        if title is not None:
            self.SetTitle(title)
        if subtitles is not None:
            self.subtitles = subtitles
        cmode = self.config_mode.lower()[:3]
        img = np.array(img)

        if len(img.shape) == 3:
            ishape = img.shape
            # make sure 3d image is shaped (NY, NX, 3)
            if ishape[2] != 3:
                if ishape[0] == 3:
                    img = img.swapaxes(0, 1).swapaxes(1, 2)
                elif ishape[1] == 3:
                    img = img.swapaxes(1, 2)

            if cmode != 'rgb':
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

        if contrast_level is None:
            if auto_contrast:
                cl_str = '1.0'
            else:
                cl_str = self.contrast_panel.choice.GetStringSelection()
        else:
            cl_int = max(np.where(Contrast_NDArray<=contrast_level)[0])
            cl_str = Contrast_List[cl_int]

        if cl_str == 'None':
            contrast_level = 0
        else:
            contrast_level = float(cl_str)

        self.contrast_panel.choice.SetStringSelection(cl_str)
        self.panel.conf.contrast_level = contrast_level

        self.panel.display(img, style=style, contrast_level=contrast_level,
                           colormap=colormap, **kws)

        self.set_contrast_levels(contrast_level=contrast_level)

        self.panel.conf.title = title
        if colormap is not None and self.config_mode == 'int':
            self.cmap_panels[0].cmap_choice.SetStringSelection(colormap)
            self.cmap_panels[0].set_colormap(name=colormap)

        if subtitles is not None:
            if isinstance(subtitles, dict):
                self.set_subtitles(**subtitles)
            elif self.config_mode == 'int':
                self.set_subtitles(red=subtitles)

        self.panel.conf.style = 'image'
        self.contrast_panel.Enable()

        if style == 'contour':
            self.panel.conf.style = 'contour'
            self.contrast_panel.Disable()
            # self.interp_panel.Disable()

        self.config_panel.Refresh()
        self.SendSizeEvent()
        wx.CallAfter(self.EnableMenus)

    def configure(self, event=None):
        """show configuration frame"""
        if self.win_config is not None:
            try:
                self.win_config.Raise()
            except:
                self.win_config = None

        if self.win_config is None:
            self.win_config = ImageConfigFrame(parent=self,
                                               config=self.panel.conf)

            self.win_config.Raise()


    def set_subtitles(self, red=None, green=None, blue=None, **kws):
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

        # image menua
        mview = self.view_menu = wx.Menu()
        conf = self.panel.conf


        MenuItem(self, mview, "Zoom Out\tCtrl+Z", "Zoom out to full data range",
                 self.panel.unzoom)

        MenuItem(self, mview, "Configure\tCtrl+K", "Configure Image Options",
                 self.configure)

        mview.AppendSeparator()
        MenuItem(self, mview, 'Enhance Contrast Cycle\tCtrl++',
                 'Cycle Through Contrast Choices', self.cycle_contrast)

        MenuItem(self, mview, 'Reduce Contrast Cycle\tCtrl+-',
                 'Cycle Through Contrast Choices',
                 partial(self.cycle_contrast, dir='back'))


        mview.AppendSeparator()
        MenuItem(self, mview, 'Show Histogram\tCtrl+H',
                 'Show Intensity Histogram', self.show_histogram)

        m = MenuItem(self, mview, 'Toggle Axes Labels\tCtrl+A',
                     'Toggle displacy of Axis labels',
                     self.onAxesLabels, kind=wx.ITEM_CHECK,
                     checked=conf.show_axis)

        m = MenuItem(self, mview, 'Toggle Grid Lines\tCtrl+G',
                     'Toggle displacy of Grid Lines at Axis labels',
                     self.onAxesGrid, kind=wx.ITEM_CHECK,
                     checked=conf.show_grid)

        m = MenuItem(self, mview, 'Toggle Contour Plot\tCtrl+N',
                     'Shown as Contour Plot',
                     self.onContourToggle, kind=wx.ITEM_CHECK,
                     checked=conf.style=='contour')
        self.optional_menus.append((m, False))

        m = MenuItem(self, mview, 'Toggle Scalebar\tCtrl+B', 'Show Scalebar',
                     self.onScalebarToggle, checked=conf.scalebar_show,
                     kind=wx.ITEM_CHECK)

        m = MenuItem(self, mview,
                     'Toggle Background Color (Black/White)\tCtrl+W',
                     'Toggle background color for 3-color images',
                     self.onTriColorBG, kind=wx.ITEM_CHECK,
                     checked=conf.tricolor_bg == 'white')
        self.optional_menus.append((m, True))

        mslice = wx.Menu()
        m1 = MenuItem(self, mslice, 'Show No X/Y Slices', 'Do not show X/Y slices',
                      self.onSliceChoice, kind=wx.ITEM_RADIO)
        m2 = MenuItem(self, mslice, 'Show X (Horizontal) Slices\tCtrl+x',
                      'show X slices',
                      self.onSliceChoice, kind=wx.ITEM_RADIO)
        m3 = MenuItem(self, mslice, 'Show Y (Vertical) Slices\tCtrl+Y', 'show Y slices',
                      self.onSliceChoice, kind=wx.ITEM_RADIO)
        self.slice_menus = {m1.GetId(): 'None', m2.GetId(): 'X', m3.GetId(): 'Y'}
        m = MenuItem(self, mslice, 'Slices Follow Mouse Motion?',
                     'Update Slices on Mouse Motion',
                     self.onSliceDynamic, checked=conf.slice_onmotion,
                     kind=wx.ITEM_CHECK)



        mrot = wx.Menu()
        MenuItem(self, mrot, 'Rotate clockwise\tCtrl+R', '',
                 partial(self.onFlip, mode='rot_cw'))
        MenuItem(self, mrot,  'Flip Top/Bottom\tCtrl+T', '',
                 partial(self.onFlip, mode='flip_ud'))
        MenuItem(self, mrot,  'Flip Left/Right\tCtrl+F', '',
                 partial(self.onFlip, mode='flip_lr'))
        MenuItem(self, mrot,  'Reset Flips/Rotations', '',
                 partial(self.onFlip, mode='restore'))


        msmooth = wx.Menu()
        self.smooth_menus = {}
        for sname in Interp_List:
            m = MenuItem(self, msmooth, sname, sname,
                         self.onSmoothChoice, kind=wx.ITEM_RADIO)
            self.smooth_menus[m.GetId()] = sname

        # help
        mhelp = wx.Menu()
        MenuItem(self, mhelp, 'Quick Reference',
                 'Quick Reference for WXMPlot', self.onHelp)
        MenuItem(self, mhelp, 'About', 'About WXMPlot', self.onAbout)

        # add all sub-menus, including user-added
        submenus = [('File', mfile),
                    ('Image', mview),
                    ('X/Y Slices', mslice),
                    ('Orientation', mrot),
                    ('Smoothing', msmooth)]
        if self.user_menus is not None:
            submenus.extend(self.user_menus)

        submenus.append(('&Help', mhelp))

        mbar = wx.MenuBar()
        for title, menu in submenus:
            mbar.Append(menu, title)

        self.SetMenuBar(mbar)
        self.Bind(wx.EVT_CLOSE,self.onExit)

    def onCursorMode(self, event=None, mode='zoom'):
        self.panel.cursor_mode = mode

    def onFlip(self, event=None, mode=None):
        panel = self.panel
        if mode == 'flip_lr':
            panel.flip_horiz()
        elif mode == 'flip_ud':
            panel.flip_vert()
        elif mode == 'rot_cw':
            panel.rotate90()
        elif mode == 'restore':
            panel.restore_flips_rotations()
        panel.unzoom_all()

    def Build_ConfigPanel(self):
        """config panel for left-hand-side of frame: RGB Maps"""
        panel = self.config_panel

        sizer = wx.BoxSizer(wx.VERTICAL)
        lsty = wx.ALIGN_LEFT|wx.LEFT|wx.TOP|wx.EXPAND

        self.contrast_panel = ContrastPanel(panel,
                                            callback=self.set_contrast_levels)

        if self.config_mode == 'rgb':
            for icol, col in enumerate(RGB_COLORS):
                self.cmap_panels[icol] =  ColorMapPanel(panel, self.panel,
                                                        title='%s: ' % col.title(),
                                                        color=icol,
                                                        default=col,
                                                        colormap_list=None)
                sizer.Add(self.cmap_panels[icol], 0, lsty, 2)

        else:
            self.cmap_panels[0] =  ColorMapPanel(panel, self.panel,
                                                 default='gray',
                                                 colormap_list=ColorMap_List)

            sizer.Add(self.cmap_panels[0],  0, lsty, 1)

        sizer.Add(self.contrast_panel, 0, lsty, 2)
        sizer.Add(wx.StaticLine(panel, size=(100, 2),
                                style=wx.LI_HORIZONTAL), 0, lsty, 2)

        cust = self.CustomConfig(panel, None, 0)
        if cust is not None:
            sizer.Add(cust, 0, lsty, 1)
        pack(panel, sizer)


    def CustomConfig(self, lpanel, lsizer, irow):
        """ override to add custom config panel items
        to bottom of config panel
        """
        pass

    def onSliceChoice(self, event=None):
        if event is not None:
            name = self.slice_menus.get(event.GetId(), Slices_List[0])
            self.panel.conf.slices = name
        self.panel.update_slices()

    def onSliceDynamic(self, event=None):
        conf  = self.panel.conf
        conf.slice_onmotion = not conf.slice_onmotion

    def onScalebarToggle(self, event=None):
        conf  = self.panel.conf
        conf.scalebar_show = not conf.scalebar_show
        self.panel.redraw()


    def onSmoothChoice(self, event=None):
        name = self.smooth_menus.get(event.GetId(), Interp_List[0])
        self.panel.conf.interp = name
        self.panel.redraw()

    def onContourToggle(self, event=None):
        if len(self.panel.conf.data.shape) > 2:
            return
        panel = self.panel
        conf  = panel.conf

        is_contour = event is None or event.IsChecked()
        conf.style = {True: 'contour', False: 'image'}[is_contour]
        self.contrast_panel.Enable(not is_contour)

        nlevels = int(conf.ncontour_levels)
        if self.config_mode == 'int':
            self.cmap_panels[0].set_colormap()
        panel.axes.cla()
        panel.display(conf.data, x=conf.xdata, y=conf.ydata, nlevels=nlevels,
                      contour_labels=conf.contour_labels, style=conf.style,
                      xlabel=conf.xlab, ylabel=conf.ylab)
        panel.redraw()

    def onAxesLabels(self, event=None):
        conf = self.panel.conf
        conf.show_axis = not conf.show_axis
        self.panel.autoset_margins()
        self.panel.redraw()

    def onAxesGrid(self, event=None):
        conf = self.panel.conf
        conf.show_grid = not conf.show_grid
        if conf.show_axis:
            self.panel.autoset_margins()
            self.panel.redraw()

    def onSliceMotion(self, event=None):
        conf = self.panel.conf
        conf.slice_onmotion = not conf.slice_onmotion
        self.panel.redraw()

    def onTriColorBG(self, event=None):
        bgcol = {True:'white', False:'black'}[event.IsChecked()]
        conf = self.panel.conf
        if bgcol == conf.tricolor_bg:
            return

        conf.tricolor_bg = bgcol
        cmaps = colors = RGB_COLORS
        if bgcol.startswith('wh'):
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

    def cycle_contrast(self, event=None, dir='fore'):
        if dir.startswith('f'):
            self.contrast_panel.advance()
        else:
            self.contrast_panel.retreat()

    def set_contrast_levels(self, contrast_level=None):
        """enhance contrast levels, or use full data range
        according to value of self.panel.conf.contrast_level
        """
        if contrast_level is None:
            clevel = self.contrast_panel.choice.GetStringSelection()
            if clevel == 'None':
                contrast_level = 0
            else:
                contrast_level = float(clevel)

        conf = self.panel.conf
        img  = self.panel.conf.data
        if contrast_level is None:
            contrast_level = 0
        conf.contrast_level = contrast_level
        clevels = [contrast_level, 100.0-contrast_level]

        if len(img.shape) == 2: # intensity map
            col = 0
            jmin = imin = img.min()
            jmax = imax = img.max()
            self.cmap_panels[col].imin_val.SetValue('%.4g' % imin)
            self.cmap_panels[col].imax_val.SetValue('%.4g' % imax)

            jmin, jmax = np.percentile(img, clevels)
            if imax == imin:
                imax = imin + 0.5
            conf.cmap_lo[col] = xlo = int((jmin-imin)*conf.cmap_range/(imax-imin))
            conf.cmap_hi[col] = xhi = int((jmax-imin)*conf.cmap_range/(imax-imin))

            self.cmap_panels[col].cmap_hi.SetValue(xhi)
            self.cmap_panels[col].cmap_lo.SetValue(xlo)
            self.cmap_panels[col].islider_range.SetLabel('Shown: [ %.4g :  %.4g ]' % (jmin, jmax))
            self.cmap_panels[col].redraw_cmap()

        if len(img.shape) == 3: # rgb map
            for ix in range(3):
                jmin = imin = img[:,:,ix].min()
                jmax = imax = img[:,:,ix].max()
                self.cmap_panels[ix].imin_val.SetValue('%.4g' % imin)
                self.cmap_panels[ix].imax_val.SetValue('%.4g' % imax)

                jmin, jmax = np.percentile(img[:,:,ix], clevels)
                if imax == imin:
                    imax = imin + 0.5
                conf.cmap_lo[ix] = xlo = int((jmin-imin)*conf.cmap_range/(imax-imin))
                conf.cmap_hi[ix] = xhi = int((jmax-imin)*conf.cmap_range/(imax-imin))
                self.cmap_panels[ix].cmap_hi.SetValue(xhi)
                self.cmap_panels[ix].cmap_lo.SetValue(xlo)

                self.cmap_panels[ix].islider_range.SetLabel('Shown: [ %.4g :  %.4g ]' % (jmin, jmax))
                self.cmap_panels[ix].redraw_cmap()
        self.panel.redraw()

    def show_grid(self, event=None):
        conf = self.panel.conf


    def show_histogram(self, event=None):
        conf = self.panel.conf
        img  = conf.data

        title = '%s: Histogram' % (self.GetTitle())
        dat, color = None, None

        if len(img.shape) == 2:
            nbins = min(101, img.size)
            dat = img.flatten()

        elif len(img.shape) == 3:
            nbins = int(min(101, img.size/3))
            color = ('red', 'green', 'blue')
            dat = [img[:,:,i].flatten() for i in range(3)]
            dat = np.array(dat).transpose()

        if dat is not None:
            pf = PlotFrame(title=title, parent=self)
            if color is None:
                color = pf.panel.conf.traces[0].color
            pf.panel.axes.hist(dat, bins=nbins, rwidth=0.75, color=color,
                               stacked=(len(dat.shape)==2))
            pf.panel.conf.relabel(xlabel='Intensity', ylabel='Population')
            pf.Raise()
            pf.Show()


    def onCMapSave(self, event=None, col='int'):
        """save color table image"""
        file_choices = 'PNG (*.png)|*.png'
        ofile = 'Colormap.png'
        dlg = wx.FileDialog(self, message='Save Colormap as...',
                            defaultDir=get_cwd(),
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


    def ExportTextFile(self, fname, title='unknown map'):
        buff = ["# Map Data for %s" % title,
                "#-------------------------------------"]
        data = self.panel.conf.data
        narr = 1
        labels = [' Y', ' X']
        if len(data.shape) == 3:
            ny, nx, narr = data.shape
            labels.extend(['Map%d' % (i+1) for i in range(narr)])
        else:
            ny, nx = data.shape
            labels.append('Map')

        labels = [(' '*(11-len(l)) + l + ' ') for l in labels]
        buff.append("#%s" % ('  '.join(labels)))
        xdata = np.arange(nx)
        ydata = np.arange(ny)
        if self.panel.conf.xdata is not None:
            xdata = self.panel.conf.xdata
        if self.panel.conf.ydata is not None:
            ydata = self.panel.conf.ydata

        for iy in range(ny):
            for ix in range(nx):
                darr = [ydata[iy], xdata[ix]]
                if narr == 1:
                    darr.append(data[iy, ix])
                else:
                    darr.extend(data[iy, ix])
                buff.append("  ".join([gformat(arr, 12) for arr in darr]))
        buff.append("")
        with open(fname, 'w') as fout:
            fout.write("\n".join(buff))
        fout.close()
