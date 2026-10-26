"""Banzai OFFLINE build/check/rollback. Never attaches, installs, or starts the game.
All workspace changes use tracked transactions; compiler output is pre-journalled.
No installation or runtime activation command is provided.
"""
import argparse,datetime,hashlib,json,os,struct,subprocess,sys,uuid
from pathlib import Path
from tracked_files import ROOT,write_bytes,write_text,digest,rollback as undo
GAME=Path('D:/Games/Total War - SHOGUN 2')
FALLBACK=ROOT/'build/type20-auto-cycle/confirmed-burst.pack'
CONFIRMED='0B497A435F4E28C2C068D7C90B60BA9D0C0FFA353BABD46242EF2FED2222D270'
DLL_HASH='022FAE2E2DA92B59B8B1B8EE52887003C624E3C8ECA060B209F5D792A7F874F5'
EXE_HASH='0AB284186E0BE3FBCDE34E2F800E3C0328008F3219490C7C25E822ADD837C4A9'
CSC=Path('C:/Windows/Microsoft.NET/Framework/v4.0.30319/csc.exe')
OUT=ROOT/'build/banzai'

def utc():return datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
def save(p,obj,reason):return write_text(p,json.dumps(obj,indent=2)+'\n','Banzai '+reason)
def hashfile(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest().upper()

def pack_index(path):
 """Bounded read of observed PFH3 header/index, including timestamp flag."""
 with path.open('rb') as f:
  h=f.read(32)
  if h[:4]!=b'PFH3':return None
  flags,deps,dep_size,count,size=struct.unpack_from('<5I',h,4)
  if count>1000000 or size>64000000 or dep_size>1000000:raise ValueError('unreasonable pack index')
  f.seek(32+dep_size);index=f.read(size);pos=0;offset=32+dep_size+size;rows=[];seen=set()
  for _ in range(count):
   length=struct.unpack_from('<I',index,pos)[0];pos+=4
   if flags&0x40:pos+=8
   end=index.index(b'\0',pos);name=index[pos:end].decode('utf-8').replace('\\','/');pos=end+1
   if name.casefold() in seen:raise ValueError('duplicate packed path: '+str(path)+' '+name)
   seen.add(name.casefold());rows.append((name,offset,length));offset+=length
  if pos!=size or offset!=path.stat().st_size:raise ValueError('pack index does not cover file exactly: '+str(path))
  return rows

def decode_threshold(raw):
 # Observed v0 schema: StringU16 key, I32 value. No invented fields.
 if raw[:4]!=bytes.fromhex('fdfefcff'):raise ValueError('unknown DB header')
 guid_len=struct.unpack_from('<H',raw,4)[0];pos=6+guid_len*2
 if guid_len!=36 or raw[pos]!=1:raise ValueError('unknown DB header flags')
 count=struct.unpack_from('<I',raw,pos+1)[0];pos+=5;rows={}
 if count>100:raise ValueError('unexpected threshold count')
 for _ in range(count):
  ln=struct.unpack_from('<H',raw,pos)[0];pos+=2
  key=raw[pos:pos+ln*2].decode('utf-16-le');pos+=ln*2
  value=struct.unpack_from('<i',raw,pos)[0];pos+=4
  if key in rows:raise ValueError('duplicate threshold key')
  rows[key]=value
 if pos!=len(raw):raise ValueError('threshold payload trailing bytes')
 return rows

def snapshots():
 paths=[GAME/'shogun2.exe',GAME/'empire.retail.dll',GAME/'data/steel_sakura_combined_test.pack',FALLBACK,
 ROOT/'build/type20-suppression/confirmed-no-reload-bursts.pack',ROOT/'build/type20-five-shot/confirmed-suppression-r2.pack',
 GAME/'mod_list.txt',Path(os.environ['APPDATA'])/'The Creative Assembly/Shogun2/scripts/user.script.txt']
 paths+=list((GAME/'data').glob('*otomo*.pack'))+list((GAME/'data/MyMods').glob('*.pack'))
 return {str(p):hashfile(p) for p in paths if p.is_file()}

def check():
 before=snapshots()
 if before[str(GAME/'shogun2.exe')]!=EXE_HASH or before[str(GAME/'empire.retail.dll')]!=DLL_HASH:raise ValueError('unsupported engine; stop')
 if before[str(FALLBACK)]!=CONFIRMED or before[str(GAME/'data/steel_sakura_combined_test.pack')]!=CONFIRMED:raise ValueError('recovered confirmed pack differs; stop without installing anything')
 sys.path.insert(0,str(ROOT/'tools/python-research'))
 import pefile,capstone
 pe=pefile.PE(str(GAME/'empire.retail.dll'),fast_load=True);cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
 # New bounded checks, all rooted at established native instruction boundaries.
 anchors={0xc0c534:('mov','ebp, 1'),0xc0c624:('mov','ebp, dword ptr [eax + 0xc]'),
 0xc0c6b0:('mov','ebp, dword ptr [esp + 0x64]'),0xc0c6bc:('cmp','ebp, 0xa'),
 0x3d453a:('call','0x1a9290'),0x3d4558:('call','0x427400'),
 0x3d45da:('mov','al, 1'),0x3d45dd:('mov','byte ptr [esi + 0x6e], al'),
 0x14ad52:('mov','eax, dword ptr [esi + 0xf1c]')}
 native=[]
 for rva,expected in anchors.items():
  ins=next(cs.disasm(pe.get_data(rva,16),rva));actual=(ins.mnemonic,ins.op_str)
  if actual!=expected:raise ValueError('native instruction mismatch '+hex(rva)+str(actual))
  native.append({'rva':hex(rva),'bytes':ins.bytes.hex(),'instruction':' '.join(actual)})
 strings={hex(r):pe.get_data(r,80).split(b'\0')[0].decode('ascii') for r in [0x1655764,0x1655788,0x1655794]}
 if list(strings.values())!=['unit_experience_thresholds_tables','land_level_','%02u']:raise ValueError('crash key construction changed')
 tables=[];unsupported=[]
 for path in sorted((GAME/'data').rglob('*.pack')):
  index=pack_index(path)
  if index is None:unsupported.append(str(path));continue
  for name,offset,length in index:
   if name.startswith('db/unit_experience_thresholds_tables/'):
    with path.open('rb') as f:f.seek(offset);raw=f.read(length)
    tables.append({'pack':str(path),'entry':name,'offset':offset,'size':length,'payload_sha256':digest(raw),'rows':decode_threshold(raw)})
 expected={prefix+('%02d'%i) for prefix in ['land_level_','naval_level_'] for i in range(1,10)}
 if not tables or not any(set(t['rows'])==expected for t in tables):raise ValueError('required vanilla experience rows absent')
 schema=ROOT/'tools/rpfm-config/data/schemas/schema_sho2.ron';txt=schema.read_text(encoding='utf-8');section=txt.split('"unit_experience_thresholds_tables": [',1)[1].split('"unit_fatigue_effects_tables"',1)[0]
 if 'field_type: StringU16' not in section or 'field_type: I32' not in section or 'version: 0' not in section:raise ValueError('schema mismatch')
 # Read preserved evidence, not mutable dumps. Preserve previous nine-dump inventory.
 pointer=json.loads((ROOT/'build/final-attempt/recovery-latest.json').read_text());session=Path(pointer['session']);inv=json.loads((session/'inventory.json').read_text());dumps=[]
 from final_recovery import dump_summary
 for row in inv:
  if not row['original_path'].lower().endswith('.dmp'):continue
  path=Path(row['snapshot'])
  if hashfile(path)!=row['sha256']:raise ValueError('preserved crash evidence changed')
  summary=dump_summary(path);b=path.read_bytes();n,dr=struct.unpack_from('<II',b,8)
  streams={struct.unpack_from('<III',b,dr+12*i)[0]:struct.unpack_from('<III',b,dr+12*i)[1:] for i in range(n)}
  q=streams[6][1];size,context=struct.unpack_from('<II',b,q+160)
  regs={name:struct.unpack_from('<I',b,context+off)[0] for name,off in [('eax',176),('ecx',172),('ebp',180),('eip',184)]}
  finding={'original':row['original_path'],'preserved':str(path),'sha256':row['sha256'],'exception':summary['exception_code'],'fault':summary['fault_module'],'registers':regs}
  if any(x['rva']=='0xc0c624' for x in summary['fault_module']):
   finding.update(inferred_missing_key='land_level_%02d'%regs['ebp'],inference_basis='constructor literal and intact loop counter; heap key not captured',table_count_after_failed_lookup=regs['ecx'])
  dumps.append(finding)
 # The fallback stays byte-for-byte identical, including every unrelated payload.
 from validate_free_fire_experiment import entries
 from inspect_anim_events import read_anim
 payloads=entries(FALLBACK);clips=[]
 for name,raw in payloads.items():
  if name.startswith('animations/steel_sakura/type20_burst/') and name.endswith('.anim'):
   clip=read_anim(raw);events=[e for block in clip['event_blocks'] for e in block if e[0].startswith('FIRE_TIME')]
   if len(clip['bones'])!=48 or [e[0] for e in events]!=['FIRE_TIME','FIRE_TIME_2']:raise ValueError('confirmed clip differs')
   clips.append({'path':name,'events':events,'duration':clip['duration']})
 if len(clips)!=2:raise ValueError('confirmed two-shot clips missing')
 return {'status':'PASS_READ_ONLY_PREFLIGHT','baseline_sha256':CONFIRMED,'preserved_hashes':before,'native_anchors':native,'experience_constructor_strings':strings,
  'experience_tables':tables,'unsupported_pack_formats':unsupported,'schema_sha256':hashfile(schema),'preserved_crashes':dumps,'baseline_entries':len(payloads),'baseline_clips':clips,
  'recovery_gameplay_confirmed':False,'live_unit_identity_verified':False,'live_cancellation_verified':False,'five_shots_verified':False,
  'conclusion':'Current experience data contains all 18 rows. Historical land_level_01 lookup failed with an empty table; loading cause and reported firing freeze remain unresolved.'}

def compiler_transaction(exe,sources):
 # The compiler cannot return bytes to tracked_files, so reserve a tracked output,
 # then preserve that original with an immutable pending record BEFORE compilation.
 init=write_bytes(exe,b'','Banzai reserve compiler output; absent original recorded')
 archive=ROOT/'backups'/('banzai-compiler-'+utc()+'-'+uuid.uuid4().hex[:8]);archive.mkdir(parents=True,exist_ok=False)
 original=archive/'original.bin';original.write_bytes(exe.read_bytes())
 record={'created_utc':utc(),'original_path':str(exe),'original_exists':True,'original_sha256':hashfile(exe),'backup_path':str(original),'operation':'external_pending','expected_new_sha256':None,'reason':'Banzai compiler output backup before invocation'}
 (archive/'pending.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
 r=subprocess.run([str(CSC),'/nologo','/noconfig','/platform:x86','/target:exe','/debug-','/optimize+','/r:System.dll','/r:System.Core.dll','/r:System.Web.Extensions.dll','/out:'+str(exe)]+[str(p) for p in sources],capture_output=True,text=True,timeout=60)
 record.update(operation='write',expected_new_sha256=hashfile(exe),rollback_command='python -B scripts/tracked_files.py rollback "'+str(archive/'manifest.json')+'"')
 (archive/'manifest.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
 if r.returncode:raise RuntimeError(r.stdout+r.stderr)
 return [init,str(archive/'manifest.json')],{'compiler':str(CSC),'sha256':hashfile(CSC),'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr}

def source_manifests():
 records=[]
 for m in (ROOT/'backups').glob('tracked-*/manifest.json'):
  r=json.loads(m.read_text());p=Path(r.get('original_path',''))
  if p.is_relative_to(ROOT/'src/banzai') and r.get('reason','').startswith('Banzai '):records.append((r['created_utc'],str(m)))
 return [m for _,m in sorted(records)]

def build():
 before=check();session=OUT/utc();session.mkdir(parents=True,exist_ok=False);ledger=source_manifests();exe=session/'BanzaiOffline.exe'
 manifests,compiler=compiler_transaction(exe,sorted((ROOT/'src/banzai').glob('*.cs')));ledger+=manifests
 def run(args):
  r=subprocess.run([str(exe)]+args,capture_output=True,text=True,timeout=60)
  if r.returncode:raise RuntimeError(r.stdout+r.stderr)
  return json.loads(r.stdout)
 tests=run(['--self-test']);replay=run(['--replay',str(ROOT/'build/burst5/runtime/20261022T121237.115098Z')])
 # The built executable has no P/Invoke imports or references to the old host.
 sys.path.insert(0,str(ROOT/'tools/python-research'));import pefile
 pe=pefile.PE(str(exe),fast_load=True)
 if pe.FILE_HEADER.Machine!=0x14c or pe.OPTIONAL_HEADER.Magic!=0x10b:raise ValueError('not PE32 x86')
 source='\n'.join(p.read_text() for p in (ROOT/'src/banzai').glob('*.cs'))
 for forbidden in ['DllImport','WriteProcessMemory','DebugActiveProcess','SetThreadContext','Process.Start','LoadLibrary','GetProcAddress']:
  if forbidden in source:raise ValueError('offline build acquired native capability: '+forbidden)
 if snapshots()!=before['preserved_hashes']:raise ValueError('game/fallback files changed during offline build')
 save(session/'preflight.json',before,'evidence and original hashes preserved')
 save(session/'compiler.json',compiler,'compiler diagnostics')
 save(session/'tests.json',tests,'deterministic faults and random schedules; model only')
 save(session/'replay.json',replay,'real trace proves missing identity; does not authorize live operation')
 dist=ROOT/'dist/banzai'/session.name
 ledger.append(write_bytes(dist/'BanzaiOffline.exe',exe.read_bytes(),'Banzai publish offline executable; cannot activate engine hooks'))
 ledger.append(write_bytes(dist/'CONFIRMED_TWO_SHOT.pack',FALLBACK.read_bytes(),'Banzai preserve confirmed playable pack unchanged; not a five-shot pack'))
 save(dist/'manifest.json',{'status':'OFFLINE_CORE_ONLY_NO_GAME_ADAPTER','five_shots_in_game':False,'files':{p.name:hashfile(p) for p in dist.iterdir() if p.is_file()},'source_hashes':{str(p.relative_to(ROOT)):hashfile(p) for p in (ROOT/'src/banzai').glob('*.cs')},'baseline_unit':'TYPE20 BURST TEST - two timed shots','limitations':['No verified native unit identity/order/death mapping.','Core assumes externally supplied verified proofs; real adapter is intentionally absent.','Intra-animation repeats are an untested alternative, not a working game implementation.'],'rollback':'python -B scripts/banzai.py rollback'},'release provenance and limitations')
 save(session/'rollback-ledger.json',{'transactions':ledger,'preserve_evidence':True,'game_changes':False},'one-command workspace rollback')
 save(OUT/'latest.json',{'session':str(session),'distribution':str(dist)},'latest offline attempt')
 rollback_check(session,dry=True)
 print(json.dumps({'status':'BUILT_OFFLINE_CORE_LIVE_BLOCKED','session':str(session),'distribution':str(dist),'tests':len(tests['cases']),'assertions':tests['assertions'],'random_schedules':tests['randomSchedules'],'real_native_pairs':replay['pairedNativeDebits'],'installed_pack_unchanged':True},indent=2))

def rollback_check(session,dry=False):
 ledger=json.loads((session/'rollback-ledger.json').read_text())['transactions'];sim={}
 for manifest in reversed(ledger):
  r=json.loads(Path(manifest).read_text());p=Path(r['original_path']);current=sim.get(str(p),hashfile(p) if p.exists() else None)
  if current!=r['expected_new_sha256']:raise ValueError('later work or already rolled back; refusing overwrite: '+str(p))
  if r['original_exists'] and hashfile(r['backup_path'])!=r['original_sha256']:raise ValueError('backup hash changed')
  sim[str(p)]=r['original_sha256'] if r['original_exists'] else None
 if not dry:
  receipts=[undo(m) for m in reversed(ledger)]
  save(session/('rollback-'+utc()+'.json'),{'receipts':receipts,'game_untouched':True},'rollback evidence retained')
 return {'preflight_passed':True,'transactions':len(ledger),'dry_run':dry,'game_changes':False}

if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('action',choices=['check','build','rollback']);ap.add_argument('--dry-run',action='store_true');a=ap.parse_args()
 if a.action=='check':print(json.dumps(check(),indent=2))
 elif a.action=='build':build()
 else:
  session=Path(json.loads((OUT/'latest.json').read_text())['session']);print(json.dumps(rollback_check(session,a.dry_run),indent=2))
