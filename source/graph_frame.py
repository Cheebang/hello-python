import argparse
import os
import wx
import numpy as np
import matplotlib
import matplotlib.colors as colors
from matplotlib.figure import Figure
from bound_control_box import BoundControlBox
from serial_reader import SerialReader

# The recommended way to use wx with mpl is with the WXAgg backend.
matplotlib.use('WXAgg')

# Those import have to be after setting matplotlib backend.
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas  # noqa
import matplotlib.pyplot as plt  # noqa


REFRESH_INTERVAL_MS = 90
DPI = 100

class GraphFrame(wx.Frame):
    """The main frame of the application."""

    title = 'Demo: dynamic matplotlib graph'

    def __init__(self, data_source):
        wx.Frame.__init__(self, None, -1, self.title)

        self.data_source = data_source
        self.data = [self.data_source.next()]
        self.paused = False

        self.plot_data = []
        self.color_offset = 1
        self.line_width = 1

        self.create_menu()
        self.create_status_bar()
        self.create_main_panel()

        self.redraw_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_plot_redraw, self.redraw_timer)
        self.redraw_timer.Start(REFRESH_INTERVAL_MS)

    def create_menu(self):
        self.menu_bar = wx.MenuBar()
        menu = wx.Menu()

        save_plot_entry = menu.Append(
            id=-1,
            item="&Save plot\tCtrl-S",
            helpString="Save plot to file"
        )
        self.Bind(wx.EVT_MENU, self.on_plot_save, save_plot_entry)

        menu.AppendSeparator()

        exit_entry = menu.Append(
            id=-1,
            item="E&xit\tCtrl-X",
            helpString="Exit"
        )
        self.Bind(wx.EVT_MENU, self.on_exit, exit_entry)

        self.menu_bar.Append(menu, "&File")
        self.SetMenuBar(self.menu_bar)

    def create_main_panel(self):
        self.panel = wx.Panel(self)

        self.plot_initialize()
        self.canvas = FigCanvas(self.panel, -1, self.figure)

        self.xmin_control_box = BoundControlBox(self.panel, "X min", 0)
        self.xmax_control_box = BoundControlBox(self.panel, "X max", 50)
        self.ymin_control_box = BoundControlBox(self.panel, "Y min", 0)
        self.ymax_control_box = BoundControlBox(self.panel, "Y max", 100)

        self.pause_button = wx.Button(self.panel, -1, "Pause")
        self.Bind(wx.EVT_BUTTON, self.on_pause_button_click, self.pause_button)
        self.Bind(
            wx.EVT_UPDATE_UI,
            self.on_pause_button_update,
            self.pause_button
        )

        self.grid_visibility_check_box = wx.CheckBox(
            self.panel, -1,
            "Show Grid",
            style=wx.ALIGN_RIGHT
        )
        self.Bind(
            wx.EVT_CHECKBOX,
            self.on_grid_visibility_control_box_toggle,
            self.grid_visibility_check_box
        )
        self.grid_visibility_check_box.SetValue(True)

        self.xlabels_visibility_check_box = wx.CheckBox(
            self.panel, -1,
            "Show X labels",
            style=wx.ALIGN_RIGHT
        )
        self.Bind(
            wx.EVT_CHECKBOX,
            self.on_xlabels_visibility_check_box_toggle,
            self.xlabels_visibility_check_box
        )
        self.xlabels_visibility_check_box.SetValue(True)

        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox1.Add(
            self.pause_button,
            border=5,
            flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL
        )
        self.hbox1.AddSpacer(20)
        self.hbox1.Add(
            self.grid_visibility_check_box,
            border=5,
            flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL
        )
        self.hbox1.AddSpacer(10)
        self.hbox1.Add(
            self.xlabels_visibility_check_box,
            border=5,
            flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL
        )

        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2.Add(self.xmin_control_box, border=5, flag=wx.ALL)
        self.hbox2.Add(self.xmax_control_box, border=5, flag=wx.ALL)
        self.hbox2.AddSpacer(24)
        self.hbox2.Add(self.ymin_control_box, border=5, flag=wx.ALL)
        self.hbox2.Add(self.ymax_control_box, border=5, flag=wx.ALL)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.GROW)
        self.vbox.Add(self.hbox1, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox2, 0, flag=wx.ALIGN_LEFT | wx.TOP)

        self.panel.SetSizer(self.vbox)
        self.vbox.Fit(self)

    def create_status_bar(self):
        self.status_bar = self.CreateStatusBar()

    def plot_initialize(self):
        self.figure = Figure((3.0, 3.0), dpi=DPI)

        self.axes = self.figure.add_subplot(111)
        self.axes.set_axis_bgcolor('black')
        self.axes.set_title('Arduino Serial Data', size=12)
        self.axes.grid(color='grey')

        plt.setp(self.axes.get_xticklabels(), fontsize=8)
        plt.setp(self.axes.get_yticklabels(), fontsize=8)

        # Plot the data and save the reference to the plotted line
        for i in range(len(self.data)):
            if len(self.plot_data) > i:
                self.plot_data[i] = self.axes.plot(
                    self.data[i], linewidth=self.line_width, color=colors.cnames.values()[self.color_offset + i],
                )[0]
            else:
                self.plot_data.append(self.axes.plot(
                    self.data[i], linewidth=self.line_width, color=colors.cnames.values()[self.color_offset + i],
                )[0])

    def get_plot_xrange(self):
        """
        Return minimal and maximal values of plot -xaxis range to be displayed.
        Values of *x_min* and *x_max* by default are determined to show sliding
        window of last 50 elements of data set and they can be manually set.
        """
        x_max = max(len(self.data[0]), 50) if self.xmax_control_box.is_auto() \
            else int(self.xmax_control_box.value)

        x_min = x_max - 50 if self.xmin_control_box.is_auto() \
            else int(self.xmin_control_box.value)

        return x_min, x_max

    def get_plot_yrange(self):
        """
        Return minimal and maximal values of plot y-axis range to be displayed.
        Values of *y_min* and *y_max* are determined by finding minimal and
        maximal values of the data set and adding minimal necessary margin.
        """
        
        smallest = []
        biggest = []
        
        for data in self.data:
            smallest.append(min(data))
            biggest.append(max(data))

        y_min = round(min(smallest)) - 1 if self.ymin_control_box.is_auto() \
            else int(self.ymin_control_box.value)
 
        y_max = round(max(biggest)) + 1 if self.ymax_control_box.is_auto() \
            else int(self.ymax_control_box.value)

        return y_min, y_max

    def draw_plot(self):
        """Redraw the plot."""

        x_min, x_max = self.get_plot_xrange()
        y_min, y_max = self.get_plot_yrange()

        self.axes.set_xbound(lower=x_min, upper=x_max)
        self.axes.set_ybound(lower=y_min, upper=y_max)

        self.axes.grid(self.grid_visibility_check_box.IsChecked())

        # Set x-axis labels visibility
        plt.setp(
            self.axes.get_xticklabels(),
            visible=self.xlabels_visibility_check_box.IsChecked()
        )

        for i in range(len(self.data)):
            if len(self.plot_data) > i:
                self.plot_data[i].set_xdata(np.arange(len(self.data[i])))
                self.plot_data[i].set_ydata(np.array(self.data[i]))
            else:
                self.plot_data.append(self.axes.plot(
                    self.data[i], linewidth=self.line_width, color=colors.cnames.values()[self.color_offset + i],
                )[0])

        self.canvas.draw()

    def on_pause_button_click(self, event):
        self.paused = not self.paused

    def on_pause_button_update(self, event):
        label = "Resume" if self.paused else "Pause"
        self.pause_button.SetLabel(label)

    def on_grid_visibility_control_box_toggle(self, event):
        self.draw_plot()

    def on_xlabels_visibility_check_box_toggle(self, event):
        self.draw_plot()

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

    def on_plot_redraw(self, event):
        """Get new value from data source if necessary and redraw the plot."""
        if not self.paused:
            values = self.data_source.next()
            for i in range(len(values)):
                if (len (self.data) > i):
                    self.data[i].append(values[i])
                else:
                    self.data.append([values[i]])
#             self.data.append(self.data_source.next())

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


def parse_script_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("port", help="serial port to be used")
    parser.add_argument("-b", "--baudrate", type=int, help="port baud rate")
    parser.add_argument("-t", "--timeout", type=float,
                        help="port timeout value")

    args = parser.parse_args()

    return {key: val for key, val in vars(args).iteritems() if val is not None}


if __name__ == "__main__":

    kwargs = parse_script_args()
    data_source = SerialReader()

    app = wx.App()
    app.frame = GraphFrame(data_source)
    app.frame.Show()
    app.MainLoop()