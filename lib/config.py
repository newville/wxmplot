#!/usr/bin/python
"""
Plot Configuration of (simplified) properties for Matplotlib Lines.  In matplotlib,
a line is a series of x,y points, which are to be connected into a single trace.

Here, we'll call the thing drawn on the screen a 'trace', and the configuration
here is for trace properties:
    color        color of trace (a color name or hex code such as #FF00FF)
    style        trace style: one of ('solid', 'dashed', 'dotted', 'dash-dot')
    drawstyle    style for joining point: one of ('default', 'steps-pre', 'steps-post')
    width        trace width
    marker       marker symbol for each point (see list below)
    markersize   size of marker
    markercolor  color for marker (defaults to same as trace color
    label        label used for trace


A matplotlib Line2D can have many more properties than this: these are not set here.

Valid marker names are:
   'no symbol', '+', 'o','x', '^','v','>','<','|','_',
   'square','diamond','thin diamond', 'hexagon','pentagon',
   'tripod 1','tripod 2'

"""

from matplotlib.font_manager import FontProperties
from matplotlib import rcParams
from . import colors

# use ordered dictionary to control order displayed in GUI dropdown lists
try:
    from collections import OrderedDict
except ImportError:
    from .ordereddict import OrderedDict

StyleMap  = OrderedDict()
DrawStyleMap  = OrderedDict()
MarkerMap = OrderedDict()

for k in ('default', 'steps-pre','steps-mid', 'steps-post'):
    DrawStyleMap[k] = k

for k,v in (('solid', ('-', None)),
            ('dashed', ('--', (6, 6))),
            ('long dashed', ('--', (12, 4))),
            ('short dashed', ('--',(4, 1))),
            ('dotted', (':', None)),
            ('dash-dot', ('-.', None))):
    StyleMap[k]=v


for k,v in (('no symbol','None'), ('+','+'), ('o','o'), ('x','x'),
            ('square','s'), ('diamond','D'), ('thin diamond','d'),
            ('^','^'), ('v','v'), ('>','>'), ('<','<'),
            ('|','|'),('_','_'), ('hexagon','h'), ('pentagon','p'),
            ('tripod 1','1'), ('tripod 2','2')):
    MarkerMap[k] = v


class LineProperties:
    """ abstraction for Line2D properties, closely related to a
    MatPlotlib Line2D.  used to set internal line properties, and
    to  make the matplotlib calls to set the Line2D properties
    """

    def __init__(self, color='black', style='solid', drawstyle='default',
                 linewidth=2, marker='no symbol',markersize=6,
                 markercolor=None, zorder=0, label=''):
        self.color      = color
        self.style      = style
        self.drawstyle  = drawstyle
        self.linewidth  = linewidth
        self.marker     = marker
        self.markersize = markersize
        self.markercolor= markercolor
        self.label      = label
        self.zorder     = zorder
        self.data_range = [None, None, None, None]

    def update(self, line=None):
        """ set a matplotlib Line2D to have the current properties"""
        if line:
            markercolor = self.markercolor
            if markercolor is None: markercolor=self.color
            # self.set_markeredgecolor(markercolor, line=line)
            # self.set_markerfacecolor(markercolor, line=line)

            self.set_label(self.label, line=line)
            self.set_color(self.color, line=line)
            self.set_style(self.style, line=line)
            self.set_drawstyle(self.drawstyle, line=line)
            self.set_marker(self.marker,line=line)
            self.set_markersize(self.markersize, line=line)
            self.set_linewidth(self.linewidth, line=line)

    def set_color(self, color,line=None):
        self.color = color
        c = colors.hexcolor(color)
        def _setc(aline, col):
            aline.set_color(col)

        if line:
            for lx in line:
                if isinstance(lx, (list, tuple)):
                    for sublx in lx:
                        _setc(sublx, c)
                else:
                    _setc(lx, c)

    def set_label(self, label,line=None):
        self.label = label
        if line:
            line[0].set_label(self.label)

    def set_zorder(self, zorder, line=None):
        self.zorder = zorder
        if line:
            line[0].set_zorder(zorder)

    def set_style(self, style, line=None):
        sty = 'solid'
        if style in StyleMap:
            sty = style
        elif style in StyleMap.values():
            for k,v in StyleMap.items():
                if v == style:  sty = k
        self.style = sty
        if line:
            _key, _opts = StyleMap[sty]
            line[0].set_linestyle(_key)
            if _key == '--' and _opts is not None:
                line[0].set_dashes(_opts)

    def set_drawstyle(self, style, line=None):
        sty = 'default'
        if style in DrawStyleMap:
            sty = style
        self.drawstyle = sty
        if line:
            line[0].set_drawstyle(DrawStyleMap[sty])

    def set_marker(self,marker,line=None):
        sym = 'no symbol'
        if marker in MarkerMap:
            sym = marker
        elif marker in MarkerMap.values():
            for k,v in MarkerMap.items():
                if v == marker:  sym = k
        self.marker = sym
        if line:
            line[0].set_marker(MarkerMap[sym])

    def set_markersize(self,markersize,line=None):
        self.markersize=markersize
        if line:
            line[0].set_markersize(self.markersize/2.0)

    def set_linewidth(self, linewidth, line=None):
        self.linewidth=linewidth
        if line:
            for l in line:
                try:
                    l.set_linewidth(self.linewidth/2.0)
                except:
                    pass

