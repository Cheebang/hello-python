import wx

class BoundControlBox(wx.Panel):
    """
    A static box with a couple of radio buttons and a text box. Allows to
    switch between an automatic mode and a manual mode with an associated value.
    """
    def __init__(self, parent, label, initial_value):
        wx.Panel.__init__(self, parent)

        self._value = initial_value

        box = wx.StaticBox(self, label=label)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        self.auto_radio_button = wx.RadioButton(
            self, label="Auto", style=wx.RB_GROUP
        )

        self.manual_radio_button = wx.RadioButton(
            self, label="Manual"
        )

        self.textbox = wx.TextCtrl(
            self,
            size=(35, -1),
            value=str(self.value),
            style=wx.TE_PROCESS_ENTER
        )

        self.Bind(
            wx.EVT_UPDATE_UI,
            self.on_radio_button_checked,
            self.textbox
        )

        self.Bind(
            wx.EVT_TEXT_ENTER,
            self.on_text_enter,
            self.textbox
        )

        manual_box = wx.BoxSizer(wx.HORIZONTAL)
        manual_box.Add(
            self.manual_radio_button,
            flag=wx.ALIGN_CENTER_VERTICAL
        )
        manual_box.Add(self.textbox, flag=wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(self.auto_radio_button, 0, wx.ALL, 10)
        sizer.Add(manual_box, 0, wx.ALL, 10)

        self.SetSizer(sizer)
        sizer.Fit(self)

    @property
    def value(self):
        return self._value

    def on_radio_button_checked(self, event):
        self.textbox.Enable(not self.is_auto())

    def on_text_enter(self, event):
        self._value = self.textbox.GetValue()

    def is_auto(self):
        return self.auto_radio_button.GetValue()
