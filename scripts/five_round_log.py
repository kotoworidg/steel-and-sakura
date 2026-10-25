"""Immutable runtime batches; no game access or untracked appends."""
from pathlib import Path
import sys,json
from tracked_files import ROOT,write_text
p=Path(sys.argv[1]).resolve()
if not p.is_relative_to(ROOT/'build/five_round/runtime') or p.suffix!='.json' or p.exists():raise ValueError('invalid fresh runtime log path')
s=sys.stdin.read(16*1024*1024+1)
if len(s)>16*1024*1024 or not isinstance(json.loads(s),list):raise ValueError('invalid bounded log batch')
print(write_text(p,s+'\n','Five-round native runtime immutable evidence batch'))
