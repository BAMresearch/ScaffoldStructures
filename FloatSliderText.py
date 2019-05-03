import wx
import FloatSlider

class FloatSliderText(wx.Panel):
    def __init__(self, parent, id, caption, value, Min, Max, res):
        wx.Panel.__init__(self, parent, id)
        self.caption = caption
        self.min = Min
        self.max = Max
        self.value = value
        self.res = res
        self.build_gui()
        self.__bind_events_wx()
        self.Show()

    def build_gui(self):
        self.sliderctrl = FloatSlider.FloatSlider(self, -1, self.value,
                                                  self.min, self.max, self.res)
        self.textbox = wx.TextCtrl(self, -1, "%.2f" % self.value, style=wx.TE_READONLY)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.StaticText(self, -1, self.caption) , 0, wx.EXPAND)
        sizer.Add(self.sliderctrl, 1, wx.EXPAND)
        sizer.Add(self.textbox, 0, wx.EXPAND)
        self.SetSizer(sizer)

        self.Layout()
        self.Update()
        self.SetAutoLayout(1)

    def __bind_events_wx(self):
        self.sliderctrl.Bind(wx.EVT_SCROLL, self.do_slider)
        self.Bind(wx.EVT_SIZE, self.onsize)

    def onsize(self, evt):
        evt.Skip()

    def do_slider(self, evt):
        self.value =  self.sliderctrl.GetValue()
        self.textbox.SetValue("%.2f" % self.value)
        evt.Skip()

    def GetValue(self):
        return self.value
