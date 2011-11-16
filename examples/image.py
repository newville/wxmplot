import wx
from numpy import exp, random, arange, outer

from mplot import ImageFrame

def gauss2d(x, y, x0, y0, sx, sy):
    return outer( exp( -(((x-x0)/float(sx))**2)/2),
                  exp( -(((y-y0)/float(sy))**2)/2) )

if __name__ == '__main__':
    app = wx.PySimpleApp()
  
    frame = ImageFrame(config_on_frame=True)
    nx, ny = 350, 400
    x = arange(nx)
    y = arange(ny)
    
    dat  = 0.50 * random.random(size=nx*ny).reshape(nx, ny)
    
    dat =  dat + (6.0*gauss2d(x, y, 90,   76,  5,  6) +
                  1.0*gauss2d(x, y, 180, 100,  7,  3) +
                  1.0*gauss2d(x, y, 175,  98,  3,  7) +
                  0.5*gauss2d(x, y, 181,  93,  4, 11) +
                  1.8*gauss2d(x, y, 270, 230, 78, 63) +
                  0.9*gauss2d(x, y, 240, 265,  8,  3) +
                  7.0*gauss2d(x, y, 40,  310,  2,  3) 
                  )
    dat = dat.transpose()
    
    # 
    #     for i in range(n1):
    # 
    #               exp(-(i-i2)*(i-i2)*v2) )
    #         for j in range(n2):
    #             dat[i,j] += d0 * (exp(-(j-j1)*(j-j1)*w1)  +
    #                             exp(-(j-j2)*(j-j2)*w2) )
    
    frame.display(dat)
    frame.Show()
    app.MainLoop()
