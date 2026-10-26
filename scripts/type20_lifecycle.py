"""Type20 synchronous lifecycle probe. Build/check never attach to the game.
An approved trace is read-only: two native emission sites and two hardware data
watchpoints. No code injection, action flags, ammunition writes or held actions.
"""
import argparse,collections,datetime,json,os,subprocess,sys,uuid
from pathlib import Path
from tracked_files import ROOT,write_text,write_bytes,digest
from banzai import compiler_transaction,hashfile,snapshots,rollback_check
OUT=ROOT/'build/type20-lifecycle'
ENGINE='022FAE2E2DA92B59B8B1B8EE52887003C624E3C8ECA060B209F5D792A7F874F5'
BASELINE='0B497A435F4E28C2C068D7C90B60BA9D0C0FFA353BABD46242EF2FED2222D270'
GAME=Path('D:/Games/Total War - SHOGUN 2')

def stamp():return datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
def save(p,obj,reason):return write_text(p,json.dumps(obj,indent=2)+'\n','Type20 lifecycle '+reason)

def preflight():
 from final_recovery import preflight as recovery_preflight
 from validate_free_fire_experiment import entries
 from inspect_anim_events import read_anim
 before=snapshots()
 if before[str(GAME/'empire.retail.dll')]!=ENGINE:raise ValueError('unsupported engine')
 if before[str(GAME/'shogun2.exe')]!='0AB284186E0BE3FBCDE34E2F800E3C0328008F3219490C7C25E822ADD837C4A9':raise ValueError('unsupported executable')
 if before[str(GAME/'data/steel_sakura_combined_test.pack')]!=BASELINE:raise ValueError('installed pack is not the restored baseline')
 pack=entries(GAME/'data/steel_sakura_combined_test.pack');clips=[]
 for name,raw in pack.items():
  if name.startswith('animations/steel_sakura/type20_burst/') and name.endswith('.anim'):
   clip=read_anim(raw);events=[e for b in clip['event_blocks'] for e in b if e[0] in ['FIRE_TIME','FIRE_TIME_2']]
   if len(clip['bones'])!=48 or [e[0] for e in events]!=['FIRE_TIME','FIRE_TIME_2']:raise ValueError('baseline clip differs')
   clips.append(dict(path=name,markers=events,duration=clip['duration']))
 if len(clips)!=2:raise ValueError('baseline clips missing')
 receipt=json.loads((ROOT/'build/final-attempt/recovery-latest.json').read_text())['transaction']
 records=json.loads(Path(receipt).read_text())['records'];recovery_preflight(records,'expected_new_sha256')
 if not all(hashfile(r['backup_path'])==r['original_sha256'] for r in records):raise ValueError('recovery backup changed')
 # No disassembler installation needed: validate PE mapping and exact known instructions.
 import pefile
 pe=pefile.PE(str(GAME/'empire.retail.dll'),fast_load=True)
 for rva,raw in [(0x3d453a,'e8514dddff'),(0x3d45b7,'c7461800000000')]:
  if pe.get_data(rva,len(bytes.fromhex(raw)))!=bytes.fromhex(raw):raise ValueError('native instruction anchor differs')
 extra=[str(p) for d in [GAME/'data',GAME/'data/MyMods'] for p in d.glob('steel_sakura*.pack') if p!=GAME/'data/steel_sakura_combined_test.pack']
 if extra:raise ValueError('unexpected extra Steel Sakura packs: '+str(extra))
 if before!=snapshots():raise ValueError('preserved files changed during preflight')
 return dict(status='PASS_READ_ONLY_PREFLIGHT',preserved_hashes=before,baseline_entries=len(pack),baseline_clips=clips,
  rollback_transaction=receipt,rollback_preconditions_match=True,capstone_required=False,
  scope='Synchronous observations only. Raw watched fields have no asserted order/life/movement semantics.')

def replace_once(text,old,new):
 if text.count(old)!=1:raise ValueError('host source anchor changed: '+old[:70])
 return text.replace(old,new,1)

