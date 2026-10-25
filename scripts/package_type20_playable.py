"""Package the validated Type20 packs and standard-library installer; no install."""
import io,json,subprocess,zipfile
from pathlib import Path
from tracked_files import ROOT,write_bytes,write_text,digest
from type20_playable import OUT,load,validate
SOURCES=['src/type20-supported.json','scripts/type20_pack_codec.py','scripts/type20_playable.py','scripts/install_type20_supported.py','scripts/validate_type20_rpfm.py','tests/test_type20_playable.py']

def main():
 pointer=load(OUT/'latest.json');session=Path(pointer['session']);validation=validate();rpfm=load(session/'rpfm-validation.json');tests=load(session/'test-results.json');profile=load(session/'profile.json')
 if rpfm['status']!='PASS_RPFM_INDEPENDENT_REOPEN' or rpfm['core_sha256']!=validation['core_sha256'] or rpfm['optional_sha256']!=validation['optional_sha256']:raise ValueError('matching independent RPFM reopen required')
 if not tests['successful'] or tests['failures'] or tests['errors'] or tests['skipped']:raise ValueError('passing regression tests required')
 for name in SOURCES:
  if tests['source_sha256'][name]!=digest((ROOT/name).read_bytes()):raise ValueError('source changed after test run: '+name)
 if load(ROOT/'src/type20-supported.json')!=profile:raise ValueError('tuning changed after build')
 files={
  'steel_sakura_combined_test.pack':(session/'steel_sakura_combined_test.pack').read_bytes(),
  'steel_sakura_type20_suppression.pack':(session/'steel_sakura_type20_suppression.pack').read_bytes(),
  'install_type20.py':(ROOT/'scripts/install_type20_supported.py').read_bytes(),
  'README.md':(ROOT/'docs/TYPE20_PLAYABLE.md').read_bytes(),
  'tuning.json':(session/'profile.json').read_bytes(),
  'validation.json':(json.dumps(validation,indent=2)+'\n').encode(),
  'rpfm-validation.json':(session/'rpfm-validation.json').read_bytes(),
  'test-results.json':(session/'test-results.json').read_bytes(),
  'Install-Core.cmd':b'@echo off\r\npython -B "%~dp0install_type20.py" install %*\r\npause\r\n',
  'Install-With-Suppression.cmd':b'@echo off\r\npython -B "%~dp0install_type20.py" install --with-suppression %*\r\npause\r\n'}
 source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 iterations=load(OUT/'iterations.json')
 release=dict(format=1,version=profile['version'],unit_name=profile['title'],source_commit=source_commit,source_base_commit='c4628a6b3fc66bfc2e2609fe50155f6f01aa325e',
  iteration=pointer['iteration'],pack_sha256={n:digest(files[n]) for n in ['steel_sakura_combined_test.pack','steel_sakura_type20_suppression.pack']},
  previous_core_hashes=[i['core_sha256'] for i in iterations[:-1]],previous_suppression_hashes=[i.get('optional_sha256') or digest((OUT/('iteration-%02d'%i['iteration'])/'steel_sakura_type20_suppression.pack').read_bytes()) for i in iterations[:-1]],
  optional_shared_scope=validation['changes']['optional_shared_scope'],core_only_is_default=True,offline_validation=True,in_game_verified=False,
  five_round_bursts=False,true_full_auto=False,per_soldier_magazine_reload=False,source_sha256=tests['source_sha256'])
 files['release.json']=(json.dumps(release,indent=2)+'\n').encode()
 files['SHA256SUMS.txt']=''.join(digest(data)+'  '+name+'\n' for name,data in sorted(files.items())).encode()
 release_dir=ROOT/'dist/type20-playable'/profile['version']
 for name,data in files.items():write_bytes(release_dir/name,data,'Type20 playable package validated installable release member '+name)
 buffer=io.BytesIO()
 with zipfile.ZipFile(buffer,'w',zipfile.ZIP_DEFLATED) as archive:
  for name,data in sorted(files.items()):archive.writestr(name,data)
 data=buffer.getvalue()
 with zipfile.ZipFile(io.BytesIO(data)) as archive:
  if archive.testzip() is not None or any(archive.read(n)!=b for n,b in files.items()):raise ValueError('release archive verification failed')
 zip_path=ROOT/'dist/type20-playable'/('steel-and-sakura-type20-'+profile['version']+'.zip')
 write_bytes(zip_path,data,'Type20 playable verified gameplay release ZIP')
 result=dict(version=profile['version'],source_commit=source_commit,iteration=pointer['iteration'],zip=str(zip_path),zip_sha256=digest(data),release_directory=str(release_dir),files=len(files),tests=tests['tests_run'],rpfm_payloads=rpfm['decoded_payloads'],gameplay_verification='PENDING_IN_GAME')
 write_text(OUT/'release.json',json.dumps(result,indent=2)+'\n','Type20 playable release location and validation provenance')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
