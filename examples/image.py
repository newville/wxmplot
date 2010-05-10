import wx
import numpy
import MPlot

if __name__ == '__main__':
    app = wx.PySimpleApp()
  
    frame = MPlot.ImageFrame(config_on_frame=True)
    n1,n2 = 200, 250
    i1,i2  = 90, 135
    w1,w2 = 1/12.1, 1/46.2
    x  = numpy.random.random(n1*n2)/4.50
    x.shape = (n1,n2)

    for i in range(n1):
        x0 = numpy.exp(-(i-i1)*(i-i1)*w1)
        for j in range(n2):
            x[i,j] += x0 * numpy.exp(-(j-i2)*(j-i2)*w2) 

    frame.display(x)
    frame.Show()
    app.MainLoop()
