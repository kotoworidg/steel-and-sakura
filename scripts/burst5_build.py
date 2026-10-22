"""One-command offline build. No game attachment or hook execution during build.
Only launch --approved-engine-hook activates the prepared experiment, after the
human's separate explicit engine-hook approval; never called by build/tests.
"""
from pathlib import Path
import argparse,base64,datetime,hashlib,io,json,os,shutil,struct,subprocess,sys,uuid,zipfile
from tracked_files import ROOT,write_text,write_bytes,digest
sys.path.insert(0,str(ROOT/'tools/python-research'))
import pefile
from setup_x32dbg import guards
OUT=ROOT/'build/burst5';DIST=ROOT/'dist/burst5';SOURCE=ROOT/'src/burst5'
CSC=Path('C:/Windows/Microsoft.NET/Framework/v4.0.30319/csc.exe')
def save(path,value,reason):
 return write_text(path,json.dumps(value,indent=2)+'\n','Burst5 '+reason)
def external_before(path):
 path=Path(path).resolve();stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
 directory=ROOT/'backups'/('external-burst5-'+stamp+'-'+uuid.uuid4().hex[:8]);directory.mkdir(parents=True)
 exists=path.exists();original=path.read_bytes() if exists else None;copy=directory/'original'/path.relative_to(ROOT)
 if exists:
  copy.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,copy)
  if digest(copy.read_bytes())!=digest(original):raise ValueError('Compiler backup hash')
 record={'original_path':str(path),'original_exists':exists,'original_sha256':digest(original) if exists else None,'backup_path':str(copy) if exists else None,'created_utc':stamp,'reason':'Burst5 backup BEFORE compiler output modification','operation':'external_pending','expected_new_sha256':None}
 # Immutable audit records are the backup mechanism, never rewritten.
 (directory/'pending.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
 return directory,record
def external_finish(directory,r):
 r=dict(r);r['operation']='write';r['expected_new_sha256']=digest(Path(r['original_path']).read_bytes());r['rollback_command']='python -B scripts/tracked_files.py rollback "'+str(directory/'manifest.json')+'"'
 (directory/'manifest.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
 return str(directory/'manifest.json')
def collect():
 found=[]
 for file in (ROOT/'backups').glob('*/manifest.json'):
  r=json.loads(file.read_text(encoding='utf-8'));p=Path(r['original_path']);rel=p.relative_to(ROOT).as_posix()
  if rel.startswith(('src/burst5/','build/burst5/','dist/burst5/')) or rel in ['scripts/burst5_build.py','scripts/burst5_validity_research.py','scripts/burst5_runtime_log.py','scripts/burst5_rollback.py','docs/BURST5_EXPERIMENT.md'] or rel in ['CONTINUE.md','PROGRESS.md','docs/TYPE20_TODO.md','src/engine-research-status.json'] and r.get('reason','').startswith('Burst5 '):
   # Do not roll back immutable release ledgers or previous rollback receipts.
   if p.name.startswith(('rollback-ledger','rollback-result')):continue
   if r['operation']=='write':found.append((r['created_utc'],str(file)))
 return [f for _,f in sorted(found)]
def build():
 before=guards();
 from burst5_validity_research import investigate
 predicate=investigate()
 rollback_test=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/burst5_rollback.py'),'--self-test'],capture_output=True,text=True,timeout=20)
 if rollback_test.returncode:raise RuntimeError(rollback_test.stdout+rollback_test.stderr)
 OUT.mkdir(parents=True,exist_ok=True);DIST.mkdir(parents=True,exist_ok=True)
 sources=sorted(SOURCE.glob('*.cs'));exe=OUT/'Burst5Experiment.exe'
 if not CSC.exists():raise RuntimeError('Installed x86 .NET compiler absent; no software installed')
 archive,record=external_before(exe)
 result=subprocess.run([str(CSC),'/nologo','/noconfig','/platform:x86','/target:exe','/debug-','/optimize+','/r:System.dll','/r:System.Core.dll','/r:System.Web.Extensions.dll','/out:'+str(exe)]+[str(p) for p in sources],capture_output=True,text=True)
 save(OUT/'compile-result.json',{'command_compiler':str(CSC),'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr},'compiler diagnostics')
 if exe.exists():external_finish(archive,record)
 if result.returncode:raise RuntimeError(result.stdout+result.stderr)
 # Offline entrypoint has no process-access or hook activation calls.
 test=subprocess.run([str(exe),'--self-test'],capture_output=True,text=True,timeout=60)
 try:report=json.loads(test.stdout)
 except Exception:report={'status':'FAIL','stdout':test.stdout,'stderr':test.stderr}
 save(OUT/'offline-tests.json',report,'shared-controller offline scenarios and fuzz results')
 if test.returncode or report['status']!='PASS_OFFLINE_ONLY':raise RuntimeError(test.stdout+test.stderr)
 bridge=subprocess.run([str(exe),'--bridge-self-test'],capture_output=True,text=True,timeout=40)
 try:transport=json.loads(bridge.stdout)
 except Exception:transport={'status':'FAIL','stdout':bridge.stdout,'stderr':bridge.stderr}
 save(OUT/'transport-tests.json',transport,'synthetic child debugger transport and detach tests')
 if bridge.returncode or transport['status']!='PASS_SYNTHETIC_PROCESS_ONLY':raise RuntimeError(bridge.stdout+bridge.stderr)
 assert digest(Path('D:/Games/Total War - SHOGUN 2/shogun2.exe').read_bytes())=='0AB284186E0BE3FBCDE34E2F800E3C0328008F3219490C7C25E822ADD837C4A9'
 game=Path('D:/Games/Total War - SHOGUN 2/empire.retail.dll');raw=game.read_bytes();pe=pefile.PE(data=raw)
 assert abs(struct.unpack('<f',pe.get_data(0x15b2448,4))[0]-.1)<1e-8
 assert digest(raw)=='022FAE2E2DA92B59B8B1B8EE52887003C624E3C8ECA060B209F5D792A7F874F5'
 masks=[]
 reloc=[]
 for block in pe.DIRECTORY_ENTRY_BASERELOC:
  for entry in block.entries:
   if entry.type==3:reloc.append(entry.rva)
 for start,size in [(0x3d4320,0x2e3),(0x3b3030,0x15),(0x1a9290,0x12d),(0x427400,32),(0x41c760,32),(0x15b2448,4),(0x15ac9c8,4),(0x3a6630,0x16),(0x420d00,0x6c)]:
  data=pe.get_data(start,size);mask=bytearray(b'\xff'*len(data))
  for rva in reloc:
   for offset in range(4):
    if start<=rva+offset<start+size:mask[rva+offset-start]=0
  masks.append({'rva':start,'bytes':base64.b64encode(data).decode(),'mask':base64.b64encode(mask).decode()})
 profile={'dll_sha256':digest(raw),'pack_sha256':before['D:/Games/Total War - SHOGUN 2/data/steel_sakura_combined_test.pack'],'revision':'TARGET_REFERENCE_SCOPE_R3','architecture':'x86','code_checks':masks,'unit_key':'steel_sakura_type20_suppressive_test','projectile_key':'steel_sakura_type20_suppressive_test_bullet','burst_size':5,'interval_ms':100,'native_tick_seconds':.1,'max_duration_ms':6000,'sustained_auto':False,'status':'EXPERIMENTAL_UNEXECUTED','uncertainties':['Unit record at unit+0xB9C and string-wrapper discovery are not runtime verified; exact dual-key proof is mandatory.','Float +0xF78 is an ammo candidate; require two native delta-one observations before extending.','Cease-fire/movement/death gates use native dispatch, animation continuity, native validity predicate, target continuity and origin displacement; exact order/death semantics are unverified.','The action may end or change animation before extra shots; that safely ends the attempt.']}
 save(DIST/'engine-profile.json',profile,'pinned engine compatibility profile and explicit unverified assumptions')
 syntax=subprocess.run([str(exe),'--check-profile',str(DIST/'engine-profile.json')],capture_output=True,text=True,timeout=10)
 if syntax.returncode or syntax.stdout.strip()!='PROFILE_OK '+str(len(masks)):raise RuntimeError('Runtime profile deserialization failed: '+syntax.stdout+syntax.stderr)
 parsed=pefile.PE(str(exe));assert parsed.FILE_HEADER.Machine==0x14c and parsed.OPTIONAL_HEADER.Magic==0x10b
 clr=parsed.OPTIONAL_HEADER.DATA_DIRECTORY[14];flags=struct.unpack('<I',parsed.get_data(clr.VirtualAddress+16,4))[0];assert flags&1 and flags&2
 boundary={}
 for rva,expected in [(0x3d4320,'81ece4000000'),(0x3b3042,'c20400'),(0x3d453a,'e8514dddff'),(0x3d45b7,'c7461800000000')]:
  assert pe.get_data(rva,len(bytes.fromhex(expected))).hex()==expected;boundary[hex(rva)]=expected
 # Branch encodings/calls verified at original and observed/alternate ASLR bases.
 b=pe.get_data(0x3b303d,5);assert b[0]==0xe8;assert 0x3b303d+5+struct.unpack('<i',b[1:])[0]==0x3d4320
 b=pe.get_data(0x3d4558,5);assert b[0]==0xe8;assert 0x3d4558+5+struct.unpack('<i',b[1:])[0]==0x427400
 for base in [0x10000000,0x70d20000,0x50000000]:assert base+0x3d4558+5+struct.unpack('<i',b[1:])[0]==base+0x427400
 validation={'x86_pe32':True,'clr_ilonly_32bitrequired':True,'instruction_boundaries':boundary,'call_targets_verified':True,'aslr_arithmetic_bases':['0x10000000','0x70D20000','0x50000000'],'native_predicate_assertions':predicate['instruction_assertions'],'live_value_regression_checked':True,'live_code_mask_checks':len(masks),'game_and_fallback_hashes_unchanged':guards()==before,'runtime_profile_deserialization':True,'synthetic_debugger_transport':transport,'offline_scenarios':len(report['cases']),'fuzz_scenarios':report['fuzzScenarios'],'engine_hook_executed':False}
 save(OUT/'binary-validation.json',validation,'PE, native boundaries, ASLR arithmetic and preservation verification')
 write_bytes(DIST/'validity-research.json',(OUT/'validity-research.json').read_bytes(),'Burst5 package reproducible predicate correction evidence')
 write_bytes(DIST/'README.md',(ROOT/'docs/BURST5_EXPERIMENT.md').read_bytes(),'Burst5 include concise approval/test/rollback instructions')
 write_bytes(DIST/'rollback-tests.json',(OUT/'rollback-tests.json').read_bytes(),'Burst5 include one-command rollback evidence')
 write_bytes(DIST/exe.name,exe.read_bytes(),'Burst5 publish compiled x86 experiment; never executed against game')
 write_bytes(DIST/'transport-tests.json',(OUT/'transport-tests.json').read_bytes(),'Burst5 include synthetic debugger transport evidence')
 write_bytes(DIST/'offline-tests.json',(OUT/'offline-tests.json').read_bytes(),'Burst5 include offline result evidence')
 write_bytes(DIST/'binary-validation.json',(OUT/'binary-validation.json').read_bytes(),'Burst5 include binary compatibility evidence')
 fallback=ROOT/'build/type20-auto-cycle/confirmed-burst.pack'
 write_bytes(DIST/'CONFIRMED_TWO_SHOT_FALLBACK_DO_NOT_AUTO_INSTALL.pack',fallback.read_bytes(),'Burst5 preserve byte-identical confirmed two-shot fallback; no automatic pack install')
 inventory={f.name:digest(f.read_bytes()) for f in DIST.iterdir() if f.is_file() and f.name not in ['release-manifest.json']}
 save(DIST/'release-manifest.json',{'revision':'TARGET_REFERENCE_SCOPE_R3','status':'PREPARED_NOT_INSTALLED_OR_GAME_TESTED','files':inventory,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'build':'python -B scripts/burst5_build.py build','rollback':'python -B scripts/burst5_rollback.py','sustained_auto_enabled':False},'release inventory')
 ledger=collect();save(OUT/'rollback-ledger.json',{'transactions':ledger,'stop_first':True,'keep_backups':True},'one-command full workspace rollback ledger')
 print(json.dumps({'release':str(DIST),'tests':len(report['cases']),'fuzz':report['fuzzScenarios'],'validation':validation,'rollback':'python -B scripts/burst5_rollback.py'}))
def launch(pid,approved,diagnostic=False):
 if not diagnostic and not approved:raise ValueError('Separate explicit human engine-hook approval is required before activation')
 manifest=json.loads((DIST/'release-manifest.json').read_text())
 for name,expected in manifest['files'].items():
  if digest((DIST/name).read_bytes())!=expected:raise ValueError('Release file changed: '+name)
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');session=OUT/'runtime'/stamp
 save(session/'session.json',{'target_pid':pid,'mode':'diagnostic' if diagnostic else 'guarded-five-shot','created_utc':stamp,'activation_requires_separate_human_approval':True},'runtime session intent before any debugger activation')
 save(OUT/'active-session.json',{'session':str(session)},'active rollback stop target')
 args=['--diagnostic',str(pid),str(ROOT),sys.executable,str(session)] if diagnostic else ['--run','--engine-experiment-approved',str(pid),str(ROOT),sys.executable,str(session)]
 quoted=subprocess.list2cmdline(args).replace("'","''")
 ps="$ErrorActionPreference='Stop'; Start-Process -FilePath '"+str(DIST/'Burst5Experiment.exe').replace("'","''")+"' -ArgumentList '"+quoted+"' -Verb RunAs -WindowStyle Hidden"
 launched=subprocess.run(['powershell','-NoProfile','-Command',ps+' -PassThru | Select-Object Id | ConvertTo-Json'],check=True,capture_output=True,text=True)
 host_pid=json.loads(launched.stdout)['Id']
 save(OUT/'active-session.json',{'session':str(session),'host_pid':host_pid},'active controller process and graceful rollback target')
 print(session)
def report_session():
 active=OUT/'active-session.json'
 if not active.exists():print(json.dumps({'status':'NOT_LAUNCHED','engine_hook_executed':False}));return
 session=Path(json.loads(active.read_text())['session']);records=[]
 for file in sorted(session.glob('log-*.json')):records.extend(json.loads(file.read_text()))
 from collections import Counter
 names=Counter(r['name'] for r in records);reasons=Counter()
 for r in records:
  if r['name'] in ['cancel','gate-refused'] and isinstance(r['detail'],dict):reasons[r['detail']['reason']]+=1
 shots=[r['detail'] for r in records if r['name']=='shot']
 result={'session':str(session),'events':dict(names),'gate_refusals':dict(reasons),'validated_shot_records':len(shots),'additional_shot_records':sum(bool(x.get('extra')) for x in shots),'five_shot_sequences_reported':sum(r['name']=='burst-end' and r['detail'].get('shots')==5 for r in records),'detached':'detached' in names,'in_game_visual_confirmation_required':True}
 save(session/'battle-report.json',result,'aggregate all experimental diagnostics from one battle')
 print(json.dumps(result,indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['build','launch','report']);p.add_argument('--approved-engine-hook',action='store_true');p.add_argument('--diagnostic',action='store_true');p.add_argument('--pid',type=int);a=p.parse_args()
 if a.action=='build':build()
 elif a.action=='report':report_session()
 elif not a.pid:p.error('--pid required')
 else:launch(a.pid,a.approved_engine_hook,a.diagnostic)
