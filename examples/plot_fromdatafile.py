#!/usr/bin/python

from wxmplot import PlotApp

f = open('xafs.dat','r')
x = []
y = []
titles = []
for i in f.readlines():
    i =  i[:-1].strip()
    if i.startswith('#'):
        titles.append(i)
    else:
        j = i.split()
        x.append(float(j[0]))
        y.append(float(j[1]))
f.close()
app = PlotApp()
app.plot(x,y,xlabel='E (eV)', label='As K', marker='+',linewidth=1)
app.set_title('Test Plot')
app.write_message('MPlot PlotFrame example: Try Help->Quick Reference')
app.run()
