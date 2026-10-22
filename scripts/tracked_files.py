"""Workspace-only file writes with immutable timestamped backups and rollback.
Audit manifests/original copies are the backup mechanism; they are never overwritten.
New-file creation is recorded with original_exists=false and original_sha256=null.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,shutil,uuid
ROOT=Path(__file__).resolve().parents[1]
def digest(data):return hashlib.sha256(data).hexdigest().upper()
def checked(path):
 p=Path(path)
 if not p.is_absolute():p=ROOT/p
 p=p.resolve()
 if not p.is_relative_to(ROOT) or any(x in p.relative_to(ROOT).parts for x in ['.git','.agents','.codex']):raise ValueError('Refusing path outside allowed project files')
 if p.is_relative_to(ROOT/'backups'):raise ValueError('Backup archive is immutable')
 return p
def write_bytes(path,data,reason):
 p=checked(path);data=bytes(data)
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
 archive=ROOT/'backups'/('tracked-'+stamp+'-'+uuid.uuid4().hex[:8]);archive.mkdir(parents=True,exist_ok=False)
 existed=p.exists()
 if existed and not p.is_file():raise ValueError('Target is not a regular file')
 original=p.read_bytes() if existed else None
 saved=archive/'original'/p.relative_to(ROOT)
 if existed:
  saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,saved)
  if digest(saved.read_bytes())!=digest(original):raise ValueError('Backup verification failed')
 record=dict(version=1,created_utc=stamp,reason=reason,original_path=str(p),original_exists=existed,original_sha256=digest(original) if existed else None,backup_path=str(saved) if existed else None,expected_new_sha256=digest(data),operation='write',rollback_command='python -B scripts/tracked_files.py rollback "'+str(archive/'manifest.json')+'"')
 manifest=archive/'manifest.json';manifest.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
 p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 if digest(p.read_bytes())!=record['expected_new_sha256']:raise ValueError('Post-write hash mismatch')
 return str(manifest)
def write_text(path,text,reason):return write_bytes(path,text.encode('utf-8'),reason)
def rollback(manifest):
 source=Path(manifest).resolve()
 if not source.is_relative_to(ROOT/'backups'):raise ValueError('Manifest must be inside project backup archive')
 r=json.loads(source.read_text());p=checked(r['original_path'])
 if r.get('operation')=='delete':
  if p.exists():raise ValueError('File was recreated; refuse to discard later work')
 elif not p.exists() or digest(p.read_bytes())!=r['expected_new_sha256']:raise ValueError('Current file differs; refuse to discard later work')
 if r['original_exists']:
  saved=Path(r['backup_path']).resolve()
  if not saved.is_relative_to(ROOT/'backups'):raise ValueError('Invalid backup path')
  data=saved.read_bytes()
  if digest(data)!=r['original_sha256']:raise ValueError('Backup hash mismatch')
  return write_bytes(p,data,'Rollback of '+str(source))
 # Back up the current new file and record deletion before rollback removes it.
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
 archive=ROOT/'backups'/('tracked-delete-'+stamp+'-'+uuid.uuid4().hex[:8]);archive.mkdir(parents=True,exist_ok=False)
 saved=archive/'original'/p.relative_to(ROOT);saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,saved)
 record=dict(version=1,created_utc=stamp,reason='Rollback creation from '+str(source),original_path=str(p),original_exists=True,original_sha256=digest(p.read_bytes()),backup_path=str(saved),expected_new_sha256=None,operation='delete',rollback_command='python -B scripts/tracked_files.py rollback \"'+str(archive/'manifest.json')+'\"')
 if digest(saved.read_bytes())!=record['original_sha256']:raise ValueError('Deletion backup mismatch')
 receipt=archive/'manifest.json';receipt.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');p.unlink();return str(receipt)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['rollback']);ap.add_argument('manifest');args=ap.parse_args();print(rollback(args.manifest))
