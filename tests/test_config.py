import tempfile
import unittest
from pathlib import Path
from axle.config import AxleConfig

class ConfigTests(unittest.TestCase):
    def test_loads_sections(self):
        content='''[server]
port=9999
[ai]
llm_base_url="http://localhost:1234/"
allow_cloud_fallback=true
[safety]
motion_state="MOVING"
'''
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"axle.toml";p.write_text(content,encoding="utf-8");c=AxleConfig.from_toml(p)
        self.assertEqual(c.port,9999)
        self.assertEqual(c.llm_base_url,"http://localhost:1234")
        self.assertTrue(c.allow_cloud_fallback)
        self.assertEqual(c.motion_state,"moving")

if __name__=="__main__":
    unittest.main()
