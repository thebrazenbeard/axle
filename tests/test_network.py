import unittest
from axle.network import parse_nmcli

class NetworkTests(unittest.TestCase):
    def test_usb_tether(self):
        s=parse_nmcli("enx001122:ethernet:connected:Pixel USB tether\n")
        self.assertTrue(s.has_uplink);self.assertTrue(s.likely_phone_tether)

    def test_hotspot(self):
        s=parse_nmcli("wlan0:wifi:connected:Patrick Hotspot\n")
        self.assertTrue(s.has_uplink);self.assertTrue(s.likely_phone_tether)

    def test_disconnected(self):
        self.assertFalse(parse_nmcli("wlan0:wifi:disconnected:--\n").has_uplink)

    def test_malformed_ignored(self):
        self.assertEqual(len(parse_nmcli("bad\nwlan0:wifi:connected:Cabin\n").links),1)

if __name__=="__main__":
    unittest.main()
