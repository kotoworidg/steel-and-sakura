"""Final recovery only: preserve evidence, restore confirmed pack, or undo that recovery.
Never launches the game, attaches a debugger, installs a hook, or writes an EXE/DLL.
Workspace writes use tracked_files; external writes have immutable pre-write backups.
"""
from pathlib import Path
import argparse,datetime,json,os,re,shutil,struct,subprocess,sys,uuid
from tracked_files import ROOT,write_bytes,write_text,digest
GAME=Path('D:/Games/Total War - SHOGUN 2')
APP=Path(os.environ['APPDATA'])/'The Creative Assembly/Shogun2'
PACK=GAME/'data/steel_sakura_combined_test.pack'
CONFIGS=[GAME/'mod_list.txt',APP/'scripts/user.script.txt']
FALLBACK=ROOT/'build/type20-auto-cycle/confirmed-burst.pack'
CONFIRMED='0B497A435F4E28C2C068D7C90B60BA9D0C0FFA353BABD46242EF2FED2222D270'
R2='1737D02D67F0C9100BBCC5255057C12B532F9805482D18ADC910542653D96DCD'
OUT=ROOT/'build/final-attempt'

def utc():return datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
def save(p,v,why):return write_text(p,json.dumps(v,indent=2)+'\n','Final recovery '+why)
def ps(code):
 p=subprocess.run(['powershell','-NoProfile','-Command',code],capture_output=True,text=True,timeout=40)
 return {'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
def require_closed():
 r=ps("@(Get-Process -Name shogun2,Burst5Experiment,x32dbg -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id) | ConvertTo-Json")
 if r['stdout'].strip():raise RuntimeError('Game/controller/debugger must be closed; no process is stopped by this script')
def ensure_enabled(raw):
 if raw.startswith(b'\xff\xfe'):bom,enc=raw[:2],'utf-16-le'
 elif raw.startswith(b'\xfe\xff'):bom,enc=raw[:2],'utf-16-be'
 elif raw.startswith(b'\xef\xbb\xbf'):bom,enc=raw[:3],'utf-8'
 else:bom,enc=b'','utf-8'
 s=raw[len(bom):].decode(enc)
 if re.search(r'(?im)^\s*mod\s+"(?:[^"\r\n]*[/\\])?steel_sakura_combined_test\.pack"\s*;',s):return raw
 newline='\r\n' if '\r\n' in s or not s else '\n'
 return bom+(s+(newline if s and not s.endswith(('\r','\n')) else '')+'mod "steel_sakura_combined_test.pack";'+newline).encode(enc)
def dump_summary(f):
 b=f.read_bytes()
 if b[:4]!=b'MDMP':return {'error':'not minidump'}
 count,dr=struct.unpack_from('<II',b,8);streams={}
 for j in range(count):
  t,z,r=struct.unpack_from('<III',b,dr+12*j);streams[t]=(z,r)
 if 6 not in streams:return {'exception_stream':False}
 q=streams[6][1];code=struct.unpack_from('<I',b,q+8)[0];address=struct.unpack_from('<Q',b,q+24)[0];n=struct.unpack_from('<I',b,q+32)[0];info=struct.unpack_from('<15Q',b,q+40);mods=[]
 q=streams[4][1]
 for j in range(struct.unpack_from('<I',b,q)[0]):
  v=q+4+j*108;base,size=struct.unpack_from('<QI',b,v);r=struct.unpack_from('<I',b,v+20)[0];ln=struct.unpack_from('<I',b,r)[0];name=b[r+4:r+4+ln].decode('utf-16-le',errors='replace');mods.append((base,size,name))
 return {'exception_code':hex(code),'address':hex(address),'access_parameters':[hex(x) for x in info[:min(n,15)]],'fault_module':[{'path':name,'rva':hex(address-base)} for base,size,name in mods if base<=address<base+size],'loaded_modules':[name for _,_,name in mods]}
def capture():
 stamp=utc();session=OUT/stamp;inventory=[]
 sources=[PACK,GAME/'mod_list.txt',APP/'scripts/user.script.txt',APP/'user.script.txt',APP/'scripts/preferences.script.txt',FALLBACK,ROOT/'build/type20-five-shot/confirmed-suppression-r2.pack',ROOT/'build/type20-suppression/confirmed-no-reload-bursts.pack',GAME/'data/mods_modern_units_otomo.pack',GAME/'data/otomo_fots_expanded.pack']
 sources+=list((APP/'logs').glob('*'))+list((Path(os.environ['LOCALAPPDATA'])/'CrashDumps').glob('*shogun*.dmp'))
 sources+=list((ROOT/'build/burst5/runtime').rglob('*.json'))
 sources+=[ROOT/'src/burst5/NativeHost.cs',ROOT/'src/burst5/BurstController.cs',ROOT/'dist/burst5/Burst5Experiment.exe',ROOT/'dist/burst5/engine-profile.json',ROOT/'dist/burst5/release-manifest.json']
 for n,p in enumerate(dict.fromkeys(sources)):
  if not p.is_file():continue
  data=p.read_bytes();dest=session/'evidence'/('%03d_'%n+p.name)
  write_bytes(dest,data,'Final recovery evidence copy; source is read-only')
  inventory.append({'original_path':str(p.resolve()),'snapshot':str(dest),'sha256':digest(data),'size':len(data),'mtime_utc':datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat()})
 events=ps("Get-WinEvent -FilterHashtable @{LogName='Application';StartTime=(Get-Date).AddDays(-4);Id=1000,1001,1002,1026} -ErrorAction SilentlyContinue | Where-Object {$_.Message -match 'shogun2|Empire.Retail|Burst5'} | ForEach-Object { [pscustomobject]@{TimeCreated=$_.TimeCreated.ToString('o');Id=$_.Id;RecordId=$_.RecordId;Message=$_.Message;Xml=$_.ToXml()} } | ConvertTo-Json -Depth 5")
 save(session/'windows-events.json',events,'preserve filtered Application events and raw XML')
 save(session/'graphics.json',ps("Get-CimInstance Win32_VideoController | Select-Object Name,Status,ConfigManagerErrorCode,DriverVersion | ConvertTo-Json"),'preserve graphics-device diagnostic')
 crashes=[]
 for row in inventory:
  if row['original_path'].lower().endswith('.dmp'):
   crashes.append({'source':row['original_path'],'snapshot':row['snapshot'],'sha256':row['sha256'],'summary':dump_summary(Path(row['snapshot']))})
 save(session/'dump-summary.json',crashes,'preserve minidump exception/module summaries')
 binaries={str(p):digest(p.read_bytes()) for p in [GAME/'shogun2.exe',GAME/'empire.retail.dll']}
 save(session/'binary-hashes.json',binaries,'record original binary hashes without modifying binaries')
 for args,name in [(['status','--short'],'git-status.json'),(['diff','--','scripts/setup_x32dbg.py','src/burst5/NativeHost.cs'],'git-diff.json'),(['log','-8','--format=%h %ad %s','--date=iso'],'git-history.json')]:
  r=subprocess.run(['git','--no-optional-locks']+args,capture_output=True,text=True);save(session/name,{'stdout':r.stdout,'stderr':r.stderr,'exit_code':r.returncode},'preserve project history')
 save(session/'inventory.json',inventory,'evidence absolute original paths, timestamps and SHA256')
 save(OUT/'latest.json',{'session':str(session),'captured_utc':stamp},'current recovery evidence pointer')
 return session

def preflight(records,field):
 for r in records:
  p=Path(r['original_path'])
  expected=r[field]
  if (digest(p.read_bytes()) if p.exists() else None)!=expected:raise RuntimeError('File changed since transaction; refusing overwrite: '+str(p))
def commit(changes,reason):
 require_closed();allowed={str(p.resolve()).casefold() for p in [PACK]+CONFIGS}
 for p,data in changes:
  if str(p.resolve()).casefold() not in allowed:raise ValueError('External write not in exact pack/config allowlist')
 changes=[(p,b) for p,b in changes if not p.exists() or p.read_bytes()!=b]
 if not changes:return None
 stamp=utc();archive=ROOT/'backups'/('final-recovery-'+stamp+'-'+uuid.uuid4().hex[:8]);archive.mkdir(parents=True,exist_ok=False);records=[]
 for n,(p,data) in enumerate(changes):
  original=p.read_bytes() if p.exists() else None;backup=archive/'original'/('%02d_'%n+p.name)
  if original is not None:
   backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,backup)
   if digest(backup.read_bytes())!=digest(original):raise RuntimeError('Backup verification failed')
  temp=p.with_name(p.name+'.ss-recovery-'+uuid.uuid4().hex+'.tmp')
  records.append({'original_path':str(p.resolve()),'original_exists':original is not None,'original_sha256':digest(original) if original is not None else None,'backup_path':str(backup) if original is not None else None,'expected_new_sha256':digest(data),'temporary_new_path':str(temp),'temporary_original_exists':False,'temporary_original_sha256':None,'temporary_expected_new_sha256':digest(data)})
 manifest=archive/'manifest.json'
 receipt={'created_utc':stamp,'reason':reason,'records':records,'rollback_command':'python -B scripts/final_recovery.py rollback --receipt "'+str(manifest)+'"','game_binary_modification':False}
 # Immutable originals/manifest are the backup mechanism, written BEFORE any external change.
 manifest.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
 preflight(records,'original_sha256')
 for (p,data),r in zip(changes,records):
  temp=Path(r['temporary_new_path'])
  with temp.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
  if digest(temp.read_bytes())!=r['expected_new_sha256']:raise RuntimeError('Staged hash mismatch')
  os.replace(temp,p)
  if digest(p.read_bytes())!=r['expected_new_sha256']:raise RuntimeError('Installed hash mismatch')
 return str(manifest)
