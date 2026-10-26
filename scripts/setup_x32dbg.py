"""Approved portable x32dbg setup only. Never launches/attaches a debugger.
Every downloaded/extracted file uses tracked_files; rollback preserves backups.
"""
from pathlib import Path, PurePosixPath
import argparse, datetime, hashlib, io, json, sys, urllib.request, zipfile
from tracked_files import ROOT, write_bytes, write_text, rollback, digest
TAG='2026.05.27'
ASSET='snapshot_2026-05-27_12-11.zip'
SHA256='D41966DFC5B435A372798245300CA0AB7BB8E48BDBF48512C6FB20FCCA427697'
SIZE=31526833
URL=f'https://github.com/x64dbg/x64dbg/releases/download/{TAG}/{ASSET}'
API=f'https://api.github.com/repos/x64dbg/x64dbg/releases/tags/{TAG}'
DEST=ROOT/'tools'/'x64dbg'/TAG
DOWNLOADS=ROOT/'build'/'tool-downloads'/'x64dbg'
GUARDS={
 'D:/Games/Total War - SHOGUN 2/empire.retail.dll':'022FAE2E2DA92B59B8B1B8EE52887003C624E3C8ECA060B209F5D792A7F874F5',
 'D:/Games/Total War - SHOGUN 2/data/steel_sakura_combined_test.pack':'1737D02D67F0C9100BBCC5255057C12B532F9805482D18ADC910542653D96DCD',
 str(ROOT/'build/type20-auto-cycle/confirmed-burst.pack'):'0B497A435F4E28C2C068D7C90B60BA9D0C0FFA353BABD46242EF2FED2222D270',
 str(ROOT/'build/type20-suppression/confirmed-no-reload-bursts.pack'):'56CCB4B44FC1520C379045ED3EC30D3EA13D6B3FB5BCF701A7259CC19EAD1299',
 str(ROOT/'build/type20-five-shot/confirmed-suppression-r2.pack'):'1737D02D67F0C9100BBCC5255057C12B532F9805482D18ADC910542653D96DCD',
 str(ROOT/'build/type20-research/current-fallback.pack'):'0A5CC547E5515CB813FB5341335E2A4D24E3596C7C9D7D3F32F39362FBB122F8',
}
def guards():
 result={p:digest(Path(p).read_bytes()) for p in GUARDS}
 if result!=GUARDS:raise RuntimeError('Preservation guard differs; inspect before continuing')
 return result

def fetch(url,limit):
 req=urllib.request.Request(url,headers={'User-Agent':'Steel-Sakura-Approved-Tool-Setup','Accept':'application/vnd.github+json' if url==API else 'application/octet-stream'})
 with urllib.request.urlopen(req,timeout=90) as response:
  data=response.read(limit+1)
 if len(data)>limit:raise ValueError('Download exceeds expected size bound')
 return data

