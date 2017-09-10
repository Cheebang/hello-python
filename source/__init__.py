from graph_frame import GraphFrame
from serial_reader import SerialReader
import argparse
import wx

def parse_script_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("port", help="serial port to be used")
    parser.add_argument("-b", "--baudrate", type=int, help="port baud rate")
    parser.add_argument("-t", "--timeout", type=float, help="port timeout value")

    args = parser.parse_args()

    return {key: val for key, val in vars(args).iteritems() if val is not None}

if __name__ == "__main__":
    data_source = SerialReader()

    app = wx.App()
    app.frame = GraphFrame(data_source)
    app.frame.Show()
    app.MainLoop()