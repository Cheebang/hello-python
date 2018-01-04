import csv
import datetime
import serial.tools.list_ports

class SerialReader:
    def __init__(self):
        self.real_probe = True

        commports = serial.tools.list_ports.comports()
        self.ports = []
        for p in commports:
            self.ports.append(p.device)
    
        self.port = self.ports[0]
        self.sers = []

    def start(self):
        for p in self.ports:
            self.sers.append(serial.Serial(p, baudrate=9600, timeout=1))
    
    def stop(self):
        for s in self.sers:
            s.close()
            
        self.sers = []
   
    def set_port(self, port):
        self.port = port
        self.ser.close()

    def parse_values(self, values):
        it = iter(values)
        result = dict(zip(it, it))
        for k in result.keys():
            result[k] = float(result[k])
        return result

    def next(self):
        if (self.real_probe):
            result = {}
            for i in range(0, len(self.sers)):
                ser = self.sers[i]
                reader = csv.reader([ser.readline()])
                values = reader.next()
                
                if (len(values) >= 5):
                    result['con'+str(i)] = float(values[5])
            return datetime.datetime.now(), result
        else:
            reader = csv.reader([self.ser.readline()])
            values = reader.next()
            data_list = []
            for raw_val in values:
                data_list.append(raw_val)
            return datetime.datetime.now(), self.parse_values(data_list)
