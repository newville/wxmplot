#!/usr/bin/python
#
#  example plot with 3 different right-hand axes with different y scales
import numpy as np
import wxmplot.interactive as wi
import pytz

noise = np.random.normal
n = 501
x  = np.linspace(0, 100, n)

# note: timestamps can be datetime objects or matplotlib dates
# which are floating point days since the 1970 epoch.
# using time.time() values (here, starting 2024-March-9 11AM)
# and defining the timezone
tstamp = (1710000000 +  x*100.0)/86400.
tzone = pytz.timezone('US/Eastern')

y1 = np.sin(x/3.4)/(0.2*x+2) + noise(size=n, scale=0.1)
y2 = (x * 0.041 + noise(size=n, scale=0.1)).astype(int)
y3 = 0.04 + 0.07*np.sin(x/46.) * np.exp(-x*x/7e3) + noise(size=n, scale=0.0003)
y4 = -210. + 0.6*x * np.exp(-x*x/7e3) + noise(size=n, scale=0.3)


disp = wi.plot(tstamp, y1, title='Test 4 Axes with different y scales',
               show_legend=True, yaxes_tracecolor=True,
               use_dates=True, timezone=tzone,
               xlabel='date/time', label='signal 1', ylabel='ylabel',
               size=(1000, 600))

wi.plot(tstamp, y2, y2label='y2label', label='state', yaxes=2,
       use_dates=True, drawstyle='steps-post')

disp.panel.set_ytick_labels({0: 'off', 1: 'staged',
                            2: 'ready', 3: 'running', 4: 'finished'},
                            yaxes=2)

wi.plot(tstamp, y3, y3label='y3 label', label='signal 3', use_dates=True, yaxes=3)
wi.plot(tstamp, y4, y4label='y4 label', label='signal 4', use_dates=True, yaxes=4)
