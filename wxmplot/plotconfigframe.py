#!/usr/bin/python
#
# wxmplott GUI to Configure Line Plots
#
import os
from functools import partial
import yaml
import numpy as np

import wx
import wx.lib.colourselect  as csel
import wx.lib.agw.flatnotebook as flat_nb

import wx.lib.scrolledpanel as scrolled
from wxutils import get_cwd
from .utils import LabeledTextCtrl, MenuItem, Choice, FloatSpin
from .config import PlotConfig
from .colors import hexcolor, hex2rgb, mpl_color

FNB_STYLE = flat_nb.FNB_NO_X_BUTTON|flat_nb.FNB_SMART_TABS|flat_nb.FNB_NO_NAV_BUTTONS|flat_nb.FNB_NODRAG

ISPINSIZE = 65
FSPINSIZE = 65

def autopack(panel, sizer):
    panel.SetAutoLayout(True)
    panel.SetSizer(sizer)
    sizer.Fit(panel)

def ffmt(val):
    """format None or floating point as string"""
    if val is not None:
        try:
            return "%.5g" % val
        except:
            pass
    return repr(val)


def clean_texmath(txt):
    """
    clean tex math string, preserving control sequences
    (incluing \n, so also '\nu') inside $ $, while allowing
    \n and \t to be meaningful in the text string
    """
    s = "%s " % txt
    out = []
    i = 0
    while i < len(s)-1:
        if s[i] == '\\' and s[i+1] in ('n', 't'):
            if s[i+1] == 'n':
                out.append('\n')
            elif s[i+1] == 't':
                out.append('\t')
            i += 1
        elif s[i] == '$':
            j = s[i+1:].find('$')
            if j < 0:
                j = len(s)
            out.append(s[i:j+2])
            i += j+2
        else:
            out.append(s[i])
        i += 1
        if i > 5000:
            break
    return ''.join(out).strip()

