import wx

class ContourDialog(wx.Dialog):
    """Configure Contour Plots"""
    msg = '''Configure Contours'''
    def __init__(self, parent=None, conf=None,
                 title='Contour Configuration',
                 size=wx.DefaultSize, pos=wx.DefaultPosition,
                 style=wx.DEFAULT_DIALOG_STYLE):

        if conf is None:
            return
        self.conf = conf

        wx.Dialog.__init__(self, parent, wx.ID_ANY, title=title)

        sizer = wx.GridBagSizer(7, 3)
        nlevels = '%i' % conf.ncontour_levels
        label = wx.StaticText(self, -1, "# Levels:")
        self.ncontour = wx.TextCtrl(self, -1, nlevels, size=(80,-1))
        self.showlabels  = wx.CheckBox(self,-1, 'Show Labels?', (-1, -1), (-1, -1))
        self.showlabels.SetValue(self.conf.contour_labels)

        sizer.Add(label,           (0, 0), (1, 1), wx.ALIGN_LEFT|wx.ALL, 2)
        sizer.Add(self.ncontour,   (0, 1), (1, 1), wx.ALIGN_LEFT|wx.ALL, 2)
        sizer.Add(self.showlabels, (1, 0), (1, 2), wx.ALIGN_LEFT|wx.ALL, 2)

        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, (2, 0), (1, 2),
                  wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 2)

        btnsizer = wx.StdDialogButtonSizer()

        nobtn = wx.Button(self, wx.ID_CANCEL)
        okbtn = wx.Button(self, wx.ID_OK)
        okbtn.SetDefault()

        btnsizer.AddButton(okbtn)
        btnsizer.AddButton(nobtn)
        btnsizer.Realize()

        sizer.Add(btnsizer, (3, 0), (1, 2), wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)


    def GetResponse(self, master=None, gname=None, ynorm=True):
        self.Raise()
        if self.ShowModal() == wx.ID_OK:
            self.conf.ncontour_levels = int(self.ncontour.GetValue())
            self.conf.contour_labels = self.showlabels.IsChecked()
        return
