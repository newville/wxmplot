import wx
from .plotframe import PlotFrame

class PlotApp(object):
    """wx.App that provides a top-level Frame containing a
    matpplotlib plot that includes (by default) zooming,
    navigation and user-customization of line colors, width,
    labels, and so on.
      arguments
      ---------
      title    frame title      "WXMPLOT"
      size     wx Size tuple    (700, 450)
      dpi      Figure dpi       150

    Additional keyword arguments will be passed to PlotPanel
    """
    def __init__(self, title='WXMPLOT', size=(700,450),  dpi=150, **kws):
        self.app   = wx.App()
        self.frame = PlotFrame(title=title, size=size, dpi=dpi, **kws)

    def plot(self, x, y, **kw):
        """plot x, y values (erasing old plot),
        for method options see PlotPanel.plot.
        """
        return self.frame.plot(x,y,**kw)

    def oplot(self, x, y, **kw):
        """overplot x, y values (on top of old plot),
        for method options see PlotPanel.oplot
        """
        return self.frame.oplot(x,y,**kw)

    def set_title(self,s):
        "set title"
        self.frame.set_title(s)

    def write_message(self, msg, **kw):
        "write message to status bar"
        return self.frame.write_message(msg, **kw)

    def draw(self):
        "update figure"
        self.frame.draW()

    def run(self):
        self.frame.Show()
        self.frame.Raise()
        self.app.MainLoop()
