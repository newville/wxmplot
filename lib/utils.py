#!/usr/bin/python
#

import wx
is_wxPhoenix = 'phoenix' in wx.PlatformInfo

import sys
import matplotlib
from matplotlib.path import Path

class Closure:
    """A very simple callback class to emulate a closure (reference to
    a function with arguments) in python.

    This class holds a user-defined function to be executed when the
    class is invoked as a function.  This is useful in many situations,
    especially for 'callbacks' where lambda's are quite enough.
    Many Tkinter 'actions' can use such callbacks.

    >>>def my_action(x=None):
    ...    print('my action: x = ', x)
    >>>c = Closure(my_action,x=1)
    ..... sometime later ...
    >>>c()
     my action: x = 1
    >>>c(x=2)
     my action: x = 2

    based on Command class from J. Grayson's Tkinter book.
    """
    def __init__(self, func=None, *args, **kws):
        self.func  = func
        self.kws   = kws
        self.args  = args

    def __call__(self,  *args, **kws):
        self.kws.update(kws)
        if hasattr(self.func, '__call__'):
            self.args = args
            return self.func(*self.args, **self.kws)

def pack(window, sizer, expand=1.1):
    "simple wxPython pack function"
    tsize =  window.GetSize()
    msize =  window.GetMinSize()
    window.SetSizer(sizer)
    sizer.Fit(window)
    nsize = (10*int(expand*(max(msize[0], tsize[0])/10)),
             10*int(expand*(max(msize[1], tsize[1])/10.)))
    window.SetSize(nsize)



def MenuItem(parent, menu, label='', longtext='', action=None, **kws):
    """Add Item to a Menu, with action
    m = Menu(parent, menu, label, longtext, action=None)
    """
    wid = wx.NewId()
    item = menu.Append(wid, label, longtext, **kws)
    if callable(action):
        parent.Bind(wx.EVT_MENU, action, item)
    return item

class LabelEntry(wx.TextCtrl):
    """
    simple extension of TextCtrl.  Typical usage:
#  entry = LabelEntry(self, -1, value='22',
#                     color='black',
#                     labeltext='X',labelbgcolor='green',
#                     style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
#  row   = wx.BoxSizer(wx.HORIZONTAL)
#  row.Add(entry.label, 1,wx.ALIGN_LEFT|wx.EXPAND)
#  row.Add(entry,    1,wx.ALIGN_LEFT|wx.EXPAND)

    """
    def __init__(self,parent,value,size=-1,
                 font=None, action=None,
                 bgcolor=None, color=None, style=None,
                 labeltext=None, labelsize=-1,
                 labelcolor=None, labelbgcolor=None):

        if style is None:
            style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE|wx.TE_PROCESS_ENTER
        if action is None:
            action = self.GetValue
        self.action = action

        if labeltext is not None:
            self.label = wx.StaticText(parent, -1, labeltext,
                                       size = (labelsize,-1),
                                       style = style)
            if labelcolor:
                self.label.SetForegroundColour(labelcolor)
            if labelbgcolor:
                self.label.SetBackgroundColour(labelbgcolor)
            if font is not None:
                self.label.SetFont(font)

        try:
            value = str(value)
        except:
            value = ' '

        wx.TextCtrl.__init__(self, parent, -1, value,
                             size=(size,-1),style=style)

        self.Bind(wx.EVT_TEXT_ENTER, self.__act)
        self.Bind(wx.EVT_KILL_FOCUS, self.__act)
        if font is not None:
            self.SetFont(font)
        if color:
            self.SetForegroundColour(color)
        if bgcolor:
            self.SetBackgroundColour(bgcolor)

    def __act(self,event=None):
        self.action(event=event)
        val = self.GetValue()
        event.Skip()
        return val

