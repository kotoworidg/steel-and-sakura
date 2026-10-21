"""Synthetic animation-format checks; no copyrighted fixture data required."""
import struct,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from inspect_anim_events import read_anim,event_bytes
def fixture():
 name="Weapon1".encode("utf-16le")
 return (struct.pack("<IffI",1,20.0,1.0,1)+struct.pack("<H",7)+name+
         struct.pack("<iI",-1,21)+struct.pack("<7f",0,0,0,0,0,0,1)*21+
         event_bytes([[["FIRE_TIME","0.05"],["FIRE_POSITION","0","0","0"]]]))
class AnimEventTests(unittest.TestCase):
 def test_roundtrip(self):
  raw=fixture();a=read_anim(raw)
  self.assertEqual(raw,raw[:a["event_offset"]]+event_bytes(a["event_blocks"]))
  self.assertEqual(a["frame_count"],21)
 def test_numbered_second_marker_preserves_frames(self):
  raw=fixture();a=read_anim(raw);blocks=a["event_blocks"]
  blocks[0].extend([["FIRE_TIME_2","0.35"],["FIRE_POSITION_2","0","0","0"]])
  result=raw[:a["event_offset"]]+event_bytes(blocks);b=read_anim(result)
  self.assertEqual(result[:b["event_offset"]],raw[:a["event_offset"]])
  self.assertEqual(b["event_blocks"][0][2],["FIRE_TIME_2","0.35"])
 def test_truncated_file_rejected(self):
  with self.assertRaises((ValueError,struct.error)):read_anim(fixture()[:-1])
 def test_wrong_version_rejected(self):
  raw=bytearray(fixture());struct.pack_into("<I",raw,0,8)
  with self.assertRaises(ValueError):read_anim(raw)
if __name__=="__main__":unittest.main()