def host_source():
 s=(ROOT/'src/read_trace/NativeObserver.cs').read_text()
 s=s.replace('ReadOnlyHost','LifecycleHost').replace('Observer controller','LifecycleObserver controller').replace('new Observer(memory,log.Add)','new LifecycleObserver(memory,log.Add,session)').replace('Observer.UnitKey','LifecycleObserver.UnitKey').replace('read_trace_log.py','type20_lifecycle_log.py')
 s=replace_once(s,'for(int k=0;k<2;k++)c[4+k*4]=image+sites[k];c[20]=0;c[24]=0x405;c.Save(h.Handle);','Configure(c);c[20]=0;c.Save(h.Handle);')
 start=s.index(' void Hit(uint tid){');end=s.index(' public int Run(){',start)
 methods=r""" void Configure(Registers c){
  c[4]=image+sites[0];c[8]=image+sites[1];c[12]=0;c[16]=0;c[24]=0x405;
  if(controller.WatchActor!=0){c[12]=controller.WatchActor+0x1b4;c[24]|=0x0d000010;}
  if(controller.WatchCurrent!=0){c[16]=controller.WatchCurrent;c[24]|=0xd0000040;}
 }
 bool OwnedHit(uint tid){
  using(var h=new ThreadHandle(tid))using(var c=new Registers(h.Handle)){
   uint mask=c[20]&15;
   for(int k=0;k<4;k++)if((mask&(1u<<k))!=0&&(c[24]&(1u<<(k*2)))!=0)return true;
   return false;
  }
 }
 void Hit(uint tid){
  using(var h=new ThreadHandle(tid))using(var c=new Registers(h.Handle)){
   uint mask=c[20]&15,ip=c[184];
   try{
    if((mask&1)!=0&&ip==image+sites[0])controller.Before(tid,c[160],c[180],c[156]);
    if((mask&2)!=0&&ip==image+sites[1])controller.After(tid,c[160],c[180]);
    if((mask&12)!=0)controller.Watch(tid,mask,ip,image);
   }catch(Exception e){controller.Expire();draining=true;log.Add("read-failed-draining",e.ToString());}
   c[20]&=0xfffffff0;if((mask&3)!=0)c[192]|=0x10000;c.Save(h.Handle);
  }
  // Debug events suspend all threads. Refresh watch addresses only at this boundary.
  foreach(uint id in new List<uint>(saved.Keys))using(var h=new ThreadHandle(id))using(var c=new Registers(h.Handle)){Configure(c);c.Save(h.Handle);}
 }
"""
 s=s[:start]+methods+s[end:]
 s=replace_once(s,'code==0x80000004&&ours','code==0x80000004&&OwnedHit(tid)')
 s=replace_once(s,'code==0x80000004&&own','code==0x80000004&&OwnedHit(pendingTid)')
 s=s.replace('timer.Elapsed.TotalSeconds>180','timer.Elapsed.TotalSeconds>90')
 s=replace_once(s,'if(args.Length==2&&args[0]=="--toy-child")','if(args.Length==1&&args[0]=="--self-test"){Console.WriteLine(new JavaScriptSerializer().Serialize(LifecycleTests.Run()));return 0;}\n  if(args.Length==2&&args[0]=="--toy-child")')
 s=s.replace('--read-only-trace-approved','--lifecycle-trace-approved')
 for forbidden in ['WriteProcessMemory','VirtualAllocEx','CreateRemoteThread','memory.Write(','controller.Enter(']:
  if forbidden in s:raise ValueError('observer gained a game mutation capability: '+forbidden)
 return s

def bridge_source():
 # Exercise two execution breakpoints plus two DWORD write watchpoints on our child.
 s=(ROOT/'src/read_trace/BridgeTests.cs').read_text()
 s=replace_once(s,'new UIntPtr(4096),0x3000,4','new UIntPtr(8192),0x3000,4')
 s=replace_once(s,'byte[] code=new byte[]{0xb8,(byte)(i+1),0,0,0,0xc3};',
  'byte[] code=i<2?new byte[]{0xc7,0x05,0,0,0,0,(byte)(i+1),0,0,0,0xb8,(byte)(i+1),0,0,0,0xc3}:new byte[]{0xb8,(byte)(i+1),0,0,0,0xc3};if(i<2)Array.Copy(BitConverter.GetBytes(unchecked((uint)block.ToInt32())+4096+(uint)i*4),0,code,2,4);')
 s=replace_once(s,'int events=0;bool restored=false;','int events=0;uint hitMask=0;bool restored=false;')
 s=replace_once(s,'memory.Read(address,6)[0]!=0xb8','memory.Read(address,6)[0]!=0xc7')
 s=replace_once(s,'saved[4]=c[20];saved[5]=c[24];original[tid]=saved;c[20]=0;c[24]=0x455;c.Save(h.Handle);',
  'saved[4]=c[20];saved[5]=c[24];original[tid]=saved;c[12]=address+4096;c[16]=address+4100;c[20]=0;c[24]=0xdd000455;c.Save(h.Handle);')
 s=replace_once(s,'hits.Add(c[184]);c[20]=0;c[192]|=0x10000;c.Save(h.Handle);',
  'hits.Add(c[184]);uint mask=c[20]&15;hitMask|=mask;c[20]=0;if((mask&3)!=0)c[192]|=0x10000;c.Save(h.Handle);')
 s=replace_once(s,'if(hits.Count==4){','if(hitMask==15){')
 s=replace_once(s,'if(hits.Count!=4)throw new Exception("toy four hardware sites not all reached");',
  'if(hitMask!=15)throw new Exception("two execution sites and two DWORD write sites not all reached");')
 s=replace_once(s,'hardwareSites=hits.Count,liveMemoryReadVerified=true,',
  'hardwareSites=4,executionSites=2,dataWriteSites=2,debugStatusMask=hitMask,liveMemoryReadVerified=true,')
 return s