class PrintoutWx(wx.Printout):
    """Simple wrapper around wx Printout class -- all the real work
    here is scaling the matplotlib canvas bitmap to the current
    printer's definition.
    """
    _title_ = 'wxmplot'
    def __init__(self, canvas, width=6.0, margin=0.25,
                 title=None):
        if title is None:
            title = self._title_

        wx.Printout.__init__(self, title=title)
        self.canvas = canvas
        self.width  = width
        self.margin = margin

    def HasPage(self, page):
        return page <= 1

    def GetPageInfo(self):
        return (1, 1, 1, 1)

    def OnPrintPage(self, page):
        self.canvas.draw()

        ppw,pph = self.GetPPIPrinter()      # printer's pixels per in
        pgw,pgh = self.GetPageSizePixels()  # page size in pixels
        if is_wxPhoenix:
            grw, grh = self.canvas.GetSize()
        else:
            grw, grh = self.canvas.GetSizeTuple()
        dc      = self.GetDC()
        dcw,dch = dc.GetSize()

        # save current figure dpi resolution and bg color,
        # so that we can temporarily set them to the dpi of
        # the printer, and the bg color to white
        bgcolor   = self.canvas.figure.get_facecolor()
        fig_dpi   = self.canvas.figure.dpi

        # draw the bitmap, scaled appropriately
        vscale    = float(ppw) / fig_dpi

        # set figure resolution,bg color for printer
        self.canvas.figure.dpi = ppw
        self.canvas.figure.set_facecolor('#FFFFFF')
        self.canvas.bitmap.SetWidth(int(self.canvas.bitmap.GetWidth() * vscale))
        self.canvas.bitmap.SetHeight(int(self.canvas.bitmap.GetHeight()* vscale))

        # occasional crash here?
        try:
            self.canvas.draw()
        except:
            return

        # page may need additional scaling on preview
        page_scale = 1.0
        if self.IsPreview():   page_scale = float(dcw)/pgw

        # get margin in pixels = (margin in in) * (pixels/in)
        top_margin  = int(self.margin * pph * page_scale)
        left_margin = int(self.margin * ppw * page_scale)

        # set scale so that width of output is self.width inches
        # (assuming grw is size of graph in inches....)
        user_scale = (self.width * fig_dpi * page_scale)/float(grw)

        dc.SetDeviceOrigin(left_margin,top_margin)
        dc.SetUserScale(user_scale,user_scale)

        # this cute little number avoid API inconsistencies in wx
        try:
            dc.DrawBitmap(self.canvas.bitmap, 0, 0)
        except:
            pass
        # restore original figure  resolution
        self.canvas.figure.set_facecolor(bgcolor)
        self.canvas.figure.dpi = fig_dpi
        self.canvas.draw()
        return True

class Printer:
    def __init__(self, parent, title=None,
                 canvas=None, width=6.0, margin=0.5):
        """initialize printer settings using wx methods"""

        self.parent = parent
        self.canvas = canvas
        self.pwidth = width
        self.pmargin= margin
        self.title = title
        self.printerData = wx.PrintData()
        self.printerData.SetPaperId(wx.PAPER_LETTER)
        self.printerData.SetPrintMode(wx.PRINT_MODE_PRINTER)
        self.printerPageData= wx.PageSetupDialogData()
        self.printerPageData.SetMarginBottomRight((25,25))
        self.printerPageData.SetMarginTopLeft((25,25))
        self.printerPageData.SetPrintData(self.printerData)

    def Setup(self, event=None):
        """set up figure for printing.  Using the standard wx Printer
        Setup Dialog. """

        if hasattr(self, 'printerData'):
            data = wx.PageSetupDialogData()
            data.SetPrintData(self.printerData)
        else:
            data = wx.PageSetupDialogData()
        data.SetMarginTopLeft( (15, 15) )
        data.SetMarginBottomRight( (15, 15) )

        dlg = wx.PageSetupDialog(None, data)

        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetPageSetupData()
            tl = data.GetMarginTopLeft()
            br = data.GetMarginBottomRight()
        self.printerData = wx.PrintData(data.GetPrintData())
        dlg.Destroy()

    def Preview(self, title=None, event=None):
        """ generate Print Preview with wx Print mechanism"""
        if title is None:
            title = self.title
        if self.canvas is None:
            self.canvas = self.parent.canvas
        po1  = PrintoutWx(self.parent.canvas, title=title,
                          width=self.pwidth,   margin=self.pmargin)
        po2  = PrintoutWx(self.parent.canvas, title=title,
                          width=self.pwidth,   margin=self.pmargin)
        self.preview = wx.PrintPreview(po1,po2,self.printerData)

        if ((is_wxPhoenix and self.preview.IsOk()) or
            (not is_wxPhoenix and self.preview.Ok())):
            self.preview.SetZoom(65)
            frameInst= self.parent
            while not isinstance(frameInst, wx.Frame):
                frameInst= frameInst.GetParent()
            frame = wx.PreviewFrame(self.preview, frameInst, "Preview")
            frame.Initialize()
            frame.SetSize((850,650))
            frame.Centre(wx.BOTH)
            frame.Show(True)

    def Print(self, title=None, event=None):
        """ Print figure using wx Print mechanism"""
        pdd = wx.PrintDialogData()
        pdd.SetPrintData(self.printerData)
        pdd.SetToPage(1)
        printer  = wx.Printer(pdd)
        if title is None:
            title = self.title
        printout = PrintoutWx(self.parent.canvas, title=title,
                              width=self.pwidth, margin=self.pmargin)
        print_ok = printer.Print(self.parent, printout, True)

        if not print_ok and not printer.GetLastError() == wx.PRINTER_CANCELLED:
            wx.MessageBox("""There was a problem printing.
            Perhaps your current printer is not set correctly?""",
                          "Printing", wx.OK)
        printout.Destroy()

def inside_poly(vertices,data):
    if(matplotlib.__version__ < '1.2'):
        mask = points_inside_poly(data, vertices)
    else:
        mask = Path(vertices).contains_points(data)

    return mask
