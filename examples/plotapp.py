from wxmplot import PlotApp
from numpy import arange, sin, cos, exp, pi

xx  = arange(0.0,12.0,0.1)
y1  = 1*sin(2*pi*xx/3.0)
y2  = 4*cos(2*pi*(xx-1)/5.0)/(6+xx)
y3  = -pi + 2*(xx/10. + exp(-(xx-3)/5.0))

p = PlotApp()
p.plot(xx, y1, color='blue',  style='dashed',
       title='Example PlotApp',  label='a',
       ylabel=r'$k^2\chi(k) $',
       xlabel=r'$  k \ (\AA^{-1}) $' )

p.oplot(xx, y2,  marker='+', linewidth=0, label =r'$ x_1 $')
p.oplot(xx, y3,  style='solid',          label ='x_2')
p.write_message('Try Help->Quick Reference')
p.run()
