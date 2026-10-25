"""Install/rollback the Type20 supported-mechanics package. Standard-library Python.
Targets only two Steel & Sakura pack names and the two mod-loading lists.
"""
import argparse,datetime,hashlib,json,os,re,shutil,subprocess,sys,uuid
from pathlib import Path
CORE='steel_sakura_combined_test.pack'
SUPP='steel_sakura_type20_suppression.pack'
BASELINE='0B497A435F4E28C2C068D7C90B60BA9D0C0FFA353BABD46242EF2FED2222D270'
ENGINE_HASHES={'shogun2.exe':'0AB284186E0BE3FBCDE34E2F800E3C0328008F3219490C7C25E822ADD837C4A9','empire.retail.dll':'022FAE2E2DA92B59B8B1B8EE52887003C624E3C8ECA060B209F5D792A7F874F5'}

def sha(data):return hashlib.sha256(data).hexdigest().upper()
def hashpath(p):return sha(p.read_bytes()) if p.is_file() else None
def utc():return datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
def user_script():return (Path(os.environ['APPDATA'])/'The Creative Assembly/Shogun2/scripts/user.script.txt').resolve()
def ensure_closed():
 if os.name=='nt':
  p=subprocess.run(['powershell','-NoProfile','-Command',"@(Get-Process -Name shogun2,shogun2.retail -ErrorAction SilentlyContinue).Count"],capture_output=True,text=True,check=True)
  if p.stdout.strip()!='0':raise ValueError('Close Shogun 2 before installing or rolling back')

def verify_game(game):
 game=game.resolve()
 for name,h in ENGINE_HASHES.items():
  if hashpath(game/name)!=h:raise ValueError('Unsupported or modified game binary: '+name)
 if not (game/'data').is_dir():raise ValueError('Game data directory missing')
 return game

def allowed(game):return {(game/'data'/CORE).resolve(),(game/'data'/SUPP).resolve(),(game/'mod_list.txt').resolve(),user_script()}

def decode_list(raw):
 for bom,enc in [(b'\xff\xfe','utf-16-le'),(b'\xfe\xff','utf-16-be'),(b'\xef\xbb\xbf','utf-8')]:
  if raw.startswith(bom):return bom,enc,raw[len(bom):].decode(enc)
 if b'\0' in raw:raise ValueError('Ambiguous loading-list encoding without BOM')
 try:return b'','utf-8',raw.decode('utf-8')
 except UnicodeDecodeError:return b'','cp1252',raw.decode('cp1252')

def entry_pattern(name):return re.compile(r'(?im)^[ \t]*mod[ \t]+"(?:[^"\r\n]*[/\\])?'+re.escape(name)+r'"[ \t]*;[ \t]*')
def edit_list(raw,suppression):
 bom,enc,text=decode_list(raw);newline='\r\r\n' if '\r\r\n' in text else '\r\n' if '\r\n' in text or not text else '\n'
 original=text
 if not suppression:text=entry_pattern(SUPP).sub('',text)
 for name in ([CORE,SUPP] if suppression else [CORE]):
  matches=list(entry_pattern(name).finditer(text))
  if len(matches)>1:raise ValueError('Duplicate own pack entries; resolve before installation')
  if not matches:text+=(newline if text and not text.endswith(('\r','\n')) else '')+'mod "'+name+'";'+newline
 def unrelated(s):
  for name in [CORE,SUPP]:s=entry_pattern(name).sub('',s)
  return s.rstrip('\r\n')
 if unrelated(text)!=unrelated(original):raise ValueError('Unrelated loading-list content would change')
 return bom+text.encode(enc)

def preservation(game):
 result={}
 for folder in [game/'data',game/'data/MyMods']:
  for p in sorted(folder.glob('*.pack')):
   if p.name in [CORE,SUPP] and p.parent==game/'data':continue
   result[str(p.resolve())]={'sha256':hashpath(p)} if p.stat().st_size<20_000_000 else {'size':p.stat().st_size,'mtime_ns':p.stat().st_mtime_ns}
 for name in ENGINE_HASHES:result[str((game/name).resolve())]={'sha256':hashpath(game/name)}
 return result

