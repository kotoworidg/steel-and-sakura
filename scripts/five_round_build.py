"""Build an actual five-round native-action adapter and its matching pack.
Build/test never launch the game or activate the hook. Native analysis uses hash-checked development copies; no proprietary binary enters the release.
"""
import argparse,base64,datetime,hashlib,io,json,os,struct,subprocess,sys,uuid,zipfile
from pathlib import Path
from tracked_files import ROOT,write_bytes,write_text,digest
from type20_pack_codec import pack_entries,pack_bytes,db_read,db_bytes,loc_read,loc_bytes
from inspect_anim_events import read_anim,event_bytes
from type20_playable import evidence,PATHS,LOC
OUT=ROOT/'build/five_round';SOURCE=ROOT/'src/five_round'
GAME=Path('D:/Games/Total War - SHOGUN 2')
ENGINE='022FAE2E2DA92B59B8B1B8EE52887003C624E3C8ECA060B209F5D792A7F874F5'
SUPPORTED={'shogun2.exe':{'size':312320,'sha256':'0AB284186E0BE3FBCDE34E2F800E3C0328008F3219490C7C25E822ADD837C4A9','file_version':'1,1,0,0','product_version':'3.1.0.0'},'empire.retail.dll':{'size':25793536,'sha256':ENGINE,'file_version':'1,0,0,0','product_version':'1,0,0,0'}}
PLAYABLE=ROOT/'build/type20-playable/iteration-02'
CSC=Path('C:/Windows/Microsoft.NET/Framework/v4.0.30319/csc.exe')

def utc():return datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,obj,reason):return write_text(p,json.dumps(obj,indent=2)+'\n','Five-round '+reason)

def candidate():
 source=(PLAYABLE/'steel_sakura_combined_test.pack').read_bytes()
 if digest(source)!='B0E51ABC7D1FC4FB0D1DE37CA106B72AD55C6DE230B19C309C3BF92AF2EA2280':raise ValueError('preserved playable release differs')
 base=pack_entries(source);files=dict(base);clips=[]
 for path in ['animations/steel_sakura/type20_burst/stand.anim','animations/steel_sakura/type20_burst/kneel.anim']:
  raw=files[path];a=read_anim(raw);blocks=a['event_blocks'];second=[e for b in blocks for e in b if e[0]=='FIRE_TIME_2']
  if len(second)!=1:raise ValueError('ambiguous secondary event')
  second[0][1]='0.50';new=raw[:a['event_offset']]+event_bytes(blocks);b=read_anim(new)
  if len(b['bones'])!=48 or new[:b['event_offset']]!=raw[:a['event_offset']] or b['duration']<=.5:raise ValueError('original motion/rig changed')
  files[path]=new;clips.append(dict(path=path,first=[e[1] for x in b['event_blocks'] for e in x if e[0]=='FIRE_TIME'][0],last='0.50',motion_bytes_unchanged=True))
 _,_,_,specs=evidence();prefix,rows=db_read(files[PATHS['units']],specs['units']);rows[0]['on_screen_name']='JSDF Type 20 - Five-Round Runtime';files[PATHS['units']]=db_bytes(prefix,rows,specs['units'])
 prefix,rows=loc_read(files[LOC]);rows[0][1]='JSDF Type 20 - Five-Round Runtime';rows[1][1]='Five-round engine-adapter candidate. Requires the separately activated Type20FiveRound runtime. Without it the native fallback has two shots.';rows[2][1]='The runtime re-arms the primary native firing slot three times within a 0.50-second paired animation window, preserving native request validation, ammunition debit, projectile spawning and action completion. No held action, DLL injection or installed binary patch. Five native emissions need in-game verification. Coarse simulation updates or cancellation produce shorter bursts; no simultaneous catch-up volley. Precision, 450 range, 210 ammunition and native ability tuning remain from v0.1.0.';files[LOC]=loc_bytes(prefix,rows)
 allowed={c['path'] for c in clips}|{PATHS['units'],LOC};changed={p for p in base if base[p]!=files[p]}
 if changed!=allowed or set(files)!=set(base):raise ValueError('unexpected pack scope')
 return pack_bytes(files),dict(status='PACK_VALIDATED_NOT_GAME_TESTED',source_sha256=digest(source),changed_payloads=sorted(changed),preserved_payloads=len(base)-len(changed),clips=clips,projectiles_per_native_event=1,extra_shots_require_runtime=True)

