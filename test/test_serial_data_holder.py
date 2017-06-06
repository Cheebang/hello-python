import unittest
from source.serial_data_holder import SerialDataHolder
import datetime

class TestSerialDataHolder(unittest.TestCase):

    def test_parse_values(self):
        sdh = SerialDataHolder()
        sdh.add(datetime.datetime.now(), {'V1': 100, 'V2': 200, 'V3': 300})
        sdh.add(datetime.datetime.now(), {'V1': 100, 'V2': 200, 'V3': 300})
        self.assertEqual(sdh.data, {'V1': [100, 100], 'V2': [200, 200], 'V3': [300, 300]})

if __name__ == '__main__':
    unittest.main()