def write_new(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())

def transaction(game,changes,backup_root,reason,recover=True):
 game=verify_game(game);ensure_closed();white=allowed(game)
 if not set(changes).issubset(white):raise ValueError('Refusing target outside exact pack/config allowlist')
 if any(p.is_symlink() for p in changes):raise ValueError('Refusing symbolic-link target')
 original={p:p.read_bytes() if p.exists() else None for p in changes}
 archive=backup_root/('type20-'+utc()+'-'+uuid.uuid4().hex[:8]);archive.mkdir(parents=True,exist_ok=False)
 rows=[]
 for i,(p,data) in enumerate(changes.items()):
  raw=original[p];backup=archive/'original'/('%02d-'%i+p.name)
  if raw is not None:
   write_new(backup,raw)
   if hashpath(backup)!=sha(raw):raise ValueError('Original backup hash mismatch')
  temp=p.with_name(p.name+'.ss-type20-'+uuid.uuid4().hex+'.tmp')
  rows.append(dict(original_path=str(p),original_exists=raw is not None,original_sha256=sha(raw) if raw is not None else None,backup_path=str(backup) if raw is not None else None,expected_new_sha256=sha(data) if data is not None else None,
   operation='preserve' if raw==data else 'write' if data is not None else 'delete',temporary_new_path=str(temp),temporary_original_exists=False))
 receipt=archive/'manifest.json';record=dict(created_utc=utc(),reason=reason,game_root=str(game),records=rows,
  rollback_command='python -B "'+str(Path(__file__).resolve())+'" rollback --receipt "'+str(receipt)+'"',game_binary_writes=False)
 # All originals and this immutable intent manifest exist BEFORE target/temp writes.
 write_new(receipt,(json.dumps(record,indent=2)+'\n').encode())
 try:
  if any(hashpath(p)!=(sha(original[p]) if original[p] is not None else None) for p in changes):raise ValueError('Target changed after backup; refusing overwrite')
  for row,(p,data) in zip(rows,changes.items()):
   if row['operation']=='preserve':continue
   if data is None:
    if hashpath(p)!=row['original_sha256']:raise ValueError('Target changed before removal')
    if p.exists():p.unlink()
   else:
    temp=Path(row['temporary_new_path']);write_new(temp,data)
    if hashpath(temp)!=row['expected_new_sha256']:raise ValueError('Staged data hash mismatch')
    if hashpath(p)!=row['original_sha256']:raise ValueError('Target changed during staging')
    os.replace(temp,p)
   if hashpath(p)!=row['expected_new_sha256']:raise ValueError('Installed hash mismatch')
 except Exception as e:
  if recover and all(hashpath(p) in [row['original_sha256'],row['expected_new_sha256']] for p,row in zip(changes,rows)):
   undo=transaction(game,original,backup_root,'Automatic restoration after failed install: '+str(receipt),recover=False)
   raise RuntimeError('Installation failed; original files restored with fresh backups: '+str(undo)) from e
  raise RuntimeError('Transaction interrupted; preserve manifest for recovery: '+str(receipt)) from e
 write_new(archive/'completed.json',(json.dumps(dict(completed_utc=utc(),manifest=str(receipt)),indent=2)+'\n').encode())
 return receipt

