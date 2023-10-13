import numpy as np
from wxmplot.interactive import plot, set_data_generator

npts = 501
x = np.linspace(0, 50, npts)
y = 3.5*np.cos(1.1*(x-1)/(25+x)) + 2.4*np.cos(3.7*(x-11))
z = 4.1*np.cos(1.6*(x-4)/(40+x)) + 1.9*np.cos(3.2*(x-21))

nx = 2
def get_more_data():
    global nx
    nx += 1
    if nx >= npts:
        return None
    return [(x[:nx], y[:nx]),
            (x[:nx], z[:nx])]

# set up initial plot
plot(x[:nx], y[:nx])

# use data generator to run function to retrieve more data
set_data_generator(get_more_data,  polltime=25)

print("consuming data from function...")
