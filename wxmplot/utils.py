#!/usr/bin/python
#

import sys
from math import log10

from matplotlib.path import Path

import wx
from wx.lib.agw import floatspin as fspin


def fix_filename(s):
    """fix string to be a 'good' filename.
    This may be a more restrictive than the OS, but
    avoids nasty cases."""
    badchars = ' <>:"\'\\\t\r\n/|?*!%$'
    t = s.translate(s.maketrans(badchars, '_'*len(badchars)))
    if t.count('.') > 1:
        for i in range(t.count('.') - 1):
            idot = t.find('.')
            t = "%s_%s" % (t[:idot], t[idot+1:])
    return t

def pack(window, sizer, expand=1.1):
    "simple wxPython pack function"
    tsize =  window.GetSize()
    msize =  window.GetMinSize()
    window.SetSizer(sizer)
    sizer.Fit(window)
    nsize = (10*int(expand*(max(msize[0], tsize[0])/10)),
             10*int(expand*(max(msize[1], tsize[1])/10.)))
    window.SetSize(nsize)


class SimpleText(wx.StaticText):
    "simple static text wrapper"
    def __init__(self, parent, label, minsize=None, font=None, colour=None,
                 bgcolour=None, style=wx.ALIGN_CENTRE, **kws):

        wx.StaticText.__init__(self, parent, -1, label=label, style=style,
                               **kws)
        if minsize is not None:
            self.SetMinSize(minsize)
        if font is not None:
            self.SetFont(font)
        if colour is not None:
            self.SetForegroundColour(colour)
        if bgcolour is not None:
            self.SetBackgroundColour(bgcolour)

def HLine(parent, size=(700, 3)):
    """Simple horizontal line
    h = HLine(parent, size=(700, 3)
    """
    return wx.StaticLine(parent, size=size, style=wx.LI_HORIZONTAL|wx.GROW)

def MenuItem(parent, menu, label='', longtext='', action=None, kind='normal',
             checked=False):
    """Add Item to a Menu, with action
    m = Menu(parent, menu, label, longtext, action=None, kind='normal')
    """
    kinds_map = {'normal': wx.ITEM_NORMAL,
                 'radio': wx.ITEM_RADIO,
                 'check': wx.ITEM_CHECK}
    menu_kind = wx.ITEM_NORMAL
    if kind in kinds_map.values():
        menu_kind = kind
    elif kind in kinds_map:
        menu_kind = kinds_map[kind]

    item = menu.Append(-1, label, longtext, kind=menu_kind)
    if menu_kind == wx.ITEM_CHECK and checked:
        item.Check(True)

    if callable(action):
        parent.Bind(wx.EVT_MENU, action, item)
    return item

class Check(wx.CheckBox):
    """Simple Checkbox
    c = Check(parent, default=True, label=None, **kws)
    kws passed to wx.CheckBox
    """
    def __init__(self, parent, label='', default=True, action=None, **kws):
        wx.CheckBox.__init__(self, parent, -1, label=label, **kws)
        self.SetValue({True: 1, False:0}[default])
        if action is not None:
            self.Bind(wx.EVT_CHECKBOX, action)

class Choice(wx.Choice):
    """Simple Choice with default and bound action
    c = Choice(panel, choices, default=0, action=None, **kws)
    """
    def __init__(self, parent, choices=None, default=0,
                 action=None, **kws):
        if choices is None:
            choices = []
        wx.Choice.__init__(self, parent, -1,  choices=choices, **kws)
        self.Select(default)
        self.Bind(wx.EVT_CHOICE, action)

    def SetChoices(self, choices):
        index = 0
        try:
            current = self.GetStringSelection()
            if current in choices:
                index = choices.index(current)
        except:
            pass
        self.Clear()
        self.AppendItems(choices)
        self.SetStringSelection(choices[index])


def FloatSpin(parent, value=0, action=None, tooltip=None,
                 size=(100, -1), digits=1, increment=1, **kws):
    """FloatSpin with action and tooltip"""
    if value is None:
        value = 0
    fs = fspin.FloatSpin(parent, -1, size=size, value=value,
                         digits=digits, increment=increment, **kws)
    if action is not None:
        fs.Bind(fspin.EVT_FLOATSPIN, action)
    if tooltip is not None:
        fs.SetToolTip(tooltip)
    return fs


def gformat(val, length=11):
    """Format a number with '%g'-like format, except that

        a) the length of the output string will be the requested length.
        b) positive numbers will have a leading blank.
        b) the precision will be as high as possible.
        c) trailing zeros will not be trimmed.

    The precision will typically be length-7.

    Arguments
    ---------
    val       value to be formatted
    length    length of output string

    Returns
    -------
    string of specified length.

    Notes
    ------
     Positive values will have leading blank.

    """
    try:
        expon = int(log10(abs(val)))
    except (OverflowError, ValueError):
        expon = 0
    length = max(length, 7)
    form = 'e'
    prec = length - 7
    if abs(expon) > 99:
        prec -= 1
    elif ((expon > 0 and expon < (prec+4)) or
          (expon <= 0 and -expon < (prec-1))):
        form = 'f'
        prec += 4
        if expon > 0:
            prec -= expon
    fmt = '{0: %i.%i%s}' % (length, prec, form)
    return fmt.format(val)


class LabeledTextCtrl(wx.TextCtrl):
    """
    simple extension of TextCtrl.  Typical usage:

    entry = LabeledTextCtrl(self, -1, value='22',
                            color='black',
                            labeltext='X',labelbgcolor='green',
                            style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
    row  = wx.BoxSizer(wx.HORIZONTAL)
    row.Add(entry.label, 1,wx.ALIGN_LEFT|wx.EXPAND)
    row.Add(entry,    1,wx.ALIGN_LEFT|wx.EXPAND)
    """
    def __init__(self,parent,value,size=(-1, -1),
                 font=None, action=None,
                 bgcolor=None, color=None, style=None,
                 labeltext=None, labelsize=(-1, -1),
                 labelcolor=None, labelbgcolor=None):

        if style is None:
            style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE|wx.TE_PROCESS_ENTER
        if action is None:
            action = self.GetValue
        self.action = action

        if labeltext is not None:
            self.label = wx.StaticText(parent, -1, labeltext,
                                       size=labelsize, style=style)

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

        wx.TextCtrl.__init__(self, parent, -1, value, size=size,
                             style=style)

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
        wx.Printout.__init__(self, title)
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
        grw, grh = self.canvas.GetSize()
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
        try:
            self.canvas.bitmap.SetWidth(int(self.canvas.bitmap.GetWidth() * vscale))
            self.canvas.bitmap.SetHeight(int(self.canvas.bitmap.GetHeight()* vscale))
        except:
            pass

        # occasional crash here?
        try:
            self.canvas.draw()
        except:
            return

        # page may need additional scaling on preview
        page_scale = 1.0
        if self.IsPreview():
            page_scale = float(dcw)/pgw

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
        self.preview = wx.PrintPreview(po1, po2, self.printerData)

        if self.preview.IsOk():
            self.preview.SetZoom(85)
            frameInst= self.parent
            while not isinstance(frameInst, wx.Frame):
                frameInst= frameInst.GetParent()
            frame = wx.PreviewFrame(self.preview, frameInst, "Preview")
            frame.Initialize()
            frame.SetSize((850, 650))
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
    return Path(vertices).contains_points(data)
