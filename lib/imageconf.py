import wx
import matplotlib.cm as colormap
from .colors import register_custom_colormaps

ColorMap_List = ['gray']

cm_names = register_custom_colormaps()

for cm in cm_names:
    ColorMap_List.append(cm)

for cm in ('coolwarm', 'cool', 'hot', 'jet', 'Reds', 'Greens', 'Blues',
           'copper', 'spring', 'summer', 'autumn', 'winter', 'hsv',
           'Spectral', 'PiYG', 'PRGn', 'Spectral', 'Accent', 'YlGn',
           'YlGnBu', 'RdBu', 'RdPu', 'RdYlBu', 'RdYlGn', 'ocean',
           'terrain', 'gist_earth', 'gist_yarg', 'gist_rainbow',
           'gist_stern'):

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
        self.auto_contrast = False
        self.datalimits = [None, None, None, None]
        self.cmap_lo = {'int': 0}
        self.cmap_hi = {'int': 1000}
        self.cmap_range = 1000
        self.tricolor_bg = 'black'
        self.cmap_splines = {'int': None, 'red': None, 'green': None, 'blue': None}
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
        self.zoom_lims = []

    def relabel(self):
        " re draw labels (title, x,y labels)"
        pass

    def set_zoombrush(self,color, style):
        self.zoombrush = wx.Brush(color, style)

    def set_zoompen(self,color, style):
        self.zoompen = wx.Pen(color, 3, style)

    def tricolor_white_bg(self, img):
        """transforms image from RGB with (0,0,0)
        showing black to  RGB with 0,0,0 showing white

        takes the Red intensity and sets
        the new intensity to go
        from (0, 0.5, 0.5) (for Red=0)  to (0, 0, 0) (for Red=1)
        and so on for the Green and Blue maps.

        Thus the image will be transformed from
          old intensity                new intensity
          (0.0, 0.0, 0.0) (black)   (1.0, 1.0, 1.0) (white)
          (1.0, 1.0, 1.0) (white)   (0.0, 0.0, 0.0) (black)
          (1.0, 0.0, 0.0) (red)     (1.0, 0.5, 0.5) (red)
          (0.0, 1.0, 0.0) (green)   (0.5, 1.0, 0.5) (green)
          (0.0, 0.0, 1.0) (blue)    (0.5, 0.5, 1.0) (blue)

        """
        tmp = 0.5*(1.0 - (img - img.min())/(img.max() - img.min()))
        out = tmp*0.0
        out[:,:,0] = tmp[:,:,1] + tmp[:,:,2]
        out[:,:,1] = tmp[:,:,0] + tmp[:,:,2]
        out[:,:,2] = tmp[:,:,0] + tmp[:,:,1]
        return out