def restore():
 require_closed();session=capture();data=FALLBACK.read_bytes()
 if digest(data)!=CONFIRMED:raise RuntimeError('Confirmed fallback differs')
 if digest(PACK.read_bytes()) not in [R2,CONFIRMED]:raise RuntimeError('Installed pack is an unrecognized later edit; evidence saved but no overwrite')
 before={str(p):digest(p.read_bytes()) for p in [GAME/'shogun2.exe',GAME/'empire.retail.dll',GAME/'data/mods_modern_units_otomo.pack',GAME/'data/otomo_fots_expanded.pack'] if p.exists()}
 changes=[(PACK,data)]+[(p,ensure_enabled(p.read_bytes() if p.exists() else b'')) for p in CONFIGS]
 receipt=commit(changes,'Restore original user-confirmed two-shot WITH reload; preserve current unrelated mod entries')
 after={p:digest(Path(p).read_bytes()) for p in before};assert after==before
 result={'status':'CONFIRMED_TWO_SHOT_BYTES_RESTORED_NOT_GAME_TESTED','session':str(session),'installed_path':str(PACK),'installed_sha256':digest(PACK.read_bytes()),'transaction':receipt,'rollback':'python -B scripts/final_recovery.py rollback','unrelated_mod_and_binary_hashes_unchanged':True,'engine_hook_installed':False,'runtime_started':False}
 save(session/'recovery-result.json',result,'restoration receipt and exact one-command rollback')
 save(OUT/'recovery-latest.json',result,'last completed recovery pointer')
 print(json.dumps(result,indent=2))
