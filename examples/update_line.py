
_doc_  = """

Fast update of a plot with update_line.

Using update_line(x, y, trace=i) will replace the data plotted
in trace i with the (x, y) values supplied.  This is much faster
than re-running plot(), and is recommended if the only change is
that the data has changed.

The example here shows two traces (1 using the right axis, 1 the
left axis) that are updated, as to simulate adding data.
"""


import time

x = arange(1200)
y1 = sin(x/123)
y2 = 41 + 22*cos(x/587.)

newplot(x[:2], y1[:2], side='left', ymin=-1.2, ymax=1.2)
#   plot(x[:2], y2[:s2], side='right',  ymin=20, ymax=70)

t0 = time.time()
npts = 40
s = int((len(x)-1) /npts)
ndraws = 0
for i in range(npts):
    print '==> '  , i, ndraws, 1+s*i, time.time()-t0
    update_line(x[:1+s*i], y1[:1+s*i], trace=1)
    # update_line(x[:1+s*i], y2[:1+s*i], trace=2, side='right')
#endfor
# now that we're done, use 'redraw=True' to fully refresh.

update_trace(x, y1, trace=1, redraw=True)

print 'updated plot %i times in %.2f seconds' % (npts, time.time()-t0)


