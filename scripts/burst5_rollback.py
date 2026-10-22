"""One-command deactivate/verify rollback; optional --project-files restores source.
Never rewrites game files or deletes backups. Stops the external experiment via
its tracked STOP marker and waits for explicit detach/end evidence.
"""
from pathlib import Path
import argparse,json,subprocess,time,sys,datetime
from tracked_files import ROOT,write_text,rollback,digest
from setup_x32dbg import guards
OUT=ROOT/'build/burst5'
def stop(timeout=110):
 active=OUT/'active-session.json'
 if not active.exists():return {'active_host':False,'reason':'No engine experiment has been launched'}
 state=json.loads(active.read_text());session=Path(state['session']).resolve()
 if not session.is_relative_to(OUT/'runtime'):raise ValueError('Invalid runtime session')
 marker=session/'STOP'
 if not marker.exists():write_text(marker,'Stop requested; drain and detach.\n','Burst5 rollback stop request before modifying any live experimental state')
 def finished():
  records=[]
  for p in session.glob('log-*.json'):records.extend(json.loads(p.read_text()))
  names=[r['name'] for r in records]
  return 'end' in names and ('detached' in names or any(r['name']=='end' and r['detail'].get('processExited') for r in records)) or 'version-or-access-refused' in names
 until=time.monotonic()+timeout
 while not finished() and time.monotonic()<until:time.sleep(.25)
 if not finished():raise RuntimeError('No confirmed detach yet. Game files remain untouched. Keep host running; do not force-close it.')
 return {'active_host':False,'detach_or_refusal_confirmed':True,'session':str(session)}
def restore_files(ledger):
 records=[(m,json.loads(Path(m).read_text())) for m in ledger]
 latest={r['original_path']:r for _,r in records}
 for p,r in latest.items():
  if not Path(p).exists() or digest(Path(p).read_bytes())!=r['expected_new_sha256']:raise ValueError('Later work differs; refusing to discard '+p)
 return [rollback(m) for m,_ in reversed(records)]
def self_test():
 # Isolated fixture, not the experiment or any game file.
 p=OUT/'rollback-fixture.txt'
 a=write_text(p,'fixture original\n','Burst5 rollback fixture original')
 b=write_text(p,'fixture changed\n','Burst5 rollback fixture modification')
 result=restore_files([b]);assert p.read_text()=='fixture original\n'
 # Verify changed files are refused without discarding their contents.
 c=write_text(p,'later edit\n','Burst5 rollback refusal fixture')
 refused=False
 try:restore_files([b])
 except ValueError:refused=True
 assert refused and p.read_text()=='later edit\n'
 receipt={'status':'PASS','restored_original':True,'later_edits_refused':True,'all_fixture_backups_preserved':True,'fixture_transactions':[a,b,c]}
 write_text(OUT/'rollback-tests.json',json.dumps(receipt,indent=2)+'\n','Burst5 rollback test receipt')
 print(json.dumps(receipt))
def main(project=False,check=False):
 ledger=json.loads((OUT/'rollback-ledger.json').read_text())['transactions']
 if check:
  records=[json.loads(Path(m).read_text()) for m in ledger];latest={r['original_path']:r for r in records}
  for p,r in latest.items():assert Path(p).exists() and digest(Path(p).read_bytes())==r['expected_new_sha256']
  for r in records:
   if r['original_exists']:assert digest(Path(r['backup_path']).read_bytes())==r['original_sha256']
  print(json.dumps({'status':'PASS','transactions':len(records),'targets':len(latest),'original_backups_verified':True}));return
 stopped=stop();preserved=guards();receipts=restore_files(ledger) if project else []
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
 result={'stopped':stopped,'game_and_fallback_hashes':preserved,'project_files_restored':project,'rollback_transactions':receipts}
 print(write_text(OUT/('rollback-result-'+stamp+'.json'),json.dumps(result,indent=2)+'\n','Burst5 rollback receipt; game files never changed'))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-files',action='store_true');p.add_argument('--check',action='store_true');p.add_argument('--self-test',action='store_true');a=p.parse_args()
 if a.self_test:self_test()
 else:main(a.project_files,a.check)
