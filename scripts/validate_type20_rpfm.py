"""Independently reopen the playable packs in the existing RPFM 5.2.0 server.
Uses its headless local API. No GUI control, game launch, or game writes.
"""
import argparse,datetime,json,os,subprocess,time,urllib.request,uuid
from pathlib import Path
from tracked_files import ROOT,write_bytes,write_text,digest
from type20_playable import load,evidence,PATHS,LOC,JUNCTION,OPTIONAL,validate
from type20_pack_codec import pack_entries,db_read,db_bytes

def stamp():return datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
def save(p,obj,why):return write_text(p,json.dumps(obj,indent=2)+'\n','Type20 playable RPFM '+why)

def begin_coverage(session):
 paths=[ROOT/'tools/rpfm-config',Path(os.environ['APPDATA'])/'FrodoWazEre/rpfm/config']
 logs=[session/'rpfm.stdout.log',session/'rpfm.stderr.log']
 for p in logs:write_bytes(p,b'','Type20 playable RPFM reserve unique tool log')
 files={p.resolve() for d in paths for p in d.rglob('*') if p.is_file()}|set(logs)
 archive=ROOT/'backups'/('type20-rpfm-'+stamp()+'-'+uuid.uuid4().hex[:8]);archive.mkdir(parents=True,exist_ok=False);rows=[]
 for i,p in enumerate(sorted(files)):
  raw=p.read_bytes();saved=archive/'original'/('%04d-'%i+p.name);saved.parent.mkdir(parents=True,exist_ok=True)
  with saved.open('xb') as f:f.write(raw)
  if digest(saved.read_bytes())!=digest(raw):raise ValueError('tool-state backup differs')
  rows.append(dict(original_path=str(p),original_exists=True,original_sha256=digest(raw),backup_path=str(saved),expected_new_sha256=None,operation='external_pending'))
 record=dict(reason='RPFM headless reopen; pre-launch config/cache/log coverage',created_utc=stamp(),directories=[str(p) for p in paths],new_files_original_exists=False,records=rows,
  rollback_command='python -B scripts/validate_type20_rpfm.py restore --receipt "'+str(archive/'completed.json')+'"')
 (archive/'pending.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
 return archive,record,logs

def complete_coverage(archive,record):
 old={r['original_path']:r for r in record['records']};current={str(p.resolve()):p for d in record['directories'] for p in Path(d).rglob('*') if p.is_file()}
 current.update({r['original_path']:Path(r['original_path']) for r in record['records']})
 rows=[]
 for name,p in current.items():
  r=old.get(name,dict(original_path=name,original_exists=False,original_sha256=None,backup_path=None));r=dict(r);r['expected_new_sha256']=digest(p.read_bytes()) if p.exists() else None;r['operation']='write' if p.exists() else 'delete';rows.append(r)
 result={**record,'records':rows,'completed_utc':stamp(),'changed_files':[r['original_path'] for r in rows if r['expected_new_sha256']!=r['original_sha256']]}
 with (archive/'completed.json').open('x',encoding='utf-8') as f:f.write(json.dumps(result,indent=2)+'\n')
 return result

class Client:
 def __init__(self):self.sid=None;self.serial=0
 def call(self,method,params):
  self.serial+=1;headers={'Content-Type':'application/json','Accept':'application/json, text/event-stream'}
  if self.sid:headers['Mcp-Session-Id']=self.sid
  request=urllib.request.Request('http://127.0.0.1:45127/mcp',data=json.dumps(dict(jsonrpc='2.0',id=self.serial,method=method,params=params)).encode(),headers=headers)
  with urllib.request.urlopen(request,timeout=30) as response:
   self.sid=response.headers.get('Mcp-Session-Id',self.sid);text=response.read().decode()
  lines=[x[6:] for x in text.splitlines() if x.startswith('data: ')]
  message=json.loads(lines[-1] if lines else text)
  if 'error' in message:raise ValueError(message['error'])
  result=message['result']
  if result.get('isError'):raise ValueError(result)
  return result
 def tool(self,name,**args):return self.call('tools/call',{'name':name,'arguments':args})

def run():
 validation=validate();pointer=load(ROOT/'build/type20-playable/latest.json');session=Path(pointer['session'])
 archive,coverage,logs=begin_coverage(session);owned=None;streams=[];decoded={}
 try:
  try:
   with urllib.request.urlopen('http://127.0.0.1:45127/version',timeout=2) as response:version=json.load(response)
  except Exception:
   streams=[p.open('wb') for p in logs]
   exe=ROOT/'tools/rpfm-5.2.0/rpfm_server.exe'
   owned=subprocess.Popen([str(exe)],cwd=exe.parent,stdout=streams[0],stderr=streams[1],creationflags=subprocess.CREATE_NO_WINDOW)
   deadline=time.monotonic()+20
   while True:
    if owned.poll() is not None:raise ValueError('RPFM server exited during startup')
    try:
     with urllib.request.urlopen('http://127.0.0.1:45127/version',timeout=1) as response:version=json.load(response)
     break
    except Exception:
     if time.monotonic()>deadline:raise ValueError('RPFM startup timeout')
     time.sleep(.25)
  if version.get('version')!='5.2.0':raise ValueError('unexpected RPFM version')
  c=Client();c.call('initialize',dict(protocolVersion='2025-03-26',capabilities={},clientInfo=dict(name='steel-sakura-type20-playable',version='1')))
  c.tool('set_game_selected',game_name='shogun_2',rebuild_dependencies=False)
  _,_,_,specs=evidence()
  for filename in ['steel_sakura_combined_test.pack','steel_sakura_type20_suppression.pack']:
   path=session/filename;entries=pack_entries(path.read_bytes());c.tool('open_packfiles',paths=[str(path)])
   targets=([*PATHS.values(),LOC,JUNCTION] if filename=='steel_sakura_combined_test.pack' else list(entries))
   for internal in targets:
    result=c.tool('decode_packed_file',pack_key=str(path),path=internal,source='PackFile');wrapper=json.loads(result['content'][0]['text'])
    if internal.endswith('.loc'):
     from type20_pack_codec import loc_read
     _,expected=loc_read(entries[internal]);actual=wrapper['LocRFileInfo'][0]['table']['table_data'];rows=[[next(iter(cell.values())) for cell in row] for row in actual]
     if rows!=expected:raise ValueError('RPFM localization differs')
    else:
     name=internal.split('/')[1].removesuffix('_tables');spec=specs[name];table=wrapper['DBRFileInfo'][0]['table']
     if table['definition']['version']!=spec['version'] or [f['name'] for f in table['definition']['fields']]!=[n for n,_ in spec['fields']]:raise ValueError('RPFM schema differs')
     rows=[dict(zip([n for n,_ in spec['fields']],[next(iter(cell.values())) for cell in row])) for row in table['table_data']]
     prefix,_=db_read(entries[internal],spec)
     if db_bytes(prefix,rows,spec)!=entries[internal]:raise ValueError('RPFM field roundtrip differs: '+internal)
    decoded[filename+':'+internal]=wrapper
  save(session/'rpfm-reopened.json',decoded,'independent decoded tables and localization')
  result=dict(status='PASS_RPFM_INDEPENDENT_REOPEN',version=version,decoded_payloads=len(decoded),core_sha256=validation['core_sha256'],optional_sha256=validation['optional_sha256'],game_started=False,in_game_verified=False)
  save(session/'rpfm-validation.json',result,'successful schema/row/LOC reopen')
  print(json.dumps(result,indent=2))
 finally:
  if owned is not None:
   owned.terminate()
   try:owned.wait(timeout=5)
   except subprocess.TimeoutExpired:owned.kill();owned.wait(timeout=5)
  for stream in streams:stream.close()
  result=complete_coverage(archive,coverage);save(session/'rpfm-tool-state.json',{'receipt':str(archive/'completed.json'),'changed_files':result['changed_files']},'tool-state backup completion')

def restore(receipt):
 r=load(receipt)
 for row in r['records']:
  p=Path(row['original_path']);actual=digest(p.read_bytes()) if p.exists() else None
  if actual!=row['expected_new_sha256']:raise ValueError('tool file changed later')
  if not p.resolve().is_relative_to(ROOT):raise ValueError('external tool-state restore requires explicit review: '+str(p))
 # Research tool logs remain evidence. Restore changed pre-existing project config only.
 for row in r['records']:
  p=Path(row['original_path'])
  if row['original_exists'] and row['original_sha256']!=row['expected_new_sha256']:
   saved=Path(row['backup_path']);data=saved.read_bytes()
   if digest(data)!=row['original_sha256']:raise ValueError('tool-state backup changed')
   write_bytes(p,data,'Type20 playable RPFM restore previous tool configuration')

if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('action',choices=['run','restore']);ap.add_argument('--receipt',type=Path);a=ap.parse_args()
 if a.action=='run':run()
 elif a.receipt:restore(a.receipt.resolve())
 else:ap.error('--receipt required')
