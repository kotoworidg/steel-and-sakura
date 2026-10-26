"""Immutable bounded batches from the Type 20 lifecycle observer."""
import json,sys
from pathlib import Path
from tracked_files import ROOT,write_text
p=Path(sys.argv[1]).resolve()
if not p.is_relative_to(ROOT/'build/type20-lifecycle') or p.parent==ROOT/'build/type20-lifecycle' or p.suffix!='.json' or p.exists():
 raise ValueError('only new lifecycle session JSON batches permitted')
s=sys.stdin.read(16*1024*1024+1)
if len(s)>16*1024*1024:raise ValueError('batch too large')
rows=json.loads(s)
if not isinstance(rows,list):raise ValueError('batch must be a list')
print(write_text(p,s+'\n','Type20 lifecycle immutable native observation batch'))
