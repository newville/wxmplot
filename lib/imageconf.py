import wx
import matplotlib.cm as colormap
from scipy.interpolate import splrep, splev
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
        self.tricolor_bg = 'black'        
        self.cmap_splines = {'int': None, 'red': None, 'green': None, 'blue': None}
        self.auto_intensity = False
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

    def make_spline_tables(self):
        for i, nam in enumerate(('Reds', 'Greens', 'Blues')):
            dat =  colormap.get_cmap(nam)._segmentdata
            xr = [1.*i[0] for i in dat['red']]
            yr = [1.*i[1] for i in dat['red']]
            xg = [1.*i[0] for i in dat['green']]
            yg = [1.*i[1] for i in dat['green']]
            xb = [1.*i[0] for i in dat['blue']]
            yb = [1.*i[1] for i in dat['blue']]

            oname = nam[:-1].lower()
            self.cmap_splines[oname] = [splrep(xr, yr),
                                        splrep(xg, yg),
                                        splrep(xb, yb)]
    def tricolor_white_bg(self, img):
        imin, imax = img.min(), img.max()
        img = (img - imin) / (imax - imin)
        if self.cmap_splines['red'] is None:
            self.make_spline_tables()
        cr = self.cmap_splines['red']
        cg = self.cmap_splines['green']
        cb = self.cmap_splines['blue']
        inew = img*0.0
        sh = inew.shape[0], inew.shape[1]
        inew[:,:,0] += splev(img[:,:,0].flatten(), cr[0]).reshape(sh)
        inew[:,:,1] += splev(img[:,:,0].flatten(), cr[1]).reshape(sh)
        inew[:,:,2] += splev(img[:,:,0].flatten(), cr[2]).reshape(sh)
        
        inew[:,:,0] += splev(img[:,:,1].flatten(), cg[0]).reshape(sh)
        inew[:,:,1] += splev(img[:,:,1].flatten(), cg[1]).reshape(sh)
        inew[:,:,2] += splev(img[:,:,1].flatten(), cg[2]).reshape(sh)
        
        inew[:,:,0] += splev(img[:,:,2].flatten(), cb[0]).reshape(sh)
        inew[:,:,1] += splev(img[:,:,2].flatten(), cb[1]).reshape(sh)
        inew[:,:,2] += splev(img[:,:,2].flatten(), cb[2]).reshape(sh)
        return inew/ inew.max()
        