class PlotConfigFrame(wx.Frame):
    """ GUI Configure Frame"""
    def __init__(self, parent=None, config=None, trace_color_callback=None):
        if config is None:
            config = PlotConfig()
        self.conf   = config
        if callable(trace_color_callback):
            self.conf.trace_color_callback = trace_color_callback

        self.parent = parent
        self.canvas = self.conf.canvas
        self.axes = self.canvas.figure.get_axes()
        self.conf.relabel()
        self.show_legend_cbs = []
        self.DrawPanel()
        mbar = wx.MenuBar()

        fmenu = wx.Menu()
        MenuItem(self, fmenu, "Save Configuration\tCtrl+S",
                 "Save Configuration",
                 self.save_config)
        MenuItem(self, fmenu, "Load Configuration\tCtrl+R",
                 "Load Configuration",
                 self.load_config)
        mbar.Append(fmenu, 'File')
        self.SetMenuBar(mbar)

    def save_config(self, evt=None, fname='wxmplot.yaml'):
        file_choices = 'YAML Config File (*.yaml)|*.yaml'
        dlg = wx.FileDialog(self, message='Save plot configuration',
                            defaultDir=get_cwd(),
                            defaultFile=fname,
                            wildcard=file_choices,
                            style=wx.FD_SAVE|wx.FD_CHANGE_DIR)

        if dlg.ShowModal() == wx.ID_OK:
            conf = self.conf.get_current_config()
            ppath = os.path.abspath(dlg.GetPath())
            with open(ppath, 'w') as fh:
                fh.write("%s\n" % yaml.dump(conf))


    def load_config(self, evt=None):
        file_choices = 'YAML Config File (*.yaml)|*.yaml'
        dlg = wx.FileDialog(self, message='Read plot configuration',
                            defaultDir=get_cwd(),
                            wildcard=file_choices,
                            style=wx.FD_OPEN)

        if dlg.ShowModal() == wx.ID_OK:
            conf = yaml.safe_load(open(os.path.abspath(dlg.GetPath()), 'r').read())
            self.conf.load_config(conf)


    def DrawPanel(self):
        style = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, self.parent, -1, 'Configure Plot', style=style)
        bgcol = hex2rgb('#FEFEFE')
        panel = wx.Panel(self, -1)
        panel.SetBackgroundColour(bgcol)

        font = wx.Font(12,wx.SWISS,wx.NORMAL,wx.NORMAL,False)
        panel.SetFont(font)

        self.nb = flat_nb.FlatNotebook(panel, wx.ID_ANY, agwStyle=FNB_STYLE)

        self.nb.SetActiveTabColour((253, 253, 230))
        self.nb.SetTabAreaColour((bgcol[0]-8, bgcol[1]-8, bgcol[2]-8))
        self.nb.SetNonActiveTabTextColour((10, 10, 100))
        self.nb.SetActiveTabTextColour((100, 10, 10))
        self.nb.AddPage(self.make_linetrace_panel(parent=self.nb, font=font),
                        'Colors and Line Properties', True)
        self.nb.AddPage(self.make_range_panel(parent=self.nb, font=font),
                        'Ranges and Margins', True)
        self.nb.AddPage(self.make_text_panel(parent=self.nb, font=font),
                        'Text, Labels, Legends', True)
        self.nb.AddPage(self.make_scatter_panel(parent=self.nb, font=font),
                        'Scatterplot Settings',
                        self.conf.plot_type == 'scatter')
        for i in range(self.nb.GetPageCount()):
            self.nb.GetPage(i).SetBackgroundColour(bgcol)

        self.nb.SetSelection(0)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sty = wx.ALIGN_LEFT|wx.LEFT|wx.TOP|wx.BOTTOM|wx.EXPAND

        sizer.Add(self.nb, 1, wx.GROW|sty, 3)
        autopack(panel, sizer)
        self.SetMinSize((875, 250))
        self.SetSize((975, 450))
        self.Show()
        self.Raise()

    def make_range_panel(self, parent, font=None):
        # bounds, margins, scales
        panel = wx.Panel(parent)
        if font is None:
            font = wx.Font(12,wx.SWISS,wx.NORMAL,wx.NORMAL,False)

        sizer = wx.GridBagSizer(4, 4)
        labstyle= wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL
        mtitle = wx.StaticText(panel, -1, 'Linear/Log Scale: ')

        logchoice = wx.Choice(panel, choices=self.conf.log_choices,  size=(200,-1))
        logchoice.SetStringSelection("x %s / y %s" % (self.conf.xscale, self.conf.yscale))
        logchoice.Bind(wx.EVT_CHOICE, self.onLogScale)

        sizer.Add(mtitle,     (1, 0), (1,1), labstyle, 2)
        sizer.Add(logchoice,  (1, 1), (1,3), labstyle, 2)


        # Zoom
        ztitle = wx.StaticText(panel, -1, 'Zoom Style: ')
        zoomchoice = wx.Choice(panel, choices=self.conf.zoom_choices, size=(200,-1))
        if self.conf.zoom_style in self.conf.zoom_choices:
            zoomchoice.SetStringSelection(self.conf.zoom_style)
        zoomchoice.Bind(wx.EVT_CHOICE, self.onZoomStyle)
        sizer.Add(ztitle,      (2, 0), (1,1), labstyle, 2)
        sizer.Add(zoomchoice,  (2, 1), (1,3), labstyle, 2)

        # Bounds
        axes = self.canvas.figure.get_axes()
        laxes = axes[0]
        raxes = None
        if len(axes) > 1:
            raxes = axes[1]
        try:
            user_lims = self.conf.user_limits[laxes]
        except:
            user_lims = 4*[None]
        auto_b  = wx.CheckBox(panel,-1, ' From Data ', (-1, -1), (-1, -1))
        auto_b.Bind(wx.EVT_CHECKBOX,self.onAutoBounds)
        try:
            auto_b.SetValue(self.conf.user_limits[laxes] == 4*[None])
        except:
            pass

        xb0, xb1 = laxes.get_xlim()
        yb0, yb1 = laxes.get_ylim()
        if user_lims[0] is not None: xb0 = user_lims[0]
        if user_lims[1] is not None: xb1 = user_lims[1]

        if user_lims[2] is not None: yb0 = user_lims[2]
        if user_lims[3] is not None: yb1 = user_lims[3]

        y2b0, y2b1 = [None, None]
        if raxes is not None:
            y2b0, y2b1 = raxes.get_ylim()
            user_lims = self.conf.user_limits[raxes]
            if user_lims[2] is not None: y2b0 = user_lims[2]
            if user_lims[3] is not None: y2b1 = user_lims[3]

        opts = dict(size=(100, -1), labeltext='', action=self.onBounds)

        self.xbounds  = [LabeledTextCtrl(panel,value=ffmt(xb0), **opts),
                         LabeledTextCtrl(panel,value=ffmt(xb1), **opts)]
        self.ybounds  = [LabeledTextCtrl(panel,value=ffmt(yb0), **opts),
                         LabeledTextCtrl(panel,value=ffmt(yb1), **opts)]
        self.y2bounds = [LabeledTextCtrl(panel,value=ffmt(y2b0), **opts),
                         LabeledTextCtrl(panel,value=ffmt(y2b1), **opts)]

        self.vpad_val = FloatSpin(panel, value=2.5, min_val=0, max_val=100,
                                  increment=0.5, digits=2,
                                  size=(FSPINSIZE, -1),
                                  action=self.onViewPadEvent)

        if user_lims == 4*[None]:
            [w.Disable() for w in self.xbounds]
            [w.Disable() for w in self.ybounds]

        if raxes is None:
            [w.Disable() for w in self.y2bounds]

        btext  = 'Plot Boundaries : '
        ptext  = ' Padding (% of Data Range): '
        xtext  = '   X axis:'
        ytext  = '   Y axis:'
        y2text = '   Y2 axis:'
        def showtext(t):
            return wx.StaticText(panel, -1, t)

        sizer.Add(showtext(btext),  (3, 0), (1, 1), labstyle, 2)
        sizer.Add(auto_b,           (3, 1), (1, 1), labstyle, 2)
        sizer.Add(showtext(ptext),  (3, 2), (1, 2), labstyle, 2)
        sizer.Add(self.vpad_val,     (3, 4), (1, 1), labstyle, 2)

        sizer.Add(showtext(xtext),  (4, 0), (1, 1), labstyle, 2)
        sizer.Add(self.xbounds[0],  (4, 1), (1, 1), labstyle, 2)
        sizer.Add(showtext(' : '),  (4, 2), (1, 1), labstyle, 2)
        sizer.Add(self.xbounds[1],  (4, 3), (1, 1), labstyle, 2)

        sizer.Add(showtext(ytext),  (5, 0), (1, 1), labstyle, 2)
        sizer.Add(self.ybounds[0],  (5, 1), (1, 1), labstyle, 2)
        sizer.Add(showtext(' : '),  (5, 2), (1, 1), labstyle, 2)
        sizer.Add(self.ybounds[1],  (5, 3), (1, 1), labstyle, 2)

        sizer.Add(showtext(y2text), (6, 0), (1, 1), labstyle, 2)
        sizer.Add(self.y2bounds[0], (6, 1), (1, 1), labstyle, 2)
        sizer.Add(showtext(' : '),  (6, 2), (1, 1), labstyle, 2)
        sizer.Add(self.y2bounds[1], (6, 3), (1, 1), labstyle, 2)

        # Margins
        _left, _top, _right, _bot = ["%.3f"% x for x in self.conf.margins]

        mtitle = wx.StaticText(panel, -1, 'Plot Margins: ')
        ltitle = wx.StaticText(panel, -1, ' Left:   ')
        rtitle = wx.StaticText(panel, -1, ' Right:  ')
        btitle = wx.StaticText(panel, -1, ' Bottom: ')
        ttitle = wx.StaticText(panel, -1, ' Top:    ')

        opts = dict(min_val=0.0, max_val=None, increment=0.01, digits=3,
                    size=(FSPINSIZE, -1), action=self.onMargins)
        lmarg = FloatSpin(panel, value=_left, **opts)
        rmarg = FloatSpin(panel, value=_right, **opts)
        bmarg = FloatSpin(panel, value=_bot, **opts)
        tmarg = FloatSpin(panel, value=_top, **opts)

        self.margins = [lmarg, tmarg, rmarg, bmarg]
        if self.conf.auto_margins:
            [m.Disable() for m in self.margins]

        auto_m  = wx.CheckBox(panel,-1, ' Default ', (-1, -1), (-1, -1))
        auto_m.Bind(wx.EVT_CHECKBOX,self.onAutoMargin)
        auto_m.SetValue(self.conf.auto_margins)

        msizer = wx.BoxSizer(wx.HORIZONTAL)
        msizer.AddMany((ltitle, lmarg, rtitle, rmarg,
                        btitle, bmarg, ttitle, tmarg))

        sizer.Add(mtitle,  (8, 0), (1,1), labstyle, 2)
        sizer.Add(auto_m,  (8, 1), (1,1), labstyle, 2)
        sizer.Add(msizer,  (9, 1), (1,6), labstyle, 2)

        autopack(panel, sizer)
        return panel

    def make_scatter_panel(self, parent, font=None):
        # list of traces
        panel = wx.Panel(parent)
        if font is None:
            font = wx.Font(12,wx.SWISS,wx.NORMAL,wx.NORMAL,False)
        sizer = wx.GridBagSizer(4, 4)

        labstyle= wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL
        slab = wx.StaticText(panel, -1, 'Symbol Size:', size=(-1,-1),style=labstyle)

        ssize = FloatSpin(panel, value=self.conf.scatter_size,
                          size=(ISPINSIZE, -1), min_val=1, max_val=500,
                          action=partial(self.onScatter, item='size'))

        sizer.Add(slab,  (0, 0), (1,1), labstyle, 5)
        sizer.Add(ssize, (0, 1), (1,1), labstyle, 5)

        conf = self.conf
        nfcol = csel.ColourSelect(panel,  -1, "",
                                  mpl_color(conf.scatter_normalcolor,
                                            default=(0, 0, 128)),
                                  size=(25, 25))
        necol = csel.ColourSelect(panel,  -1, "",
                                  mpl_color(conf.scatter_normaledge,
                                            default=(0, 0, 200)),
                                  size=(25, 25))
        sfcol = csel.ColourSelect(panel,  -1, "",
                                  mpl_color(conf.scatter_selectcolor,
                                            default=(128, 0, 0)),
                                  size=(25, 25))
        secol = csel.ColourSelect(panel,  -1, "",
                                  mpl_color(conf.scatter_selectedge,
                                           default=(200, 0, 0)),
                                  size=(25, 25))
        nfcol.Bind(csel.EVT_COLOURSELECT, partial(self.onScatter, item='scatt_nf'))
        necol.Bind(csel.EVT_COLOURSELECT, partial(self.onScatter, item='scatt_ne'))
        sfcol.Bind(csel.EVT_COLOURSELECT, partial(self.onScatter, item='scatt_sf'))
        secol.Bind(csel.EVT_COLOURSELECT, partial(self.onScatter, item='scatt_se'))

        btnstyle= wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL|wx.ALL

        sizer.Add(wx.StaticText(panel, -1, 'Colors: ',
                                style=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL),
                  (1, 0), (1,1), labstyle,2)
        sizer.Add(wx.StaticText(panel, -1, 'Normal Symbol:',
                                style=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL),
                  (1, 1), (1,1), labstyle,2)
        sizer.Add(wx.StaticText(panel, -1, 'Selected Symbol:',
                                style=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL),
                  (1, 2), (1,1), labstyle,2)
        sizer.Add(wx.StaticText(panel, -1, 'Face Color:',
                                style=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL),
                  (2, 0), (1,1), labstyle,2)
        sizer.Add(wx.StaticText(panel, -1, 'Edge Color:',
                                style=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL),
                  (3, 0), (1,1), labstyle,2)

        sizer.Add(nfcol,   (2, 1), (1,1), btnstyle,2)
        sizer.Add(necol,   (3, 1), (1,1), btnstyle,2)
        sizer.Add(sfcol,   (2, 2), (1,1), btnstyle,2)
        sizer.Add(secol,   (3, 2), (1,1), btnstyle,2)

        autopack(panel, sizer)
        return panel


    def make_text_panel(self, parent, font=None):
        panel = scrolled.ScrolledPanel(parent, size=(875, 225),
                                       style=wx.GROW|wx.TAB_TRAVERSAL, name='p1')
        if font is None:
            font = wx.Font(12,wx.SWISS,wx.NORMAL,wx.NORMAL,False)

        sizer = wx.GridBagSizer(2, 2)
        labstyle= wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL

        self.titl = LabeledTextCtrl(panel, self.conf.title.replace('\n', '\\n'),
                                    action = partial(self.onText, item='title'),
                                    labeltext='Title: ', size=(400, -1))
        self.ylab = LabeledTextCtrl(panel, self.conf.ylabel.replace('\n', '\\n'),
                                    action = partial(self.onText, item='ylabel'),
                                    labeltext='Y Label: ', size=(400, -1))
        self.y2lab= LabeledTextCtrl(panel, self.conf.y2label.replace('\n', '\\n'),
                                    action = partial(self.onText, item='y2label'),
                                    labeltext='Y2 Label: ', size=(400, -1))
        self.xlab = LabeledTextCtrl(panel, self.conf.xlabel.replace('\n', '\\n'),
                                    action = partial(self.onText, item='xlabel'),
                                    labeltext='X Label: ', size=(400, -1))

        sizer.Add(self.titl.label,  (0, 0), (1, 1), labstyle)
        sizer.Add(self.titl,        (0, 1), (1, 4), labstyle)
        sizer.Add(self.ylab.label,  (1, 0), (1, 1), labstyle)
        sizer.Add(self.ylab,        (1, 1), (1, 4), labstyle)
        sizer.Add(self.y2lab.label, (2, 0), (1, 1), labstyle)
        sizer.Add(self.y2lab,       (2, 1), (1, 4), labstyle)
        sizer.Add(self.xlab.label,  (3, 0), (1, 1), labstyle)
        sizer.Add(self.xlab,        (3, 1), (1, 4), labstyle)

        t0 = wx.StaticText(panel, -1, 'Text Sizes:', style=labstyle)
        t1 = wx.StaticText(panel, -1, 'Titles:', style=labstyle)
        t2 = wx.StaticText(panel, -1, 'Axis Labels:',  style=labstyle)
        t3 = wx.StaticText(panel, -1, 'Legends:',  style=labstyle)

        fsopts = dict(size=(ISPINSIZE, -1), min_val=2, max_val=32, increment=0.5)
        ttl_size = FloatSpin(panel, value=self.conf.labelfont.get_size(),
                             action=partial(self.onText, item='titlesize'),
                             **fsopts)

        leg_size = FloatSpin(panel, value=self.conf.legendfont.get_size(),
                             action=partial(self.onText, item='legendsize'),
                             **fsopts)
        lab_size = FloatSpin(panel, value=self.conf.labelfont.get_size(),
                             action=partial(self.onText, item='labelsize'),
                             **fsopts)

        self.title_fontsize = ttl_size
        self.legend_fontsize = leg_size
        self.label_fontsize = lab_size

        sizer.Add(t0,        (4, 0), (1, 1), labstyle)
        sizer.Add(t1,        (4, 1), (1, 1), labstyle)
        sizer.Add(ttl_size,  (4, 2), (1, 2), labstyle)
        sizer.Add(t2,        (5, 1), (1, 1), labstyle)
        sizer.Add(lab_size,  (5, 2), (1, 2), labstyle)
        sizer.Add(t3,        (6, 1), (1, 1), labstyle)
        sizer.Add(leg_size,  (6, 2), (1, 2), labstyle)

        # Legend
        bstyle=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ST_NO_AUTORESIZE
        labstyle= wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL

        ax = self.axes[0]

        leg_ttl = wx.StaticText(panel, -1, 'Legend:', size=(-1, -1), style=labstyle)
        loc_ttl = wx.StaticText(panel, -1, 'Location:', size=(-1, -1), style=labstyle)
        leg_loc = wx.Choice(panel, -1, choices=self.conf.legend_locs, size=(150, -1))
        leg_loc.Bind(wx.EVT_CHOICE,partial(self.onShowLegend, item='loc'))
        leg_loc.SetStringSelection(self.conf.legend_loc)

        leg_onax = wx.Choice(panel, -1, choices=self.conf.legend_onaxis_choices,
                             size=(120, -1))
        leg_onax.Bind(wx.EVT_CHOICE,partial(self.onShowLegend, item='onaxis'))
        leg_onax.SetStringSelection(self.conf.legend_onaxis)

        togg_leg  = wx.CheckBox(panel,-1, 'Click Legend to Show/Hide Line',
                                (-1, -1), (-1, -1))
        togg_leg.Bind(wx.EVT_CHECKBOX, self.onHideWithLegend)
        togg_leg.SetValue(self.conf.hidewith_legend)

        show_leg = wx.CheckBox(panel,-1, 'Show Legend', (-1, -1), (-1, -1))
        show_leg.Bind(wx.EVT_CHECKBOX,partial(self.onShowLegend, item='legend'))
        show_leg.SetValue(self.conf.show_legend)
        if show_leg not in self.show_legend_cbs:
            self.show_legend_cbs.append(show_leg)

        show_lfr = wx.CheckBox(panel,-1, 'Show Legend Frame', (-1, -1), (-1, -1))
        show_lfr.Bind(wx.EVT_CHECKBOX,partial(self.onShowLegend,item='frame'))
        show_lfr.SetValue(self.conf.show_legend_frame)

        lsizer = wx.BoxSizer(wx.HORIZONTAL)

        lsizer.AddMany((leg_ttl, show_leg, show_lfr, togg_leg))
        sizer.Add(lsizer,    (8, 0), (1, 8), labstyle, 2)

        lsizer = wx.BoxSizer(wx.HORIZONTAL)
        lsizer.AddMany((loc_ttl, leg_loc, leg_onax))
        sizer.Add(lsizer,  (9, 1), (1, 4), labstyle, 2)
        autopack(panel, sizer)
        return panel

    def make_linetrace_panel(self, parent, font=None):
        """colours and line properties"""

        panel = scrolled.ScrolledPanel(parent, size=(900, 250),
                                       style=wx.GROW|wx.TAB_TRAVERSAL, name='p1')
        if font is None:
            font = wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL, False)

        sizer = wx.GridBagSizer(2, 2)
        i = 0
        cnf = self.conf
        ax = self.axes[0]

        labstyle= wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL

        theme_names = list(cnf.themes.keys())
        themechoice = Choice(panel, choices=theme_names, action=self.onTheme)
        themechoice.SetStringSelection(cnf.current_theme)


        textcol = csel.ColourSelect(panel, label=" Text ", size=(80, -1),
                                    colour=mpl_color(cnf.textcolor))
        gridcol = csel.ColourSelect(panel, label=" Grid ", size=(80, -1),
                                    colour=mpl_color(cnf.gridcolor))
        bgcol = csel.ColourSelect(panel, label=" Background ", size=(120, -1),
                                  colour=mpl_color(ax.get_facecolor()))
        fbgcol = csel.ColourSelect(panel,  label=" Frame ", size=(80, -1),
                                   colour=mpl_color(self.canvas.figure.get_facecolor()))

        self.colwids = {'text': textcol, 'face': bgcol,
                        'grid': gridcol, 'frame': fbgcol}

        bgcol.Bind(csel.EVT_COLOURSELECT,   partial(self.onColor, item='face'))
        fbgcol.Bind(csel.EVT_COLOURSELECT,  partial(self.onColor, item='frame'))
        gridcol.Bind(csel.EVT_COLOURSELECT, partial(self.onColor, item='grid'))
        textcol.Bind(csel.EVT_COLOURSELECT, partial(self.onColor, item='text'))

        show_grid  = wx.CheckBox(panel,-1, ' Show Grid  ')
        show_grid.Bind(wx.EVT_CHECKBOX,self.onShowGrid)
        show_grid.SetValue(cnf.show_grid)

        show_box  = wx.CheckBox(panel,-1, ' Show Top/Right Axes  ')
        show_box.Bind(wx.EVT_CHECKBOX, self.onShowBox)
        show_box.SetValue(cnf.axes_style == 'box')

        show_leg = wx.CheckBox(panel,-1, 'Show Legend  ')
        show_leg.Bind(wx.EVT_CHECKBOX,partial(self.onShowLegend, item='legend'))
        show_leg.SetValue(cnf.show_legend)
        if show_leg not in self.show_legend_cbs:
            self.show_legend_cbs.append(show_leg)

        tsizer = wx.BoxSizer(wx.HORIZONTAL)
        tsizer.Add(wx.StaticText(panel, -1, ' Theme: '), 0, labstyle, 3)
        tsizer.Add(themechoice,  1, labstyle, 3)
        tsizer.Add(wx.StaticText(panel, -1, ' Colors: '), 0, labstyle, 3)
        tsizer.Add(textcol,   0, labstyle, 3)
        tsizer.Add(gridcol,   0, labstyle, 3)
        tsizer.Add(bgcol,     0, labstyle, 3)
        tsizer.Add(fbgcol ,   0, labstyle, 3)
        sizer.Add(tsizer,    (1, 0), (1, 9), labstyle, 3)

        tsizer = wx.BoxSizer(wx.HORIZONTAL)
        tsizer.Add(wx.StaticText(panel, -1, ' Options: '), 0, labstyle, 3)
        tsizer.Add(show_grid, 0, labstyle, 3)
        tsizer.Add(show_leg,  0, labstyle, 3)
        tsizer.Add(show_box,  0, labstyle, 3)

        sizer.Add(tsizer,    (2, 0), (1, 9), labstyle, 3)

        tsizer = wx.BoxSizer(wx.HORIZONTAL)
        tsizer.Add(wx.StaticText(panel, -1, ' All Traces:  Thickness: '), 0, labstyle, 3)
        ##
        allthk = FloatSpin(panel, size=(FSPINSIZE, -1), value=cnf.traces[0].linewidth,
                           min_val=0, max_val=20, increment=0.5, digits=1,
                           action=partial(self.onThickness, trace=-1))

        self.last_thickness_event = 0.0
        tsizer.Add(allthk, 0, labstyle, 3)
        msz = FloatSpin(panel, size=(FSPINSIZE, -1), value=cnf.traces[0].markersize,
                        min_val=0, max_val=30, increment=0.5, digits=1,
                        action=partial(self.onMarkerSize, trace=-1))
        tsizer.Add(wx.StaticText(panel, -1, ' Symbol Size: '), 0, labstyle, 3)
        tsizer.Add(msz, 0, labstyle, 3)


        sizer.Add(tsizer,    (3, 0), (1, 9), labstyle, 3)

        sizer.Add(wx.StaticText(panel, -1, 'Thing 1'), (4, 0), (1, 9), labstyle, 3)

        irow = 5

        for t in ('#','Label','Color', 'Alpha', 'Fill', 'Line Style',
                  'Thickness', 'Symbol',
                  'Size', 'Z Order', 'Join Style'):
            x = wx.StaticText(panel, -1, t)
            x.SetFont(font)
            sizer.Add(x,(irow,i),(1,1),wx.ALIGN_LEFT|wx.ALL, 3)
            i = i+1
        self.trace_labels = []
        self.choice_linewidths = []
        self.choice_markersizes = []
        ntrace_display = min(cnf.ntrace+2, len(cnf.traces))
        for i in range(ntrace_display):
            irow += 1
            label  = "trace %i" % i
            lin  = cnf.traces[i]
            dlab = lin.label
            dcol = hexcolor(lin.color)
            dthk = lin.linewidth
            dalp = lin.alpha
            dmsz = lin.markersize
            dsty = lin.style
            djsty = lin.drawstyle
            dfill = lin.fill
            dzord = lin.zorder
            dsym = lin.marker
            lab = LabeledTextCtrl(panel, dlab, size=(125, -1), labeltext="%i" % (i+1),
                                  action = partial(self.onText, item='trace', trace=i))
            self.trace_labels.append(lab)

            col = csel.ColourSelect(panel,  -1, "", dcol, size=(25, 25))
            col.Bind(csel.EVT_COLOURSELECT, partial(self.onColor, trace=i))

            self.colwids[i] = col

            thk = FloatSpin(panel, size=(FSPINSIZE, -1), value=dthk,
                            min_val=0, max_val=20, increment=0.5, digits=1,
                            action=partial(self.onThickness, trace=i))
            self.choice_linewidths.append(thk)

            sty = Choice(panel, choices=cnf.styles, size=(100,-1),
                         action=partial(self.onStyle,trace=i))
            sty.SetStringSelection(dsty)

            msz = FloatSpin(panel, size=(FSPINSIZE, -1), value=dmsz,
                            min_val=0, max_val=30, increment=0.5, digits=1,
                            action=partial(self.onMarkerSize, trace=i))
            self.choice_markersizes.append(msz)
            zor = FloatSpin(panel, size=(FSPINSIZE, -1), value=dzord,
                            min_val=-500, max_val=500, increment=1, digits=0,
                            action=partial(self.onZorder, trace=i))

            sym = Choice(panel, choices=cnf.symbols, size=(120,-1),
                         action=partial(self.onSymbol,trace=i))

            sym.SetStringSelection(dsym)

            jsty = wx.Choice(panel, -1, choices=cnf.drawstyles, size=(100,-1))
            jsty.Bind(wx.EVT_CHOICE, partial(self.onJoinStyle, trace=i))
            jsty.SetStringSelection(djsty)

            ffil = wx.CheckBox(panel, -1, '')
            ffil.Bind(wx.EVT_CHECKBOX, partial(self.onFill, trace=i))
            ffil.SetValue(dfill)

            alp = FloatSpin(panel, size=(FSPINSIZE, -1), value=dalp,
                            min_val=0, max_val=1, increment=0.05, digits=2,
                            action=partial(self.onAlpha, trace=i))


            sizer.Add(lab.label,(irow,0),(1,1),wx.ALIGN_LEFT|wx.ALL, 4)
            sizer.Add(lab, (irow,1),(1,1),wx.ALIGN_LEFT|wx.ALL, 4)
            sizer.Add(col, (irow,2),(1,1),wx.ALIGN_LEFT|wx.ALL, 4)
            sizer.Add(alp, (irow,3),(1,1),wx.ALIGN_LEFT|wx.ALL, 4)
            sizer.Add(ffil,(irow,4),(1,1),wx.ALIGN_LEFT|wx.ALL, 4)
            sizer.Add(sty, (irow,5),(1,1),wx.ALIGN_LEFT|wx.ALL, 4)
            sizer.Add(thk, (irow,6),(1,1),wx.ALIGN_LEFT|wx.ALL, 4)
            sizer.Add(sym, (irow,7),(1,1),wx.ALIGN_LEFT|wx.ALL, 4)
            sizer.Add(msz, (irow,8),(1,1),wx.ALIGN_LEFT|wx.ALL, 4)
            sizer.Add(zor, (irow,9),(1,1),wx.ALIGN_LEFT|wx.ALL, 4)
            sizer.Add(jsty, (irow,10),(1,1),wx.ALIGN_LEFT|wx.ALL, 4)


        autopack(panel,sizer)
        panel.SetupScrolling()
        return panel

    def onResetLines(self, event=None):
        pass

    def onColor(self, event=None, color=None, item='trace', trace=1, draw=True):
        event_col = event.GetValue()
        if color is None and event is not None:
            color = hexcolor(event_col)

        if item == 'trace':
            self.conf.set_trace_color(color, trace=trace)
            self.colwids[trace].SetColour(color)

        elif item == 'grid':
            self.conf.set_gridcolor(color)
        elif item == 'face':
            self.conf.set_facecolor(color)
        elif item == 'frame':
            self.conf.set_framecolor(color)
        elif item == 'text':
            self.conf.set_textcolor(color)
        if draw:
            self.canvas.draw()


    def onTheme(self, event):
        theme = event.GetString()
        conf = self.conf
        conf.set_theme(theme=theme)
        self.colwids['text'].SetColour(conf.textcolor)
        self.colwids['grid'].SetColour(conf.gridcolor)
        self.colwids['face'].SetColour(conf.facecolor)
        self.colwids['frame'].SetColour(conf.framecolor)

        self.title_fontsize.SetValue(self.conf.titlefont.get_size())
        self.legend_fontsize.SetValue(self.conf.legendfont.get_size())

        ntrace_display = min(self.conf.ntrace+2, len(self.conf.traces))
        for i in range(ntrace_display):
            try:
                lin = self.conf.traces[i]
                curcol = hexcolor(self.colwids[i].GetColour())
                newcol = hexcolor(lin.color)
                self.colwids[i].SetColour(newcol)
                if newcol != curcol:
                    self.conf.set_trace_color(newcol, trace=i)
            except KeyError:
                pass
        conf.draw_legend()

    def onLogScale(self, event):
        xword, yword = event.GetString().split(' / ')
        xscale = xword.replace('x', '').strip()
        yscale = yword.replace('y', '').strip()
        self.conf.set_logscale(xscale=xscale, yscale=yscale)

    def onZoomStyle(self, event=None):
        self.conf.zoom_style = event.GetString()

    def onStyle(self, event, trace=0):
        self.conf.set_trace_style(event.GetString(),trace=trace)

    def onJoinStyle(self, event, trace=0):
        self.conf.set_trace_drawstyle(event.GetString(), trace=trace)

    def onFill(self, event, trace=0):
        self.conf.set_trace_fill(event.IsChecked(), trace=trace)

    def onSymbol(self, event, trace=0):
        self.conf.set_trace_marker(event.GetString(), trace=trace)

    def onMarkerSize(self, event, trace=0):
        val = event.GetEventObject().GetValue()
        if trace == -1:
            for t, c in enumerate(self.choice_markersizes):
                c.SetValue(val)
                self.conf.set_trace_markersize(val, trace=t)
        else:
            self.conf.set_trace_markersize(val, trace=trace)

    def onAlpha(self, event, trace=0):
        self.conf.set_trace_alpha(event.GetEventObject().GetValue(), trace=trace,
                                  delay_draw=False)

    def onZorder(self, event, trace=0):
        self.conf.set_trace_zorder(event.GetEventObject().GetValue(),
                                   trace=trace)

    def onThickness(self, event, trace=0):
        val = event.GetEventObject().GetValue()
        if trace == -1:
            for t, c in enumerate(self.choice_linewidths):
                c.SetValue(val)
                self.conf.set_trace_linewidth(val, trace=t)
        else:
            self.conf.set_trace_linewidth(val, trace=trace)


    def onAutoBounds(self,event):
        axes = self.canvas.figure.get_axes()
        if event.IsChecked():
            for ax in axes:
                self.conf.user_limits[ax] = [None, None, None, None]
            [m.Disable() for m in self.xbounds]
            [m.Disable() for m in self.ybounds]
            [m.Disable() for m in self.y2bounds]
            self.vpad_val.Enable()
            self.conf.unzoom(full=True)
        else:
            self.vpad_val.Disable()
            xb = axes[0].get_xlim()
            yb = axes[0].get_ylim()
            for m, v in zip(self.xbounds, xb):
                m.Enable()
                m.SetValue(ffmt(v))
            for m, v in zip(self.ybounds, yb):
                m.Enable()
                m.SetValue(ffmt(v))
            if len(axes) > 1:
                y2b = axes[1].get_ylim()
                for m, v in zip(self.y2bounds, y2b):
                    m.Enable()
                    m.SetValue(ffmt(v))

    def onBounds(self, event=None):
        def FloatNone(v):
            if v in ('', 'None', 'none'):
                return None
            try:
                return float(v)
            except:
                return None

        axes = self.canvas.figure.get_axes()
        xmin, xmax = [FloatNone(w.GetValue()) for w in self.xbounds]
        ymin, ymax = [FloatNone(w.GetValue()) for w in self.ybounds]
        self.conf.user_limits[axes[0]] = [xmin, xmax, ymin, ymax]

        if len(axes) > 1:
            y2min, y2max = [FloatNone(w.GetValue()) for w in self.y2bounds]
            self.conf.user_limits[axes[1]] = [xmin, xmax, y2min, y2max]
        self.conf.set_viewlimits()
        self.conf.canvas.draw()


    def onAutoMargin(self,event):
        self.conf.auto_margins = event.IsChecked()
        if self.conf.auto_margins:
            [m.Disable() for m in self.margins]
        else:
            ppanel = self.GetParent()
            vals = ppanel.get_default_margins()
            for m, v in zip(self.margins, vals):
                m.Enable()
                m.SetValue(v)
        self.conf.canvas.draw()

    def onMargins(self, event=None):
        left, top, right, bottom = [float(w.GetValue()) for w in self.margins]
        self.conf.set_margins(left=left, top=top, right=right, bottom=bottom)

    def onViewPadEvent(self, event=None):

        self.conf.viewpad = float(self.vpad_val.GetValue())
        self.conf.set_viewlimits()
        self.conf.canvas.draw()

        axes = self.canvas.figure.get_axes()
        xb = axes[0].get_xlim()
        yb = axes[0].get_ylim()
        for m, v in zip(self.xbounds, xb):
            m.SetValue(ffmt(v))

        for m, v in zip(self.ybounds, yb):
            m.SetValue(ffmt(v))

    def onScatter(self, event, item=None):
        conf = self.conf
        axes = self.canvas.figure.get_axes()[0]
        if item == 'size':
            conf.scatter_size = event.GetInt()
        elif item == 'scatt_nf':
            self.conf.scatter_normalcolor = hexcolor(event.GetValue())
        elif item == 'scatt_ne':
            self.conf.scatter_normaledge = hexcolor(event.GetValue())
        elif item == 'scatt_sf':
            self.conf.scatter_selectcolor = hexcolor(event.GetValue())
        elif item == 'scatt_se':
            self.conf.scatter_selectedge = hexcolor(event.GetValue())

        axes.cla()
        xd, yd = conf.scatter_xdata, conf.scatter_ydata
        mask = conf.scatter_mask
        if mask is  None:
            axes.scatter(xd, yd, s=conf.scatter_size,
                         c=conf.scatter_normalcolor,
                         edgecolors=conf.scatter_normaledge)
        else:
            axes.scatter(xd[np.where(~mask)], yd[np.where(~mask)],
                         s=conf.scatter_size,
                         c=conf.scatter_normalcolor,
                         edgecolors=conf.scatter_normaledge)
            axes.scatter(xd[np.where(mask)], yd[np.where(mask)],
                         s=conf.scatter_size,
                         c=conf.scatter_selectcolor,
                         edgecolors=conf.scatter_selectedge)
        self.conf.relabel(delay_draw=False)

    def onText(self, event=None, item='trace', trace=0):
        if item=='labelsize':
            size = self.label_fontsize.GetValue()
            self.conf.labelfont.set_size(size)
            for ax in self.axes:
                for lab in ax.get_xticklabels()+ax.get_yticklabels():
                    lab.set_fontsize(size)
            self.conf.relabel()
            return
        elif item=='titlesize':
            size = self.title_fontsize.GetValue()
            self.conf.titlefont.set_size(size)
            self.conf.relabel()
            return
        elif item=='legendsize':
            size = self.legend_fontsize.GetValue()
            self.conf.legendfont.set_size(size)
            self.conf.draw_legend()
            return

        if item == 'title':
            wid = self.titl
        elif item == 'ylabel':
            wid = self.ylab
        elif item == 'y2label':
            wid = self.y2lab
        elif item == 'xlabel':
            wid = self.xlab
        elif item == 'trace':
            wid = self.trace_labels[trace]

        s = wid.GetValue()
        try:
            s = str(s).strip()
        except TypeError:
            s = ''

        if item in ('xlabel', 'ylabel', 'y2label', 'title'):
            try:
                kws = {item: s}
                self.conf.relabel(**kws)
                wid.SetBackgroundColour((255, 255, 255))
            except: # as from latex error!
                wid.SetBackgroundColour((250, 250, 150))
        elif item == 'trace':
            try:
                self.conf.set_trace_label(s, trace=trace)
            except:
                pass

    def onShowGrid(self,event):
        self.conf.enable_grid(show=event.IsChecked())

    def onShowBox(self, event=None):
        style='box'
        if not event.IsChecked(): style='open'
        self.conf.set_axes_style(style=style)

    def onShowLegend(self, event, item=''):
        auto_location = True
        if item == 'legend':
            self.conf.show_legend  = checked = event.IsChecked()
            for cb in self.show_legend_cbs:
                if cb.GetValue() != checked:
                    cb.SetValue(checked)

        elif item=='frame':
            self.conf.show_legend_frame = event.IsChecked()
        elif item=='loc':
            self.conf.legend_loc  = event.GetString()
            auto_location = False
        elif item=='onaxis':
            self.conf.legend_onaxis  = event.GetString()
        self.conf.draw_legend(auto_location=auto_location)

    def onDragLegend(self, event=None):
        self.conf.draggable_legend = event.IsChecked()
        self.conf.draw_legend()

    def onHideWithLegend(self, event=None):
        self.conf.hidewith_legend = event.IsChecked()
        self.conf.draw_legend()

    def redraw_legend(self):
        self.conf.draw_legend()

    def onExit(self, event):
        self.Close(True)