def rollback(receipt=None):
 require_closed()
 if receipt is None:receipt=json.loads((OUT/'recovery-latest.json').read_text())['transaction']
 if receipt is None:print('No files were changed by recovery.');return
 p=Path(receipt).resolve()
 if not p.is_relative_to(ROOT/'backups') or p.name!='manifest.json':raise ValueError('Invalid immutable manifest path')
 r=json.loads(p.read_text());preflight(r['records'],'expected_new_sha256');changes=[]
 for row in r['records']:
  if not row['original_exists']:raise RuntimeError('Original missing: automatic deletion is forbidden; stop for review')
  b=Path(row['backup_path']).read_bytes()
  if digest(b)!=row['original_sha256']:raise RuntimeError('Backup hash differs')
  changes.append((Path(row['original_path']),b))
 inverse=commit(changes,'Undo final recovery; preserve a new timestamped copy of every affected file first')
 save(OUT/('rollback-'+utc()+'.json'),{'source':str(p),'inverse_transaction':inverse,'all_backups_preserved':True},'rollback receipt')
 print('Restored pre-recovery pack/configuration with backups: '+str(inverse))
def check():
 from validate_free_fire_experiment import entries
 from inspect_anim_events import read_anim
 cases=[]
 for enc,bom in [('utf-8',b''),('utf-8',b'\xef\xbb\xbf'),('utf-16-le',b'\xff\xfe'),('utf-16-be',b'\xfe\xff')]:
  for source in ['', 'mod "otomo_fots_expanded.pack";\r\n', 'mod "other.pack";']:
   original=bom+source.encode(enc);out=ensure_enabled(original);assert out.startswith(original);assert ensure_enabled(out)==out;assert 'mod "otomo_fots_expanded.pack";' not in source or 'mod "otomo_fots_expanded.pack";' in out[len(bom):].decode(enc);cases.append(enc+': preserve and idempotent')
 pack=entries(FALLBACK);assert digest(FALLBACK.read_bytes())==CONFIRMED
 timing=[]
 for path,b in pack.items():
  if path in ['animations/steel_sakura/type20_burst/stand.anim','animations/steel_sakura/type20_burst/kneel.anim']:
   a=read_anim(b);events=[v for block in a['event_blocks'] for v in block];assert len(a['bones'])==48;assert sum(v[0]=='FIRE_TIME' for v in events)==sum(v[0]=='FIRE_TIME_2' for v in events)==1;timing.append(path)
 assert len(timing)==2
 result={'status':'PASS_OFFLINE_RECOVERY_ONLY','configuration_cases':len(cases),'confirmed_pack_hash':CONFIRMED,'validated_pack_entries':len(pack),'two_marker_48_bone_clips':timing,'five_shot_claim':False,'game_started':False}
 save(OUT/'recovery-offline-checks.json',result,'offline fallback and encoding/reference checks')
 print(json.dumps(result))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['capture','restore','rollback','check']);ap.add_argument('--receipt');a=ap.parse_args()
 if a.action=='capture':print(capture())
 elif a.action=='restore':restore()
 elif a.action=='rollback':rollback(a.receipt)
 else:check()
