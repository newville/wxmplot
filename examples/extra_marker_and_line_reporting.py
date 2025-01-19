#
"""
this example shows how to add individual markers, and
vertical and horizontal lines to a plot, and also to
add extra information to report for cursor events (left-down)
at this objects.
"""


import numpy as np
import wxmplot.interactive as wi

x = np.linspace(0, 100, 201)
y = np.sin(x/5) + x*0.014

plot = wi.plot(x, y, xlabel='x', ylabel='y',
              title='click on the lines and markers',
              show_legend=True)

plot.panel.add_vline(44, report_data='Vertical Line at x=44!',
                     color='#449999')


# note: adding a 'label' to any of these, will cause it to
# show up in the list of traces - and so can be toggled on/off
# from the legend.

plot.panel.add_hline(-0.25, report_data='Horizion=-0.25!',
                         label='horizon',     color='#999944')


# a single marker
plot.panel.add_marker(x[121], y[121], marker='o',
                      report_data='Yes, that is the best point!',
                      label='best point', color='#337722')
