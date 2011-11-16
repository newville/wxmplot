#!/usr/bin/python

from mplot import PlotApp

f = open('time.dat','r')
l = f.readlines()
f.close()
t = []
x = []
for i in l:
    j =  i[:-1].strip().split()
    t.append(float(j[0]))
    x.append(float(j[1]))    


app = PlotApp()
app.plot(t, x, use_dates=True, drawstyle='steps-post')
app.set_title('Time series data:')
app.run()

