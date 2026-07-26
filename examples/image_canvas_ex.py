#!/usr/bin/python
#
# use image canvas

import wx

import numpy as np
from pathlib import Path
from tifffile import imread

from wxutils import pack
from wxmplot.interactive import get_wxapp
from wxmplot.image_canvas import ImageCanvas

class ImageCanvasFrame(wx.Frame):
    def __init__(self, title='WXMPLOT Image Canvas', size=(700,600)):
        wx.Frame.__init__(self, None, title=title, size=size,
                          style=wx.DEFAULT_FRAME_STYLE)

        self.im_canvas = ImageCanvas(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.im_canvas, 1, wx.ALL|wx.GROW)
        pack(self, sizer)

    def set_colormap(self, colormap: str):
        self.im_canvas.set_colormap(colormap)

    def set_image(self, image: np.ndarray):
        self.im_canvas.set_image(image)
        self.im_canvas.set_auto_scale(True, level=0.5)

if __name__ == '__main__':
    wxapp = get_wxapp()
    icanvas = ImageCanvasFrame()

    img = imread(Path(__file__).parent / 'ceo2.tiff')

    icanvas.set_image(img)
    icanvas.set_colormap('magma')

    icanvas.Show()
