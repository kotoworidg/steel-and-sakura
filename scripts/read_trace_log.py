"""New immutable JSON batches only; no untracked append or game writes."""
from pathlib import Path
import sys,json
from tracked_files import ROOT,write_text
p=Path(sys.argv[1]).resolve()
if not p.is_relative_to(ROOT/'build/read-trace') or p.suffix!='.json' or p.exists():raise ValueError('invalid fresh trace destination')
s=sys.stdin.read(16*1024*1024+1)
if len(s)>16*1024*1024:raise ValueError('trace batch limit')
json.loads(s)
print(write_text(p,s+'\n','Read trace bounded immutable observation batch'))
