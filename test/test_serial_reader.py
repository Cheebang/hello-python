import unittest
from source.serial_reader import SerialReader

class TestSerialReader(unittest.TestCase):

    def test_get_port(self):
        sr = SerialReader()
        self.assertEquals("COM3", sr.get_default_port("Windows"))
        self.assertEquals("/dev/cu.SLAB_USBtoUART", sr.get_default_port("Mac"))

    def test_parse_values(self):
        sr = SerialReader()
        result = sr.parse_values(['V1', '100', 'V2', '200', 'V3', 300])
        self.assertEqual(result, {'V1': 100, 'V2': 200, 'V3': 300})
        self.assertEqual(result.values(), [100, 200, 300])

if __name__ == '__main__':
    unittest.main()