def build():
 before=preflight();session=OUT/('build-'+stamp());ledger=[]
 # Include this attempt's source transactions for a refusal-safe workspace undo.
 targets={ROOT/'scripts/type20_lifecycle.py',ROOT/'scripts/type20_lifecycle_log.py'}|set((ROOT/'src/type20_lifecycle').glob('*.cs'))
 rows=[]
 for p in (ROOT/'backups').glob('tracked-*/manifest.json'):
  r=json.loads(p.read_text())
  if Path(r.get('original_path','')) in targets and r.get('reason','').startswith('Type20 lifecycle '):rows.append((r['created_utc'],str(p)))
 ledger+=[m for _,m in sorted(rows)]
 host=session/'NativeLifecycle.cs';ledger.append(write_text(host,host_source(),'Type20 lifecycle generate reviewed read-only transport'))
 bridge=session/'LifecycleBridgeTests.cs';ledger.append(write_text(bridge,bridge_source(),'Type20 lifecycle generate mixed execution/data watchpoint child fixture'))
 sources=[host,ROOT/'src/type20_lifecycle/Observer.cs',ROOT/'src/type20_lifecycle/SelfTests.cs',ROOT/'src/capture_adapter/IdentityReader.cs',bridge]
 exe=session/'Type20LifecycleTrace.exe';transactions,compiler=compiler_transaction(exe,sources);ledger+=transactions
 def run(args):
  p=subprocess.run([str(exe)]+args,capture_output=True,text=True,timeout=45)
  if p.returncode:raise RuntimeError(p.stdout+p.stderr)
  return json.loads(p.stdout)
 tests=run(['--self-test'])
 # Transport fixture operates on our own child executable, never Shogun 2.
 bridge=run(['--bridge-self-test'])
 if before['preserved_hashes']!=snapshots():raise ValueError('game or fallbacks changed')
 save(session/'preflight.json',before,'preflight evidence')
 save(session/'compiler.json',compiler,'compiler receipt')
 save(session/'tests.json',tests,'targeted observer regressions')
 save(session/'transport.json',bridge,'synthetic child-only debug transport verification')
 manifest=dict(status='READY_FOR_APPROVED_READ_ONLY_TRACE_NOT_A_COMBAT_RELEASE',exe=str(exe),sha256=hashfile(exe),
  source_hashes={str(p.relative_to(ROOT)):hashfile(p) for p in sources},game_writes=False,game_attach_performed=False,
  watchpoints=['actor+0x1B4 DWORD writes','selected animation object first DWORD writes'],
  code_sites=['empire.retail.dll+0x3D453A','empire.retail.dll+0x3D45B7'],max_wall_seconds=90,
  limitations=['No five-shot, magazine or full-auto implementation in this tool.','Observed state changes are not assigned life/order/movement meanings.','Debug watchpoints can slow the game.','A traced actor may never receive the requested command; command markers record intent only.'])
 save(session/'manifest.json',manifest,'reviewable exact probe scope')
 save(session/'rollback-ledger.json',{'transactions':ledger,'game_changes':False,'preserve_evidence':True},'workspace rollback ledger')
 rollback_check(session,dry=True)
 save(OUT/'latest-build.json',{'session':str(session),'exe':str(exe),'sha256':hashfile(exe)},'latest compiled probe pointer')
 print(json.dumps(dict(status=manifest['status'],session=str(session),tests=tests,transport=bridge,installed_pack_unchanged=True),indent=2))

