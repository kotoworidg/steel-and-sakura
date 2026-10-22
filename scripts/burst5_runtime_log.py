"""Bounded stdin-to-tracked-file bridge used only by the experimental host."""
from pathlib import Path
import json,sys
from tracked_files import ROOT,write_text
p=Path(sys.argv[1]).resolve();allowed=ROOT/'build/burst5/runtime'
if not p.is_relative_to(allowed) or p.suffix!='.json' or p.exists():raise ValueError('Runtime logs must be new JSON files in the burst5 session directory')
s=sys.stdin.read(8*1024*1024+1)
if len(s)>8*1024*1024:raise ValueError('Runtime log bound')
json.loads(s)
print(write_text(p,s+'\n','Burst5 runtime batch; timestamped pre-write transaction'))
