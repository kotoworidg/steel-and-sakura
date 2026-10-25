"""Run/stop/report the five-round native adapter. No game binary installation.
Activation requires separate human approval for this specific runtime hook.
"""
import argparse,collections,datetime,json,os,subprocess,sys,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
from tracked_files import write_text,digest
RUNTIME=ROOT/'build/five_round/runtime'

def save(path,obj,why):return write_text(path,json.dumps(obj,indent=2)+'\n','Five-round '+why)
def stamp():return datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
def loaded(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def process_ids(names):
 quoted=','.join(names)
 r=subprocess.run(['powershell','-NoProfile','-Command','@(Get-Process -Name '+quoted+' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id) | ConvertTo-Json'],capture_output=True,text=True,check=True)
 result=json.loads(r.stdout) if r.stdout.strip() else []
 return result if isinstance(result,list) else [result]
def verify():
 m=loaded(ROOT/'runtime-release.json')
 for name,h in m['runtime_sha256'].items():
  p=(ROOT/name).resolve()
  if not p.is_relative_to(ROOT) or not p.is_file() or digest(p.read_bytes())!=h:raise ValueError('Runtime release differs: '+name)
 return m

def latest():
 p=loaded(ROOT/'build/five_round/active.json');s=Path(p['session']).resolve()
 if not s.is_relative_to(RUNTIME):raise ValueError('Runtime session outside package')
 return p,s

def report(session):
 rows=[r for f in sorted(session.glob('log-*.json')) for r in loaded(f)];names=collections.Counter(r['name'] for r in rows)
 shots=[r['detail'] for r in rows if r['name']=='native-shot-confirmed'];counts=collections.Counter(r['detail'].get('reason','') for r in rows if r['name']=='cancel')
 return dict(session=str(session),events=dict(names),native_debit_spawn_pairs=len(shots),additional_native_pairs=sum(bool(s['extra']) for s in shots),five_native_bursts=names['five-native-emissions-accounted'],
  short_bursts=names['short-native-burst'],cancellation_reasons=dict(counts),detached=bool(names['detached']),finished=bool(names['end']),
  native_exceptions=[r['detail'] for r in rows if r['name']=='native-exception'],runtime_errors=[r['detail'] for r in rows if r['name'] in ['version-or-access-refused','runtime-error','admission-refused']],visual_projectile_damage_verification=False)

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('action',choices=['start','stop','status','report']);ap.add_argument('--approved-engine-hook',action='store_true');ap.add_argument('--pid',type=int);ap.add_argument('--seconds',type=int,default=90);ap.add_argument('--game-root',type=Path,default=Path('D:/Games/Total War - SHOGUN 2'));a=ap.parse_args()
 if a.action=='start':
  if not a.approved_engine_hook:raise ValueError('Separate human approval is required for this mutating runtime hook')
  if not 10<=a.seconds<=3600:raise ValueError('Runtime duration must be 10..3600 seconds')
  m=verify();profile=loaded(ROOT/'engine-profile.json');game=a.game_root.resolve()
  if digest((game/'data/steel_sakura_combined_test.pack').read_bytes())!=profile['pack_sha256']:raise ValueError('Install the paired candidate pack with the game closed before starting it')
  busy=process_ids(['Type20FiveRound','Burst5Experiment','ReadOnlyTrace','Type20LifecycleTrace'])
  if busy:raise ValueError('Another controller/observer is running; stop and confirm its detach first')
  ids=process_ids(['shogun2'])
  if a.pid is None:
   if len(ids)!=1:raise ValueError('Exactly one running Shogun 2 is required; launcher does not start the game')
   pid=ids[0]
  else:
   if a.pid not in ids:raise ValueError('PID does not identify a running shogun2 process')
   pid=a.pid
  session=RUNTIME/stamp();preserved={str(p):digest(p.read_bytes()) for p in [game/'shogun2.exe',game/'empire.retail.dll',game/'data/steel_sakura_combined_test.pack',game/'mod_list.txt']}
  preserved.update({str(p):digest(p.read_bytes()) for p in (game/'data').glob('*otomo*.pack')})
  user=Path(os.environ['APPDATA'])/'The Creative Assembly/Shogun2/scripts/user.script.txt'
  if user.is_file():preserved[str(user)]=digest(user.read_bytes())
  save(session/'request.json',dict(game_pid=pid,mode='five-round native action re-arm',duration_seconds=a.seconds,write_offset='action+0x6C only',completion_and_ammo_writes=False,preserved_hashes=preserved),'exact approved runtime intent before activation')
  proc=subprocess.Popen([str(ROOT/'Type20FiveRound.exe'),'--run','--five-round-runtime-approved',str(pid),str(ROOT),sys.executable,str(session)],creationflags=subprocess.CREATE_NO_WINDOW,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  result=dict(session=str(session),host_pid=proc.pid,game_pid=pid);save(ROOT/'build/five_round/active.json',result,'active host and graceful-stop target');print(json.dumps(result,indent=2))
 else:
  _,session=latest()
  if a.action=='stop':
   path=session/'STOP'
   if not path.exists():print(write_text(path,'Stop extra shots, restore any unconsumed re-arm and owned debug registers, then detach.\n','Five-round graceful stop request'))
  else:
   r=report(session)
   if a.action=='report':
    if not r['detached'] or not r['finished']:raise ValueError('Confirmed detach/end required for final report')
    before=loaded(session/'request.json')['preserved_hashes'];r['preserved_disk_hashes_unchanged']=all(Path(p).is_file() and digest(Path(p).read_bytes())==h for p,h in before.items());save(session/'battle-report.json',r,'aggregate actual runtime outcomes; no visual damage claim')
   print(json.dumps(r,indent=2))
if __name__=='__main__':main()
