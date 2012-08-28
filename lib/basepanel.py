#!/usr/bin/python
##
## MPlot BasePanel: a Basic Panel for 2D line and image plotting
##

import sys
import time
import os
import wx
import matplotlib
from matplotlib.widgets import Lasso

from utils import Printer

class BasePanel(wx.Panel):
    """
    wx.Panel component shared by PlotPanel and ImagePanel.

    provides:
         Basic support Zooming / Unzooming
         support for Printing
         popup menu
         bindings for keyboard short-cuts
    """
    def __init__(self, parent, messenger=None,
                 show_config_popup=True,
                 output_title=None, **kws):

        wx.Panel.__init__(self, parent, -1, **kws)

        self.is_macosx = False
        if os.name == 'posix':
            if os.uname()[0] == 'Darwin':
                self.is_macosx = True

        self.messenger = messenger
        if messenger is None:
            self.messenger = self.__def_messenger

        self.popup_menu =  None
        self.cursor_state = None
        self._yfmt = '%.4f'
        self._y2fmt = '%.4f'
        self._xfmt = '%.4f'
        self.use_dates = False
        self.show_config_popup = show_config_popup
        self.launch_dir  = os.getcwd()

        self.mouse_uptime = time.time()
        self.user_limits = {}
        self.zoom_lims = []           # store x, y coords zoom levels
        self.zoom_ini  = (-1, -1, -1, -1)  # store init axes, x, y coords for zoom-box
        self.rbbox = None
        self.zdc = None

        self.parent = parent
        self.printer = Printer(self, title=output_title)

    def addCanvasEvents(self):
        # use matplotlib events
        self.canvas.mpl_connect("motion_notify_event",
                                self.__onMouseMotionEvent)
        self.canvas.mpl_connect("button_press_event",
                                self.__onMouseButtonEvent)
        self.canvas.mpl_connect("button_release_event",
                                self.__onMouseButtonEvent)
        self.canvas.mpl_connect("key_press_event",
                                self.__onKeyEvent)
        self.BuildPopup()

    def BuildPopup(self):
        # build pop-up menu for right-click display
        self.popup_unzoom_all = wx.NewId()
        self.popup_unzoom_one = wx.NewId()
        self.popup_config     = wx.NewId()
        self.popup_save   = wx.NewId()
        self.popup_menu = wx.Menu()
        self.popup_menu.Append(self.popup_unzoom_one, 'Zoom out')
        self.popup_menu.Append(self.popup_unzoom_all, 'Zoom all the way out')
        self.popup_menu.AppendSeparator()
        if self.show_config_popup:
            self.popup_menu.Append(self.popup_config,'Configure')

        self.popup_menu.Append(self.popup_save,  'Save Image')
        self.Bind(wx.EVT_MENU, self.unzoom,       id=self.popup_unzoom_one)
        self.Bind(wx.EVT_MENU, self.unzoom_all,   id=self.popup_unzoom_all)
        self.Bind(wx.EVT_MENU, self.save_figure,  id=self.popup_save)
        self.Bind(wx.EVT_MENU, self.configure,    id=self.popup_config)

    def clear(self):
        """ clear plot """
        self.axes.cla()
        self.conf.ntrace = 0
        self.conf.xlabel = ''
        self.conf.ylabel = ''
        self.conf.title  = ''

    def unzoom_all(self, event=None):
        """ zoom out full data range """
        if len(self.zoom_lims) > 0:
            self.zoom_lims = [self.zoom_lims[0]]
        self.unzoom(event)

    def unzoom(self, event=None, set_bounds=True):
        """ zoom out 1 level, or to full data range """
        lims = None
        if len(self.zoom_lims) > 1:
            lims = self.zoom_lims.pop()
        ax = self.axes
        # print 'base unzoom ', lims, set_bounds
        if lims is None: # auto scale
            self.zoom_lims = [None]
            xmin, xmax, ymin, ymax = self.data_range
            ax.set_xlim((xmin, xmax), emit=True)
            ax.set_ylim((ymin, ymax), emit=True)
            if set_bounds:
                ax.update_datalim(((xmin, ymin), (xmax, ymax)))
                ax.set_xbound(ax.xaxis.get_major_locator(
                    ).view_limits(xmin, xmax))
                ax.set_ybound(ax.yaxis.get_major_locator(
                    ).view_limits(ymin, ymax))
        else:
            self.set_viewlimits()

        self.canvas.draw()

    def get_right_axes(self):
        "create, if needed, and return right-hand y axes"
        if len(self.fig.get_axes()) < 2:
            ax = self.axes.twinx()

        return self.fig.get_axes()[1]

    def set_xylims(self, limits, axes=None):
        if axes not in self.user_limits:
            axes = self.axes
        self.user_limits[axes] = limits
        self.unzoom_all()

    def get_viewlimits(self, axes=None):
        if axes is None: axes = self.axes
        xmin, xmax = axes.get_xlim()
        ymin, ymax = axes.get_ylim()
        return (xmin, xmax, ymin, ymax)

    def set_title(self, s):
        "set plot title"
        self.conf.relabel(title=s)

    def set_xlabel(self, s):
        "set plot xlabel"
        self.conf.relabel(xlabel=s)

    def set_ylabel(self, s):
        "set plot ylabel"
        self.conf.relabel(ylabel=s)

    def set_y2label(self, s):
        "set plot ylabel"
        self.conf.relabel(y2label=s)

    def write_message(self, s, panel=0):
        """ write message to message handler
        (possibly going to GUI statusbar)"""
        self.messenger(s, panel=panel)

    def save_figure(self, event=None):
        """ save figure image to file"""
        file_choices = "PNG (*.png)|*.png"
        ofile = self.conf.title.strip()
        if len(ofile) > 64:
            ofile = ofile[:63].strip()
        if len(ofile) < 1:
            ofile = 'plot'

        for c in ' :";|/\\': # "
            ofile = ofile.replace(c, '_')

        ofile = ofile + '.png'

        dlg = wx.FileDialog(self, message='Save Plot Figure as...',
                            defaultDir = os.getcwd(),
                            defaultFile=ofile,
                            wildcard=file_choices,
                            style=wx.SAVE|wx.CHANGE_DIR)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.canvas.print_figure(path, dpi=600)
            if (path.find(self.launch_dir) ==  0):
                path = path[len(self.launch_dir)+1:]
            self.write_message('Saved plot to %s' % path)

    def set_bg(self, color= None):
        if color is None:
            color = '#FDFDFB'
        self.fig.set_facecolor(color)

    ####
    ## GUI events
    ####
    def reportLeftDown(self, event=None, **kw):
        if event is None:
            return
        self.write_message("%f, %f" % (event.xdata, event.ydata), panel=1)

    def onLeftDown(self, event=None):
        """ left button down: report x,y coords, start zooming mode"""
        if event is None:
            return
        if event.inaxes not in self.fig.get_axes():
            return

        self.cursor_state = self.conf.cursor_mode # 'zoom'  # or 'lasso'!
        if event.inaxes is not None:
            self.reportLeftDown(event=event)
            if self.cursor_state == 'zoom':
                self.zoom_ini = (event.x, event.y, event.xdata, event.ydata)
            elif self.cursor_state == 'lasso':
                self.lasso = Lasso(event.inaxes, (event.xdata, event.ydata),
                                   self.lassoHandler)
                ## set lasso color
                cmap = getattr(self.conf, 'cmap', None)
                if cmap is not None:
                    rgb = (int(i*255)^255 for i in cmap._lut[0][:3])
                    col = '#%02x%02x%02x' % tuple(rgb)
                    self.lasso.line.set_color(col)
                else:
                    self.lasso.line.set_color('goldenrod')
            self.ForwardEvent(event=event.guiEvent)


    def toggle_legend(self, evt=None, show=None):
        pass
    def toggle_grid(self, evt=None, show=None):
        pass

    def lassoHandler(self, vertices):
        try:
            print 'default lasso handler -- override!'
            del self.lasso
            self.canvas.draw_idle()
        except:
            pass

    def zoom_OK(self, start, stop):
        return True

    def onLeftUp(self, event=None):
        """ left button up: zoom in or handle lasso"""
        if event is None:
            return
        if self.cursor_state == 'zoom':
            self._onLeftUp_Zoom(event)

        self.canvas.draw()
        self.cursor_state = None
        self.ForwardEvent(event=event.guiEvent)

    def _onLeftUp_Zoom(self, event=None):
        """ left up / zoom mode"""
        ini_x, ini_y, ini_xd, ini_yd = self.zoom_ini
        try:
            dx = abs(ini_x - event.x)
            dy = abs(ini_y - event.y)
        except:
            dx, dy = 0, 0
        t0 = time.time()
        self.rbbox = None
        if (dx > 3) and (dy > 3) and (t0-self.mouse_uptime)>0.1:
            self.mouse_uptime = t0
            zlims, tlims = {}, {}
            for ax in self.fig.get_axes():
                xmin, xmax = ax.get_xlim()
                ymin, ymax = ax.get_ylim()
                zlims[ax] = [xmin, xmax, ymin, ymax]
            if len(self.zoom_lims) == 0:
                self.zoom_lims.append(zlims)
            # for multiple axes, we first collect all the new limits, and
            # only then apply them
            for ax in self.fig.get_axes():
                ax_inv = ax.transData.inverted
                try:
                    x1, y1 = ax_inv().transform((event.x, event.y))
                except:
                    x1, y1 = event.xdata, event.ydata
                try:
                    x0, y0 = ax_inv().transform((ini_x, ini_y))
                except:
                    x0, y0 = ini_xd, ini_yd

                tlims[ax] = [min(x0, x1), max(x0, x1),
                             min(y0, y1), max(y0, y1)]
            self.zoom_lims.append(tlims)
            # now apply limits:
            self.set_viewlimits()

    def ForwardEvent(self, event=None):
        """finish wx event, forward it to other wx objects"""
        if event is not None:
            event.Skip()
            if os.name == 'posix' or  self.HasCapture():
                try:
                    self.ReleaseMouse()
                except:
                    pass

    def onRightDown(self, event=None):
        """ right button down: show pop-up"""
        if event is None:
            return
        # note that the matplotlib event location have to be converted
        if event.inaxes is not None and self.popup_menu is not None:
            pos = event.guiEvent.GetPosition()
            wx.CallAfter(self.PopupMenu, self.popup_menu, pos)
        self.ForwardEvent(event=event.guiEvent)

    def onRightUp(self, event=None):
        """ right button up: put back to cursor mode"""
        if event is not None:
            self.ForwardEvent(event=event.guiEvent)

    ####
    ## private methods
    ####
    def __def_messenger(self, s, panel=0):
        """ default, generic messenger: write to stdout"""
        sys.stdout.write(s)

    def __date_format(self, x):
        """ formatter for date x-data. primitive, and probably needs
        improvement, following matplotlib's date methods.
        """
        interval = self.axes.xaxis.get_view_interval()
        ticks = self.axes.xaxis.get_major_locator()()
        span = max(interval) - min(interval)
        fmt = "%m/%d"
        if span < 1800:
            fmt = "%I%p \n%M:%S"
        elif span < 86400*5:
            fmt = "%m/%d \n%H:%M"
        elif span < 86400*20:
            fmt = "%m/%d"
        # print 'date formatter  span: ', span, fmt
        s = time.strftime(fmt, time.localtime(x))
        return s

    def xformatter(self, x, pos):
        " x-axis formatter "
        if self.use_dates:
            return self.__date_format(x)
        else:
            return self.__format(x, type='x')

    def yformatter(self, y, pos):
        " y-axis formatter "
        return self.__format(y, type='y')

    def y2formatter(self, y, pos):
        " y-axis formatter "
        return self.__format(y, type='y2')

    def __format(self, x, type='x'):
        """ home built tick formatter to use with FuncFormatter():
        x     value to be formatted
        type  'x' or 'y' or 'y2' to set which list of ticks to get

        also sets self._yfmt/self._xfmt for statusbar
        """
        fmt, v = '%1.5g','%1.5g'
        if type == 'y':
            ax = self.axes.yaxis
        elif type == 'y2' and len(self.fig.get_axes()) > 1:
            ax =  self.fig.get_axes()[1].yaxis
        else:
            ax = self.axes.xaxis

        try:
            dtick = 0.1 * ax.get_view_interval().span()
        except:
            dtick = 0.2
        try:
            ticks = ax.get_major_locator()()
            dtick = abs(ticks[1] - ticks[0])
        except:
            pass
        # print ' tick ' , type, dtick, ' -> ',
        if   dtick > 99999:
            fmt, v = ('%1.6e', '%1.7g')
        elif dtick > 0.99:
            fmt, v = ('%1.0f', '%1.2f')
        elif dtick > 0.099:
            fmt, v = ('%1.1f', '%1.3f')
        elif dtick > 0.0099:
            fmt, v = ('%1.2f', '%1.4f')
        elif dtick > 0.00099:
            fmt, v = ('%1.3f', '%1.5f')
        elif dtick > 0.000099:
            fmt, v = ('%1.4f', '%1.6e')
        elif dtick > 0.0000099:
            fmt, v = ('%1.5f', '%1.6e')

        s =  fmt % x
        s.strip()
        s = s.replace('+', '')
        while s.find('e0')>0:
            s = s.replace('e0','e')
        while s.find('-0')>0:
            s = s.replace('-0','-')
        if type == 'y':
            self._yfmt = v
        if type == 'y2':
            self._y2fmt = v
        if type == 'x':
            self._xfmt = v
        return s

    def __onKeyEvent(self, event=None):
        """ handles key events on canvas
        """
        if event is None:
            return
        # print 'KeyEvent ', event
        key = event.guiEvent.GetKeyCode()
        if (key < wx.WXK_SPACE or  key > 255):
            return
        ckey = chr(key)
        mod  = event.guiEvent.ControlDown()
        if self.is_macosx:
            mod = event.guiEvent.MetaDown()
        if mod:
            if ckey == 'C':
                self.canvas.Copy_to_Clipboard(event)
            elif ckey == 'S':
                self.save_figure(event)
            elif ckey == 'K':
                self.configure(event)
            elif ckey == 'Z':
                self.unzoom(event)
            elif ckey == 'P':
                self.canvas.printer.Print(event)

    def __onMouseButtonEvent(self, event=None):
        """ general mouse press/release events. Here, event is
        a MplEvent from matplotlib.  This routine just dispatches
        to the appropriate onLeftDown, onLeftUp, onRightDown, onRightUp....
        methods.
        """
        if event is None:
            return
        button = event.button or 1

        handlers = {(1, 'button_press_event'):   self.onLeftDown,
                    (1, 'button_release_event'): self.onLeftUp,
                    (3, 'button_press_event'):   self.onRightDown,
                    }
        # (3,'button_release_event'): self.onRightUp}

        handle_event = handlers.get((button, event.name), None)
        if hasattr(handle_event, '__call__'):
            handle_event(event)

    def __onMouseMotionEvent(self, event=None):
        """Draw a cursor over the axes"""
        if event is None:
            return
        ax = event.inaxes
        if self.cursor_state not in ('zoom', 'lasso'):
            if ax is not None:
                self.reportMotion(event=event)
            return
        try:
            x, y  = event.x, event.y
        except:
            return
        if self.cursor_state == 'lasso':
            return
        ini_x, ini_y, ini_xd, ini_yd = self.zoom_ini
        x0     = min(x, ini_x)
        ymax   = max(y, ini_y)
        width  = abs(x -ini_x)
        height = abs(y -ini_y)
        y0     = self.canvas.figure.bbox.height - ymax

        zdc = wx.ClientDC(self.canvas)
        zdc.SetLogicalFunction(wx.XOR)
        zdc.SetBrush(wx.TRANSPARENT_BRUSH)
        zdc.SetPen(wx.Pen('White', 2, wx.SOLID))

        zdc.ResetBoundingBox()
        zdc.BeginDrawing()

        # erase previous box
        # print 'erase? draw?  ', self.rbbox
        if self.rbbox is not None:
            zdc.DrawRectangle(*self.rbbox)

        self.rbbox = (x0, y0, width, height)
        zdc.DrawRectangle(*self.rbbox)
        zdc.EndDrawing()

    def reportMotion(self, event=None):
        fmt = "X,Y= %s, %s" % (self._xfmt, self._yfmt)
        y  = event.ydata
        if len(self.fig.get_axes()) > 1:
            try:
                x, y = self.axes.transData.inverted().transform((event.x, event.y))
            except:
                pass
        self.write_message(fmt % (event.xdata, y), panel=1)

    def Print(self, event=None, **kw):
        self.printer.Print(event=event, **kw)

    def PrintPreview(self, event=None, **kw):
        self.printer.Preview(event=event, **kw)

    def PrintSetup(self, event=None, **kw):
        self.printer.Setup(event=event, **kw)

