#!/usr/bin/python
#
#  compare, for reference:
#   https://www2.mps.mpg.de/dislin/exa_curv.html
#   https://www2.mps.mpg.de/dislin/exa_python.html#section_1
#

import numpy as np

x  = 3.6*np.arange(101)
y1 = np.cos(np.pi*x/180)
y2 = np.sin(np.pi*x/180)


# Note:  with matplotlib.pyplot, this would be
mpl_script = """
import  matplotlib.pyplot as plt
plt.plot(x, y1, '-', color='r')
plt.plot(x, y2, '-+', color='g')
plt.title('DISLIN Comparison\nsin(x) and cos(x)')
plt.xlabel('x')
plt.ylabel('y')
plt.show()
"""

from wxmplot.interactive import plot, wxloop
plot(x, y1, title='DISLIN Comparison\nsin(x) and cos(x)',
     color='red', xlabel='x', ylabel='y')
plot(x, y2, color='green3', marker='+')
wxloop()
