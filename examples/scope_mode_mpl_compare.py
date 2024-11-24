# This could be comparable to
# https://matplotlib.org/stable/gallery/animation/strip_chart.html

import numpy as np
from wxmplot.interactive import plot, set_data_generator

np.random.seed(19680801 // 10)

class Scope:
    def __init__(self, nmax=50, dt=0.1):
        self.dt = dt
        self.nmax = nmax
        self.t, self.y = [], []
        print(nmax, dt)

    def update(self):
        if len(self.y) > self.nmax:
            self.t, self.y = [], []
        self.t.append(self.dt*len(self.y))
        p = np.random.rand()
        self.y.append(np.random.rand() if p < 0.15 else 0)
        return [(self.t, self.y)]

NMAX, DT = 200, 0.05
scope = Scope(nmax=NMAX, dt=DT)

plot([0], [0], xmax=NMAX*DT)
set_data_generator(scope.update)
