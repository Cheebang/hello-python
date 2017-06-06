import csv
import platform
import serial
import datetime

class SerialReader:
    def __init__(self):
        self.port = self.get_port(str(platform.system()))
        self.ser = serial.Serial(self.port, baudrate=9600, timeout=1)
   
    def get_port(self, platf):
        if platf == 'Windows':
            return "COM3"
        else:
            return "/dev/cu.SLAB_USBtoUART"

    def parse_values(self, values):
        labels = []
        readings = []
        for i in range(len(values)):
            if i % 2 == 0:
                labels.append(values[i])
            else:
                readings.append(float(values[i]))

        return dict(zip(labels, readings))

    def next(self):
        reader = csv.reader([self.ser.readline()])
        values = reader.next()
        data_list = []
        for raw_val in values:
            data_list.append(raw_val)
        return datetime.datetime.now(), self.parse_values(data_list)
