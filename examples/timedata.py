#!/usr/bin/python

from wxmplot import PlotApp
from datetime import datetime

with open('time.dat','r') as fh:
    lines = fh.readlines()

t, x = [], []
for i in lines:
    j =  i[:-1].strip().split()
    t.append(datetime.fromtimestamp(float(j[0])))
    x.append(float(j[1]))


app = PlotApp()
app.plot(t, x, use_dates=True, drawstyle='steps-post', marker='+')
app.set_title('Time series data:')
app.run()
