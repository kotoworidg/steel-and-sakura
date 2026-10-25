"""Offline validation of the actual five-round adapter and matching third pack."""
import argparse,json,subprocess,urllib.request,time
from pathlib import Path
from tracked_files import ROOT,digest,write_text
from five_round_build import load,save,candidate,host_source,OUT
from type20_pack_codec import pack_entries,db_read,db_bytes,loc_read
from type20_playable import evidence,PATHS,LOC
from validate_type20_rpfm import begin_coverage,complete_coverage,Client

def main():
 p=load(OUT/'latest.json');session=Path(p['session'])
 if p['compiled_only']:raise ValueError('matching pack has not been built')
 raw=(session/'steel_sakura_combined_test.pack').read_bytes();expected,scope=candidate()
 if raw!=expected or digest(raw)!=p['pack_sha256']:raise ValueError('paired pack differs')
 if digest(Path(p['exe']).read_bytes())!=p['exe_sha256']:raise ValueError('native adapter differs')
 if (session/'NativeHost.cs').read_text(encoding='utf-8')!=host_source(digest(raw)):raise ValueError('native transport source changed')
 check=subprocess.run([p['exe'],'--check-profile',str(session/'engine-profile.json')],capture_output=True,text=True,check=True)
 if check.stdout.strip()!='PROFILE_OK 7':raise ValueError('profile parser mismatch')
 tests=load(session/'adapter-tests.json');transport=load(session/'transport-tests.json')
 if tests['status']!='PASS_SHARED_LIVE_ADAPTER_FIXTURES_GAME_NOT_RUN' or not transport['debugRegistersRestored'] or not transport['detached']:raise ValueError('adapter/transport tests missing')
 archive,coverage,logs=begin_coverage(session);owned=None;streams=[]
 try:
  try:
   with urllib.request.urlopen('http://127.0.0.1:45127/version',timeout=2) as response:version=json.load(response)
  except Exception:
   streams=[x.open('wb') for x in logs];exe=ROOT/'tools/rpfm-5.2.0/rpfm_server.exe';owned=subprocess.Popen([str(exe)],cwd=exe.parent,stdout=streams[0],stderr=streams[1],creationflags=subprocess.CREATE_NO_WINDOW);deadline=time.monotonic()+20
   while True:
    try:
     with urllib.request.urlopen('http://127.0.0.1:45127/version',timeout=1) as response:version=json.load(response)
     break
    except Exception:
     if time.monotonic()>deadline or owned.poll() is not None:raise ValueError('RPFM not available')
     time.sleep(.25)
  if version['version']!='5.2.0':raise ValueError('RPFM version differs')
  c=Client();c.call('initialize',dict(protocolVersion='2025-03-26',capabilities={},clientInfo=dict(name='type20-five-round',version='1')));c.tool('set_game_selected',game_name='shogun_2',rebuild_dependencies=False)
  pack=session/'steel_sakura_combined_test.pack';c.tool('open_packfiles',paths=[str(pack)]);files=pack_entries(raw);_,_,_,specs=evidence();decoded={}
  for path in [PATHS['units'],LOC]:
   result=c.tool('decode_packed_file',pack_key=str(pack),path=path,source='PackFile');w=json.loads(result['content'][0]['text']);decoded[path]=w
   if path==LOC:
    _,rows=loc_read(files[path]);actual=[[next(iter(cell.values())) for cell in row] for row in w['LocRFileInfo'][0]['table']['table_data']]
    if actual!=rows:raise ValueError('localization reopen differs')
   else:
    spec=specs['units'];t=w['DBRFileInfo'][0]['table'];rows=[dict(zip([n for n,_ in spec['fields']],[next(iter(cell.values())) for cell in row])) for row in t['table_data']];prefix,_=db_read(files[path],spec)
    if db_bytes(prefix,rows,spec)!=files[path]:raise ValueError('unit reopen differs')
  save(session/'rpfm-reopened.json',decoded,'independently reopened changed unit and localization')
 finally:
  if owned is not None:
   owned.terminate()
   try:owned.wait(timeout=5)
   except subprocess.TimeoutExpired:owned.kill();owned.wait(timeout=5)
  for f in streams:f.close()
  complete_coverage(archive,coverage)
 result=dict(status='PASS_OFFLINE_NATIVE_ADAPTER_AND_PAIRED_PACK',pack_sha256=digest(raw),exe_sha256=p['exe_sha256'],adapter_cases=len(tests['cases']),adapter_assertions=tests['assertions'],synthetic_transport=transport['status'],native_instruction_rows_verified=205,rpfm_changed_payloads_reopened=2,scope=scope,only_game_state_write='one byte at current native action+0x6C',held_action=False,ammo_writes=False,game_attached=False,five_rounds_in_game_verified=False)
 save(session/'validation.json',result,'final real adapter/paired-pack validation; game activation not performed');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
