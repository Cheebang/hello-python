import argparse
import os
import wx
import csv
import numpy as np
import matplotlib
import matplotlib.colors as colors
from matplotlib.figure import Figure
from serial_reader import SerialReader
from serial_data_holder import SerialDataHolder

# The recommended way to use wx with mpl is with the WXAgg backend.
matplotlib.use('WXAgg')

# Those import have to be after setting matplotlib backend.
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas
import matplotlib.pyplot as plt

REFRESH_INTERVAL_MS = 500
DPI = 200

class GraphFrame(wx.Frame):
    title = 'Demo: dynamic matplotlib graph'

    def __init__(self, data_source):
        wx.Frame.__init__(self, None, -1, self.title)

        self.data_source = data_source
        self.data = SerialDataHolder()
        self.paused = True
        self.x_size = 0

        self.plot_data = []
        self.color_offset = 1
        self.line_width = 1

        self.comm_ports = self.data_source.ports

        self.create_status_bar()
        self.create_main_panel()

        self.redraw_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_plot_redraw, self.redraw_timer)
        self.redraw_timer.Start(REFRESH_INTERVAL_MS)
        self.Maximize(True)

    def create_menu(self):
        self.menu_bar = wx.MenuBar()
        menu = wx.Menu()

        save_plot_entry = menu.Append(
            id=-1,
            item="&Save plot\tCtrl-S",
            helpString="Save plot to file"
        )
        self.Bind(wx.EVT_MENU, self.on_plot_save, save_plot_entry)

        self.setup_save_plot(menu)
        self.setup_export_plot(menu)

        self.menu_bar.Append(menu, "&File")
        self.SetMenuBar(self.menu_bar)

    def setup_save_plot(self, menu):
        menu.AppendSeparator()
        export_plot_entry = menu.Append(
            id=-1, 
            item="&Export plot\tCtrl-E", 
            helpString="Export plot data to CSV file")
        self.Bind(wx.EVT_MENU, self.on_plot_export, export_plot_entry)

    def on_plot_save(self, event):
        file_choices = "PNG (*.png)|*.png"

        dlg = wx.FileDialog(
            self,
            message="Save plot as...",
            defaultDir=os.getcwd(),
            defaultFile="plot.png",
            wildcard=file_choices,
            style=wx.FD_SAVE
        )

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.canvas.print_figure(path, dpi=DPI)
            self.flash_status_message("Saved to {}".format(path))

    def on_plot_export(self, event):
        file_choices = "CSV (*.csv)|*.csv"

        dlg = wx.FileDialog(
            self,
            message="Export plot data as...",
            defaultDir=os.getcwd(),
            defaultFile="serial_data.csv",
            wildcard=file_choices,
            style=wx.FD_SAVE
        )

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.export_csv_file(path)
            self.flash_status_message("Saved to {}".format(path))

    def export_csv_file(self, path):
        csvfile = open(path, 'wb')
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(["Timestamps"] + self.data.timestamps)
        for key in self.data.data.keys():
            csvwriter.writerow([key] + self.data.data[key])

    def create_main_panel(self):
        self.panel = wx.Panel(self)

        self.plot_initialize()
        self.canvas = FigCanvas(self.panel, -1, self.figure)

        self.setup_pause_button()
        self.setup_export_button()

        self.setup_grid_visibility_checkbox()
        self.setup_x_axis_visibility_checkbox()

        self.setup_hbox1()
        self.setup_hbox2()
        self.setup_vbox()

        self.panel.SetSizer(self.vbox)
        self.vbox.Fit(self)

    def setup_grid_visibility_checkbox(self):
        self.grid_visibility_check_box = wx.CheckBox(
            self.panel, -1, 
            "Show Grid", 
            style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.on_grid_visibility_control_box_toggle, self.grid_visibility_check_box)
        self.grid_visibility_check_box.SetValue(True)

    def setup_x_axis_visibility_checkbox(self):
        self.xlabels_visibility_check_box = wx.CheckBox(
            self.panel, -1, 
            "Show X labels", 
            style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.on_xlabels_visibility_check_box_toggle, self.xlabels_visibility_check_box)
        self.xlabels_visibility_check_box.SetValue(True)

    def setup_hbox1(self):
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)

        self.comm_choice = wx.Choice(self.panel, choices = self.comm_ports)
        self.comm_choice.SetStringSelection(self.data_source.port)
        self.comm_choice.Bind(wx.EVT_CHOICE, self.on_comm_choice)

        self.hbox1.Add(self.comm_choice, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(20)
        self.hbox1.Add(self.pause_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(20)
        self.hbox1.Add(self.export_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(20)
        self.hbox1.Add(self.grid_visibility_check_box, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(10)
        self.hbox1.Add(self.xlabels_visibility_check_box, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(10)
        self.legend_label = wx.StaticText(self.panel, -1, "Legend: ", style=wx.ALIGN_RIGHT)
        self.hbox1.Add(self.legend_label, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

    def setup_hbox2(self):
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
#         self.hbox2.Add(self.xmin_control_box, border=5, flag=wx.ALL)
#         self.hbox2.Add(self.xmax_control_box, border=5, flag=wx.ALL)
        self.hbox2.AddSpacer(24)
#         self.hbox2.Add(self.ymin_control_box, border=5, flag=wx.ALL)
#         self.hbox2.Add(self.ymax_control_box, border=5, flag=wx.ALL)

    def setup_vbox(self):
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.GROW)
        self.vbox.Add(self.hbox1, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox2, 0, flag=wx.ALIGN_LEFT | wx.TOP)

    def setup_pause_button(self):
        self.pause_button = wx.Button(self.panel, -1, "Pause")
        self.Bind(wx.EVT_BUTTON, self.on_pause_button_click, self.pause_button)
        self.Bind(wx.EVT_UPDATE_UI, self.on_pause_button_update, self.pause_button)

    def setup_export_button(self):
        self.export_button = wx.Button(self.panel, -1, "Export")
        self.Bind(wx.EVT_BUTTON, self.on_plot_export, self.export_button)

    def create_status_bar(self):
        self.status_bar = self.CreateStatusBar()

    def plot_latest_values(self):
        i = 0
        for key in self.data.data.keys():
            if len(self.plot_data) > i:
                self.plot_data[i] = self.plot_values_for_key(i, key)
            else:
                self.plot_data.append(self.plot_values_for_key(i, key))
            i += 1

    def plot_values_for_key(self, i, key):
        return self.axes.plot(self.data.data[key], linewidth=self.line_width, color=colors.cnames.values()[self.color_offset + i])[0]

    def plot_initialize(self):
        self.figure = Figure((5.0, 5.0), dpi=DPI)

        self.axes = self.figure.add_subplot(111)
        self.axes.set_facecolor('black')
        self.axes.set_title('Arduino Serial Data', size=12)
        self.axes.grid(color='grey')

        plt.setp(self.axes.get_xticklabels(), fontsize=8)
        plt.setp(self.axes.get_yticklabels(), fontsize=8)

        self.plot_latest_values()

    def get_plot_xrange(self):
        x_max = max(self.x_size, 50)
        x_min = x_max - 50

        return x_min, x_max

    def get_plot_yrange(self):       
        smallest = [0]
        biggest = [20]
        
        for key in self.data.data.keys():
            smallest.append(min(self.data.data[key]))
            biggest.append(max(self.data.data[key]))

        y_min = round(min(smallest)) - 1
  
        y_max = round(max(biggest)) + 1

        return y_min, y_max

    def on_pause_button_click(self, event):
        self.paused = not self.paused

    def on_pause_button_update(self, event):
        label = "Resume" if self.paused else "Pause"
        self.pause_button.SetLabel(label)

    def on_comm_choice(self, event): 
        paused = True
        self.data_source.set_port(self.comm_choice.GetString(self.comm_choice.GetSelection()))

    def on_grid_visibility_control_box_toggle(self, event):
        self.draw_plot()

    def on_xlabels_visibility_check_box_toggle(self, event):
        self.draw_plot()

    def on_plot_redraw(self, event):
        if not self.paused:
            self.data.add(self.data_source.next())
            self.x_size += 1

        self.draw_plot()

    def draw_plot(self):
        x_min, x_max = self.get_plot_xrange()
        y_min, y_max = self.get_plot_yrange()

        self.axes.set_xbound(lower=x_min, upper=x_max)
        self.axes.set_ybound(lower=y_min, upper=y_max)

        self.axes.grid(self.grid_visibility_check_box.IsChecked())

        plt.setp(
            self.axes.get_xticklabels(),
            visible=self.xlabels_visibility_check_box.IsChecked()
        )

        i = 0
        for key in self.data.data.keys():
            if len(self.plot_data) > i:
                self.plot_data[i].set_xdata(np.arange(len(self.data.data[key])))
                self.plot_data[i].set_ydata(np.array(self.data.data[key]))
            else:
                label = wx.StaticText(self.panel, -1, key, style=wx.ALIGN_RIGHT)
                label.SetForegroundColour(colors.cnames.values()[self.color_offset + i])
                self.hbox1.Add(label, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
                self.plot_data.append(self.plot_values_for_key(i, key))
            i += 1

        self.canvas.draw()

    def on_exit(self, event):
        self.Destroy()

    def flash_status_message(self, message, display_time=1500):
        self.status_bar.SetStatusText(message)
        self.message_timer = wx.Timer(self)
        self.Bind(
            wx.EVT_TIMER,
            self.on_flash_status_off,
            self.message_timer
        )
        self.message_timer.Start(display_time, oneShot=True)

    def on_flash_status_off(self, event):
        self.status_bar.SetStatusText('')


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