def profile(pack_hash):
 import pefile
 for name,identity in SUPPORTED.items():
  installed=GAME/name
  if not installed.is_file() or installed.stat().st_size!=identity['size'] or digest(installed.read_bytes())!=identity['sha256']:raise ValueError('unsupported engine binary: '+name)
  preserved=OUT/'binary-baseline'/name
  if not preserved.is_file():write_bytes(preserved,installed.read_bytes(),'Five-round preserve pinned development binary before native analysis')
  if preserved.stat().st_size!=identity['size'] or digest(preserved.read_bytes())!=identity['sha256']:raise ValueError('development binary copy differs: '+name)
 raw=(OUT/'binary-baseline/empire.retail.dll').read_bytes()
 pe=pefile.PE(data=raw);base=pe.OPTIONAL_HEADER.ImageBase
 old=load(ROOT/'build/type20-five-shot/limit-audit.json');count=0
 for i in old['code']['dispatch_B']:
  rva=int(i['address'],16)-base;expected=bytes.fromhex(i['bytes'])
  if pe.get_data(rva,len(expected))!=expected:raise ValueError('preserved native instruction differs')
  count+=1
 anchors={0x3d438a:'33ed',0x3b3042:'c20400',0x3d453a:'e8514dddff',0x3d45b7:'c7461800000000'}
 for rva,expected in anchors.items():
  if pe.get_data(rva,len(bytes.fromhex(expected)))!=bytes.fromhex(expected):raise ValueError('native site differs')
 if abs(struct.unpack('<f',pe.get_data(0x15b2448,4))[0]-.1)>1e-8:raise ValueError('native quantum changed')
 reloc=[e.rva for block in pe.DIRECTORY_ENTRY_BASERELOC for e in block.entries if e.type==3];checks=[]
 for rva,size in [(0x3d4320,0x2e3),(0x3b3030,0x15),(0x3d2ef0,0x2f),(0x1a9290,0x12d),(0x427400,32),(0x420d00,0x6c),(0x15b2448,4)]:
  b=pe.get_data(rva,size);mask=bytearray(b'\xff'*len(b))
  for loc in reloc:
   for offset in range(4):
    if rva<=loc+offset<rva+size:mask[loc+offset-rva]=0
  checks.append(dict(rva=rva,bytes=base64.b64encode(b).decode(),mask=base64.b64encode(mask).decode()))
 return dict(engine_sha256=ENGINE,pack_sha256=pack_hash,burst_size=5,interval_ms=100,last_marker_ms=500,hold_action=False,ammo_writes=False,only_action_write_offset='0x6C',native_instruction_rows_verified=count,native_sites={hex(k):v for k,v in anchors.items()},code_checks=checks,live_test_performed=False,supported_binaries=SUPPORTED,
  runtime_changes=[dict(location='current native action + 0x6C',original='01',replacement='00',purpose='Re-arm one already-fired primary slot; at most three times before native 500 ms second event',restore='01 only if an unconsumed reset still has the same owner and tick'),dict(location='owned thread DR0..DR3/DR6/DR7',original='Read and saved per thread before arming; existing enabled slots refused',replacement='image+3D438A, image+3B3042, image+3D453A, image+3D45B7; DR6=0; DR7=0x455',purpose='Execution breakpoints; no code-byte patch',restore='Saved original registers; DR0..DR3 and DR7 readback before detach'),dict(location='thread EIP at image+3D453A',original='Native next instruction',replacement='image+3D45BE only when an added primary request fails adapter checks',purpose='Skip only rejected extra emission; original slots continue normally',restore='One instruction-flow decision; no persistent code patch')],
  read_only_offsets={'action':['+04 actor','+14 battle-context pointer','+38 target','+6D secondary flag','+6E completion flag','+88 animation'],'actor':['+1D8 100 ms native tick','+1F8 variant','+214 unit','+474 current-animation pointer'],'unit':['+28 terminated UTF-16 exact unit key','+F78 native shared ammunition'],'metadata':['+90 first time','+94 first valid','+98 second time','+9C second valid']},installed_binary_patch_bytes=[])

def once(s,old,new):
 if s.count(old)!=1:raise ValueError('native host source changed at '+old[:70])
 return s.replace(old,new,1)

def host_source(pack_hash):
 s=(SOURCE/'NativeHost.cs').read_text(encoding='utf-8')
 s=once(s,'__FIVE_ROUND_PACK_SHA256__',pack_hash)
 for forbidden in ['c[176]&=','memory.Write(action+0x6e','CreateRemoteThread','VirtualAllocEx','hold-native-action']:
  if forbidden in s:raise ValueError('forbidden old activation behavior: '+forbidden)
 return s

