#!/usr/bin/python
#
# compare to plplot example at
#  http://plplot.sourceforge.net/examples.php?demo=00&lbind=Python
##
## def main(w):
##    w.plenv( 0, 100, 0, 1, 0, 0)
##    w.pllab( "x", "y=100 x#u2#d", "Simple PLplot demo of a line plot" )
##    w.plline( x, y )


import numpy as np

x = np.linspace(0, 1, 101)
y = 100*x**2

import wxmplot.interactive as wi
wi.plot(x, y, color='red', xlabel='x', ylabel=r'$y=100 x^2$',
        title="Simple PLplot demo of a line plot", theme='dark')
