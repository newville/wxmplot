import numpy as np
from wxmplot.interactive import plot, set_data_generator

# generator of datasets
npts = 501
x = np.linspace(0, 50, npts)
datasets = ((np.cos(1.3*x) + np.sin(0.8*(x+nx/7)),
             np.cos(1.1*x) - np.sin(0.6*(x+nx/43)))
            for nx in range(npts))

def more_data():
    """yield next pair of datasets from data generator"""
    while True:
        try:
            ds = next(datasets)
            yield [(x, ds[0]), (x, ds[1])]
        except StopIteration:
            break

# set up an initial plot
plot(x, np.zeros(len(x)))

# now set data generator and wait
set_data_generator(more_data,  polltime=30)
print("consuming data from generator...")
