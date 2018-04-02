import wx

class FloatSlider(wx.Slider):

    def __init__(self, parent, id, value, minval, maxval, res,
                 size=wx.DefaultSize, style=wx.SL_HORIZONTAL,
                 name='floatslider'):
        self._value = value
        self._min = minval
        self._max = maxval
        self._res = res
        ival, imin, imax = [round(v/res) for v in (value, minval, maxval)]
        self._islider = super(FloatSlider, self)
        self._islider.__init__(
            parent, id, ival, imin, imax, size=size, style=style, name=name
        )
        self.Bind(wx.EVT_SCROLL, self._OnScroll)

    def _OnScroll(self, event):
        ival = self._islider.GetValue()
        imin = self._islider.GetMin()
        imax = self._islider.GetMax()
        if ival == imin:
            self._value = self._min
        elif ival == imax:
            self._value = self._max
        else:
            self._value = ival * self._res
        event.Skip()
        #print 'OnScroll: value=%f, ival=%d' % (self._value, ival)

    def GetValue(self):
        return self._value

    def GetMin(self):
        return self._min

    def GetMax(self):
        return self._max

    def GetRes(self):
        return self._res

    def SetValue(self, value):
        self._islider.SetValue(round(value/self._res))
        self._value = value

    def SetMin(self, minval):
        self._islider.SetMin(round(minval/self._res))
        self._min = minval

    def SetMax(self, maxval):
        self._islider.SetMax(round(maxval/self._res))
        self._max = maxval

    def SetRes(self, res):
        self._islider.SetRange(round(self._min/res), round(self._max/res))
        self._islider.SetValue(round(self._value/res))
        self._res = res

    def SetRange(self, minval, maxval):
        self._islider.SetRange(round(minval/self._res), round(maxval/self._res))
        self._min = minval
        self._max = maxval
