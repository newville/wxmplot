#!/usr/bin/python
"""
 wxmplot PlotFrame: a wx.Frame for line plotting, using matplotlib
"""
import numpy as np

from .plotpanel import PlotPanel
from .baseframe import BaseFrame
from .utils import gformat

class PlotFrame(BaseFrame):
    """
    MatPlotlib 2D plot as a wx.Frame, using PlotPanel
    """
    def __init__(self, parent=None, title=None, with_data_process=True, **kws):
        if title is None:
            title = 'Line Plot Frame'
        BaseFrame.__init__(self, parent=parent, title=title,
                           with_data_process=with_data_process, **kws)
        self.BuildFrame()

    def get_figure(self):
        """return MPL plot figure"""
        return self.panel.fig

    def add_text(self, text, x, y, **kws):
        """add text to plot"""
        self.panel.add_text(text, x, y, **kws)

    def add_arrow(self, x1, y1, x2, y2, **kws):
        """add arrow to plot"""
        self.panel.add_arrow(x1, y1, x2, y2, **kws)

    def plot(self, x, y, **kw):
        """plot after clearing current plot """
        self.panel.plot(x, y, **kw)

    def oplot(self, x, y, **kw):
        """generic plotting method, overplotting any existing plot """
        self.panel.oplot(x, y, **kw)

    def plot_many(self, datalist, **kws):
        self.panel.plot_many(datalist, **kws)

    def scatterplot(self, x, y, **kw):
        """plot after clearing current plot """
        self.panel.scatterplot(x, y, **kw)

    def draw(self):
        "explicit draw of underlying canvas"
        self.panel.canvas.draw()

    def clear(self):
        "clear plot"
        self.panel.clear()

    def reset_config(self):
        self.panel.reset_config()

    def update_line(self, t, x, y, **kw):
        """overwrite data for trace t """
        self.panel.update_line(t, x, y, **kw)

    def ExportTextFile(self, fname, title='unknown plot'):
        "save plot data to external file"

        buff = ["# Plot Data for %s" % title,
                "#---------------------------------"]

        out = []
        labels = []
        itrace = 0
        for ax in self.panel.fig.get_axes():
            for line in ax.lines:
                itrace += 1
                x = line.get_xdata()
                y = line.get_ydata()
                ylab = line.get_label()

                if len(ylab) < 1:
                    ylab = 'Y%i' % itrace
                for c in ' .:";|/\\(){}[]\'&^%*$+=-?!@#':
                    ylab = ylab.replace(c, '_')
                xlab = (' X%d' % itrace + ' '*3)[:4]
                ylab = ' '*(18-len(ylab)) + ylab + '  '
                out.extend([x, y])
                labels.extend([xlab, ylab])

        if itrace == 0:
            return

        buff.append('# %s' % (' '.join(labels)))

        npts = [len(a) for a in out]
        for i in range(max(npts)):
            oline = []
            for a in out:
                d = np.nan
                if i < len(a):
                    d = a[i]
                oline.append(gformat(d, 12))
            buff.append(' '.join(oline))

        buff.append('')
        with open(fname, 'w') as fout:
            fout.write("\n".join(buff))
        fout.close()
        self.write_message("Exported data to '%s'" % fname, panel=0)
