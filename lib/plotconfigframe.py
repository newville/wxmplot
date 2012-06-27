#!/usr/bin/python
#
# MPlot GUI to Configure (2D) Plots
#
import wx
import wx.lib.colourselect  as csel
import wx.lib.agw.flatnotebook as flat_nb
import wx.lib.scrolledpanel as scrolled
import numpy as np

import matplotlib
from matplotlib import rcParams
from matplotlib.colors import colorConverter
from matplotlib.font_manager import fontManager, FontProperties
from matplotlib.pyparsing import ParseFatalException
from matplotlib.colors import colorConverter
to_rgba = colorConverter.to_rgba

from utils import Closure, LabelEntry
from config import PlotConfig
from colors import hexcolor

FNB_STYLE = flat_nb.FNB_NO_X_BUTTON|flat_nb.FNB_SMART_TABS|flat_nb.FNB_NO_NAV_BUTTONS

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
        wx.Frame.__init__(self, self.parent, -1, 'Configure 2D Plot', style=style)
        bgcol = mpl_color(self.canvas.figure.get_facecolor())
        self.bgcol = bgcol
        panel = self.mainpanel = wx.Panel(self, -1)
        panel.SetBackgroundColour(bgcol)

        font = wx.Font(13,wx.SWISS,wx.NORMAL,wx.NORMAL,False)
        panel.SetFont(font)

        topsizer  = wx.GridBagSizer(5,8)
        labstyle= wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL
        ltitle = wx.StaticText(panel, -1, 'Plot Configuration',
                              style=labstyle)
        ltitle.SetFont(font)
        ltitle.SetForegroundColour("Blue")

        topsizer.Add(ltitle, (0, 0), (1, 5),  labstyle, 2)

        self.titl = LabelEntry(panel, self.conf.title.replace('\n', '\\n'),
                               labeltext='Title: ',size=420,
                               action = Closure(self.onText, argu='title'))
        self.ylab = LabelEntry(panel, self.conf.ylabel.replace('\n', '\\n'),
                               labeltext='Y Label: ',size=420,
                               action = Closure(self.onText, argu='ylabel'))
        self.y2lab= LabelEntry(panel, self.conf.y2label.replace('\n', '\\n'),
                               labeltext='Y2 Label: ',size=420,
                               action = Closure(self.onText, argu='y2label'))
        self.xlab = LabelEntry(panel, self.conf.xlabel.replace('\n', '\\n'),
                               labeltext='X Label: ',size=420,
                               action = Closure(self.onText, argu='xlabel'))

        topsizer.Add(self.titl.label, (1, 0), (1, 1), labstyle, 5)
        topsizer.Add(self.titl,       (1, 1), (1, 5), labstyle, 5)
        topsizer.Add(self.ylab.label, (2, 0), (1, 1), labstyle, 5)
        topsizer.Add(self.ylab,       (2, 1), (1, 5), labstyle, 5)
        topsizer.Add(self.y2lab.label,(3, 0), (1, 1), labstyle, 5)
        topsizer.Add(self.y2lab,      (3, 1), (1, 5), labstyle, 5)
        topsizer.Add(self.xlab.label, (4, 0), (1, 1), labstyle, 5)
        topsizer.Add(self.xlab,       (4, 1), (1, 5), labstyle, 5)


        tl2 = wx.StaticText(panel, -1, 'Text Size:', size=(-1, -1), style=labstyle)
        txt_size = wx.SpinCtrl(panel, -1, "", (-1, -1), (55, 30))
        txt_size.SetRange(5, 30)
        txt_size.SetValue(self.conf.labelfont.get_size())
        txt_size.Bind(wx.EVT_SPINCTRL, Closure(self.onText, argu='size'))

        topsizer.Add(tl2,        (1, 6), (1, 1), labstyle, 2)
        topsizer.Add(txt_size,   (1, 7), (1, 1), labstyle, 2)


        show_grid  = wx.CheckBox(panel,-1, 'Show Grid', (-1, -1), (-1, -1))
        show_grid.Bind(wx.EVT_CHECKBOX,self.onShowGrid)
        show_grid.SetValue(self.conf.show_grid)

        show_leg = wx.CheckBox(panel,-1, 'Show Legend', (-1, -1), (-1, -1))
        show_leg.Bind(wx.EVT_CHECKBOX,Closure(self.onShowLegend,argu='legend'))
        show_leg.SetValue(self.conf.show_legend)

        show_lfr = wx.CheckBox(panel,-1, 'Legend Frame', (-1, -1), (-1, -1))
        show_lfr.Bind(wx.EVT_CHECKBOX,Closure(self.onShowLegend,argu='frame'))
        show_lfr.SetValue(self.conf.show_legend_frame)

        topsizer.Add(show_grid, (2, 6), (1, 2), labstyle, 2)
        topsizer.Add(show_leg,  (3, 6), (1, 2), labstyle, 2)
        topsizer.Add(show_lfr,  (4, 6), (1, 2), labstyle, 2)


        tcol = wx.StaticText(panel, -1, 'Colors',style=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)

        bstyle=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ST_NO_AUTORESIZE

        ax = self.axes[0]

        col = mpl_color(ax.get_xgridlines()[0].get_color(), default=(240, 240, 240))
        gridcol = csel.ColourSelect(panel, -1, "Grid", col, size=(50, 30))

        col = mpl_color(ax.get_axis_bgcolor(), default=(255, 255, 252))
        bgcol = csel.ColourSelect(panel,  -1, "Background", col, size=(100, 30))

        col = mpl_color(self.canvas.figure.get_facecolor(), default=(255,255,252))
        fbgcol = csel.ColourSelect(panel,  -1, "Frame", col, size=(80, 30))

        col = mpl_color(self.conf.textcolor, default=(2, 2, 2))
        textcol = csel.ColourSelect(panel,  -1, "Text", col, size=(80, 30))


        bgcol.Bind(csel.EVT_COLOURSELECT,   Closure(self.onColor, argu='bg'))
        fbgcol.Bind(csel.EVT_COLOURSELECT,  Closure(self.onColor, argu='fbg'))
        gridcol.Bind(csel.EVT_COLOURSELECT, Closure(self.onColor, argu='grid'))
        textcol.Bind(csel.EVT_COLOURSELECT, Closure(self.onColor, argu='text'))

        btnstyle= wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL

        midsizer  = wx.GridBagSizer(5, 8)

        midsizer.Add(tcol,      (0, 0), (1, 1), labstyle, 2)
        midsizer.Add(gridcol,   (0, 1), (1, 1), btnstyle, 2)
        midsizer.Add(bgcol,     (0, 2), (1, 1), btnstyle, 2)
        midsizer.Add(fbgcol,    (0, 3), (1, 1), btnstyle, 2)
        midsizer.Add(textcol,   (0, 4), (1, 1), btnstyle, 2)


        tl1 = wx.StaticText(panel, -1, '  Legend at:', size=(-1, -1), style=labstyle)
        leg_loc = wx.Choice(panel, -1, choices=self.conf.legend_locs, size=(120, -1))
        leg_loc.Bind(wx.EVT_CHOICE,Closure(self.onShowLegend,argu='loc'))
        leg_loc.SetStringSelection(self.conf.legend_loc)

        leg_onax = wx.Choice(panel, -1, choices=self.conf.legend_onaxis_choices,
                             size=(90, -1))
        leg_onax.Bind(wx.EVT_CHOICE,Closure(self.onShowLegend,argu='onaxis'))
        leg_onax.SetStringSelection(self.conf.legend_onaxis)


        midsizer.Add(tl1,      (0, 5), (1, 1), wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        midsizer.Add(leg_loc,  (0, 6), (1, 1), labstyle, 2)
        midsizer.Add(leg_onax, (0, 7), (1, 1), labstyle, 2)

        self.nb = flat_nb.FlatNotebook(panel, wx.ID_ANY, agwStyle=FNB_STYLE)

        self.nb.SetActiveTabColour((253, 253, 230))
        self.nb.SetTabAreaColour((self.bgcol[0]-2, self.bgcol[1]-2, self.bgcol[2]-2))
        self.nb.SetNonActiveTabTextColour((10, 10, 100))
        self.nb.SetActiveTabTextColour((100, 10, 10))
        self.nb.AddPage(self.make_linetrace_panel(parent=self.nb, font=font),
                        'Line Traces', True)
        self.nb.AddPage(self.make_scatter_panel(parent=self.nb, font=font),
                        'Scatterplot Settings',
                        self.conf.plot_type == 'scatter')

        #bok = wx.Button(panel, -1, 'OK',    size=(-1,-1))
        #bok.Bind(wx.EVT_BUTTON,self.onExit)
        
        #btnsizer = wx.BoxSizer(wx.HORIZONTAL)
        #btnsizer.Add(bok,0, wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.LEFT, 2)

        mainsizer = wx.BoxSizer(wx.VERTICAL)
        a = wx.ALIGN_LEFT|wx.LEFT|wx.TOP|wx.BOTTOM|wx.EXPAND
        mainsizer.Add(topsizer, 0, a, 3)
        mainsizer.Add(midsizer, 0, a, 3)
        mainsizer.Add(self.nb,  1, wx.GROW|a, 3)
        #mainsizer.Add(btnsizer, 1, a, 2)
        autopack(panel,mainsizer)

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(panel,   1, a, 2)
        autopack(self,s)
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
        ssize = wx.SpinCtrl(panel, -1, "", (-1, -1), (55,30))
        ssize.SetRange(1, 100)
        ssize.SetValue(self.conf.scatter_size)
        ssize.Bind(wx.EVT_SPINCTRL, Closure(self.onScatter, argu='size'))

        sizer.Add(slab,  (0, 0), (1,1), labstyle, 5)
        sizer.Add(ssize, (0, 1), (1,1), labstyle, 5)

        conf = self.conf
        nfcol = csel.ColourSelect(panel,  -1, "",
                                  mpl_color(conf.scatter_normalcolor,
                                            default=(0, 0, 128)),
                                  size=(45, 30))
        necol = csel.ColourSelect(panel,  -1, "",
                                  mpl_color(conf.scatter_normaledge,
                                            default=(0, 0, 200)),
                                  size=(45, 30))
        sfcol = csel.ColourSelect(panel,  -1, "",
                                  mpl_color(conf.scatter_selectcolor,
                                            default=(128, 0, 0)),
                                  size=(45, 30))
        secol = csel.ColourSelect(panel,  -1, "",
                                  mpl_color(conf.scatter_selectedge,
                                           default=(200, 0, 0)),
                                  size=(45, 30))
        nfcol.Bind(csel.EVT_COLOURSELECT, Closure(self.onScatter, argu='scatt_nf'))
        necol.Bind(csel.EVT_COLOURSELECT, Closure(self.onScatter, argu='scatt_ne'))
        sfcol.Bind(csel.EVT_COLOURSELECT, Closure(self.onScatter, argu='scatt_sf'))
        secol.Bind(csel.EVT_COLOURSELECT, Closure(self.onScatter, argu='scatt_se'))

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

    def make_linetrace_panel(self, parent, font=None):
        # list of traces

        # panel = wx.Panel(parent)
        panel = scrolled.ScrolledPanel(parent, size=(800, 200),
                                       style=wx.GROW|wx.TAB_TRAVERSAL, name='p1')
        
        if font is None:
            font = wx.Font(13,wx.SWISS,wx.NORMAL,wx.NORMAL,False)

        sizer = wx.GridBagSizer(5, 5)
        i = 0
        irow = 0
        for t in ('#','Label','Color', 'Line Style',
                  'Thickness','Symbol',' Size', 'Join Style'):
            x = wx.StaticText(panel, -1, t)
            x.SetFont(font)
            sizer.Add(x,(irow,i),(1,1),wx.ALIGN_LEFT|wx.ALL, 5)
            i = i+1
        self.trace_labels = []
        ntrace_display = min(self.conf.ntrace+1, len(self.conf.traces))
        for i in range(ntrace_display): # len(self.axes.get_lines())):
            irow += 1
            argu  = "trace %i" % i
            lin  = self.conf.traces[i]
            dlab = lin.label
            dcol = lin.color
            dthk = lin.linewidth
            dmsz = lin.markersize
            dsty = lin.style
            djsty = lin.drawstyle
            dsym = lin.marker
            lab = LabelEntry(panel, dlab, size=140,labeltext="%i" % (i+1),
                               action = Closure(self.onText,argu=argu))
            self.trace_labels.append(lab)

            col = csel.ColourSelect(panel,  -1, "", dcol, size=wx.DefaultSize)
            col.Bind(csel.EVT_COLOURSELECT,Closure(self.onColor,argu=argu))

            thk = wx.SpinCtrl(panel, -1, "", (-1,-1),(55,30))
            thk.SetRange(0, 20)
            thk.SetValue(dthk)
            thk.Bind(wx.EVT_SPINCTRL, Closure(self.onThickness, argu=argu))

            sty = wx.Choice(panel, -1, choices=self.conf.styles, size=(100,-1))
            sty.Bind(wx.EVT_CHOICE,Closure(self.onStyle,argu=argu))
            sty.SetStringSelection(dsty)

            msz = wx.SpinCtrl(panel, -1, "", (-1,-1),(55,30))
            msz.SetRange(0, 30)
            msz.SetValue(dmsz)
            msz.Bind(wx.EVT_SPINCTRL, Closure(self.onMarkerSize, argu=argu))

            sym = wx.Choice(panel, -1, choices=self.conf.symbols, size=(120,-1))
            sym.Bind(wx.EVT_CHOICE,Closure(self.onSymbol,argu=argu))

            sym.SetStringSelection(dsym)

            jsty = wx.Choice(panel, -1, choices=self.conf.drawstyles, size=(100,-1))
            jsty.Bind(wx.EVT_CHOICE,Closure(self.onJoinStyle, argu=argu))
            jsty.SetStringSelection(djsty)

            sizer.Add(lab.label,(irow,0),(1,1),wx.ALIGN_LEFT|wx.ALL, 5)
            sizer.Add(lab,(irow,1),(1,1),wx.ALIGN_LEFT|wx.ALL, 5)
            sizer.Add(col,(irow,2),(1,1),wx.ALIGN_LEFT|wx.ALL, 5)
            sizer.Add(sty,(irow,3),(1,1),wx.ALIGN_LEFT|wx.ALL, 5)
            sizer.Add(thk,(irow,4),(1,1),wx.ALIGN_LEFT|wx.ALL, 5)
            sizer.Add(sym,(irow,5),(1,1),wx.ALIGN_LEFT|wx.ALL, 5)
            sizer.Add(msz,(irow,6),(1,1),wx.ALIGN_LEFT|wx.ALL, 5)
            sizer.Add(jsty,(irow,7),(1,1),wx.ALIGN_LEFT|wx.ALL, 5)

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
        try:
            self.conf.set_trace_markersize(event.GetInt(),trace=int(argu[6:]))
            self.redraw_legend()
            self.canvas.draw()
        except:
            return

    def onThickness(self, event,argu=''):
        try:
            self.conf.set_trace_linewidth(event.GetInt(),trace=int(argu[6:]))
            self.redraw_legend()
            self.canvas.draw()
        except:
            return

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
        if argu=='size':
            size = event.GetInt()
            self.conf.labelfont.set_size(size)
            self.conf.titlefont.set_size(size+1)
            for ax in self.axes:
                for lab in ax.get_xticklabels()+ax.get_yticklabels():
                    lab.set_fontsize(size)
            self.conf.relabel()
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

        if '\\n' in s:
            s = s.replace('\\n', '\n')
        if argu in ('xlabel', 'ylabel', 'y2label', 'title'):
            try:
                kws = {argu: s}
                self.conf.relabel(**kws)
                wid.SetBackgroundColour((255, 255, 255))
            except ParseFatalException: # as from latex error!
                wid.SetBackgroundColour((250, 250, 200))
        elif argu[:6] == 'trace ':
            try:
                self.conf.set_trace_label(s, trace=int(argu[6:]))
                self.redraw_legend()
            except:
                pass

    def onShowGrid(self,event):
        self.conf.enable_grid(show=event.IsChecked())

    def onShowLegend(self,event,argu=''):
        if (argu == 'legend'):
            self.conf.show_legend  = event.IsChecked()
        elif (argu=='frame'):
            self.conf.show_legend_frame = event.IsChecked()
        elif (argu=='loc'):
            self.conf.legend_loc  = event.GetString()
        elif (argu=='onaxis'):
            self.conf.legend_onaxis  = event.GetString()
        self.conf.draw_legend()

    def redraw_legend(self):
        self.conf.draw_legend()

    def onExit(self, event):
        self.Close(True)
