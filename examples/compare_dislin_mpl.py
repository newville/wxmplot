#!/usr/bin/python
#
# compare basic wxmplot plotting to DISLIN and matplotlib,
# inspired from example at
#     https://www2.mps.mpg.de/dislin/exa_curv.html
#

# make data
import numpy as np
x  = 3.6*np.arange(101)
y1 = np.sin(np.pi*x/180)
y2 = np.cos(np.pi*x/180)

# dislin:
#   See script at:
#   https://www2.mps.mpg.de/dislin/exa_python.html#section_1

# matplotlib/pyplot:
mpl_script = """
import  matplotlib.pyplot as plt
plt.plot(x, y1, '-', color='r')
plt.plot(x, y2, '-+', color='g')
plt.title('DISLIN Comparison\nsin(x) and cos(x)')
plt.xlabel('X axis')
plt.ylabel('Y axis')
plt.show()
"""

# wxmplot:
import wxmplot.interactive as wi
wi.plot(x, y1, color='red', xlabel='X axis', ylabel='Y axis',
        title='DISLIN Comparison\nsin(x) and cos(x)')
wi.plot(x, y2, color='green3', marker='+')
