import numpy as np
import matplotlib
import matplotlib.colors as colors
from matplotlib.figure import Figure

matplotlib.use('WXAgg')

# Those import have to be after setting matplotlib backend.
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

DPI = 200
COLORS = ['red', 'blue', 'lime', 'orange', 'purple', 'magenta', 'cyan', 'brown']

class Plot():
    
    def __init__(self):
        self.x_size = 0
        self.plot_data = []
        self.color_offset = 0
        self.line_width = 1

    def plot_initialize(self, data):
        self.figure = Figure((5.0, 5.0), dpi=DPI)

        self.axes = self.figure.add_subplot(111)
        self.axes.set_facecolor('white')
        self.axes.set_title('Serial Data', size=12)
        self.axes.yaxis.grid(True)

        plt.setp(self.axes.get_xticklabels(), fontsize=8)
        plt.setp(self.axes.get_yticklabels(), fontsize=8)

        self.plot_latest_values(data)
   
    def plot_latest_values(self, data):
        i = 0
        for key in data.keys():
            if len(self.plot_data) > i:
                self.plot_data[i] = self.plot_values_for_key(i, key)
            else:
                self.plot_data.append(self.plot_values_for_key(i, key))
            i += 1

    def plot_values_for_key(self, i, key):
        return self.axes.plot(key, linewidth=self.line_width, color=colors.cnames[COLORS[self.color_offset + i]])[0]

    def draw_plot(self, data):
        self.x_size += 1
        x_min, x_max = self.get_plot_xrange()
        y_min, y_max = self.get_plot_yrange(data)

        self.axes.set_xbound(lower=x_min, upper=x_max)
        self.axes.set_ybound(lower=y_min, upper=y_max)

        legend_patch = []

        i = 0
        for key in data.keys():
            legend_patch.append(mpatches.Patch(color=COLORS[i], label=key))
            if len(self.plot_data) > i:
                self.plot_data[i].set_xdata(np.arange(len(data[key])))
                self.plot_data[i].set_ydata(np.array(data[key]))
            else:
                self.plot_data.append(self.plot_values_for_key(i, data[key]))
            i += 1       

        self.axes.legend(legend_patch, data.keys())

    def get_plot_xrange(self):
        x_max = max(self.x_size, 10)
        #x_min = x_max - 50
        x_min = 0

        return x_min, x_max

    def get_plot_yrange(self, data):       
        smallest = [0]
        biggest = [1]
        
        for key in data.keys():
            smallest.append(min(data[key]))
            biggest.append(max(data[key]))

        y_min = round(min(smallest)) - 1
  
        y_max = round(max(biggest)) + 1

        return y_min, y_max