def compile_exe(session,host,bridge):
 exe=session/'Type20FiveRound.exe';init=write_bytes(exe,b'','Five-round reserve compiler output')
 archive=ROOT/'backups'/('five-round-compiler-'+utc()+'-'+uuid.uuid4().hex[:8]);archive.mkdir(parents=True,exist_ok=False)
 original=archive/'original.bin';original.write_bytes(exe.read_bytes());record=dict(original_path=str(exe),original_exists=True,original_sha256=digest(exe.read_bytes()),backup_path=str(original),operation='external_pending',expected_new_sha256=None,created_utc=utc())
 (archive/'pending.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
 sources=[SOURCE/'NativeBurst.cs',SOURCE/'SelfTests.cs',host,bridge]
 p=subprocess.run([str(CSC),'/nologo','/noconfig','/platform:x86','/target:exe','/debug-','/optimize+','/r:System.dll','/r:System.Core.dll','/r:System.Web.Extensions.dll','/out:'+str(exe)]+[str(x) for x in sources],capture_output=True,text=True,timeout=45)
 if exe.exists():
  record.update(operation='write',expected_new_sha256=digest(exe.read_bytes()),rollback_command='python -B scripts/tracked_files.py rollback "'+str(archive/'manifest.json')+'"');(archive/'manifest.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
 save(session/'compiler.json',dict(exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr),'compiler diagnostics')
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 def run(args):
  r=subprocess.run([str(exe)]+args,capture_output=True,text=True,timeout=45)
  if r.returncode:raise RuntimeError(r.stdout+r.stderr)
  return json.loads(r.stdout)
 tests=run(['--self-test']);transport=run(['--bridge-self-test'])
 save(session/'adapter-tests.json',tests,'same live adapter fixture results; not game evidence')
 save(session/'transport-tests.json',transport,'synthetic process debugger transport and restoration')
 return exe,dict(tests=tests,transport=transport,compiler_transactions=[init,str(archive/'manifest.json')])

def build(prepare_only=False):
 raise RuntimeError("Historical five-round candidate is frozen after the unsuccessful gameplay test. Use scripts/prepare_projectile_evidence.py prepare for the separately approved evidence mode; no new combat build is authorized by this command.")

def _historical_build(prepare_only=False):
 core,pack_evidence=candidate();engine_profile=profile(digest(core));session=OUT/('build-'+utc())
 host=session/'NativeHost.cs';bridge=session/'BridgeTests.cs';write_text(host,host_source(digest(core)),'Five-round generate actual non-retaining native host');write_bytes(bridge,(ROOT/'src/burst5/BridgeTests.cs').read_bytes(),'Five-round preserve tested four-site transport fixture')
 exe,test_result=compile_exe(session,host,bridge)
 save(session/'engine-profile.json',engine_profile,'pinned native ABI and paired pack compatibility')
 save(session/'pack-validation.json',{**pack_evidence,'pack_sha256':digest(core)},'paired firing window and scope validation')
 if not prepare_only:
  ledger_path=ROOT/'build/type20-playable/iterations.json';ledger=load(ledger_path)
  if len(ledger)==3:
   if ledger[-1].get('version')!='0.2.0-five-round-runtime' or ledger[-1]['core_sha256']!=digest(core):raise ValueError('No further gameplay build iteration authorized')
  elif len(ledger)==2:
   save(ledger_path,ledger+[dict(iteration=3,version='0.2.0-five-round-runtime',core_sha256=digest(core),optional_sha256=digest((PLAYABLE/'steel_sakura_type20_suppression.pack').read_bytes()),status='EXPERIMENTAL_NATIVE_ADAPTER_GAME_TEST_PENDING')],'reserve final third gameplay iteration; stable v0.1 remains intact')
  else:raise ValueError('Only the third remaining gameplay build iteration is authorized')
  write_bytes(session/'steel_sakura_combined_test.pack',core,'Five-round build third gameplay candidate with native five-shot adapter window')
  write_bytes(session/'steel_sakura_type20_suppression.pack',(PLAYABLE/'steel_sakura_type20_suppression.pack').read_bytes(),'Five-round retain optional native suppression module unchanged')
 save(OUT/'latest.json',dict(session=str(session),exe=str(exe),compiled_only=prepare_only,pack_sha256=digest(core),exe_sha256=digest(exe.read_bytes())),'latest real adapter build pointer')
 print(json.dumps(dict(status='NATIVE_ADAPTER_BUILT_GAME_TEST_REQUIRED',session=str(session),compile_only=prepare_only,cases=len(test_result['tests']['cases']),assertions=test_result['tests']['assertions'],native_instructions_verified=engine_profile['native_instruction_rows_verified'],pack_sha256=digest(core),no_game_attachment=True,no_game_binary_writes=True),indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['compile','build']);a=p.parse_args();build(a.action=='compile')
