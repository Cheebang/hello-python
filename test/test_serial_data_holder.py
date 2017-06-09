import unittest
from source.serial_data_holder import SerialDataHolder
import datetime

class TestSerialDataHolder(unittest.TestCase):

    def test_parse_values(self):
        sdh = SerialDataHolder()
        sdh.add((datetime.datetime.now(), {'V1': 100, 'V2': 200, 'V3': 300}))
        sdh.add((datetime.datetime.now(), {'V1': 150, 'V2': 250, 'V3': 350}))
        self.assertEqual(sdh.data, {'V1': [100, 150], 'V2': [200, 250], 'V3': [300, 350]})

if __name__ == '__main__':
    unittest.main()