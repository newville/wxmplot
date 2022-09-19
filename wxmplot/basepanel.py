#!/usr/bin/python
##
## wxmplot BasePanel: a Basic Panel for line and image plotting
##

import sys
import time
import os
from math import log10

import wx
from wxutils import get_cwd
import numpy as np
import matplotlib
from matplotlib.widgets import Lasso
from matplotlib import dates
from matplotlib.backends.backend_wx import RendererWx

from .utils import Printer, MenuItem

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
                 show_config_popup=True, zoom_callback=None,
                 output_title=None, **kws):

        wx.Panel.__init__(self, parent, -1, **kws)

        self.is_macosx = (os.name == 'posix' and
                          sys.platform.lower().startswith('darw'))

        self.messenger = messenger
        if messenger is None:
            self.messenger = self.__def_messenger

        self.popup_menu =  None
        self._yfmt  = self._y2fmt = self._xfmt  = None
        self.use_dates = False
        self.show_config_popup = show_config_popup
        self.launch_dir  = get_cwd()

        self.mouse_uptime = time.time()
        self.user_limits = {}
        self.zoom_ini  = None  # x, y coords for zoom-box
        self.zoom_callback = zoom_callback
        self.rbbox = None
        # self.zdc = None
        self.cursor_modes = {}
        self.cursor_mode = 'report'
        self.parent = parent
        self.motion_sbar = None
        self.printer = Printer(self, title=output_title)
        self.add_cursor_mode('report', motion = self.report_motion,
                             leftdown = self.report_leftdown)
        self.add_cursor_mode('zoom', motion = self.zoom_motion,
                             leftdown = self.zoom_leftdown,
                             leftup   = self.zoom_leftup)
        self.add_cursor_mode('lasso', motion = self.lasso_motion,
                             leftdown = self.lasso_leftdown,
                             leftup   = self.lasso_leftup)


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

        if os.name == 'posix':
            def swallow_mouse(*args):
                pass
            self.canvas.CaptureMouse = swallow_mouse
            self.canvas.ReleaseeMouse = swallow_mouse

        self.BuildPopup()

    def BuildPopup(self):
        # build pop-up menu for right-click display
        self.popup_menu = popup = wx.Menu()
        MenuItem(self, popup, 'Undo last zoom', '',   self.unzoom)
        MenuItem(self, popup, 'Zoom all the way out', '',   self.unzoom_all)

        if self.show_config_popup:
            MenuItem(self, popup, 'Configure', '',   self.configure)

        MenuItem(self, popup, 'Save Image', '',   self.save_figure)


    def clear(self):
        """ clear plot """
        self.axes.cla()
        self.conf.ntrace = 0
        self.conf.xlabel = ''
        self.conf.ylabel = ''
        self.conf.title  = ''

    def unzoom_all(self, event=None):
        """ zoom out full data range """
        if len(self.conf.zoom_lims) > 0:
            self.conf.zoom_lims = [self.conf.zoom_lims[0]]
        self.user_lims[self.axes] = 4*[None]
        self.unzoom(event)

    def unzoom(self, event=None, set_bounds=True):
        """ zoom out 1 level, or to full data range """
        lims = None
        if len(self.conf.zoom_lims) > 1:
            lims = self.conf.zoom_lims.pop()
        ax = self.axes
        if lims is None: # auto scale
            self.conf.zoom_lims = [None]
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

    def set_title(self, s, delay_draw=False):
        "set plot title"
        self.conf.relabel(title=s, delay_draw=delay_draw)

    def set_xlabel(self, s, delay_draw=False):
        "set plot xlabel"
        self.conf.relabel(xlabel=s, delay_draw=delay_draw)

    def set_ylabel(self, s, delay_draw=False):
        "set plot ylabel"
        self.conf.relabel(ylabel=s, delay_draw=delay_draw)

    def set_y2label(self, s, delay_draw=False):
        "set plot ylabel"
        self.conf.relabel(y2label=s, delay_draw=delay_draw)

    def write_message(self, s, panel=0):
        """ write message to message handler
        (possibly going to GUI statusbar)"""
        self.messenger(s, panel=panel)

    def save_figure(self, event=None, transparent=False, dpi=600):
        """ save figure image to file"""
        file_choices = "PNG (*.png)|*.png|SVG (*.svg)|*.svg|PDF (*.pdf)|*.pdf"
        try:
            ofile = self.conf.title.strip()
        except:
            ofile = 'Image'
        if len(ofile) > 64:
            ofile = ofile[:63].strip()
        if len(ofile) < 1:
            ofile = 'plot'

        for c in ' :";|/\\': # "
            ofile = ofile.replace(c, '_')

        ofile = ofile + '.png'
        orig_dir = os.path.abspath(get_cwd())
        dlg = wx.FileDialog(self, message='Save Plot Figure as...',
                            defaultDir=orig_dir,
                            defaultFile=ofile,
                            wildcard=file_choices,
                            style=wx.FD_SAVE|wx.FD_CHANGE_DIR)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if hasattr(self, 'fig'):
                self.fig.savefig(path, transparent=transparent, dpi=dpi)
            else:
                self.canvas.print_figure(path, transparent=transparent, dpi=dpi)
            if (path.find(self.launch_dir) ==  0):
                path = path[len(self.launch_dir)+1:]
            self.write_message('Saved plot to %s' % path)
        os.chdir(orig_dir)

    def set_bg(self, color= None):
        if color is None:
            color = '#FBFBFB'
        self.fig.set_facecolor(color)

    def configure(self, evt=None, **kws):
        pass

    ## cursor modes:
    def add_cursor_mode(self, modename, leftdown=None, leftup=None,
                        rightdown=None, rightup=None, motion=None,
                        keyevent=None):

        d = {'leftdown':  leftdown,     'leftup':    leftup,
             'rightdown': rightdown,    'rightup':   rightup,
             'motion':    motion,       'keyevent':  keyevent}
        self.cursor_modes[modename]  = d

    def cursor_mode_action(self,  eventname, **kws):
        mode = self.cursor_mode
        if mode not in self.cursor_modes:
            return
        if hasattr(self.cursor_modes[mode][eventname], '__call__'):
            self.cursor_modes[mode][eventname](**kws)

    ####
    ## GUI events
    ####
    def toggle_legend(self, evt=None, show=None):
        pass

    def toggle_grid(self, evt=None, show=None):
        pass

    def lassoHandler(self, vertices):
        try:
            del self.lasso
            self.canvas.draw_idle()
        except:
            pass

    def zoom_OK(self, start, stop):
        return True

    def report_leftdown(self, event=None):
        if event is None:
            return
        self.write_message("%g, %g" % (event.xdata, event.ydata), panel=1)

    def onLeftDown(self, event=None):
        """ left button down: report x,y coords, start zooming mode"""
        if event is None:
            return
        self.cursor_mode_action('leftdown', event=event)
        self.ForwardEvent(event=event.guiEvent)

    def onLeftUp(self, event=None):
        """ left button up"""
        if event is None:
            return
        self.cursor_mode_action('leftup', event=event)
        self.canvas.draw_idle()
        self.canvas.draw()
        self.ForwardEvent(event=event.guiEvent)

    def ForwardEvent(self, event=None):
        """finish wx event, forward it to other wx objects"""
        if event is not None:
            event.Skip()
            if self.HasCapture():
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
        self.cursor_mode_action('rightdown', event=event)
        self.ForwardEvent(event=event.guiEvent)

    def onRightUp(self, event=None):
        """ right button up: put back to cursor mode"""
        if event is None:
            return
        self.cursor_mode_action('rightup', event=event)
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

        if x < 1: x = 1

        span = self.axes.xaxis.get_view_interval()
        tmin = max(1.0, span[0])
        tmax = max(2.0, span[1])
        tmin = time.mktime(dates.num2date(tmin).timetuple())
        tmax = time.mktime(dates.num2date(tmax).timetuple())
        nhours = (tmax - tmin)/3600.0
        fmt = "%m/%d"
        if nhours < 0.1:
            fmt = "%H:%M\n%Ssec"
        elif nhours < 4:
            fmt = "%m/%d\n%H:%M"
        elif nhours < 24*8:
            fmt = "%m/%d\n%H:%M"
        try:
            return time.strftime(fmt, dates.num2date(x).timetuple())
        except:
            return "?"

    def reset_formats(self):
        self._xfmt = self._yfmt = self._y2fmt = None

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

    def set_format_str(self, axis):
        try:
            ticks = axis.get_major_locator()()
        except:
            ticks = [0, 1]

        if len(ticks) < 2:
            ticks.append(0)
            ticks.append(1)

        step = max(2.e-15, abs(np.diff(ticks).mean()))
        if step > 5e4 or (step < 5.e-4 and ticks.mean() < 5.e-2):
            fmt = '%.2e'
        else:
            ndigs = max(0, 3 - round(log10(step)))
            while ndigs >= 0:
                if np.abs(ticks- np.round(ticks, decimals=ndigs)).max() < 2e-3*step:
                    ndigs -= 1
                else:
                    break
            fmt = '%%1.%df' % min(9, ndigs+1)
        return fmt


    def __format(self, x, type='x'):
        """ home built tick formatter to use with FuncFormatter():
        x     value to be formatted
        type  'x' or 'y' or 'y2' to set which list of ticks to get

        also sets self._yfmt/self._xfmt for statusbar
        """
        fmt, v = '%1.5g','%1.5g'
        if type == 'y':
            ax = self.axes.yaxis
            if self._yfmt is None:
                self._yfmt = self.set_format_str(ax)
            fmt = self._yfmt
        elif type == 'y2' and len(self.fig.get_axes()) > 1:
            ax =  self.fig.get_axes()[1].yaxis
            if self._y2fmt is None:
                self._y2fmt = self.set_format_str(ax)
            fmt = self._y2fmt
        else:
            ax = self.axes.xaxis
            if self._xfmt is None:
                self._xfmt = self.set_format_str(ax)
            fmt = self._xfmt

        s =  fmt % x
        s.strip()
        s = s.replace('+', '')
        while s.find('e0')>0:
            s = s.replace('e0','e')
        if s.endswith('e'):
            s = s[:-1]
        while s.find('-0')>0:
             s = s.replace('-0','-')
        return s

    def __onKeyEvent(self, event=None):
        """ handles key events on canvas
        """
        if event is None:
            return
        key = event.guiEvent.GetKeyCode()
        shift = event.guiEvent.ShiftDown()
        mod  = event.guiEvent.ControlDown()
        if self.is_macosx:
            mod = event.guiEvent.MetaDown()
        if mod:
            if (key < wx.WXK_SPACE or  key > 255):
                return
            ckey = chr(key)
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
            elif ckey == 'X':
                self.conf.zoom_style = 'x only'
            elif ckey == 'Y':
                self.conf.zoom_style = 'y only'
            elif ckey == 'W':
                self.conf.zoom_style = 'both x and y'
        elif key in (wx.WXK_LEFT, wx.WXK_NUMPAD_LEFT):
            self._onPan(direction='left', shift=shift)
        elif key in (wx.WXK_RIGHT, wx.WXK_NUMPAD_RIGHT):
            self._onPan(direction='right', shift=shift)
        elif key in (wx.WXK_UP, wx.WXK_NUMPAD_UP):
            self._onPan(direction='up', shift=shift)
        elif key in (wx.WXK_DOWN, wx.WXK_NUMPAD_DOWN):
            self._onPan(direction='down', shift=shift)

    def _onPan(self, direction=None, shift=False):
        if direction not in ('left', 'right', 'up', 'down'):
            return

        axes = self.fig.get_axes()[0]
        try:
            if len(self.conf.zoom_lims) > 0:
                x0, x1, y0, y1 = self.conf.zoom_lims[-1][axes]
            else:
                x0, x1 = axes.get_xlim()
                y0, y1 = axes.get_ylim()
        except:
            return

        step = 0.10 if shift else 0.02
        if direction in ('left', 'right'):
            step *= abs(x1 - x0) * {'right': 1, 'left': -1}[direction]
            x0, x1 = x0+step, x1+step
        elif direction in ('up', 'down'):
            step *= abs(y1 - y0) * {'up': 1, 'down': -1}[direction]
            y0, y1 = y0+step, y1+step

        self.conf.zoom_lims.append({axes: [x0, x1, y0, y1]})
        self.set_viewlimits()
        self.canvas.draw()

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
                    (3, 'button_press_event'):   self.onRightDown}

        handle_event = handlers.get((button, event.name), None)
        if hasattr(handle_event, '__call__'):
            handle_event(event)
        event.guiEvent.Skip()


    def __onMouseMotionEvent(self, event=None):
        """Draw a cursor over the axes"""
        if event is None:
            return
        self.cursor_mode_action('motion', event=event)


    def gui_repaint(self, drawDC=None):
        """
        Update the displayed image on the GUI canvas, using the supplied
        wx.PaintDC device context.

        The 'WXAgg' backend sets origin accordingly.
        """
        if not drawDC:
            drawDC = wx.ClientDC(self.canvas)

        bmp = self.canvas.bitmap
        if (wx.Platform == '__WXMSW__'
            and isinstance(self.canvas.figure._cachedRenderer, RendererWx)):
            bmp = bmp.ConvertToImage().ConvertToBitmap()

        drawDC.DrawBitmap(bmp, 0, 0)
        if self.rbbox is not None:
            drawDC.SetLogicalFunction(wx.XOR)
            drawDC.SetBrush(wx.Brush('Black', wx.BRUSHSTYLE_TRANSPARENT))
            drawDC.SetPen(wx.Pen('WHITE', 2, wx.SOLID))
            drawDC.DrawRectangle(*self.rbbox)

    def zoom_motion(self, event=None):
        """motion event handler for zoom mode"""
        try:
            x, y  = event.x, event.y
        except:
            return
        self.report_motion(event=event)
        if self.zoom_ini is None:
            return
        ini_x, ini_y, ini_xd, ini_yd = self.zoom_ini
        if event.xdata is not None:
            self.x_lastmove = event.xdata
        if event.ydata is not None:
            self.y_lastmove = event.ydata
        x0     = min(x, ini_x)
        ymax   = max(y, ini_y)
        width  = abs(x-ini_x)
        height = abs(y-ini_y)
        y0     = self.canvas.figure.bbox.height - ymax
        limits = self.canvas.figure.axes[0].bbox.corners()
        if self.conf.zoom_style.startswith('x'):
            height = int(round(limits[3][1] - limits[0][1]))
            y0 = 1 + self.canvas.GetSize()[1] - int(round(limits[1][1]))

        elif self.conf.zoom_style.startswith('y'):
            width = 1 + int(round(limits[2][0] - limits[0][0]))
            x0 = 1 + int(round(limits[0][0]))

        self.rbbox = (int(x0), int(y0), int(width), int(height))
        self.canvas.Refresh()


    def zoom_leftdown(self, event=None):
        """leftdown event handler for zoom mode"""
        self.x_lastmove, self.y_lastmove = None, None
        self.zoom_ini = (event.x, event.y, event.xdata, event.ydata)
        self.report_leftdown(event=event)

    def zoom_leftup(self, event=None):
        """leftup event handler for zoom mode"""
        if self.zoom_ini is None:
            return
        self.canvas._rubberband_rect = None

        ini_x, ini_y, ini_xd, ini_yd = self.zoom_ini
        try:
            dx = abs(ini_x - event.x)
            dy = abs(ini_y - event.y)
        except:
            dx, dy = 0, 0
        t0 = time.time()
        self.rbbox = None
        self.zoom_ini = None
        if (dx > 3) and (dy > 3) and (t0-self.mouse_uptime)>0.1:
            self.mouse_uptime = t0
            zlims, tlims = {}, {}
            for ax in self.fig.get_axes():
                xmin, xmax = ax.get_xlim()
                ymin, ymax = ax.get_ylim()
                zlims[ax] = [xmin, xmax, ymin, ymax]
            if len(self.conf.zoom_lims) == 0:
                self.conf.zoom_lims.append(zlims)
            # for multiple axes, we first collect all the new limits, and
            # only then apply them
            for ax in self.fig.get_axes():
                ax_inv = ax.transData.inverted
                try:
                    x1, y1 = ax_inv().transform((event.x, event.y))
                except:
                    x1, y1 = self.x_lastmove, self.y_lastmove
                try:
                    x0, y0 = ax_inv().transform((ini_x, ini_y))
                except:
                    x0, y0 = ini_xd, ini_yd

                tlims[ax] = [min(x0, x1), max(x0, x1),
                             min(y0, y1), max(y0, y1)]
                if self.conf.zoom_style.startswith('x'):
                    tlims[ax][2:] = [ymin, ymax]
                elif self.conf.zoom_style.startswith('y'):
                    tlims[ax][:2] = [xmin, xmax]

            self.conf.zoom_lims.append(tlims)
            # now apply limits:
            self.set_viewlimits()

            if callable(self.zoom_callback):
                self.zoom_callback(wid=self.GetId(), limits=tlims[ax])


    def lasso_motion(self, event=None):
        """motion event handler for lasso mode"""
        self.report_motion(event=event)

    def lasso_leftdown(self, event=None):
        """leftdown event handler for lasso mode"""
        try:
            self.report_leftdown(event=event)
        except:
            return

        if event.inaxes:
            # set lasso color
            color='goldenrod'
            cmap = getattr(self.conf, 'cmap', None)
            if isinstance(cmap, dict):
                cmap = cmap['int']
            try:
                if cmap is not None:
                    rgb = (int(i*255)^255 for i in cmap._lut[0][:3])
                    color = '#%02x%02x%02x' % tuple(rgb)
            except:
                pass
            self.lasso = Lasso(event.inaxes, (event.xdata, event.ydata),
                               self.lassoHandler)
            self.lasso.line.set_color(color)

    def lasso_leftup(self, event=None):
        """leftup event handler for lasso mode"""
        pass

    def report_motion(self, event=None):
        if event.inaxes is None:
            return

        fmt = "X,Y= %g, %g"
        x, y  = event.xdata, event.ydata
        if len(self.fig.get_axes()) > 1:
            try:
                x, y = self.axes.transData.inverted().transform((event.x, event.y))
            except:
                pass
        if self.motion_sbar is None:
            try:
                self.motion_sbar = self.nstatusbar-1
            except AttributeError:
                self.motion_sbar = 1

        self.write_message(fmt % (x, y), panel=self.motion_sbar)

    def Print(self, event=None, **kw):
        self.printer.Print(event=event, **kw)

    def PrintPreview(self, event=None, **kw):
        self.printer.Preview(event=event, **kw)

    def PrintSetup(self, event=None, **kw):
        self.printer.Setup(event=event, **kw)
