
from numpy import exp, random, arange, outer
import wxmplot.interactive as wi

def gauss2d(x, y, x0, y0, sx, sy):
    return outer( exp( -(((y-y0)/float(sy))**2)/2),
                  exp( -(((x-x0)/float(sx))**2)/2) )

ny, nx = 350, 400
x = arange(nx)
y = arange(ny)
ox =  x /200.0
oy = -1 + y / 200.0
dat  = 0.3 * random.random(size=nx*ny).reshape(ny, nx)
dat =  dat + (16.0*gauss2d(x, y, 190,   96,  15,  26) +
              27.0*gauss2d(x, y, 140,  210,  51,  42))

wi.imshow(dat, x=ox, y=oy, style='contour', contour_labels=True)
