import wx
import matplotlib.cm as colormap
from .colors import register_custom_colormaps

ColorMap_List = ['gray']

cm_names = register_custom_colormaps()

for cm in cm_names:
    ColorMap_List.append(cm)

for cm in ('coolwarm', 'cool', 'hot', 'jet', 'Reds', 'Greens',
           'Blues', 'copper', 'spring', 'summer', 'autumn', 'winter',
           'hsv', 'Spectral'):
    # 'gist_earth', 'gist_yarg', 'gist_rainbow',
    # 'gist_stern',
    # 'PiYG', 'PRGn', 'Spectral', 'Accent', 'YlGn', 'YlGnBu',
    # 'RdBu', 'RdPu', 'RdYlBu', 'RdYlGn', 'ocean', 'terrain'
    if hasattr(colormap, cm):
        ColorMap_List.append(cm)

Interp_List = ('nearest', 'bilinear', 'bicubic', 'gaussian', 'catrom',
               'spline16', 'spline36', 'hanning', 'hamming', 'hermite',
               'kaiser', 'quadric', 'bessel', 'mitchell', 'sinc',
               'lanczos')

class ImageConfig:
    def __init__(self, axes=None, fig=None, canvas=None):
        self.axes   = axes
        self.fig  = fig
        self.canvas  = canvas
        self.cmap  = {'int': colormap.gray}
        self.cmap_reverse = False
        self.interp = 'nearest'
        self.log_scale = False
        self.flip_ud = False
        self.flip_lr = False
        self.rot  = False
        self.datalimits = [None, None, None, None]
        self.cmap_lo = {'int': 0}
        self.cmap_hi = {'int': 100}
        self.cmap_range = 100
        self.auto_intensity = True
        self.int_lo = {'int': '0', 'red': '0', 'green': '0', 'blue': '0'}
        self.int_hi = {'int': '1', 'red': '1', 'green': '1', 'blue': '1'}
        self.data = None
        self.indices = None
        self.title = 'image'
        self.style = 'image'
        self.highlight_areas = []
        self.ncontour_levels = 10
        self.contour_levels = None
        self.contour_labels = True
        self.cursor_mode = 'zoom'
        self.zoombrush = wx.Brush('#040410',  wx.SOLID)
        self.zoompen   = wx.Pen('#101090',  3, wx.SOLID)

    def relabel(self):
        " re draw labels (title, x,y labels)"
        pass

    def set_zoombrush(self,color, style):
        self.zoombrush = wx.Brush(color, style)

    def set_zoompen(self,color, style):
        self.zoompen = wx.Pen(color, 3, style)

