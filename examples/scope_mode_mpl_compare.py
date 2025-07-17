# This could be comparable to
# https://matplotlib.org/stable/gallery/animation/strip_chart.html

from random import random
import numpy as np
from wxmplot.interactive import plot, set_data_generator

class Scope:
    def __init__(self, nmax=50, dt=0.1):
        self.dt = dt
        self.nmax = nmax
        self.tmax = dt*nmax
        self.t = []
        self.y = []

    def update(self):
        n = len(self.y)
        if n > self.nmax:
            self.t, self.y, n = [0], [0], 1
        self.t.append(n*self.dt)
        self.y.append(random() if random() < 0.15 else 0)
        return [(self.t, self.y)]

scope = Scope(nmax=200, dt=0.05)

plotter = plot([0], [0], xmax=scope.tmax, ymin=-0.05, ymax=1.05, drawstyle='steps-mid')

set_data_generator(scope.update, win=plotter.window)
