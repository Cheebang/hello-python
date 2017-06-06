import unittest
from source.serial_reader import SerialReader

class TestSerialReader(unittest.TestCase):

    def test_parse_values(self):
        sr = SerialReader()
        result = sr.parse_values(['V1', 100, 'V2', 200])
        self.assertEqual(result, {'V1': 100, 'V2': 200})

if __name__ == '__main__':
    unittest.main()