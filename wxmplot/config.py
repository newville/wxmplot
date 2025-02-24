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
   'no symbol', 'o', '+', 'x', '^','v','>','<','|','_',
   'square','diamond','thin diamond', 'hexagon','pentagon',
   'tripod 1','tripod 2'

"""
from copy import copy
import numpy as np
import matplotlib
from matplotlib.font_manager import FontProperties
from matplotlib import rc_params, rcParams
import matplotlib.style
from cycler import cycler
from .colors import hexcolor, mpl2hexcolor, DARK_THEME

SIDE_YAXES = {'left': 1, 'right': 2, 'right2': 3, 'right3': 4}

StyleMap  = {}
DrawStyleMap  = {}
MarkerMap = {}

for k in ('default', 'steps-pre','steps-mid', 'steps-post'):
    DrawStyleMap[k] = k

for k,v in (('solid', ('-', None)),
            ('short dashed', ('--',(4, 1))),
            ('dash-dot', ('-.', None)),
            ('dashed', ('--', (6, 6))),
            ('dotted', (':', None)),
            ('long dashed', ('--', (12, 4)))):
    StyleMap[k]=v


for k,v in (('no symbol','None'), ('o','o'), ('+','+'), ('x','x'),
            ('square','s'), ('diamond','D'), ('thin diamond','d'),
            ('^','^'), ('v','v'), ('>','>'), ('<','<'),
            ('|','|'),('_','_'), ('hexagon','h'), ('pentagon','p'),
            ('tripod 1','1'), ('tripod 2','2')):
    MarkerMap[k] = v

ViewPadPercents = [0.0, 2.5, 5.0, 7.5, 10.0]

linecolors = ('#1f77b4', '#d62728', '#2ca02c', '#ff7f0e', '#9467bd',
              '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf')

light_theme = {'axes.grid': True,
               'axes.axisbelow': True,
               'axes.linewidth': 0.5,
               'axes.edgecolor': '#000000',
               'axes.facecolor': '#FEFEFE',
               'grid.linestyle': '-',
               'grid.linewidth': 0.5,
               'lines.linewidth': 2.5,
               'lines.markersize': 3,
               'lines.markeredgewidth': 0.75,
               'xtick.labelsize': 9,
               'ytick.labelsize': 9,
               'legend.fontsize': 8,
               'axes.labelsize': 9,
               'axes.titlesize': 10,
               'xtick.major.size': 4,
               'ytick.major.size': 4,
               'xtick.major.width': 0.5,
               'ytick.major.width': 0.5,
               'xtick.color': '#000000',
               'ytick.color': '#000000',
               'text.color': '#000000',
               'grid.color': '#ECECE5',
               'figure.facecolor': '#FCFCFA',
               'axes.prop_cycle': cycler('color', linecolors),
               'savefig.bbox': None,
               'savefig.directory': '~',
               'savefig.dpi': 'figure',
               'savefig.edgecolor': 'white',
               'savefig.facecolor': 'white',
               'savefig.format': 'png',
               'savefig.orientation': 'portrait',
               'savefig.pad_inches': 0.1,
               }

dark_theme = {'axes.facecolor': '#202020',
              'axes.edgecolor': '#FDFDC0',
              'xtick.color': '#FDFDC0',
              'ytick.color': '#FDFDC0',
              'text.color': '#FDFDC0',
              'grid.color': '#404040',
              'figure.facecolor': '#161616',
              'savefig.edgecolor': 'black',
              'savefig.facecolor': 'black',
              }

whitebg_theme = {'axes.facecolor': '#FFFFFF',
               'figure.facecolor': '#FFFFFF'}

Themes = {}

for tname in ('light', 'white-background', 'dark', 'matplotlib', 'ggplot',
              'bmh', 'fivethirtyeight', 'grayscale', 'dark_background',
              'tableau-colorblind10', 'Solarize_Light2', 'seaborn',
              'seaborn-bright', 'seaborn-colorblind', 'seaborn-dark',
              'seaborn-darkgrid', 'seaborn-dark-palette', 'seaborn-deep',
              'seaborn-notebook', 'seaborn-muted', 'seaborn-pastel',
              'seaborn-paper', 'seaborn-poster', 'seaborn-talk',
              'seaborn-ticks', 'seaborn-white', 'seaborn-whitegrid'):
    theme = rc_params()
    theme['backend'] = 'WXAgg'
    if tname == 'matplotlib':
        pass
    elif tname == 'light':
        theme.update(light_theme)
    elif tname == 'dark':
        theme.update(light_theme)
        theme.update(dark_theme)
    elif tname == 'white-background':
        theme.update(light_theme)
        theme.update(whitebg_theme)
    elif tname == 'fivethirtyeight':  # text sizes are way off the norm
        theme.update(matplotlib.style.library['fivethirtyeight'])
        theme.update({'legend.fontsize': 10, 'xtick.labelsize': 9,
                      'ytick.labelsize': 9, 'axes.labelsize': 9,
                      'axes.titlesize': 13})
    elif tname.startswith('seaborn'):
        sthemes = ['seaborn', 'seaborn-v0_8']
        sname = tname.replace('seaborn', 'seaborn-v0_8')
        for xname in (tname, sname):
            if xname not in sthemes:
                sthemes.append(xname)
        for xname in sthemes:
            if xname in matplotlib.style.library:
                theme.update(matplotlib.style.library[xname])
    elif tname in matplotlib.style.library:
        theme.update(matplotlib.style.library[tname])
    Themes[tname.lower()] = theme

default_config = {'auto_margins': True,
                  'axes_style': 'box',
                  'current_theme': 'dark' if DARK_THEME else 'light',
                  'data_deriv': False,
                  'data_expr': None,
                  'draggable_legend': False,
                  'hidewith_legend': True,
                  'legend_loc':  'best',
                  'legend_onaxis': 'on plot',
                  'linecolors': linecolors,
                  'margins': (0.15, 0.05, 0.05, 0.15),
                  'mpl_legend': None,
                  'plot_type': 'lineplot',
                  'scatter_size': 30,
                  'scatter_mask': None,
                  'scatter_normalcolor': 'blue',
                  'scatter_normaledge': 'blue',
                  'scatter_selectcolor': 'red',
                  'scatter_selectedge': 'red',
                  'show_grid': True,
                  'show_legend': False,
                  'show_legend_frame': False,
                  'textcolor': '#000000',
                  'title': '',
                  'xscale': 'linear', 'yscale': 'linear',
                  'xlabel': '',  'ylabel': '',
                  'y2label': '', 'y3label': '', 'y4label': '',
                  'y3offset': 0.2, 'yaxes_tracecolor': False,
                  'viewpad': 2.5,
                  'with_data_process': True,
                  'zoom_style': 'both x and y',
                  'labelfont': 9, 'legendfont': 7, 'titlefont': 10}


def ifnot_none(val, default):
    "return val if val is not None else default"
    return val if val is not None else default


class LineProps:
    """ abstraction for Line2D properties, closely related to a
    MatPlotlib Line2D.  used to set internal line properties, and
    to  make the matplotlib calls to set the Line2D properties
    """
    REPRFMT = """LineProps(color='{color:s}', style='{style:s}', linewidth={linewidth:.1f},
          label='{label:s}', zorder={zorder:d}, drawstyle='{drawstyle:s}', alpha={alpha:3f},
          marker='{marker:s}', markersize={markersize:.1f}, markercolor={markercolor:s})"""

    def __init__(self, color='black', style='solid', drawstyle='default',
                 linewidth=2, marker='no symbol',markersize=4,
                 markercolor=None, fill=False, alpha=1.0, zorder=1, label='',
                 mpline=None, yaxes=1):
        self.color      = color
        self.alpha      = alpha
        self.style      = style
        self.drawstyle  = drawstyle
        self.fill       = fill
        self.linewidth  = linewidth
        self.marker     = marker
        self.markersize = markersize
        if markercolor is None:
            markercolor = color
        self.markercolor= markercolor
        self.label      = label
        self.zorder     = zorder
        self.mpline     = mpline
        self.yaxes      = yaxes

    def __repr__(self):
        if self.zorder is None:
            self.zorder = 30
        return self.REPRFMT.format(**self.__dict__)

    def set(self, color=None, style=None, drawstyle=None, linewidth=None,
            marker=None, markersize=None, markercolor=None, zorder=None,
            label=None, fill=False, alpha=None, yaxes=None):
        self.color      = ifnot_none(color, self.color)
        self.style      = ifnot_none(style, self.style)
        self.drawstyle  = ifnot_none(drawstyle, self.drawstyle)
        self.fill       = ifnot_none(fill, self.fill)
        self.linewidth  = ifnot_none(linewidth, self.linewidth)
        self.marker     = ifnot_none(marker, self.marker)
        self.markersize = ifnot_none(markersize, self.markersize)
        self.markercolor= ifnot_none(markercolor,self.markercolor)
        self.label      = ifnot_none(label, self.label)
        self.zorder     = ifnot_none(zorder, self.zorder)
        self.alpha      = ifnot_none(alpha, self.alpha)
        self.yaxes      = ifnot_none(yaxes, self.yaxes)


    def asdict(self):
        "as dictionary"
        return {'color': self.color, 'style': self.style,
                'linewidth': self.linewidth, 'zorder': self.zorder,
                'fill': self.fill, 'label': self.label, 'yaxes': self.yaxes,
                'drawstyle': self.drawstyle, 'alpha': self.alpha,
                'marker': self.marker, 'markersize': self.markersize,
                'markercolor': self.markercolor}



class PlotConfig:
    """Plot Configuration for Line Plots, holding most configuration data """

    def __init__(self, canvas=None, panel=None, with_data_process=True,
                 theme=None, theme_color_callback=None,
                 margin_callback=None, trace_color_callback=None,
                 custom_config=None):

        self.canvas = canvas
        self.panel = panel
        self.styles      = list(StyleMap.keys())
        self.drawstyles  = list(DrawStyleMap.keys())
        self.symbols     = list(MarkerMap.keys())
        self.trace_color_callback = trace_color_callback
        self.theme_color_callback = theme_color_callback
        self.margin_callback = margin_callback
        self.current_theme = theme
        if self.current_theme is None:
            self.current_theme = 'dark' if DARK_THEME else 'light'
        self.legend_map = {}
        self.legend_locs = ['best', 'upper right' , 'lower right', 'center right',
                            'upper left', 'lower left',  'center left',
                            'upper center', 'lower center', 'center']

        self.legend_abbrevs = {'ur': 'upper right' ,  'ul': 'upper left',
                               'cr': 'center right',  'cl': 'center left',
                               'lr': 'lower right',   'll': 'lower left',
                               'uc': 'upper center',  'lc': 'lower center',
                               'cc': 'center'}

        self.data_expressions = (None, "y*x", "y*x^2", "y^2", "sqrt(y)", "1/y")

        self.log_choices = ("x linear / y linear", "x linear / y log",
                            "x log / y linear", "x log / y log")
        self.zoom_choices = ('both x and y', 'x only', 'y only')
        self.zoom_style = self.zoom_choices[0]
        self.data_deriv = False
        self.data_expr  = None
        self.data_save  = {}
        self.with_data_process = with_data_process
        self.marker_report_data = []
        self.axes_style_choices = ['box', 'open']
        self.legend_onaxis_choices =  ['on plot', 'off plot']

        self.configdict = {k: v for k, v in default_config.items()}
        if custom_config is not None:
            self.configdict.update(custom_config)
        self.themes = Themes

        self.set_defaults()

    def set_defaults(self):
        self.zoom_lims = []
        self.added_texts = []
        self.scatter_xdata = None
        self.scatter_ydata = None
        self.scatter_mask = None

        self.margins = None
        self.mpl_legend  = None
        self.axes_traces = {}

        # preload some traces
        self.traces = []
        self.reset_lines()

        self.labelfont = FontProperties()
        self.titlefont = FontProperties()
        self.legendfont = FontProperties()

        for key, val in self.configdict.items():
            if 'font' in key:
                thisfont = getattr(self, key, FontProperties())
                thisfont.set_size(val)
            else:
                setattr(self, key, val)
        self.set_theme()


    def set_theme(self, theme=None):
        if theme in self.themes:
            self.current_theme = theme
        cur_theme = self.themes[self.current_theme]
        rcParams.update(cur_theme)

        self.show_grid  = cur_theme['axes.grid']
        self.legendfont.set_size(cur_theme['legend.fontsize'])
        self.labelfont.set_size(cur_theme['axes.labelsize'])
        self.titlefont.set_size(cur_theme['axes.titlesize'])

        self.set_facecolor(mpl2hexcolor(cur_theme['axes.facecolor']))
        self.set_gridcolor(mpl2hexcolor(cur_theme['grid.color']))
        self.set_framecolor(mpl2hexcolor(cur_theme['figure.facecolor']))
        self.set_textcolor(mpl2hexcolor(cur_theme['text.color']))

        self.linecolors = [a['color'] for a in cur_theme['axes.prop_cycle']]
        self.reset_trace_properties()
        self.set_axes_style()

    def get_config(self):
        """save json-ifiable dict of current configuration options
        to self.configdict
        """
        cnf = {}

        for attr in ('added_texts', 'auto_margins', 'axes_style', 'current_theme',
                     'data_deriv', 'data_expr', 'draggable_legend', 'facecolor',
                     'framecolor', 'gridcolor', 'hidewith_legend', 'legend_loc',
                     'legend_onaxis', 'linecolors', 'margins', 'mpl_legend', 'ntrace',
                     'plot_type', 'scatter_mask', 'scatter_normalcolor',
                     'scatter_normaledge', 'scatter_selectcolor', 'scatter_selectedge',
                     'scatter_size', 'show_grid', 'show_legend', 'show_legend_frame',
                     'textcolor', 'title', 'viewpad', 'with_data_process',
                     'xlabel', 'xscale', 'y2label', 'y3label', 'y4label',
                     'ylabel', 'yscale', 'zoom_lims',
                     'zoom_style', 'legendfont', 'labelfont', 'titlefont',
                     'fills', 'traces'):

            val = getattr(self, attr)
            if attr in ('legendfont', 'labelfont', 'titlefont'):
                val = val.get_size()
            elif attr == 'fills':
                val = val[:self.ntrace]
            elif attr == 'traces':
                val = self.get_traces()[:self.ntrace]

            cnf[attr] = val
        self.configdict = cnf
        return cnf

    def load_config(self, conf):
        self.get_config()
        self.configdict.update(conf)
        cnf = self.configdict

        self.ntrace = cnf.get('ntrace', 1)

        self.set_theme(theme=cnf['current_theme'])
        for attr in ('added_texts', 'auto_margins', 'axes_style', 'current_theme',
                     'data_deriv', 'data_expr', 'draggable_legend', 'facecolor',
                     'framecolor', 'gridcolor', 'hidewith_legend', 'legend_loc',
                     'legend_onaxis', 'linecolors', 'margins', 'mpl_legend',
                     'plot_type', 'scatter_mask', 'scatter_normalcolor',
                     'scatter_normaledge', 'scatter_selectcolor', 'scatter_selectedge',
                     'scatter_size', 'show_grid', 'show_legend', 'show_legend_frame',
                     'textcolor', 'title', 'viewpad', 'with_data_process',
                     'xlabel', 'xscale', 'y2label', 'y3label', 'y4label',
                     'ylabel', 'yscale', 'zoom_lims', 'zoom_style'):
            if attr in cnf:
                setattr(self, attr, cnf.get(attr))

    def reset_lines(self):
        self.lines = [None]*len(self.traces)
        self.dy    = [None]*len(self.traces)
        self.fills = [None]*len(self.traces)
        self.ntrace = 0
        self.marker_report_data = []
        return self.lines

    def reset_trace_properties(self):
        i = -1
        for style, marker in (('solid', None), ('short dashed', None),
                              ('dash-dot', None), ('solid', 'o'),
                              ('dotted', None), ('solid', '+'),
                              ('dashed', None), ('solid', 'x'),
                              ('long dashed', None), ('dashed', 'square')):
            for color in self.linecolors:
                i += 1
                self.init_trace(i, color, style, marker=marker)

    def init_trace(self, n, color, style, label=None, linewidth=None,
                   zorder=None, marker=None, markersize=None,
                   drawstyle=None, fill=None, alpha=1):
        """ used for building set of traces"""
        while n >= len(self.traces):
            self.traces.append(LineProps())
            self.fills.append(None)
            self.dy.append(None)
        line = self.traces[n]

        line.label     = ifnot_none(label, "trace %i" % (n+1))
        line.color     = ifnot_none(color, line.color)
        line.alpha     = ifnot_none(alpha, line.alpha)
        line.style     = ifnot_none(style, line.style)
        line.linewidth = ifnot_none(linewidth, line.linewidth)
        line.drawstyle = ifnot_none(drawstyle, line.drawstyle)
        line.fill      = ifnot_none(fill, line.fill)
        line.zorder    = ifnot_none(zorder, 5*(n+1))
        line.marker    = ifnot_none(marker, line.marker)
        line.markersize = ifnot_none(markersize, line.markersize)


    def get_mpline(self, trace):
        n = max(0, int(trace))
        while n >= len(self.traces):
            self.traces.append(LineProps())
        nlines = len(self.lines)
        for i in range(nlines, len(self.traces)+1):
            self.lines.append(None)
        try:
            return self.lines[n]
        except IndexError:
            return self.lines[n-1]

    def get_trace(self, trace):
        if trace is None:
            trace = self.ntrace
        while trace >= len(self.traces):
            self.traces.append(LineProps())
        return trace

    def get_traces(self):
        out = []
        for i in range(self.ntrace):
            out.append(self.traces[i].asdict())
        return out


    def relabel(self, xlabel=None, ylabel=None, y2label=None, y3label=None,
                y4label=None, title=None, delay_draw=False):
        " re draw labels (title, x, y labels)"
        n = self.labelfont.get_size()
        # self.titlefont.set_size(n+1)
        rcParams['xtick.labelsize'] =  rcParams['ytick.labelsize'] =  n

        if xlabel is not None:
            self.xlabel = xlabel
        if ylabel is not None:
            self.ylabel = ylabel
        if y2label is not None:
            self.y2label = y2label
        if y3label is not None:
            self.y3label = y3label
        if y4label is not None:
            self.y4label = y4label
        if title is not None:
            self.title = title
        if self.canvas is None:
            return
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
        if (len(axes) > 2 and len(self.y3label) > 0 and
            self.y3label not in ('', None, 'None')):
            axes[2].set_ylabel(self.y3label, **kws)
        if (len(axes) > 3 and len(self.y4label) > 0 and
            self.y4label not in ('', None, 'None')):
            axes[3].set_ylabel(self.y4label, **kws)


        if len(axes) > 2:
            axes[2].spines.right.set_position(("axes", 1 + self.y3offset))
            if len(axes) > 3:
                axes[3].spines.right.set_position(("axes", 1 + 2*self.y3offset))

        for axes in self.canvas.figure.get_axes():
            for ax in axes.xaxis, axes.yaxis:
                for t in ax.get_ticklabels():
                    t.set_color(self.textcolor)
                    if hasattr(t, 'set_fontsize'):
                        t.set_fontsize(n)

        self.set_added_text_size()
        if self.mpl_legend is not None:
            for t in self.mpl_legend.get_texts():
                t.set_color(self.textcolor)

        self.set_yaxes_tracecolor(delay_draw=True)
        if not delay_draw:
            self.canvas.draw()

    def set_margins(self, left=0.1, top=0.1, right=0.1, bottom=0.1,
                    delay_draw=False):
        "set margins"
        self.margins = (left, top, right, bottom)
        if self.panel is not None:
            self.panel.gridspec.update(left=left, top=1-top,
                                       right=1-right, bottom=bottom)
        for i, ax in enumerate(self.canvas.figure.get_axes()):
            figpos = ax.get_subplotspec().get_position(self.canvas.figure)
            ax.set_position(figpos)

        if not delay_draw:
            self.canvas.draw()
        if callable(self.margin_callback):
            self.margin_callback(left=left, top=top, right=right, bottom=bottom)

    def set_gridcolor(self, color):
        """set color for grid"""
        self.gridcolor = color
        if self.canvas is None:
            return

        rcParams['grid.color'] = color
        for ax in self.canvas.figure.get_axes():
            for i in ax.get_xgridlines()+ax.get_ygridlines():
                i.set_color(color)
                i.set_zorder(-1)
        if callable(self.theme_color_callback):
            self.theme_color_callback(color, 'grid')

    def set_facecolor(self, color):
        """set color for background of plot"""
        self.facecolor = color
        if self.canvas is None:
            return
        for ax in self.canvas.figure.get_axes():
            ax.set_facecolor(color)
        if callable(self.theme_color_callback):
            self.theme_color_callback(color, 'axes.facecolor')

    def set_framecolor(self, color):
        """set color for outer frame"""
        self.framecolor = color
        if self.canvas is None:
            return
        self.canvas.figure.set_facecolor(color)
        if callable(self.theme_color_callback):
            self.theme_color_callback(color, 'figure.facecolor')

    def set_textcolor(self, color, delay_draw=True):
        """set color for labels and axis text"""
        self.textcolor = color
        self.relabel(delay_draw=delay_draw)
        if callable(self.theme_color_callback):
            self.theme_color_callback(color, 'text')


    def set_added_text_size(self):
        # for text added to plot, reset font size to match legend
        n = self.legendfont.get_size()
        for dynamic, txt in self.added_texts:
            if dynamic:
                txt.set_fontsize(n)

    def refresh_trace(self, trace=None):
        trace = self.get_trace(trace)
        prop = self.traces[trace]

        self.set_trace_label(prop.label, trace=trace, delay_draw=True)
        self.set_trace_linewidth(prop.linewidth, trace=trace, delay_draw=True)
        self.set_trace_color(prop.color, trace=trace, delay_draw=True)
        self.set_trace_alpha(prop.alpha, trace=trace, delay_draw=True)
        self.set_trace_style(prop.style, trace=trace, delay_draw=True)
        self.set_trace_drawstyle(prop.drawstyle, trace=trace, delay_draw=True)
        self.set_trace_fill(prop.fill, trace=trace, delay_draw=True)
        self.set_trace_marker(prop.marker, trace=trace, delay_draw=True)
        self.set_trace_markersize(prop.markersize, trace=trace, delay_draw=True)
        self.set_trace_zorder(prop.zorder, trace=trace, delay_draw=True)

    def set_trace_color(self, color, trace=None, delay_draw=True):
        trace = self.get_trace(trace)
        color = hexcolor(color)
        self.traces[trace].color = color
        mline = self.get_mpline(trace)
        if mline:
            for comp in mline:
                if hasattr(comp, '__iter__'):
                    for line in comp:
                        line.set_color(color)
                else:
                    comp.set_color(color)

        if self.fills[trace] is not None:
            self.fills[trace].set_color(color)

        self.set_yaxes_tracecolor(delay_draw=False)
        if not delay_draw:
            self.draw_legend()
        if callable(self.trace_color_callback) and mline:
            self.trace_color_callback(color, line=mline)

    def set_trace_alpha(self, alpha, trace=None, delay_draw=True):
        trace = self.get_trace(trace)
        alpha = min(1, max(0, float(alpha)))
        self.traces[trace].alpha = alpha
        mline = self.get_mpline(trace)
        if mline:
            for comp in mline:
                if hasattr(comp, '__iter__'):
                    for line in comp:
                        line.set_alpha(alpha)
                else:
                    comp.set_alpha(alpha)
        if self.fills[trace] is not None:
            self.fills[trace].set_alpha(alpha)
        if not delay_draw:
            self.draw_legend()

    def set_trace_yaxes(self, yaxes=1, side=None, trace=None, delay_draw=False):
        trace = self.get_trace(trace)
        # print("SET TRACE YAXES ", trace, yaxes, side)
        if side is not None:
            _yaxes = SIDE_YAXES.get(side, None)
            if _yaxes is not None:
                yaxes = _yaxes
        self.traces[trace].yaxes = yaxes
        if not delay_draw:
            self.canvas.draw()

    def set_trace_zorder(self, zorder, trace=None, delay_draw=False):
        trace = self.get_trace(trace)
        zorder = ifnot_none(zorder, 5*(trace+1))
        self.traces[trace].zorder = zorder
        mline = self.get_mpline(trace)
        if mline:
            mline[0].set_zorder(zorder)

        if not delay_draw:
            self.canvas.draw()


    def set_trace_label(self, label, trace=None, delay_draw=False):
        trace = self.get_trace(trace)
        self.traces[trace].label = label
        mline = self.get_mpline(trace)
        if mline:
            mline[0].set_label(label)
        if not delay_draw:
            self.draw_legend()

    def set_trace_style(self, style, trace=None, delay_draw=False):
        trace = self.get_trace(trace)
        sty = 'solid'
        if style in StyleMap:
            sty = style
        elif style in StyleMap.values():
            for k, v in StyleMap.items():
                if v == style:
                    sty = k
        style = sty
        self.traces[trace].style = style
        mline = self.get_mpline(trace)
        if mline:
            _key, _opts = StyleMap[style]
            mline[0].set_linestyle(_key)
            if _key == '--' and _opts is not None:
                mline[0].set_dashes(_opts)
        if not delay_draw:
            self.draw_legend()

    def set_trace_drawstyle(self, drawstyle, trace=None, delay_draw=False):
        trace = self.get_trace(trace)
        sty = 'default'
        if drawstyle in DrawStyleMap:
            sty = drawstyle
        drawstyle = sty
        self.traces[trace].drawstyle = drawstyle

        mline = self.get_mpline(trace)
        if mline:
            mline[0].set_drawstyle(DrawStyleMap[drawstyle])
            mline[0]._invalidx = True

        if not delay_draw:
            self.draw_legend()

    def set_trace_fill(self, fill, trace=None, delay_draw=False):
        trace = self.get_trace(trace)

        cur_fill = self.fills[trace]
        axes = self.canvas.figure.get_axes()[0]

        def del_collection(thisfill):
            for i, coll in enumerate(axes.collections):
                if id(thisfill) == id(coll):
                    try:
                        axes.collections[i].remove()
                    except Exception:
                        pass

        if not fill:
            self.traces[trace].fill = False
            if cur_fill is not None:
                del_collection(cur_fill)
                try:
                    del cur_fill
                except Exception:
                    pass
                self.fills[trace] = None
        else:
            if cur_fill is not None:
                del_collection(cur_fill)
                try:
                    del cur_fill
                except Exception:
                    pass


            self.traces[trace].fill = True
            atrace = self.traces[trace]
            this = self.get_mpline(trace)
            dy  = self.dy[trace]
            if this is not None:
                fkws = dict(step=None, zorder=atrace.zorder,
                            color=atrace.color,
                            alpha=atrace.alpha)
                if atrace.drawstyle != 'default':
                    dstyle = atrace.drawstyle[:]
                    if dstyle.startswith('steps-'):
                        dstyle = dstyle[6:]
                    fkws['step'] = dstyle
                x = this[0].get_xdata()
                y = this[0].get_ydata()
                y2 = 0
                if dy is not None:
                    y, y2 = y-dy, y+dy

                _fill = axes.fill_between(x, y, y2=y2, **fkws)

                self.fills[trace] = _fill
        if not delay_draw:
            self.draw_legend()

    def set_trace_marker(self, marker, trace=None, delay_draw=False):
        trace = self.get_trace(trace)
        sym = 'no symbol'
        if marker in MarkerMap:
            sym = marker
        elif marker in MarkerMap.values():
            for k,v in MarkerMap.items():
                if v == marker:
                    sym = k
        marker = sym
        self.traces[trace].marker = marker

        mline = self.get_mpline(trace)
        if mline:
            mline[0].set_marker(MarkerMap[marker])

        if not delay_draw:
            self.draw_legend()

    def set_trace_markersize(self, markersize, trace=None, delay_draw=False):
        trace = self.get_trace(trace)
        self.traces[trace].markersize = markersize

        mline = self.get_mpline(trace)
        if mline:
            mline[0].set_markersize(markersize)
            if mline[0].get_markeredgewidth() == 0:
                mline[0].set_markeredgewidth(0.75)

        if not delay_draw:
            self.draw_legend()

    def set_trace_linewidth(self, linewidth, trace=None, delay_draw=False):
        trace = self.get_trace(trace)
        self.traces[trace].linewidth = linewidth

        mline = self.get_mpline(trace)
        if mline:
            for line in mline:
                try:
                    line.set_linewidth(linewidth/2.0)
                except AttributeError:
                    pass

        if not delay_draw:
            self.draw_legend()

    def set_trace_datarange(self, datarange, trace=None):
        pass


    def get_mpl_line(self, trace=None):
        this = self.get_mpline(self.get_trace(trace))
        if this is None:
            trace = 5
            while this is None and trace > 0:
                trace = trace - 1
                this = self.get_mpline(self.get_trace(trace))
        return this[0]


    def enable_grid(self, show=None, delay_draw=False):
        "enable/disable grid display"
        if show is not None:
            self.show_grid = show
        axes = self.canvas.figure.get_axes()
        ax0 = axes[0]
        for i in ax0.get_xgridlines() + ax0.get_ygridlines():
            i.set_color(self.gridcolor)
            i.set_zorder(-1)
        axes[0].grid(self.show_grid)
        for ax in axes[1:]:
            ax.grid(False)
        if not delay_draw:
            self.canvas.draw()

    def set_yaxes_tracecolor(self, yaxes_tracecolor=None, delay_draw=False):
        """set yaxes_tracecolor, to control whether the
        tick markers and labels for the y axes use the
        color of the first trace for that 'side'
        """
        if yaxes_tracecolor is not None:
            self.yaxes_tracecolor = bool(yaxes_tracecolor)

        cur_theme = self.themes[self.current_theme]
        tcolor = mpl2hexcolor(cur_theme['ytick.color'])

        axes = self.canvas.figure.get_axes()
        colors = [tcolor]*(len(axes)+2)
        if self.yaxes_tracecolor:
            for iax in range(4):
                for iline, line in enumerate(self.lines):
                    if line is not None:
                        trace = self.traces[iline]
                        if trace.yaxes == (iax+1):
                            colors[iax] = trace.color
                            break
        # print(colors, len(axes))
        for i, ax in enumerate(axes):
            color = colors[i]
            if color is not None:
                ax.yaxis.label.set_color(color)
                ax.tick_params(axis='y', colors=color)

        if not delay_draw:
            self.canvas.draw()

    def set_axes_style(self, style=None, delay_draw=False):
        """set axes style: one of
           'box' / 'fullbox'  : show all four axes borders
           'open' / 'leftbot' : show left and bottom axes
           'bottom'           : show bottom axes only
        """
        if style is not None:
            self.axes_style = style

        try:
            axes = self.canvas.figure.get_axes()
            ax = axes[0]
        except AttributeError:
            return

        for tline in (ax.xaxis.get_majorticklines() + ax.yaxis.get_majorticklines()):
            tline.set_color(rcParams['xtick.color'])
            tline.set_markeredgewidth(rcParams['xtick.major.width'])
            tline.set_markersize(rcParams['xtick.major.size'])
            tline.set_linestyle('-')
            tline.set_visible(True)

        for spine in ('top', 'bottom', 'left', 'right'):
            ax.spines[spine].set_linewidth(rcParams['axes.linewidth'])
            ax.spines[spine].set_facecolor(rcParams['axes.facecolor'])
            ax.spines[spine].set_edgecolor(rcParams['axes.edgecolor'])

        _sty = self.axes_style.lower()
        if  _sty in ('fullbox', 'full'):
            _sty = 'box'
        if  _sty == 'leftbot':
            _sty = 'open'

        if _sty == 'box':
            ax.xaxis.set_ticks_position('both')
            ax.yaxis.set_ticks_position('both')
            ax.spines['top'].set_visible(True)
            ax.spines['right'].set_visible(True)
        elif _sty == 'open':
            ax.xaxis.set_ticks_position('bottom')
            ax.yaxis.set_ticks_position('left')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
        elif _sty == 'bottom':
            ax.xaxis.set_ticks_position('bottom')
            ax.spines['top'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['right'].set_visible(False)

        # if 2 y-axes, don't draw ticks on right side for axes[0]
        if len(axes) > 1:
            axes[0].yaxis.set_tick_params(right=False)
            axes[1].yaxis.set_tick_params(left=False)

        if not delay_draw:
            self.canvas.draw()

    def draw_legend(self, show=None, auto_location=True, delay_draw=False):
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
        except Exception:
            pass

        labs = []
        lins = []
        traces = []
        for ax in axes:
            for trace, xline in enumerate(ax.get_lines()):
                xlab = xline.get_label()
                if (xlab != '_nolegend_' and len(xlab)>0):
                    lins.append(xline)
                    traces.append(trace)

        for lin in lins:
            xl = lin.get_label()
            if not self.show_legend:
                xl = ''
            labs.append(xl)
        labs = tuple(labs)

        lgn = axes[-1].legend
        if self.legend_onaxis.startswith('off'):
            lgn = self.canvas.figure.legend
            # 'best' and 'off axis' not implemented yet
            if self.legend_loc == 'best':
                self.legend_loc = 'upper right'

        if self.show_legend:
            self.mpl_legend = lgn(lins, labs, prop=self.legendfont,
                                  loc=self.legend_loc)
            self.mpl_legend.draw_frame(self.show_legend_frame)
            facecol = axes[0].get_facecolor()

            self.mpl_legend.legendPatch.set_facecolor(facecol)
            if self.draggable_legend:
                self.mpl_legend.set_draggable(True, update='loc')
            self.legend_map = {}
            for legline, legtext, mainline, trace in zip(self.mpl_legend.get_lines(),
                                                         self.mpl_legend.get_texts(),
                                                         lins, traces):
                legline.set_pickradius(20)
                legtext.set_picker(5)
                self.legend_map[legline] = (mainline, trace, legline, legtext)
                self.legend_map[legtext] = (mainline, trace, legline, legtext)
                legtext.set_color(self.textcolor)

        self.set_added_text_size()
        if not delay_draw:
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

    def process_data(self):
        if not self.with_data_process:
            return
        expr = self.data_expr
        if expr is not None:
            expr = expr.upper()
        for ax in self.canvas.figure.get_axes():
            for trace, lines in enumerate(ax.get_lines()):
                try:
                    dats = copy(self.data_save[ax][trace])
                except:
                    return
                xd, yd = np.asarray(dats[0][:]), np.asarray(dats[1][:])
                if expr == 'Y*X':
                    yd = yd * xd
                elif expr == 'Y*X^2':
                    yd = yd * xd * xd
                elif expr == 'Y^2':
                    yd = yd * yd
                elif expr == 'SQRT(Y)':
                    yd = np.sqrt(yd)
                elif expr == '1/Y':
                    yd = 1./yd
                if self.data_deriv:
                    yd = np.gradient(yd)/np.gradient(xd)
                lines.set_ydata(yd)
                lines.set_xdata(xd)

        self.unzoom(full=True)

    def unzoom(self, full=False, delay_draw=False):
        """unzoom display 1 level or all the way"""
        if full:
            self.zoom_lims = self.zoom_lims[:1]
            self.zoom_lims = []
        elif len(self.zoom_lims) > 0:
            self.zoom_lims.pop()
        self.set_viewlimits()
        if not delay_draw:
            self.canvas.draw()

    def set_viewlimits(self):
        all_limits = []
        x_minpos = None
        y_minpos = None
        for ax in self.canvas.figure.get_axes():
            limits = [None, None, None, None]
            if ax in self.axes_traces:
                try:
                    for trace, lines in enumerate(ax.get_lines()):
                        if lines.get_label() == '_nolegend_':
                            continue
                        x, y = lines.get_xdata(), lines.get_ydata()
                        try:
                            if not isinstance(y, np.ndarray):
                                y = np.array(y)
                            if not isinstance(x, np.ndarray):
                                x = np.array(x)
                            if y_minpos is None:
                                y_minpos= min(y[np.where(y>0)])
                            else:
                                y_minpos= min(y_minpos, min(y[np.where(y>0)]))
                            if x_minpos is None:
                                x_minpos= min(x[np.where(x>0)])
                            else:
                                x_minpos= min(x_minpos, min(x[np.where(x>0)]))
                        except:
                            pass
                        if limits == [None, None, None, None]:
                            limits = [min(x), max(x), min(y), max(y)]
                        else:
                            limits = [min(limits[0], min(x)),
                                      max(limits[1], max(x)),
                                      min(limits[2], min(y)),
                                      max(limits[3], max(y))]
                except ValueError:
                    pass
            if x_minpos is None:
                x_minpos = 1.e-8
            if y_minpos is None:
                y_minpos = 1.e-8
            if ax in self.user_limits:
                for i, val in  enumerate(self.user_limits[ax]):
                    if val is not None:
                        limits[i] = val
            # add padding to data range
            if self.viewpad > 0 and (None not in limits):
                xrange = limits[1] - limits[0]
                try:
                    if xrange < 1.e-10:
                        xrange = max(1.e-10, (limits[1] + limits[0] )/2.0)
                except:
                    pass

                yrange = limits[3] - limits[2]
                try:
                    if yrange < 1.e-10:
                        yrange = max(1.e-10, (limits[3] + limits[2] )/2.0)
                except:
                    pass

                limits[0] = limits[0] - xrange * self.viewpad /100.0
                limits[1] = limits[1] + xrange * self.viewpad /100.0
                limits[2] = limits[2] - yrange * self.viewpad /100.0
                limits[3] = limits[3] + yrange * self.viewpad /100.0
                if self.xscale == 'log':
                    limits[0] = max(x_minpos/2, limits[0])

                if self.yscale == 'log':
                    limits[2] = max(y_minpos/2, limits[2])


            if ax in self.user_limits:
                for i, val in  enumerate(self.user_limits[ax]):
                    if val is not None:
                        limits[i] = val

            if len(self.zoom_lims) > 0:
                limits = self.zoom_lims[-1][ax]
            all_limits.append(limits)
            try:
                ax.set_xlim((limits[0], limits[1]), emit=True)
            except:
                pass
            try:
                ax.set_ylim((limits[2], limits[3]), emit=True)
            except:
                pass
        return all_limits

    def set_logscale(self, xscale='linear', yscale='linear',
                     delay_draw=False):
        "set log or linear scale for x, y axis"
        self.xscale = xscale
        self.yscale = yscale
        for axes in self.canvas.figure.get_axes():
            try:
                axes.set_yscale(yscale)
            except:
                axes.set_yscale('linear')
            try:
                axes.set_xscale(xscale)
            except:
                axes.set_xscale('linear')
        if not delay_draw:
            self.process_data()

    def get_viewpads(self):
        o = [round(i*100.0) for i in ViewPadPercents]
        cur = round(100.0*self.viewpad)
        if cur not in o:
            o.append(cur)
        return [i/100.0 for i in sorted(o)]
