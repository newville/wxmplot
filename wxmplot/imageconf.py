import wx
import numpy as np
import matplotlib.cm as colormap
from matplotlib.ticker import FuncFormatter
from .colors import register_custom_colormaps
from .config import bool_ifnotNone, ifnotNone

cm_names = register_custom_colormaps()

# for cm in cm_names:
#     if cm not in cm_names:
#         ColorMap_List.append(cm)

ColorMap_List = []

for cm in ('gray', 'coolwarm', 'viridis', 'inferno', 'plasma', 'magma', 'red',
           'green', 'blue', 'magenta', 'yellow', 'cyan', 'Reds', 'Greens',
           'Blues', 'cool', 'hot', 'copper', 'red_heat', 'green_heat',
           'blue_heat', 'spring', 'summer', 'autumn', 'winter', 'ocean',
           'terrain', 'jet', 'stdgamma', 'hsv', 'Accent', 'Spectral', 'PiYG',
           'PRGn', 'Spectral', 'YlGn', 'YlGnBu', 'RdBu', 'RdPu', 'RdYlBu',
           'RdYlGn'):

    if cm in cm_names or hasattr(colormap, cm):
        ColorMap_List.append(cm)


Contrast_List = ['None', '0.01', '0.02', '0.05', '0.1', '0.2', '0.5', '1.0',
                 '2.0', '5.0']

Contrast_NDArray = np.array((-1.0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1., 2, 5.))

Interp_List = ('nearest', 'bicubic', 'quadric', 'gaussian', 'kaiser',
               'bessel', 'mitchell', 'catrom', 'spline16', 'spline36',
               'bilinear', 'hanning', 'hamming', 'hermite', 'sinc', 'lanczos')

Projection_List = ('None', 'X', 'Y') # , 'Both')

RGB_COLORS = ('red', 'green', 'blue')