def setup():
 before=guards()
 release=json.loads(fetch(API,2000000))
 assets=[x for x in release['assets'] if x['name']==ASSET]
 if len(assets)!=1:raise ValueError('Official release asset is missing or ambiguous')
 asset=assets[0]
 if release['tag_name']!=TAG or asset['size']!=SIZE or asset['digest'].upper()!='SHA256:'+SHA256 or asset['browser_download_url']!=URL:
  raise ValueError('Official release metadata differs from pinned approval source')
 archive=fetch(URL,SIZE)
 if len(archive)!=SIZE or digest(archive)!=SHA256:raise ValueError('Official archive size/hash mismatch')
 # Validate every member and its data before any extraction write.
 entries=[];seen=set()
 with zipfile.ZipFile(io.BytesIO(archive)) as package:
  if sum(x.file_size for x in package.infolist())>500*1024*1024:raise ValueError('Unexpected unpacked size')
  for info in package.infolist():
   raw=info.filename
   posix=PurePosixPath(raw)
   if '\\' in raw or ':' in raw or posix.is_absolute() or '..' in posix.parts or any(x.rstrip(' .')!=x for x in posix.parts):raise ValueError('Unsafe archive member: '+raw)
   target=(DEST/Path(*posix.parts)).resolve()
   if not target.is_relative_to(DEST.resolve()):raise ValueError('Archive traversal')
   if (info.external_attr>>16)&0o170000==0o120000:raise ValueError('Archive symlink')
   if info.is_dir():continue
   key=str(target).casefold()
   if key in seen:raise ValueError('Duplicate archive destination')
   seen.add(key);data=package.read(info)
   entries.append((target,data))
 transactions=[];inventory=[]
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
 receipt_path=DOWNLOADS/f'setup-{stamp}.json'
 def put(path,data,reason):
  path=Path(path)
  if path.exists() and path.read_bytes()==data:return None
  manifest=write_bytes(path,data,reason)
  transactions.append(manifest)
  # Checkpoint after every write so interrupted extraction remains reversible.
  checkpoint={'status':'IN_PROGRESS','transactions':transactions,'destination':str(DEST),'approval':'SETUP_ONLY_NO_ATTACH_OR_EXECUTION'}
  write_text(DOWNLOADS/f'checkpoint-{stamp}.json',json.dumps(checkpoint,indent=2)+'\n','Record reversible debugger setup progress')
  return manifest
 put(DOWNLOADS/ASSET,archive,'Store verified official portable debugger archive')
 put(DOWNLOADS/f'release-{TAG}.json',(json.dumps(release,indent=2)+'\n').encode(),'Preserve official tool provenance metadata')
 for target,data in entries:
  manifest=put(target,data,'Extract approved official portable debugger; setup only')
  inventory.append({'path':str(target),'sha256':digest(data),'size':len(data),'manifest':manifest})
 x32=[x for x in inventory if Path(x['path']).name.lower()=='x32dbg.exe']
 if len(x32)!=1:raise ValueError('Expected one x32dbg executable')
 plugins=[x['path'] for x in inventory if Path(x['path']).suffix.lower() in ('.dp32','.dp64')]
 receipt={'status':'SETUP_COMPLETE_NOT_LAUNCHED','created_utc':stamp,'source':URL,'release':release['html_url'],'published_sha256':SHA256,'archive_size':SIZE,'destination':str(DEST),'x32dbg':x32[0],'plugins':plugins,'files':inventory,'transactions':transactions,'preserved_before':before,'preserved_after':guards(),'runtime_attach_performed':False,'debugger_executed':False,'experimental_patch_installed':False,'rollback_command':f'python -B scripts/setup_x32dbg.py rollback --receipt "{receipt_path}"'}
 manifest=write_text(receipt_path,json.dumps(receipt,indent=2)+'\n','Record verified debugger setup and complete rollback list')
 print(json.dumps({'receipt':str(receipt_path),'receipt_manifest':manifest,'x32dbg':x32[0]['path'],'archive_sha256':SHA256,'files':len(inventory),'plugins':plugins,'preservation_guards':len(before),'rollback_command':receipt['rollback_command']}))

def undo(receipt_path):
 path=Path(receipt_path).resolve()
 if not path.is_relative_to(DOWNLOADS):raise ValueError('Receipt must be in project download directory')
 receipt=json.loads(path.read_text(encoding='utf-8'))
 # Preflight every modified file before changing anything.
 for manifest in receipt['transactions']:
  r=json.loads(Path(manifest).read_text(encoding='utf-8'));p=Path(r['original_path'])
  if not p.exists() or digest(p.read_bytes())!=r['expected_new_sha256']:raise ValueError('Later change prevents safe rollback: '+str(p))
 results=[rollback(m) for m in reversed(receipt['transactions'])]
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
 record=write_text(DOWNLOADS/f'rollback-{stamp}.json',json.dumps({'receipt':str(path),'transactions':results},indent=2)+'\n','Record reversible portable debugger rollback')
 print(record)
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=['setup','rollback']);parser.add_argument('--receipt');args=parser.parse_args()
 if args.action=='setup':setup()
 elif not args.receipt:parser.error('--receipt required for rollback')
 else:undo(args.receipt)
