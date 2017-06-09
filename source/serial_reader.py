import csv
import platform
import serial
import datetime

class SerialReader:
    def __init__(self):
        self.port = self.get_default_port(str(platform.system()))
        self.ser = serial.Serial(self.port, baudrate=9600, timeout=1)
   
    def get_default_port(self, platf):
        if platf == 'Windows':
            return "COM3"
        else:
            return "/dev/cu.SLAB_USBtoUART"
    
    def set_port(self, port):
        self.port = port
        self.ser.close()
        self.ser = serial.Serial(self.port, baudrate=9600, timeout=1)

    def parse_values(self, values):
        it = iter(values)
        result = dict(zip(it, it))
        for k in result.keys():
            result[k] = float(result[k])
        return result

    def next(self):
        reader = csv.reader([self.ser.readline()])
        values = reader.next()
        data_list = []
        for raw_val in values:
            data_list.append(raw_val)
        return datetime.datetime.now(), self.parse_values(data_list)