class ImageConfig:
    def __init__(self, axes=None, fig=None, canvas=None):
        self.axes   = axes
        self.fig  = fig
        self.canvas  = canvas
        self.cmap  = [colormap.gray, colormap.gray, colormap.gray]
        self.cmap_reverse = False
        self.interp = 'nearest'
        self.show_axis = False
        self.log_scale = False
        self.flip_ud = False
        self.flip_lr = False
        self.rot_level  = 0
        self.contrast_level = 0
        self.datalimits = [None, None, None, None]
        self.cmap_lo = [0, 0, 0]
        self.cmap_range = 1000
        self.cmap_hi = [1000, 1000, 1000]
        self.tricolor_bg = 'black'
        self.tricolor_mode = 'rgb'
        self.int_lo = [0, 0, 0]
        self.int_hi = [1, 1, 1]
        self.data = None
        self.xdata = None
        self.ydata = None
        self.xlab = 'X'
        self.ylab = 'Y'
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
        self.projections = None
        self.projection_xy = -1, -1
        self.projection_width = 1
        self.projection_onmotion = False
        self.set_formatters()


    def flip_vert(self):
        "flip image along vertical axis (up/down)"
        self.data = np.flipud(self.data)
        if self.ydata is not None:
            self.ydata = self.ydata[::-1]
        self.flip_ud = not self.flip_ud

    def flip_horiz(self):
        "flip image along horizontal axis (left/right)"
        self.data = np.fliplr(self.data)
        if self.xdata is not None:
            self.xdata = self.xdata[::-1]
        self.flip_lr = not self.flip_lr

    def rotate90(self, event=None):
        "rotate 90 degrees, CW"
        if self.xdata is not None:
            self.xdata = self.xdata[::-1]
        if self.ydata is not None:
            self.ydata = self.ydata[:]
        self.xdata, self.ydata = self.ydata, self.xdata
        self.xlab, self.ylab = self.ylab, self.xlab
        self.data = np.rot90(self.data)
        self.rot_level += 1
        if self.rot_level == 4:
            self.rot_level = 0

    def set_formatters(self):
        if self.axes is not None:
            self.axes.xaxis.set_major_formatter(FuncFormatter(self.xformatter))
            self.axes.yaxis.set_major_formatter(FuncFormatter(self.yformatter))

    def xformatter(self, x, pos):
        " x-axis formatter "
        return self._format(x, pos, dtype='x')

    def yformatter(self, y, pos):
        " y-axis formatter "
        return self._format(y, pos, dtype='y')

    def _format(self, x, pos, dtype='x'):
        """ home built tick formatter to use with FuncFormatter():
        x     value to be formatted
        type  'x' or 'y' or 'y2' to set which list of ticks to get

        also sets self._yfmt/self._xfmt for statusbar
        """
        fmt, v = '%1.5g','%1.5g'
        if dtype == 'y':
            ax = self.axes.yaxis
            dat  = self.ydata
            if dat is None:
                dat = np.arange(self.data.shape[0])
        else:
            ax = self.axes.xaxis
            dat = self.xdata
            if dat is None:
                dat = np.arange(self.data.shape[1])

        ticks = [0,1]
        try:
            dtick = 0.1 * (dat.max() - dat.min())
        except:
            dtick = 0.2
        try:
            ticks = ax.get_major_locator()()
        except:
            ticks = [0, 1]
        try:
            dtick = abs(dat[int(ticks[1])] - dat[int(ticks[0])])
        except:
            pass

        if dtick > 89999:
            fmt, v = ('%.1e',  '%1.6g')
        elif dtick > 1.99:
            fmt, v = ('%1.0f', '%1.2f')
        elif dtick > 0.099:
            fmt, v = ('%1.1f', '%1.3f')
        elif dtick > 0.0099:
            fmt, v = ('%1.2f', '%1.4f')
        elif dtick > 0.00099:
            fmt, v = ('%1.3f', '%1.5f')
        elif dtick > 0.000099:
            fmt, v = ('%1.4f', '%1.6e')
        elif dtick > 0.0000099:
            fmt, v = ('%1.5f', '%1.6e')

        try:
            s =  fmt % dat[int(x)]
            s.strip()
            s = s.replace('+', '')
        except:
            s = ''
        while s.find('e0')>0:
            s = s.replace('e0','e')
        while s.find('-0')>0:
            s = s.replace('-0','-')
        if type == 'y':
            self._yfmt = v
        if type == 'y2':
            self._y2fmt = v
        if type == 'x':
            self._xfmt = v
        return s

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

    def rgb2cmy(self, img, whitebg=False):
        """transforms image from RGB to CMY"""
        tmp = img*1.0
        if whitebg:
            tmp = (1.0 - (img - img.min())/(img.max() - img.min()))
        out = tmp*0.0
        out[:,:,0] = (tmp[:,:,1] + tmp[:,:,2])/2.0
        out[:,:,1] = (tmp[:,:,0] + tmp[:,:,2])/2.0
        out[:,:,2] = (tmp[:,:,0] + tmp[:,:,1])/2.0
        return out

    def set_config(self, interp=None, colormap=None, reverse_colormap=None,
                   contrast_level=None, flip_ud=None, flip_lr=None,
                   rot=None, tricolor_bg=None, ncontour_levels=None,
                   title=None, style=None):
        """set configuration options:

           interp, colormap, reverse_colormap, contrast_levels, flip_ud,
           flip_lr, rot, tricolor_bg, ncontour_levels, title, style
        """
        if interp is not None:
            interp = interp.lower()
            self.interp = interp if interp in Interp_List else self.interp

        if colormap is not None:
            colormap = colormap.lower()
            if colormap.endswith('_r'):
                reverse_colormap = True
                colormap = colormap[:-2]
            self.colormap = colormap if colormap in ColorMap_List else self.colormap

        if contrast_level is not None:
            self.contrast_level = float(contrast_level)

        self.cmap_reverse = bool_ifnotNone(reverse_colormap, self.cmap_reverse)
        self.flip_ud = bool_ifnotNone(flip_ud, self.flip_ud)
        self.flip_lr = bool_ifnotNone(flip_lr, self.flip_lr)
        self.rot     = bool_ifnotNone(rot, self.rot)

        if tricolor_bg is not None:
            tricolor_bg = tricolor_bg.lower()
            if tricolor_bg in ('black', 'white'):
                self.tricolor_bg = tricolor_bg

        if ncontour_levels is not None:
            self.ncontour_level = int(ncontour_levels)

        if style is not None:
            style = style.lower()
            if style in ('image', 'contour'):
                self.style = style

        self.title = ifnotNone(title, self.title)


    def get_config(self):
        """get dictionary of configuration options"""
        out = {'reverse_colormap': self.cmap_reverse}
        for attr in ('interp', 'colormap', 'contrast_levels', 'flip_ud',
                     'flip_lr', 'rot', 'tricolor_bg', 'ncontour_levels',
                     'title', 'style'):
            out[attr] = getattr(self, attr)
        return out
