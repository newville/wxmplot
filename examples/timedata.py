#!/usr/bin/python

import  MPlot

f = open('examples/time.dat','r')
l = f.readlines()
f.close()
t = []
x = []
for i in l:
    j =  i[:-1].strip().split()
    t.append(float(j[0]))
    x.append(float(j[1]))    


app = MPlot.PlotApp()
app.plot(t,x,use_dates=True)
app.set_title('Time series data:')
app.run()

