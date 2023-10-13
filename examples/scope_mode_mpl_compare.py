# This could be comparable to
# https://matplotlib.org/stable/gallery/animation/strip_chart.html

import numpy as np
from wxmplot.interactive import plot, set_data_generator

class Scope:
    def __init__(self, nmax=50, dt=0.1):
        self.dt = dt
        self.nmax = nmax
        self.t = [0]
        self.y = [0]

    def update(self):
        if len(self.t) > self.nmax:
            self.t = [0]
            self.y = [0]

        p = np.random.rand()
        v = np.random.rand() if p < 0.15 else 0
        self.y.append(v)
        self.t.append(len(self.t))
        return [(np.array(self.t)*self.dt, np.array(self.y))]

NMAX, dt = 200, 0.05
scope = Scope(nmax=NMAX, dt=dt)

plot([0], [0], xmax=dt*NMAX)
set_data_generator(scope.update, polltime=int(1000*dt))
