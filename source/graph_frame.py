import os
import wx
import csv
import matplotlib

from serial_data_holder import SerialDataHolder
from plot import Plot

matplotlib.use('WXAgg')

# Those import have to be after setting matplotlib backend.
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas

REFRESH_INTERVAL_MS = 100
DPI = 200
COLORS = ['red', 'blue', 'lime', 'orange', 'purple', 'magenta', 'cyan', 'brown']

class GraphFrame(wx.Frame):
    title = 'Furmtech'

    def __init__(self, data_source):
        wx.Frame.__init__(self, None, -1, self.title)

        self.data_source = data_source
        self.serial_data = SerialDataHolder()
        self.paused = True

        self.color_offset = 0
        self.line_width = 1
        
        self.plot = Plot()

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
        csvwriter.writerow(["Timestamps"] + self.serial_data.data.keys())
        #for each timestamp, write out a new line with that timestamp and all data logs at that time
        for i in range(0, len(self.serial_data.timestamps)):
            csvwriter.writerow([self.serial_data.timestamps[i]] + [self.serial_data.data[key][i] for key in self.serial_data.data.keys()])

    def on_plot_clear(self, event):
        self.serial_data = SerialDataHolder()
        #self.plot.plot_initialize(self.serial_data.data)
        self.canvas.draw()

    def create_main_panel(self):
        self.panel = wx.Panel(self)

        self.plot.plot_initialize(self.serial_data.data)
        self.canvas = FigCanvas(self.panel, -1, self.plot.figure)

        self.setup_pause_button()
        self.setup_export_button()
        self.setup_clear_button()

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
        self.hbox1.Add(self.clear_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(20)

    def setup_hbox2(self):
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2.AddSpacer(24)

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

    def setup_clear_button(self):
        self.clear_button = wx.Button(self.panel, -1, "Clear")
        self.Bind(wx.EVT_BUTTON, self.on_plot_clear, self.clear_button)

    def create_status_bar(self):
        self.status_bar = self.CreateStatusBar()

    def on_pause_button_click(self, event):
        self.paused = not self.paused
        if not self.paused:
            self.data_source.start()
        else:
            self.data_source.stop()

    def on_pause_button_update(self, event):
        label = "Start" if self.paused else "Stop"
        self.pause_button.SetLabel(label)

    def on_comm_choice(self, event): 
        self.data_source.set_port(self.comm_choice.GetString(self.comm_choice.GetSelection()))

    def on_grid_visibility_control_box_toggle(self, event):
        self.draw_plot()

    def on_xlabels_visibility_check_box_toggle(self, event):
        self.draw_plot()

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

    def on_plot_redraw(self, data):
        if not self.paused:
            self.serial_data.add(self.data_source.next())
            self.draw_plot()
    
    def draw_plot(self):
        if not self.paused:
            self.plot.draw_plot(self.serial_data.data)

        self.canvas.draw()
