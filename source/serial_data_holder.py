class SerialDataHolder:
    def __init__(self):
        self.data = {}
        self.timestamps = []

    def add(self, (timestamp, values)):
        if len(values) > 0:
            self.timestamps.append(timestamp)
            for key in values.keys():
                if (self.data.has_key(key)):
                    self.data[key].append(values[key])
                else:
                    self.data[key] = [values[key]]
