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

[voice]
enabled=true
work_dir="/var/lib/axle/voice"
stt_model="/models/ggml-base.en.bin"
tts_model="en_US-lessac-medium"
capture_command=["pw-record","--rate=16000","{wav}"]
'''
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"axle.toml";p.write_text(content,encoding="utf-8");c=AxleConfig.from_toml(p)
        self.assertEqual(c.port,9999)
        self.assertEqual(c.llm_base_url,"http://localhost:1234")
        self.assertTrue(c.allow_cloud_fallback)
        self.assertEqual(c.motion_state,"moving")
        self.assertTrue(c.voice_enabled)
        self.assertEqual(c.voice_work_dir, "/var/lib/axle/voice")
        self.assertEqual(c.voice_stt_model, "/models/ggml-base.en.bin")
        self.assertEqual(c.voice_tts_model, "en_US-lessac-medium")
        self.assertEqual(c.voice_capture_command, ("pw-record", "--rate=16000", "{wav}"))

if __name__=="__main__":
    unittest.main()