def plan_install(package,game,suppression):
 release=json.loads((package/'release.json').read_text());game=verify_game(game);ensure_closed()
 if release.get('format')!=1:raise ValueError('Unsupported release manifest')
 for name in [CORE,SUPP]:
  if hashpath(package/name)!=release['pack_sha256'][name]:raise ValueError('Package hash mismatch: '+name)
 target=(game/'data'/CORE).resolve();optional=(game/'data'/SUPP).resolve()
 known={None,BASELINE,release['pack_sha256'][CORE]}|set(release.get('previous_core_hashes',[]))
 if hashpath(target) not in known:raise ValueError('Unrecognized installed Steel Sakura pack; refusing overwrite')
 if hashpath(optional) not in {None,release['pack_sha256'][SUPP]}|set(release.get('previous_suppression_hashes',[])):raise ValueError('Unrecognized optional module')
 extras=[p for folder in [game/'data',game/'data/MyMods'] for p in folder.glob('steel_sakura*.pack') if p.resolve() not in [target,optional]]
 if extras:raise ValueError('Other Steel Sakura packs present; refusing a conflicting install')
 configs=[(game/'mod_list.txt').resolve(),user_script()]
 if any(p.exists() and not p.is_file() for p in [target,optional,*configs]):raise ValueError('Pack/config target is not a regular file')
 changes={target:(package/CORE).read_bytes(),optional:(package/SUPP).read_bytes() if suppression else None}
 changes.update({p:edit_list(p.read_bytes() if p.exists() else b'',suppression) for p in configs})
 return game,changes,release

def install(package,game,suppression=False,dry=False):
 game,changes,release=plan_install(package,game,suppression)
 result=dict(status='DRY_RUN' if dry else 'INSTALLED_OFFLINE_VALIDATED_NOT_GAME_TESTED',game_root=str(game),suppression_module=suppression,targets={str(p):sha(b) if b is not None else None for p,b in changes.items()},
  optional_shared_scope=release['optional_shared_scope'] if suppression else None)
 if not dry:
  before=preservation(game)
  receipt=transaction(game,changes,package/'backups','Install Type20 supported-mechanics '+release['version'])
  if preservation(game)!=before:raise RuntimeError('Unrelated file changed during install; inspect preserved transaction '+str(receipt))
  result.update(receipt=str(receipt),unrelated_mods_and_binaries_unchanged=True,rollback_command='python -B "'+str(Path(__file__).resolve())+'" rollback --receipt "'+str(receipt)+'"')
 print(json.dumps(result,indent=2));return result

def rollback(receipt,dry=False):
 r=json.loads(receipt.read_text());game=verify_game(Path(r['game_root']));ensure_closed();white=allowed(game);changes={}
 for row in r['records']:
  p=Path(row['original_path']).resolve()
  if p not in white or p.is_symlink():raise ValueError('Invalid rollback target')
  if p in changes:raise ValueError('Duplicate rollback target')
  if hashpath(p)!=row['expected_new_sha256']:raise ValueError('Later edits detected; refusing rollback: '+str(p))
  b=Path(row['backup_path']).resolve() if row['original_exists'] else None
  if b is not None and (not b.is_relative_to(receipt.parent.resolve()/'original') or hashpath(b)!=row['original_sha256']):raise ValueError('Invalid or changed original backup')
  changes[p]=b.read_bytes() if b is not None else None
 result=dict(status='ROLLBACK_DRY_RUN' if dry else 'ROLLED_BACK',source_receipt=str(receipt),files=len(changes))
 if not dry:
  before=preservation(game);inverse=transaction(game,changes,receipt.parent.parent,'Undo Type20 transaction '+str(receipt))
  if before!=preservation(game):raise RuntimeError('Unrelated file changed during rollback')
  result.update(inverse_receipt=str(inverse),unrelated_mods_and_binaries_unchanged=True)
 print(json.dumps(result,indent=2));return result

def main():
 ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='action',required=True)
 p=sub.add_parser('install');p.add_argument('--game-root',type=Path,default=Path('D:/Games/Total War - SHOGUN 2'));p.add_argument('--with-suppression',action='store_true');p.add_argument('--dry-run',action='store_true')
 p=sub.add_parser('rollback');p.add_argument('--receipt',type=Path,required=True);p.add_argument('--dry-run',action='store_true')
 a=ap.parse_args()
 if a.action=='install':install(Path(__file__).resolve().parent,a.game_root.resolve(),a.with_suppression,a.dry_run)
 else:rollback(a.receipt.resolve(),a.dry_run)
if __name__=='__main__':main()