class PlotConfig:
    """ MPlot Configuration for 2D Plots... holder class for most configuration data """
    def __init__(self, canvas=None): # trace_color_callback=None):
        self.canvas = canvas

        self.styles      = list(StyleMap.keys())
        self.drawstyles  = list(DrawStyleMap.keys())
        self.symbols     = list(MarkerMap.keys())

        self.legend_locs = ['best', 'upper right' , 'lower right', 'center right',
                            'upper left', 'lower left',  'center left',
                            'upper center', 'lower center', 'center']

        self.legend_abbrevs = {'ur': 'upper right' ,  'ul': 'upper left',
                               'cr': 'center right',  'cl': 'center left',
                               'lr': 'lower right',   'll': 'lower left',
                               'uc': 'upper center',  'lc': 'lower center',
                               'cc': 'center'}

        self.axes_style_choices = ['box', 'open']
        self.legend_onaxis_choices =  ['on plot', 'off plot']
        self.set_defaults()

    def set_defaults(self):
        self.zoom_x = 0
        self.zoom_y = 0
        self.zoom_init = (0, 1)
        self.zoom_lims = []
        self.title  = ' '
        self.yscale = 'linear'
        self.xlabel = ' '
        self.ylabel = ' '
        self.y2label = ' '
        self.added_texts = []
        self.plot_type = 'lineplot'
        self.scatter_size = 6
        self.scatter_normalcolor = 'blue'
        self.scatter_normaledge  = 'blue'
        self.scatter_selectcolor = 'red'
        self.scatter_selectedge  = 'red'
        self.scatter_data = None
        self.scatter_coll = None
        self.scatter_mask = None

        self.margins = None
        self.auto_margins = True
        self.legend_loc    = 'best'
        self.legend_onaxis = 'on plot'
        self.mpl_legend  = None
        self.show_grid   = True
        self.draggable_legend = False
        self.hidewith_legend = True
        self.show_legend = False
        self.show_legend_frame = False
        self.axes_style = 'box'

        # self.trace_color_callback = trace_color_callback
        f0 =  FontProperties()
        self.labelfont = f0.copy()
        self.titlefont = f0.copy()
        self.legendfont = f0.copy()
        self.legendfont.set_size(7)
        self.labelfont.set_size(9)
        self.titlefont.set_size(10)
        self.textcolor = '#000000'
        self.grid_color = '#E5E5E5'
        # preload some traces
        self.ntrace = 0
        self.lines  = [None]*30
        self.traces = []
        self._init_trace( 0, 'blue',      'solid')
        self._init_trace( 1, 'red',       'solid')
        self._init_trace( 2, 'black',     'solid')
        self._init_trace( 3, 'magenta',   'solid')
        self._init_trace( 4, 'green3',    'solid')
        self._init_trace( 5, 'maroon',    'solid')
        self._init_trace( 6, 'blue',     'dashed')
        self._init_trace( 7, 'red',      'dashed')
        self._init_trace( 8, 'black',    'dashed')
        self._init_trace( 9, 'magenta',  'dashed')
        self._init_trace(10, 'green3',   'dashed')
        self._init_trace(11, 'maroon',   'dashed')
        self._init_trace(12, 'blue',     'dotted')
        self._init_trace(13, 'red',      'dotted')
        self._init_trace(14, 'black',    'dotted')
        self._init_trace(15, 'magenta',  'dotted')
        self._init_trace(16, 'green3',   'dotted')
        self._init_trace(17, 'maroon',   'dotted')
        self._init_trace(18, 'blue',      'solid', marker='+')
        self._init_trace(19, 'red',       'solid', marker='+')
        self._init_trace(20, 'black',     'solid', marker='o')

    def _init_trace(self, n,  color, style,
                    linewidth=2.5, zorder=None, marker=None, markersize=8):
        """ used for building set of traces"""
        while n >= len(self.traces):
            self.traces.append(LineProperties())
        line = self.traces[n]
        label = "trace %i" % (n+1)
        line.label = label
        line.drawstyle = 'default'
        if zorder     is None:
            zorder = 5 * (n+1)
        line.zorder = zorder
        if color      is not None: line.color = color
        if style      is not None: line.style = style
        if linewidth  is not None: line.linewidth = linewidth
        if marker     is not None: line.marker = marker
        if markersize is not None: line.markersize = markersize
        self.traces[n] = line

    def __mpline(self, trace):
        n = max(0, int(trace))
        while n >= len(self.traces):
            self.traces.append(LineProperties())
        try:
            return self.lines[n]
        except:
            return self.lines[n-1]

    def __gettrace(self, trace):
        if trace is None:
            trace = self.ntrace
        while trace >= len(self.traces):
            self.traces.append(LineProperties())
        return trace

    def relabel(self, xlabel=None, ylabel=None, y2label=None, title=None):
        " re draw labels (title, x, y labels)"
        n = self.labelfont.get_size()

        rcParams['xtick.labelsize'] =  rcParams['ytick.labelsize'] =  n
        rcParams['xtick.color'] =  rcParams['ytick.color'] =  self.textcolor

        if xlabel is not None:  self.xlabel = xlabel
        if ylabel is not None:  self.ylabel = ylabel
        if y2label is not None: self.y2label = y2label
        if title is not None:   self.title = title

        axes = self.canvas.figure.get_axes()
        kws = dict(fontproperties=self.titlefont, color=self.textcolor)
        axes[0].set_title(self.title, **kws)
        kws['fontproperties'] = self.labelfont

        if len(self.xlabel) > 0 and self.xlabel not in ('', None, 'None'):
            axes[0].set_xlabel(self.xlabel, **kws)

        if len(self.ylabel) > 0 and self.ylabel not in ('', None, 'None'):
            axes[0].set_ylabel(self.ylabel, **kws)
        if (len(axes) > 1 and len(self.y2label) > 0 and
            self.y2label not in ('', None, 'None')):
            axes[1].set_ylabel(self.y2label, **kws)

        for ax in axes[0].xaxis, axes[0].yaxis:
            for t in (ax.get_ticklabels() + ax.get_ticklines()):
                t.set_color(self.textcolor)
        self.set_added_text_size()
        if self.mpl_legend is not None:
            for t in self.mpl_legend.get_texts():
                t.set_color(self.textcolor)
        self.canvas.draw()


    def set_added_text_size(self):
        # for text added to plot, reset font size to match legend
        n = self.legendfont.get_size()
        for dynamic, txt in self.added_texts:
            if dynamic:
                txt.set_fontsize(n)

    def refresh_trace(self,trace=None):
        trace = self.__gettrace(trace)
        self.traces[trace].update(self.__mpline(trace))

    def set_trace_color(self,color,trace=None):
        trace = self.__gettrace(trace)
        self.traces[trace].set_color(color,line=self.__mpline(trace))

    def set_trace_zorder(self, zorder, trace=None):
        trace = self.__gettrace(trace)
        self.traces[trace].set_zorder(zorder, line=self.__mpline(trace))

    def set_trace_label(self, label, trace=None):
        trace = self.__gettrace(trace)
        self.traces[trace].set_label(label,line=self.__mpline(trace))

    def set_trace_style(self,style,trace=None):
        trace = self.__gettrace(trace)
        self.traces[trace].set_style(style,line=self.__mpline(trace))

    def set_trace_drawstyle(self, style,trace=None):
        trace = self.__gettrace(trace)
        self.traces[trace].set_drawstyle(style, line=self.__mpline(trace))

    def set_trace_marker(self,marker,trace=None):
        trace = self.__gettrace(trace)
        self.traces[trace].set_marker(marker,line=self.__mpline(trace))

    def set_trace_markersize(self,markersize,trace=None):
        trace = self.__gettrace(trace)
        self.traces[trace].set_markersize(markersize,line=self.__mpline(trace))

    def set_trace_linewidth(self,linewidth,trace=None):
        trace = self.__gettrace(trace)
        self.traces[trace].set_linewidth(linewidth,line=self.__mpline(trace))

    def set_trace_datarange(self, datarange, trace=None):
        trace = self.__gettrace(trace)
        self.traces[trace].data_range = datarange

    def get_trace_datarange(self, trace=None):
        trace = self.__gettrace(trace)
        return self.traces[trace].data_range

    def get_mpl_line(self,trace=None):
        this = self.__mpline(self.__gettrace(trace))
        if this is None:
            trace = 5
            while this is None and trace > 0:
                trace = trace - 1
                this = self.__mpline(self.__gettrace(trace))
        return this[0]


    def enable_grid(self, show=None):
        "enable/disable grid display"
        if show is not None:
            self.show_grid = show
        axes = self.canvas.figure.get_axes()
        ax0 = axes[0]
        for i in ax0.get_xgridlines() + ax0.get_ygridlines():
            i.set_color(self.grid_color)
            i.set_zorder(-30)
        axes[0].grid(self.show_grid)
        for ax in axes[1:]:
            ax.grid(False)
        self.canvas.draw()

    def set_axes_style(self, style=None):
        """set axes style: one of
           'box' / 'fullbox'  : show all four axes borders
           'open' / 'leftbot' : show left and bottom axes
           'bottom'           : show bottom axes only
        """
        if style is not None:
            self.axes_style = style
        axes0 = self.canvas.figure.get_axes()[0]
        _sty = self.axes_style.lower()
        if  _sty in ('fullbox', 'full'): _sty = 'box'
        if  _sty == 'leftbot':           _sty = 'open'

        if _sty == 'box':
            axes0.xaxis.set_ticks_position('both')
            axes0.yaxis.set_ticks_position('both')
            axes0.spines['top'].set_visible(True)
            axes0.spines['right'].set_visible(True)
        elif _sty == 'open':
            axes0.xaxis.set_ticks_position('bottom')
            axes0.yaxis.set_ticks_position('left')
            axes0.spines['top'].set_visible(False)
            axes0.spines['right'].set_visible(False)
        elif _sty == 'bottom':
            axes0.xaxis.set_ticks_position('bottom')
            axes0.spines['top'].set_visible(False)
            axes0.spines['left'].set_visible(False)
            axes0.spines['right'].set_visible(False)
        self.canvas.draw()

    def draw_legend(self, show=None, auto_location=True):
        "redraw the legend"
        if show is not None:
            self.show_legend = show

        axes = self.canvas.figure.get_axes()
        # clear existing legend
        try:
            lgn = self.mpl_legend
            if lgn:
                for i in lgn.get_texts():
                    i.set_text('')
                for i in lgn.get_lines():
                    i.set_linewidth(0)
                    i.set_markersize(0)
                    i.set_marker('None')
                lgn.draw_frame(False)
                lgn.set_visible(False)
        except:
            pass

        labs = []
        lins = []
        for ax in axes:
            for xline in ax.get_lines():
                xlab = xline.get_label()
                if (xlab != '_nolegend_' and len(xlab)>0):
                    lins.append(xline)

        for l in lins:
            xl = l.get_label()
            if not self.show_legend: xl = ''
            labs.append(xl)
        labs = tuple(labs)

        lgn = axes[0].legend
        if self.legend_onaxis.startswith('off'):
            lgn = self.canvas.figure.legend
            # 'best' and 'off axis' not implemented yet
            if self.legend_loc == 'best':
                self.legend_loc = 'upper right'

        if self.show_legend:
            self.mpl_legend = lgn(lins, labs, prop=self.legendfont,
                                  loc=self.legend_loc)
            self.mpl_legend.draw_frame(self.show_legend_frame)
            self.mpl_legend.legendPatch.set_facecolor(axes[0].get_axis_bgcolor())
            if self.draggable_legend:
                self.mpl_legend.draggable(True, update='loc')
            self.legend_map = {}
            for legline, legtext, mainline in zip(self.mpl_legend.get_lines(),
                                                  self.mpl_legend.get_texts(),
                                                  lins):
                legline.set_picker(5)
                legtext.set_picker(5)
                self.legend_map[legline] = (mainline, legline, legtext)
                self.legend_map[legtext] = (mainline, legline, legtext)
                legtext.set_color(self.textcolor)


        self.set_added_text_size()
        self.canvas.draw()

    def set_legend_location(self, loc, onaxis):
        "set legend location"
        self.legend_onaxis = 'on plot'
        if not onaxis:
            self.legend_onaxis = 'off plot'
            if loc == 'best':
                loc = 'upper right'
        if loc in self.legend_abbrevs:
            loc = self.legend_abbrevs[loc]
        if loc in self.legend_locs:
            self.legend_loc = loc
