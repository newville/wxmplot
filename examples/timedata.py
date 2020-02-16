#!/usr/bin/python

from wxmplot import PlotApp
from datetime import datetime
f = open('time.dat','r')
l = f.readlines()
f.close()
t = []
x = []
for i in l:
    j =  i[:-1].strip().split()
    t.append(datetime.fromtimestamp(float(j[0])))
    x.append(float(j[1]))


app = PlotApp()
app.plot(t, x, use_dates=True, drawstyle='steps-post', marker='+')
app.set_title('Time series data:')
app.run()
