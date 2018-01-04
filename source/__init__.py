import wx
import os
import sys
import wx.lib.agw.advancedsplash as AS

from graph_frame import GraphFrame
from serial_reader import SerialReader

SPLASH_FN = "splashscreen.png"
SPLASH_TIME = 3000

if __name__ == "__main__":
    app = wx.App(0)
    bitmap = wx.Bitmap(SPLASH_FN, wx.BITMAP_TYPE_PNG)
    shadow = wx.WHITE
    splash = AS.AdvancedSplash(None, bitmap=bitmap, timeout=SPLASH_TIME,
                               agwStyle=AS.AS_TIMEOUT |
                               AS.AS_CENTER_ON_PARENT |
                               AS.AS_SHADOW_BITMAP,
                               shadowcolour=shadow)
    
    data_source = SerialReader()  
    app.frame = GraphFrame(data_source)
    app.frame.Show()
    app.MainLoop()
