import csv
import datetime
import serial.tools.list_ports

class SerialReader:
    def __init__(self):
        commports = serial.tools.list_ports.comports()
        self.ports = []
        for p in commports:
            self.ports.append(p.device)
    
        self.port = self.ports[0]

    def start(self):
        self.ser = serial.Serial(self.port, baudrate=9600, timeout=1)
    
    def stop(self):
        self.ser.close()
   
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
