"""Graceful observer stop plus hash-checked workspace undo; preserves all evidence."""
import argparse,json,subprocess,time
from pathlib import Path
from tracked_files import ROOT,write_text,rollback,digest
from read_trace_control import current,summary

def main(dry):
 _,session=current();ledger=json.loads((session/'rollback-ledger.json').read_text())['transactions'];state=summary(session)
 if not state['detached'] or not state['finished']:
  if dry:raise RuntimeError('observer still attached')
  if not (session/'STOP').exists():write_text(session/'STOP','Graceful detach requested.\n','Read trace rollback stop request')
  end=time.monotonic()+30
  while time.monotonic()<end:
   state=summary(session)
   if state['detached'] and state['finished']:break
   time.sleep(.25)
  else:raise RuntimeError('detach unconfirmed; preserve observer and ask for recovery; do not terminate it')
 process=subprocess.run(['powershell','-NoProfile','-Command',"@(Get-Process ReadOnlyTrace -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id) | ConvertTo-Json"],capture_output=True,text=True,timeout=10)
 if process.stdout.strip():raise RuntimeError('observer process still exists; refuse removing its executable')
 simulated={}
 for m in reversed(ledger):
  r=json.loads(Path(m).read_text());p=Path(r['original_path']);actual=simulated.get(str(p),digest(p.read_bytes()) if p.exists() else None)
  if actual!=r['expected_new_sha256']:raise RuntimeError('later edit or already undone; refusing overwrite: '+str(p))
  if r['original_exists'] and digest(Path(r['backup_path']).read_bytes())!=r['original_sha256']:raise RuntimeError('backup changed')
  simulated[str(p)]=r['original_sha256'] if r['original_exists'] else None
 if not dry:
  receipts=[rollback(m) for m in reversed(ledger)]
  import datetime
  stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
  write_text(session/('workspace-rollback-'+stamp+'.json'),json.dumps({'receipts':receipts,'game_untouched':True},indent=2)+'\n','Read trace workspace rollback audit')
 print(json.dumps({'rollback_preflight_passed':True,'transactions':len(ledger),'dry_run':dry,'preserves_crash_and_trace_evidence':True,'game_changes':False}))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--dry-run',action='store_true');main(ap.parse_args().dry_run)
