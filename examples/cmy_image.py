"""
example showing display of C, M, Y maps
"""
import wx
from numpy import exp, random, arange, outer, array
from wxmplot import ImageFrame

def gauss2d(x, y, x0, y0, sx, sy):
    return outer( exp( -(((y-y0)/float(sy))**2)/2),
                  exp( -(((x-x0)/float(sx))**2)/2) )

if __name__ == '__main__':
    app = wx.App()
    frame = ImageFrame(mode='cmy')
    ny, nx = 350, 400
    x = arange(nx)
    y = arange(ny)
    ox =  x / 100.0
    oy = -1 + y / 200.0
    cyan  = 2. * random.random(size=nx*ny).reshape(ny, nx)
    cyan += 0.25 + (6.0*gauss2d(x, y, 90,   76,  5,  6) +
                    3.0*gauss2d(x, y, 160, 190,  70,  33) +
                    2.0*gauss2d(x, y, 180, 100,  12,  6))
    magenta  = 0.3 * random.random(size=nx*ny).reshape(ny, nx)
    magenta += 0.11 + (1.0*gauss2d(x, y, 175,  98,  3,  7) +
                       1.2*gauss2d(x, y, 270, 230, 78, 63))

    yellow = 0.6 * random.random(size=nx*ny).reshape(ny, nx)
    yellow += (2.9*gauss2d(x, y, 240, 265,  78,  23) +
                   3.5*gauss2d(x, y, 181,  93,  34, 11) +
                   7.0*gauss2d(x, y, 220,  310,  40,  133))

    dat = array([cyan, magenta, yellow]).swapaxes(2, 0)
    frame.display(dat, x=ox, y=oy,
                  subtitles={'cyan':'Cyan Image', 'magenta': 'Magenta Blob', 'yellow': 'other'})
    frame.Show()
    app.MainLoop()