def latest_build():
 p=json.loads((OUT/'latest-build.json').read_text());session=Path(p['session']).resolve()
 if not session.is_relative_to(OUT) or hashfile(p['exe'])!=p['sha256']:raise ValueError('build pointer or executable differs')
 m=json.loads((session/'manifest.json').read_text())
 for name,expected in m['source_hashes'].items():
  if hashfile(ROOT/name)!=expected:raise ValueError('source changed after compilation')
 return p,session

def latest_run():
 p=json.loads((OUT/'latest-run.json').read_text());session=Path(p['session']).resolve()
 if not session.is_relative_to(OUT):raise ValueError('invalid runtime session')
 return p,session

def status(session):
 rows=[r for f in sorted(session.glob('log-*.json')) for r in json.loads(f.read_text())]
 counts=collections.Counter(r['name'] for r in rows)
 return dict(session=str(session),events=dict(counts),finished=bool(counts['end']),detached=bool(counts['detached']),
  actors=[r['detail'] for r in rows if r['name']=='actor-bound'],
  native_deltas=dict(collections.Counter(str(r['detail']['delta']) for r in rows if r['name']=='native-after')),
  life_order_movement_verified=False,five_shots_implemented=False,
  native_exceptions=[r['detail'] for r in rows if r['name']=='native-exception'])

def start(approved):
 if not approved:raise ValueError('Explicit approval for the game debugger attachment is required')
 build,_=latest_build();before=preflight()
 p=subprocess.run(['powershell','-NoProfile','-Command',"@(Get-Process shogun2 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id) | ConvertTo-Json"],capture_output=True,text=True,check=True)
 ids=json.loads(p.stdout) if p.stdout.strip() else []
 ids=ids if isinstance(ids,list) else [ids]
 if len(ids)!=1:raise ValueError('exactly one running shogun2 is required; tool does not start the game')
 if (OUT/'latest-run.json').exists():
  _,old=latest_run();state=status(old)
  if not state['finished'] or not state['detached']:raise ValueError('previous trace has not confirmed detach')
 session=OUT/('runtime-'+stamp())
 save(session/'request.json',dict(game_pid=ids[0],scope='approved read-only lifecycle trace',preserved_hashes=before['preserved_hashes']),'pre-attachment scope and preservation hashes')
 child=subprocess.Popen([build['exe'],'--observe','--lifecycle-trace-approved',str(ids[0]),str(ROOT),sys.executable,str(session)],creationflags=subprocess.CREATE_NO_WINDOW,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 result=dict(session=str(session),host_pid=child.pid,game_pid=ids[0],exe=build['exe'])
 save(OUT/'latest-run.json',result,'active probe pointer')
 print(json.dumps(result,indent=2))

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('action',choices=['check','build','start','status','stop','mark','report','rollback']);ap.add_argument('--approved',action='store_true');ap.add_argument('--label',choices=['fire-requested','stop-requested','move-requested','casualty-observed','battle-ended']);ap.add_argument('--unit',default='unverified selection');ap.add_argument('--dry-run',action='store_true');a=ap.parse_args()
 if a.action=='check':print(json.dumps(preflight(),indent=2))
 elif a.action=='build':build()
 elif a.action=='start':start(a.approved)
 elif a.action=='rollback':
  _,s=latest_build()
  p=subprocess.run(['powershell','-NoProfile','-Command',"@(Get-Process Type20LifecycleTrace -ErrorAction SilentlyContinue).Count"],capture_output=True,text=True,check=True)
  if p.stdout.strip()!='0':raise ValueError('probe still running; stop and confirm detach first')
  print(json.dumps(rollback_check(s,dry=a.dry_run)))
 else:
  _,s=latest_run()
  if a.action=='stop':
   if not (s/'STOP').exists():print(write_text(s/'STOP','Request graceful register restoration and detach.\n','Type20 lifecycle graceful detach request'))
  elif a.action=='mark':
   if not a.label:raise ValueError('--label required')
   print(save(s/'markers'/(stamp()+'-'+uuid.uuid4().hex[:8]+'.json'),dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),command_intent=a.label,intended_unit=a.unit,selection_verified=False),'command intent marker; native order not assumed'))
  else:
   result=status(s)
   if a.action=='report':
    if not result['detached'] or not result['finished']:raise ValueError('detach/end required for final report')
    before=json.loads((s/'request.json').read_text())['preserved_hashes'];result['preserved_hashes_unchanged']=before==snapshots()
    save(s/'report.json',result,'completed read-only trace report')
   print(json.dumps(result,indent=2))
if __name__=='__main__':main()
