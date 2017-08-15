"""
example showing 2 maps
"""
import wx
from numpy import exp, random, arange, outer, array, linspace
from wxmplot import ImageMatrixFrame

def gauss2d(x, y, x0, y0, sx, sy):
    return outer( exp( -(((y-y0)/float(sy))**2)/2),
                  exp( -(((x-x0)/float(sx))**2)/2) )

if __name__ == '__main__':
    app = wx.App()
    frame = ImageMatrixFrame()
    ny, nx = 41, 51

    x = linspace(0, 1, nx)
    y = linspace(-1, 1, ny)
    ox =  x / 10.0
    oy = -1 + y / 20.0

    map1  = 0.5 * random.random(size=nx*ny).reshape(ny, nx)
    map1 += 0.02 + (16.0*gauss2d(x, y, .50,  .25,   .09,  .08) +
                    18.0*gauss2d(x, y,  .12, -.06,  .23,  .21))
    map2  = 0.3 * random.random(size=nx*ny).reshape(ny, nx)
    map2 += 0.11 + (1.0*gauss2d(x, y,   .44,  .3,   .1,  .15) +
                    1.2*gauss2d(x, y,   .7,  -0.1, .09, .11))

    frame.display(map1, map2, x=x, y=y, name1='Iron', name2='Carbon',
                  xlabel='X', ylabel='Y')
    frame.Show()
    app.MainLoop()
