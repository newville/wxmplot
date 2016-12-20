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
from .colors import hexcolor

FNB_STYLE = flat_nb.FNB_NO_X_BUTTON|flat_nb.FNB_SMART_TABS|flat_nb.FNB_NO_NAV_BUTTONS

ISPINSIZE = 110
FSPINSIZE = 135
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
        if config is None: config = PlotConfig()
        self.conf   = config
        self.trace_color_callback = trace_color_callback
        self.parent = parent
        self.canvas = self.conf.canvas
        self.axes = self.canvas.figure.get_axes()
        self.conf.relabel()
        self.DrawPanel()

    def DrawPanel(self):
        style = wx.DEFAULT_FRAME_STYLE## |wx.TAB_TRAVERSAL
        wx.Frame.__init__(self, self.parent, -1, 'Configure Plot', style=style)
        bgcol = mpl_color(self.canvas.figure.get_facecolor())
        self.bgcol = bgcol
        panel = wx.Panel(self, -1)
        panel.SetBackgroundColour(bgcol)

        font = wx.Font(13,wx.SWISS,wx.NORMAL,wx.NORMAL,False)
        panel.SetFont(font)

        self.nb = flat_nb.FlatNotebook(panel, wx.ID_ANY, agwStyle=FNB_STYLE)

        self.nb.SetActiveTabColour((253, 253, 230))
        self.nb.SetTabAreaColour((self.bgcol[0]-2, self.bgcol[1]-2, self.bgcol[2]-2))
        self.nb.SetNonActiveTabTextColour((10, 10, 100))
        self.nb.SetActiveTabTextColour((100, 10, 10))
        self.nb.AddPage(self.make_linetrace_panel(parent=self.nb, font=font),
                        'Line Traces', True)
        self.nb.AddPage(self.make_colors_panel(parent=self.nb, font=font),
                        'Colors and Margins', True)
        self.nb.AddPage(self.make_text_panel(parent=self.nb, font=font),
                        'Text and Labels', True)
        self.nb.AddPage(self.make_legend_panel(parent=self.nb, font=font),
                        'Legend Settings', True)
        self.nb.AddPage(self.make_scatter_panel(parent=self.nb, font=font),
                        'Scatterplot Settings',
                        self.conf.plot_type == 'scatter')
        for i in range(self.nb.GetPageCount()):
            self.nb.GetPage(i).SetBackgroundColour(self.bgcol)

        self.nb.SetSelection(0)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sty = wx.ALIGN_LEFT|wx.LEFT|wx.TOP|wx.BOTTOM|wx.EXPAND

        sizer.Add(self.nb,  1, wx.GROW|sty, 3)
        autopack(panel, sizer)
        self.SetMinSize((750, 200))
        self.SetSize((850, 400))
        self.Show()
        self.Raise()

    def make_scatter_panel(self, parent, font=None):
        # list of traces
        panel = wx.Panel(parent)
        if font is None:
            font = wx.Font(13,wx.SWISS,wx.NORMAL,wx.NORMAL,False)
        sizer = wx.GridBagSizer(4, 4)

        labstyle= wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL
        slab = wx.StaticText(panel, -1, 'Symbol Size:', size=(-1,-1),style=labstyle)
        ssize = wx.SpinCtrl(panel, -1, "", (-1, -1), (ISPINSIZE, 30))
        ssize.SetRange(1, 100)
        ssize.SetValue(self.conf.scatter_size)
        ssize.Bind(wx.EVT_SPINCTRL, partial(self.onScatter, argu='size'))

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
        nfcol.Bind(csel.EVT_COLOURSELECT, partial(self.onScatter, argu='scatt_nf'))
        necol.Bind(csel.EVT_COLOURSELECT, partial(self.onScatter, argu='scatt_ne'))
        sfcol.Bind(csel.EVT_COLOURSELECT, partial(self.onScatter, argu='scatt_sf'))
        secol.Bind(csel.EVT_COLOURSELECT, partial(self.onScatter, argu='scatt_se'))

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
            font = wx.Font(13,wx.SWISS,wx.NORMAL,wx.NORMAL,False)

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
        t_size.Bind(wx.EVT_SPINCTRL, partial(self.onText, argu='labelsize'))

        l_size = wx.SpinCtrl(panel, -1, " ", (-1, -1), (ISPINSIZE, 25))
        l_size.SetRange(2, 20)
        l_size.SetValue(self.conf.legendfont.get_size())
        l_size.Bind(wx.EVT_SPINCTRL, partial(self.onText, argu='legendsize'))

        sizer.Add(t0,      (0, 0), (1, 1), labstyle)
        sizer.Add(t1,      (0, 1), (1, 1), labstyle)
        sizer.Add(t_size,  (0, 2), (1, 1), labstyle)
        sizer.Add(t2,      (0, 3), (1, 1), labstyle)
        sizer.Add(l_size,  (0, 4), (1, 1), labstyle)

        self.titl = LabelEntry(panel, self.conf.title.replace('\n', '\\n'),
                               labeltext='Title: ',size=400,
                               action = partial(self.onText, argu='title'))
        self.ylab = LabelEntry(panel, self.conf.ylabel.replace('\n', '\\n'),
                               labeltext='Y Label: ',size=400,
                               action = partial(self.onText, argu='ylabel'))
        self.y2lab= LabelEntry(panel, self.conf.y2label.replace('\n', '\\n'),
                               labeltext='Y2 Label: ',size=400,
                               action = partial(self.onText, argu='y2label'))
        self.xlab = LabelEntry(panel, self.conf.xlabel.replace('\n', '\\n'),
                               labeltext='X Label: ',size=400,
                               action = partial(self.onText, argu='xlabel'))

        sizer.Add(self.titl.label, (1, 0), (1, 1), labstyle)
        sizer.Add(self.titl,       (1, 1), (1, 4), labstyle)
        sizer.Add(self.ylab.label, (2, 0), (1, 1), labstyle)
        sizer.Add(self.ylab,       (2, 1), (1, 4), labstyle)
        sizer.Add(self.y2lab.label,(3, 0), (1, 1), labstyle)
        sizer.Add(self.y2lab,      (3, 1), (1, 4), labstyle)
        sizer.Add(self.xlab.label, (4, 0), (1, 1), labstyle)
        sizer.Add(self.xlab,       (4, 1), (1, 4), labstyle)

        autopack(panel, sizer)
        return panel

    def make_legend_panel(self, parent, font=None):
        panel = scrolled.ScrolledPanel(parent, size=(800, 200),
                                       style=wx.GROW|wx.TAB_TRAVERSAL, name='p1')
        if font is None:
            font = wx.Font(13,wx.SWISS,wx.NORMAL,wx.NORMAL,False)

        sizer = wx.GridBagSizer(2, 2)
        i = 0
        irow = 0
        bstyle=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ST_NO_AUTORESIZE
        labstyle= wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL

        ax = self.axes[0]

        tl1 = wx.StaticText(panel, -1, 'Legend location:', size=(-1, -1), style=labstyle)
        leg_loc = wx.Choice(panel, -1, choices=self.conf.legend_locs, size=(120, -1))
        leg_loc.Bind(wx.EVT_CHOICE,partial(self.onShowLegend,argu='loc'))
        leg_loc.SetStringSelection(self.conf.legend_loc)

        leg_onax = wx.Choice(panel, -1, choices=self.conf.legend_onaxis_choices,
                             size=(80, -1))
        leg_onax.Bind(wx.EVT_CHOICE,partial(self.onShowLegend,argu='onaxis'))
        leg_onax.SetStringSelection(self.conf.legend_onaxis)

        drag_leg  = wx.CheckBox(panel,-1, 'Draggable Legend (experimental)', (-1, -1), (-1, -1))
        drag_leg.Bind(wx.EVT_CHECKBOX, self.onDragLegend)
        drag_leg.SetValue(self.conf.draggable_legend)

        hide_leg  = wx.CheckBox(panel,-1, 'Click Legend to Show/Hide Line', (-1, -1), (-1, -1))
        hide_leg.Bind(wx.EVT_CHECKBOX, self.onHideWithLegend)
        hide_leg.SetValue(self.conf.hidewith_legend)

        show_leg = wx.CheckBox(panel,-1, 'Show Legend', (-1, -1), (-1, -1))
        show_leg.Bind(wx.EVT_CHECKBOX,partial(self.onShowLegend,argu='legend'))
        show_leg.SetValue(self.conf.show_legend)

        show_lfr = wx.CheckBox(panel,-1, 'Show Legend Frame', (-1, -1), (-1, -1))
        show_lfr.Bind(wx.EVT_CHECKBOX,partial(self.onShowLegend,argu='frame'))
        show_lfr.SetValue(self.conf.show_legend_frame)

        sizer.Add(tl1,      (0, 0), (1, 1), wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(leg_loc,  (0, 1), (1, 2), labstyle)
        sizer.Add(leg_onax, (0, 3), (1, 1), labstyle)

        sizer.Add(show_leg,  (1, 0), (1, 2), labstyle)
        sizer.Add(show_lfr,  (2, 0), (1, 2), labstyle)
        sizer.Add(hide_leg,  (3, 0), (1, 2), labstyle)
        sizer.Add(drag_leg,  (4, 0), (1, 3), labstyle)

        autopack(panel, sizer)
        return panel


    def make_colors_panel(self, parent, font=None):
        panel = scrolled.ScrolledPanel(parent, size=(800, 200),
                                       style=wx.GROW|wx.TAB_TRAVERSAL, name='p1')
        if font is None:
            font = wx.Font(13,wx.SWISS,wx.NORMAL,wx.NORMAL,False)

        sizer = wx.GridBagSizer(2, 2)
        i = 0
        irow = 0
        bstyle=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ST_NO_AUTORESIZE
        labstyle= wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL
        btnstyle= wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL

        ax = self.axes[0]


        ctitle = wx.StaticText(panel, -1, 'Colors:', style=labstyle)

        ltext = wx.StaticText(panel, -1, ' Labels and Titles:', style=labstyle)
        lgrid = wx.StaticText(panel, -1, ' Grid:',       style=labstyle)
        lbgr  = wx.StaticText(panel, -1, ' Background:', style=labstyle)
        lframe= wx.StaticText(panel, -1, ' Plot Frame:', style=labstyle)

        textcol = csel.ColourSelect(panel,  -1, "",
                                    mpl_color(self.conf.textcolor, default=(2, 2, 2)),
                                    size=(25, 25))
        gridcol = csel.ColourSelect(panel, -1, "",
                                    mpl_color(self.conf.grid_color),
                                    size=(25, 25))
        bgcol = csel.ColourSelect(panel,  -1, "",
                                  mpl_color(ax.get_axis_bgcolor(), default=(255, 255, 252)),
                                  size=(25, 25))


        fbgcol = csel.ColourSelect(panel,  -1, "",
                                   mpl_color(self.canvas.figure.get_facecolor(), default=(255,255,252)),
                                   size=(25, 25))

        bgcol.Bind(csel.EVT_COLOURSELECT,   partial(self.onColor, argu='bg'))
        fbgcol.Bind(csel.EVT_COLOURSELECT,  partial(self.onColor, argu='fbg'))
        gridcol.Bind(csel.EVT_COLOURSELECT, partial(self.onColor, argu='grid'))
        textcol.Bind(csel.EVT_COLOURSELECT, partial(self.onColor, argu='text'))

        sizer.Add(ctitle,    (0, 0), (1, 1), labstyle, 2)
        sizer.Add(ltext,     (0, 1), (1, 1), labstyle, 2)
        sizer.Add(textcol,   (0, 2), (1, 1), labstyle, 2)
        sizer.Add(lbgr,      (1, 1), (1, 1), labstyle, 2)
        sizer.Add(bgcol,     (1, 2), (1, 1), labstyle, 2)
        sizer.Add(lgrid,     (2, 1), (1, 1), labstyle, 2)
        sizer.Add(gridcol,   (2, 2), (1, 1), labstyle, 2)
        sizer.Add(lframe,    (3, 1), (1, 1), labstyle, 2)
        sizer.Add(fbgcol,    (3, 2), (1, 1), labstyle, 2)

        ctitle = wx.StaticText(panel, -1, ' Plot Components:', style=labstyle)
        show_grid  = wx.CheckBox(panel,-1, 'Show Grid', (-1, -1), (-1, -1))
        show_grid.Bind(wx.EVT_CHECKBOX,self.onShowGrid)
        show_grid.SetValue(self.conf.show_grid)

        show_box  = wx.CheckBox(panel,-1, 'Show Top/Right Axes', (-1, -1), (-1, -1))
        show_box.Bind(wx.EVT_CHECKBOX, self.onShowBox)
        show_box.SetValue(self.conf.axes_style == 'box')
        
        sizer.Add(ctitle,     (0, 3), (1, 2), labstyle, 2)
        sizer.Add(show_grid,  (1, 4), (1, 2), labstyle, 2)
        sizer.Add(show_box,   (2, 4), (1, 2), labstyle, 2)

        # margins
        ppanel = self.GetParent()
        _left, _top, _right, _bot = ["%.3f"% x for x in ppanel.get_default_margins()]

        mtitle = wx.StaticText(panel, -1, 'Margins: ', style=labstyle)
        ltitle = wx.StaticText(panel, -1, ' left: ',   style=labstyle)
        rtitle = wx.StaticText(panel, -1, ' right: ',  style=labstyle)
        btitle = wx.StaticText(panel, -1, ' bottom: ', style=labstyle)
        ttitle = wx.StaticText(panel, -1, ' top: ',    style=labstyle)

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

        sizer.Add(mtitle,   (4, 0), (1, 1), labstyle, 2)
        sizer.Add(auto_m,   (4, 1), (1, 2), labstyle, 5)
        sizer.Add(ltitle,   (5, 1), (1, 1), labstyle, 5)
        sizer.Add(lmarg,    (5, 2), (1, 2), labstyle, 5)
        sizer.Add(rtitle,   (6, 1), (1, 1), labstyle, 5)
        sizer.Add(rmarg,    (6, 2), (1, 2), labstyle, 5)
        sizer.Add(btitle,   (7, 1), (1, 1), labstyle, 5)
        sizer.Add(bmarg,    (7, 2), (1, 2), labstyle, 5)
        sizer.Add(ttitle,   (8, 1), (1, 1), labstyle, 5)
        sizer.Add(tmarg,    (8, 2), (1, 2), labstyle, 5)

        autopack(panel, sizer)
        return panel

    def make_linetrace_panel(self, parent, font=None):
        # list of traces

        # panel = wx.Panel(parent)
        panel = scrolled.ScrolledPanel(parent, size=(800, 200),
                                       style=wx.GROW|wx.TAB_TRAVERSAL, name='p1')

        if font is None:
            font = wx.Font(13,wx.SWISS,wx.NORMAL,wx.NORMAL,False)

        sizer = wx.GridBagSizer(2, 2)
        i = 0
        irow = 0
        for t in ('#','Label','Color', 'Line Style',
                  'Thickness','Symbol',' Size', 'Z Order', 'Join Style'):
            x = wx.StaticText(panel, -1, t)
            x.SetFont(font)
            sizer.Add(x,(irow,i),(1,1),wx.ALIGN_LEFT|wx.ALL, 3)
            i = i+1
        self.trace_labels = []
        ntrace_display = min(self.conf.ntrace+1, len(self.conf.traces))
        for i in range(ntrace_display): # len(self.axes.get_lines())):
            irow += 1
            argu  = "trace %i" % i
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
                               action = partial(self.onText,argu=argu))
            self.trace_labels.append(lab)

            col = csel.ColourSelect(panel,  -1, "", dcol, size=(25, 25))
            col.Bind(csel.EVT_COLOURSELECT,partial(self.onColor,argu=argu))

            thk = FloatSpin(panel, -1,  pos=(-1,-1), size=(FSPINSIZE, 30), value=dthk,
                            min_val=0, max_val=10, increment=0.5, digits=1)
            thk.Bind(EVT_FLOATSPIN, partial(self.onThickness, argu=argu))

            sty = wx.Choice(panel, choices=self.conf.styles, size=(110,-1))
            sty.Bind(wx.EVT_CHOICE,partial(self.onStyle,argu=argu))
            sty.SetStringSelection(dsty)

            msz = FloatSpin(panel, -1,  pos=(-1,-1), size=(FSPINSIZE, 30), value=dmsz,
                            min_val=0, max_val=30, increment=1, digits=0)
            msz.Bind(EVT_FLOATSPIN, partial(self.onMarkerSize, argu=argu))

            zor = FloatSpin(panel, -1,  pos=(-1,-1), size=(FSPINSIZE, 30),
                            value=dzord,
                            min_val=-500, max_val=500, increment=1, digits=0)
            zor.Bind(EVT_FLOATSPIN, partial(self.onZorder, argu=argu))

            sym = wx.Choice(panel, -1, choices=self.conf.symbols, size=(120,-1))
            sym.Bind(wx.EVT_CHOICE,partial(self.onSymbol,argu=argu))

            sym.SetStringSelection(dsym)

            jsty = wx.Choice(panel, -1, choices=self.conf.drawstyles, size=(100,-1))
            jsty.Bind(wx.EVT_CHOICE, partial(self.onJoinStyle, argu=argu))
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

    def onColor(self, event, argu='grid'):
        color = hexcolor( event.GetValue() )
        if argu[:6] == 'trace ':
            trace = int(argu[6:])
            self.conf.set_trace_color(color,trace=trace)
            if hasattr(self.trace_color_callback, '__call__'):
                self.trace_color_callback(trace, color)
            self.redraw_legend()

        elif argu == 'grid':
            self.conf.grid_color = color
            for ax in self.axes:
                for i in ax.get_xgridlines()+ax.get_ygridlines():
                    i.set_color(color)
                    i.set_zorder(-30)
        elif argu == 'bg':
            for ax in self.axes:
                ax.set_axis_bgcolor(color)
        elif argu == 'fbg':
            self.canvas.figure.set_facecolor(color)
        elif argu == 'text':
            self.conf.textcolor = color
            self.conf.relabel()
            return
        self.canvas.draw()

    def onStyle(self,event,argu='grid'):
        try:
            self.conf.set_trace_style(event.GetString(),trace=int(argu[6:]))
            self.redraw_legend()
            self.canvas.draw()
        except:
            return

    def onJoinStyle(self, event, argu='grid'):
        try:
            self.conf.set_trace_drawstyle(event.GetString(), trace=int(argu[6:]))
            self.redraw_legend()
            self.canvas.draw()
        except:
            return

    def onSymbol(self,event,argu='grid'):
        try:
            self.conf.set_trace_marker(event.GetString(),trace=int(argu[6:]))
            self.redraw_legend()
            self.canvas.draw()
        except:
            return

    def onMarkerSize(self, event,argu=''):
        val = event.GetEventObject().GetValue()
        try:
            self.conf.set_trace_markersize(val, trace=int(argu[6:]))
            self.redraw_legend()
            self.canvas.draw()
        except:
            return

    def onZorder(self, event,argu=''):
        val = event.GetEventObject().GetValue()
        try:
            self.conf.set_trace_zorder(val, trace=int(argu[6:]))
            self.redraw_legend()
            self.canvas.draw()
        except:
            return

    def onThickness(self, event, argu=''):
        val = event.GetEventObject().GetValue()
        try:
            self.conf.set_trace_linewidth(val, trace=int(argu[6:]))
            self.redraw_legend()
            self.canvas.draw()
        except:
            return

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
        panel = self.GetParent()
        self.conf.margins = [float(w.GetValue()) for w in self.margins]
        left, top, right, bottom = self.conf.margins
        panel.gridspec.update(left=left, top=1-top, right=1-right, bottom=bottom)
        for ax in panel.fig.get_axes():
            ax.update_params()
            ax.set_position(ax.figbox)
        self.canvas.draw()

    def onScatter(self, event, argu=None):

        if self.conf.scatter_coll is None or argu is None:
            return
        conf = self.conf
        coll = conf.scatter_coll
        recolor = True
        if argu == 'size':
            conf.scatter_size = event.GetInt()
            coll._sizes = (conf.scatter_size,)
            recolor = False
        elif argu == 'scatt_nf':
            self.conf.scatter_normalcolor = hexcolor(event.GetValue())
        elif argu == 'scatt_ne':
            self.conf.scatter_normaledge = hexcolor(event.GetValue())
        elif argu == 'scatt_sf':
            self.conf.scatter_selectcolor = hexcolor(event.GetValue())
        elif argu == 'scatt_se':
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

    def onText(self, event, argu=''):
        if argu=='labelsize':
            size = event.GetInt()
            self.conf.labelfont.set_size(size)
            self.conf.titlefont.set_size(size+1)
            for ax in self.axes:
                for lab in ax.get_xticklabels()+ax.get_yticklabels():
                    lab.set_fontsize(size)
            self.conf.relabel()
            return
        if argu=='legendsize':
            size = event.GetInt()
            self.conf.legendfont.set_size(size)
            # self.conf.relabel()
            self.conf.draw_legend()
            return
        if argu == 'title':
            wid = self.titl
        elif argu == 'ylabel':
            wid = self.ylab
        elif argu == 'y2label':
            wid = self.y2lab
        elif argu == 'xlabel':
            wid = self.xlab
        elif argu[:6] == 'trace ':
            wid = self.trace_labels[int(argu[6:])]


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
        if argu in ('xlabel', 'ylabel', 'y2label', 'title'):
            try:
                kws = {argu: s}
                self.conf.relabel(**kws)
                wid.SetBackgroundColour((255, 255, 255))
            except: # as from latex error!
                wid.SetBackgroundColour((250, 250, 200))
        elif argu[:6] == 'trace ':
            try:
                self.conf.set_trace_label(s, trace=int(argu[6:]))
                self.redraw_legend()
            except:
                pass

    def onShowGrid(self,event):
        self.conf.enable_grid(show=event.IsChecked())

    def onShowBox(self, event=None):
        style='box'
        if not event.IsChecked(): style='open'
        self.conf.set_axes_style(style=style)

    def onShowLegend(self,event,argu=''):
        auto_location = True
        if (argu == 'legend'):
            self.conf.show_legend  = event.IsChecked()
        elif (argu=='frame'):
            self.conf.show_legend_frame = event.IsChecked()
        elif (argu=='loc'):
            self.conf.legend_loc  = event.GetString()
            auto_location = False
        elif (argu=='onaxis'):
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
