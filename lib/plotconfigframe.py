#!/usr/bin/python
#
# WXMPlot GUI to Configure (2D) Plots
#
import os, sys
from functools import partial
import wx
import wx.lib.colourselect  as csel
import wx.lib.agw.flatnotebook as flat_nb
from wx.lib.agw.floatspin import FloatSpin, EVT_FLOATSPIN, FS_LEFT

import wx.lib.scrolledpanel as scrolled
import numpy as np

import matplotlib
from matplotlib import rcParams
from matplotlib.colors import colorConverter
from matplotlib.font_manager import fontManager, FontProperties
from matplotlib.colors import colorConverter
to_rgba = colorConverter.to_rgba

from .utils import Closure, LabelEntry
from .config import PlotConfig
from .colors import hexcolor, hex2rgb

FNB_STYLE = flat_nb.FNB_NO_X_BUTTON|flat_nb.FNB_SMART_TABS|flat_nb.FNB_NO_NAV_BUTTONS

ISPINSIZE = 110
FSPINSIZE = 150
if os.name == 'nt' or sys.platform.lower().startswith('darwin'):
    ISPINSIZE = 50
    FSPINSIZE = 70


def mpl_color(c, default = (242, 243, 244)):
    try:
        r = map(lambda x: int(x*255), colorConverter.to_rgb(c))
        return tuple(r)
    except:
        return default

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
        self.DrawPanel()

    def DrawPanel(self):
        style = wx.DEFAULT_FRAME_STYLE## |wx.TAB_TRAVERSAL
        wx.Frame.__init__(self, self.parent, -1, 'Configure Plot', style=style)
        bgcol =  hex2rgb(self.conf.color_themes['light']['bg'])
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
        self.SetMinSize((775, 200))
        self.SetSize((950, 400))
        self.Show()
        self.Raise()

    def make_range_panel(self, parent, font=None):
        # bounds, margins, scales
        panel = wx.Panel(parent)
        if font is None:
            font = wx.Font(12,wx.SWISS,wx.NORMAL,wx.NORMAL,False)

        conf = self.conf

        sizer = wx.GridBagSizer(4, 4)

        labstyle= wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL
        mtitle = wx.StaticText(panel, -1, 'Linear/Log Scale: ')

        logchoice = wx.Choice(panel, choices=self.conf.log_choices,  size=(200,-1))
        logchoice.SetStringSelection("x %s / y %s" % (self.conf.xscale, self.conf.yscale))
        logchoice.Bind(wx.EVT_CHOICE, self.onLogScale)

        sizer.Add(mtitle,     (1, 0), (1,1), labstyle, 2)
        sizer.Add(logchoice,  (1, 1), (1,3), labstyle, 2)


        # Bounds
        axes = self.canvas.figure.get_axes()
        laxes = axes[0]
        raxes = None
        if len(axes) > 1:
            raxes = axes[1]
        user_lims = self.conf.user_limits[laxes]

        auto_b  = wx.CheckBox(panel,-1, 'Auto-set', (-1, -1), (-1, -1))
        auto_b.Bind(wx.EVT_CHECKBOX,self.onAutoBounds)
        auto_b.SetValue(self.conf.user_limits[laxes] == 4*[None])

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

        opts = dict(size=100, labeltext='', action=self.onBounds)


        self.xbounds  = [LabelEntry(panel,value=ffmt(xb0), **opts),
                         LabelEntry(panel,value=ffmt(xb1), **opts)]
        self.ybounds  = [LabelEntry(panel,value=ffmt(yb0), **opts),
                         LabelEntry(panel,value=ffmt(yb1), **opts)]
        self.y2bounds = [LabelEntry(panel,value=ffmt(y2b0), **opts),
                         LabelEntry(panel,value=ffmt(y2b1), **opts)]

        if user_lims == 4*[None]:
            [w.Disable() for w in self.xbounds]
            [w.Disable() for w in self.ybounds]

        if raxes is None:
            [w.Disable() for w in self.y2bounds]


        sizer.Add(wx.StaticText(panel, -1, 'Bounds: '),    (3, 0), (1, 1), labstyle, 2)
        sizer.Add(auto_b,                                  (3, 1), (1, 1), labstyle, 2)
        sizer.Add(wx.StaticText(panel, -1, '   X axis:'),  (4, 0), (1, 1), labstyle, 2)
        sizer.Add(self.xbounds[0],                         (4, 1), (1, 1), labstyle, 2)
        sizer.Add(wx.StaticText(panel, -1, ' : '),         (4, 2), (1, 1), labstyle, 2)
        sizer.Add(self.xbounds[1],                         (4, 3), (1, 1), labstyle, 2)

        sizer.Add(wx.StaticText(panel, -1, '   Y axis:'),  (5, 0), (1, 1), labstyle, 2)
        sizer.Add(self.ybounds[0],                         (5, 1), (1, 1), labstyle, 2)
        sizer.Add(wx.StaticText(panel, -1, ' : '),         (5, 2), (1, 1), labstyle, 2)
        sizer.Add(self.ybounds[1],                         (5, 3), (1, 1), labstyle, 2)

        sizer.Add(wx.StaticText(panel, -1, '   Y2 axis:'), (6, 0), (1, 1), labstyle, 2)
        sizer.Add(self.y2bounds[0],                        (6, 1), (1, 1), labstyle, 2)
        sizer.Add(wx.StaticText(panel, -1, ' : '),         (6, 2), (1, 1), labstyle, 2)
        sizer.Add(self.y2bounds[1],                        (6, 3), (1, 1), labstyle, 2)

        # Margins
        _left, _top, _right, _bot = ["%.3f"% x for x in self.conf.margins]

        mtitle = wx.StaticText(panel, -1, 'Margins: ')
        ltitle = wx.StaticText(panel, -1, ' Left:   ')
        rtitle = wx.StaticText(panel, -1, ' Right:  ')
        btitle = wx.StaticText(panel, -1, ' Bottom: ')
        ttitle = wx.StaticText(panel, -1, ' Top:    ')

        opts = dict(min_val=0.0, max_val=None, increment=0.01, digits=3,
                    pos=(-1,-1), size=(FSPINSIZE, 30))
        lmarg = FloatSpin(panel, -1, value=_left, **opts)
        lmarg.Bind(EVT_FLOATSPIN, self.onMargins)
        rmarg = FloatSpin(panel, -1, value=_right, **opts)
        rmarg.Bind(EVT_FLOATSPIN, self.onMargins)
        bmarg = FloatSpin(panel, -1, value=_bot, **opts)
        bmarg.Bind(EVT_FLOATSPIN, self.onMargins)
        tmarg = FloatSpin(panel, -1, value=_top, **opts)
        tmarg.Bind(EVT_FLOATSPIN, self.onMargins)

        self.margins = [lmarg, tmarg, rmarg, bmarg]
        if self.conf.auto_margins:
            [m.Disable() for m in self.margins]

        auto_m  = wx.CheckBox(panel,-1, 'Auto-set', (-1, -1), (-1, -1))
        auto_m.Bind(wx.EVT_CHECKBOX,self.onAutoMargin) # ShowGrid)
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
        ssize = wx.SpinCtrl(panel, -1, "", (-1, -1), (ISPINSIZE, 30))
        ssize.SetRange(1, 100)
        ssize.SetValue(self.conf.scatter_size)
        ssize.Bind(wx.EVT_SPINCTRL, partial(self.onScatter, item='size'))

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
        panel = scrolled.ScrolledPanel(parent, size=(800, 200),
                                       style=wx.GROW|wx.TAB_TRAVERSAL, name='p1')
        if font is None:
            font = wx.Font(12,wx.SWISS,wx.NORMAL,wx.NORMAL,False)

        sizer = wx.GridBagSizer(2, 2)
        i = 0
        irow = 0
        bstyle=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ST_NO_AUTORESIZE
        labstyle= wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL

        ax = self.axes[0]

        t0 = wx.StaticText(panel, -1, 'Text Size:', style=labstyle)
        t1 = wx.StaticText(panel, -1, 'Labels and Titles:',  style=labstyle)
        t2 = wx.StaticText(panel, -1, 'Legends:',  style=labstyle)

        t_size = wx.SpinCtrl(panel, -1, "", (-1, -1), (ISPINSIZE, 25))
        t_size.SetRange(2, 20)
        t_size.SetValue(self.conf.labelfont.get_size())
        t_size.Bind(wx.EVT_SPINCTRL, partial(self.onText, item='labelsize'))

        l_size = wx.SpinCtrl(panel, -1, " ", (-1, -1), (ISPINSIZE, 25))
        l_size.SetRange(2, 20)
        l_size.SetValue(self.conf.legendfont.get_size())
        l_size.Bind(wx.EVT_SPINCTRL, partial(self.onText, item='legendsize'))


        self.titl = LabelEntry(panel, self.conf.title.replace('\n', '\\n'),
                               labeltext='Title: ',size=400,
                               action = partial(self.onText, item='title'))
        self.ylab = LabelEntry(panel, self.conf.ylabel.replace('\n', '\\n'),
                               labeltext='Y Label: ',size=400,
                               action = partial(self.onText, item='ylabel'))
        self.y2lab= LabelEntry(panel, self.conf.y2label.replace('\n', '\\n'),
                               labeltext='Y2 Label: ',size=400,
                               action = partial(self.onText, item='y2label'))
        self.xlab = LabelEntry(panel, self.conf.xlabel.replace('\n', '\\n'),
                               labeltext='X Label: ',size=400,
                               action = partial(self.onText, item='xlabel'))

        sizer.Add(self.titl.label, (0, 0), (1, 1), labstyle)
        sizer.Add(self.titl,       (0, 1), (1, 4), labstyle)
        sizer.Add(self.ylab.label, (1, 0), (1, 1), labstyle)
        sizer.Add(self.ylab,       (1, 1), (1, 4), labstyle)
        sizer.Add(self.y2lab.label,(2, 0), (1, 1), labstyle)
        sizer.Add(self.y2lab,      (2, 1), (1, 4), labstyle)
        sizer.Add(self.xlab.label, (3, 0), (1, 1), labstyle)
        sizer.Add(self.xlab,       (3, 1), (1, 4), labstyle)

        sizer.Add(t0,      (4, 0), (1, 1), labstyle)
        sizer.Add(t1,      (4, 1), (1, 1), labstyle)
        sizer.Add(t_size,  (4, 2), (1, 1), labstyle)
        sizer.Add(t2,      (4, 3), (1, 1), labstyle)
        sizer.Add(l_size,  (4, 4), (1, 1), labstyle)

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

        togg_leg  = wx.CheckBox(panel,-1, 'Click Legend to Show/Hide Line', (-1, -1), (-1, -1))
        togg_leg.Bind(wx.EVT_CHECKBOX, self.onHideWithLegend)
        togg_leg.SetValue(self.conf.hidewith_legend)

        show_leg = wx.CheckBox(panel,-1, 'Show Legend', (-1, -1), (-1, -1))
        show_leg.Bind(wx.EVT_CHECKBOX,partial(self.onShowLegend, item='legend'))
        show_leg.SetValue(self.conf.show_legend)

        show_lfr = wx.CheckBox(panel,-1, 'Show Legend Frame', (-1, -1), (-1, -1))
        show_lfr.Bind(wx.EVT_CHECKBOX,partial(self.onShowLegend,item='frame'))
        show_lfr.SetValue(self.conf.show_legend_frame)

        lsizer = wx.BoxSizer(wx.HORIZONTAL)

        lsizer.AddMany((leg_ttl, show_leg, show_lfr, togg_leg))
        sizer.Add(lsizer,    (6, 0), (1, 8), labstyle, 2)

        lsizer = wx.BoxSizer(wx.HORIZONTAL)
        lsizer.AddMany((loc_ttl, leg_loc, leg_onax))
        sizer.Add(lsizer,  (7, 1), (1, 4), labstyle, 2)



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

        ax = self.axes[0]
        if matplotlib.__version__ < '2.0':
            axis_bgcol = ax.get_axis_bgcolor()
        else:
            axis_bgcol = ax.get_facecolor()

        labstyle= wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL

        opts = dict(size=(-1, 25), style=labstyle)

        ctitle = wx.StaticText(panel, -1, 'Colors:  ')
        ltheme = wx.StaticText(panel, -1, 'Use Color Theme: ')

        themes = list(self.conf.color_themes.keys())

        coltheme = wx.Choice(panel, choices=themes,  size=(100,-1))
        coltheme.SetStringSelection(self.conf.color_theme)
        coltheme.Bind(wx.EVT_CHOICE, self.onColorThemeStyle)

        textcol = csel.ColourSelect(panel, label=" Text ",
                                    colour=mpl_color(self.conf.textcolor), **opts)

        gridcol = csel.ColourSelect(panel, label=" Grid ",
                                    colour=mpl_color(self.conf.gridcolor), **opts)

        bgcol = csel.ColourSelect(panel, label=" Background ",
                                  colour=mpl_color(axis_bgcol),  **opts)

        fbgcol = csel.ColourSelect(panel,  label=" Outer Frame ",
                                   colour=mpl_color(self.canvas.figure.get_facecolor()),
                                   **opts)

        self.colwids = {'text': textcol, 'bg': bgcol,
                        'grid': gridcol, 'frame': fbgcol}

        bgcol.Bind(csel.EVT_COLOURSELECT,   partial(self.onColor, item='bg'))
        fbgcol.Bind(csel.EVT_COLOURSELECT,  partial(self.onColor, item='frame'))
        gridcol.Bind(csel.EVT_COLOURSELECT, partial(self.onColor, item='grid'))
        textcol.Bind(csel.EVT_COLOURSELECT, partial(self.onColor, item='text'))

        show_grid  = wx.CheckBox(panel,-1, ' Show Grid ', (-1, -1), (-1, -1))
        show_grid.Bind(wx.EVT_CHECKBOX,self.onShowGrid)
        show_grid.SetValue(self.conf.show_grid)

        show_box  = wx.CheckBox(panel,-1, ' Show Top/Right Axes ', (-1, -1), (-1, -1))
        show_box.Bind(wx.EVT_CHECKBOX, self.onShowBox)
        show_box.SetValue(self.conf.axes_style == 'box')

        csizer = wx.BoxSizer(wx.HORIZONTAL)

        csizer.Add(ctitle,    0, labstyle, 3)
        csizer.Add(textcol,   0, labstyle, 3)
        csizer.Add(gridcol,   0, labstyle, 3)
        csizer.Add(bgcol,     0, labstyle, 3)
        csizer.Add(fbgcol ,   0, labstyle, 3)
        csizer.Add(ltheme,    1, labstyle, 3)
        csizer.Add(coltheme,  1, labstyle, 3)
        csizer.Add(show_grid, 0, labstyle, 3)
        csizer.Add(show_box,  0, labstyle, 3)

        sizer.Add(csizer,    (1, 0), (1, 9), labstyle, 2)

        reset_btn = wx.Button(panel, label='Reset Line Colors', size=(200, -1))
        reset_btn.Bind(wx.EVT_BUTTON, self.onResetLines)

        sizer.Add(reset_btn, (2, 1), (1, 4))

        irow = 3
        for t in ('#','Label','Color', 'Style',
                  'Thickness','Symbol',' Size', 'Z Order', 'Join Style'):
            x = wx.StaticText(panel, -1, t)
            x.SetFont(font)
            sizer.Add(x,(irow,i),(1,1),wx.ALIGN_LEFT|wx.ALL, 3)
            i = i+1
        self.trace_labels = []
        ntrace_display = min(self.conf.ntrace+2, len(self.conf.traces))
        for i in range(ntrace_display):
            irow += 1
            label  = "trace %i" % i
            lin  = self.conf.traces[i]
            dlab = lin.label
            dcol = hexcolor(lin.color)
            dthk = lin.linewidth
            dmsz = lin.markersize
            dsty = lin.style
            djsty = lin.drawstyle
            dzord = lin.zorder
            dsym = lin.marker
            lab = LabelEntry(panel, dlab, size=125,labeltext="%i" % (i+1),
                               action = partial(self.onText, item='trace', trace=i))
            self.trace_labels.append(lab)

            col = csel.ColourSelect(panel,  -1, "", dcol, size=(25, 25))
            col.Bind(csel.EVT_COLOURSELECT, partial(self.onColor, trace=i))

            self.colwids[i] = col

            thk = FloatSpin(panel, -1,  pos=(-1,-1), size=(FSPINSIZE, 25), value=dthk,
                            min_val=0, max_val=10, increment=0.5, digits=1)
            thk.Bind(EVT_FLOATSPIN, partial(self.onThickness, trace=i))

            sty = wx.Choice(panel, choices=self.conf.styles, size=(100,-1))
            sty.Bind(wx.EVT_CHOICE,partial(self.onStyle,trace=i))
            sty.SetStringSelection(dsty)

            msz = FloatSpin(panel, -1,  pos=(-1,-1), size=(FSPINSIZE, 25), value=dmsz,
                            min_val=0, max_val=30, increment=1, digits=0)
            msz.Bind(EVT_FLOATSPIN, partial(self.onMarkerSize, trace=i))

            zor = FloatSpin(panel, -1,  pos=(-1,-1), size=(FSPINSIZE, 25),
                            value=dzord,
                            min_val=-500, max_val=500, increment=1, digits=0)
            zor.Bind(EVT_FLOATSPIN, partial(self.onZorder, trace=i))

            sym = wx.Choice(panel, -1, choices=self.conf.symbols, size=(120,-1))
            sym.Bind(wx.EVT_CHOICE,partial(self.onSymbol,trace=i))

            sym.SetStringSelection(dsym)

            jsty = wx.Choice(panel, -1, choices=self.conf.drawstyles, size=(100,-1))
            jsty.Bind(wx.EVT_CHOICE, partial(self.onJoinStyle, trace=i))
            jsty.SetStringSelection(djsty)

            sizer.Add(lab.label,(irow,0),(1,1),wx.ALIGN_LEFT|wx.ALL, 5)
            sizer.Add(lab, (irow,1),(1,1),wx.ALIGN_LEFT|wx.ALL, 5)
            sizer.Add(col, (irow,2),(1,1),wx.ALIGN_LEFT|wx.ALL, 5)
            sizer.Add(sty, (irow,3),(1,1),wx.ALIGN_LEFT|wx.ALL, 5)
            sizer.Add(thk, (irow,4),(1,1),wx.ALIGN_LEFT|wx.ALL, 5)
            sizer.Add(sym, (irow,5),(1,1),wx.ALIGN_LEFT|wx.ALL, 5)
            sizer.Add(msz, (irow,6),(1,1),wx.ALIGN_LEFT|wx.ALL, 5)
            sizer.Add(zor, (irow,7),(1,1),wx.ALIGN_LEFT|wx.ALL, 5)
            sizer.Add(jsty, (irow,8),(1,1),wx.ALIGN_LEFT|wx.ALL, 5)

        autopack(panel,sizer)
        panel.SetupScrolling()
        return panel

    def onResetLines(self, event=None):
        self.conf.reset_trace_properties()

        ntrace_display = min(self.conf.ntrace+2, len(self.conf.traces))
        for i in range(ntrace_display):
            lin = self.conf.traces[i]
            curcol = hexcolor(self.colwids[i].GetColour())
            newcol = hexcolor(lin.color)
            self.colwids[i].SetColour(newcol)
            if newcol != curcol:
                self.onColor(event=None, color=newcol, trace=i)

    def onColor(self, event=None, color=None, item='trace', trace=1, draw=True):
        if color is None and event is not None:
            color = hexcolor( event.GetValue() )
        if item == 'trace':
            self.conf.set_trace_color(color, trace=trace)
        elif item == 'grid':
            self.conf.set_gridcolor(color)
        elif item == 'bg':
            self.conf.set_bgcolor(color)
        elif item == 'frame':
            self.conf.set_framecolor(color)
        elif item == 'text':
            self.conf.set_textcolor(color)

        if draw:
            self.canvas.draw()

    def onColorThemeStyle(self, event):
        theme = event.GetString()
        conf = self.conf
        conf.set_color_theme(theme)

        self.colwids['text'].SetColour(conf.textcolor)
        self.colwids['grid'].SetColour(conf.gridcolor)
        self.colwids['bg'].SetColour(conf.bgcolor)
        self.colwids['frame'].SetColour(conf.framecolor)

        self.onColor(color=conf.bgcolor,    item='bg',    draw=False)
        self.onColor(color=conf.gridcolor,  item='grid',  draw=False)
        self.onColor(color=conf.framecolor, item='frame', draw=False)
        self.onColor(color=conf.textcolor,  item='text',  draw=False)

    def onLogScale(self, event):
        xword, yword = event.GetString().split(' / ')
        xscale = xword.replace('x', '').strip()
        yscale = yword.replace('y', '').strip()
        self.conf.set_logscale(xscale=xscale, yscale=yscale)

    def onStyle(self, event, trace=0):
        self.conf.set_trace_style(event.GetString(),trace=trace)

    def onJoinStyle(self, event, trace=0):
        self.conf.set_trace_drawstyle(event.GetString(), trace=trace)

    def onSymbol(self, event, trace=0):
        self.conf.set_trace_marker(event.GetString(), trace=trace)

    def onMarkerSize(self, event, trace=0):
        self.conf.set_trace_markersize(event.GetEventObject().GetValue(),
                                       trace=trace)

    def onZorder(self, event, trace=0):
        self.conf.set_trace_zorder(event.GetEventObject().GetValue(),
                                   trace=trace)

    def onThickness(self, event, trace=0):
        self.conf.set_trace_linewidth(event.GetEventObject().GetValue(),
                                      trace=trace)

    def onAutoBounds(self,event):
        axes = self.canvas.figure.get_axes()
        if event.IsChecked():
            for ax in axes:
                self.conf.user_limits[ax] = [None, None, None, None]
            [m.Disable() for m in self.xbounds]
            [m.Disable() for m in self.ybounds]
            [m.Disable() for m in self.y2bounds]
            self.conf.unzoom(full=True)
        else:

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

    def onMargins(self, event=None):
        left, top, right, bottom = [float(w.GetValue()) for w in self.margins]
        self.conf.set_margins(left=left, top=top, right=right, bottom=bottom)

    def onScatter(self, event, item=None):
        if self.conf.scatter_coll is None or item is None:
            return
        conf = self.conf
        coll = conf.scatter_coll
        recolor = True
        if item == 'size':
            conf.scatter_size = event.GetInt()
            coll._sizes = (conf.scatter_size,)
            recolor = False
        elif item == 'scatt_nf':
            self.conf.scatter_normalcolor = hexcolor(event.GetValue())
        elif item == 'scatt_ne':
            self.conf.scatter_normaledge = hexcolor(event.GetValue())
        elif item == 'scatt_sf':
            self.conf.scatter_selectcolor = hexcolor(event.GetValue())
        elif item == 'scatt_se':
            self.conf.scatter_selectedge = hexcolor(event.GetValue())

        if recolor:
            fcols = coll.get_facecolors()
            ecols = coll.get_edgecolors()
            try:
                pts = np.nonzero(self.conf.scatter_mask)[0]
            except:
                pts = []
            for i in range(len(conf.scatter_data)):
                if i in pts:
                    ecols[i] = to_rgba(conf.scatter_selectedge)
                    fcols[i] = to_rgba(conf.scatter_selectcolor)
                    fcols[i][3] = 0.5
                else:
                    fcols[i] = to_rgba(conf.scatter_normalcolor)
                    ecols[i] = to_rgba(conf.scatter_normaledge)
        self.canvas.draw()

    def onText(self, event, item='trace', trace=0):
        if item=='labelsize':
            size = event.GetInt()
            self.conf.labelfont.set_size(size)
            self.conf.titlefont.set_size(size+1)
            for ax in self.axes:
                for lab in ax.get_xticklabels()+ax.get_yticklabels():
                    lab.set_fontsize(size)
            self.conf.relabel()
            return
        if item=='legendsize':
            size = event.GetInt()
            self.conf.legendfont.set_size(size)
            # self.conf.relabel()
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

        if wx.EVT_TEXT_ENTER.evtType[0] == event.GetEventType():
            s = str(event.GetString()).strip()
        elif wx.EVT_KILL_FOCUS.evtType[0] == event.GetEventType():
            s = wid.GetValue()

        try:
            s = str(s).strip()
        except TypeError:
            s = ''

        if '\\' in s and '$' in s:
            s = clean_texmath(s)
            # print(" s = ", s)
        if item in ('xlabel', 'ylabel', 'y2label', 'title'):
            try:
                kws = {item: s}
                self.conf.relabel(**kws)
                wid.SetBackgroundColour((255, 255, 255))
            except: # as from latex error!
                wid.SetBackgroundColour((250, 250, 200))
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
        if (item == 'legend'):
            self.conf.show_legend  = event.IsChecked()
        elif (item=='frame'):
            self.conf.show_legend_frame = event.IsChecked()
        elif (item=='loc'):
            self.conf.legend_loc  = event.GetString()
            auto_location = False
        elif (item=='onaxis'):
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
