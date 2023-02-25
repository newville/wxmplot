#!/usr/bin/python

import time
from datetime import datetime
import numpy as np
from wxmplot import PlotApp


npts = 725
y = np.arange(npts) + np.random.normal(scale=3., size=npts)
t0  = time.time() - 700

t = np.array([datetime.fromtimestamp(t0 + i) for i in range(npts)])

app = PlotApp()
app.plot(t, y, use_dates=True,  marker='+')
app.set_title('Time series data:')
app.run()
