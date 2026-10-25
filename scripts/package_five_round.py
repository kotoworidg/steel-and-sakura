"""Package the actual native adapter, paired pack, supported fallback and recovery."""
import io,json,subprocess,zipfile
from pathlib import Path
from tracked_files import ROOT,write_bytes,digest
from five_round_build import OUT,load,save
from restore_confirmed_type20 import CONFIRMED
CORE='steel_sakura_combined_test.pack';SUPP='steel_sakura_type20_suppression.pack'


def archive_bytes(files):
 buffer=io.BytesIO()
 with zipfile.ZipFile(buffer,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for name,data in sorted(files.items()):
   info=zipfile.ZipInfo(name,(2026,10,25,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.create_system=3;info.external_attr=0o100644<<16
   z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
 return buffer.getvalue()


def main():
 latest=load(OUT/'latest.json');session=Path(latest['session']);v=load(session/'validation.json')
 if v['status']!='PASS_OFFLINE_NATIVE_ADAPTER_AND_PAIRED_PACK' or latest['pack_sha256']!=v['pack_sha256'] or latest['exe_sha256']!=v['exe_sha256']:raise ValueError('matching final adapter/pack validation required')
 files={name:(session/name).read_bytes() for name in ['Type20FiveRound.exe','engine-profile.json',CORE,SUPP,'adapter-tests.json','transport-tests.json','validation.json','delivery-verification.json']}
 install=(ROOT/'INSTALL.md').read_text(encoding='utf-8');start=install.index('<!-- CURRENT-FIVE-ROUND-INSTALL -->');end=install.index('<!-- END-CURRENT-FIVE-ROUND-INSTALL -->')
 guide=install[start+len('<!-- CURRENT-FIVE-ROUND-INSTALL -->'):end].strip()+'\n'
 files.update({'install_type20.py':(ROOT/'scripts/install_type20_supported.py').read_bytes(),'restore_confirmed.py':(ROOT/'scripts/restore_confirmed_type20.py').read_bytes(),'run_five_round.py':(ROOT/'scripts/run_five_round.py').read_bytes(),'scripts/five_round_log.py':(ROOT/'scripts/five_round_log.py').read_bytes(),'scripts/tracked_files.py':(ROOT/'scripts/tracked_files.py').read_bytes(),'README.md':guide.encode('utf-8')})
 for name in ['NativeBurst.cs','SelfTests.cs','NativeHost.cs']:files['source/'+name]=(ROOT/'src/five_round'/name).read_bytes()
 for name in ['NativeHost.cs','BridgeTests.cs']:files['source/'+('CompiledNativeHost.cs' if name=='NativeHost.cs' else name)]=(session/name).read_bytes()
 fallback=(ROOT/'build/type20-auto-cycle/confirmed-burst.pack').read_bytes()
 if digest(fallback)!=CONFIRMED:raise ValueError('confirmed fallback differs')
 files['fallback/confirmed_two_shot.pack']=fallback
 commands={'Install-Core':'python -B "%~dp0install_type20.py" install %*','Install-With-Suppression':'python -B "%~dp0install_type20.py" install --with-suppression %*','Install-Supported-Fallback':'python -B "%~dp0supported\\install_type20.py" install %*','Restore-Confirmed':'python -B "%~dp0restore_confirmed.py" %*','Test-Five-Round-90s':'python -B "%~dp0run_five_round.py" start --approved-engine-hook --seconds 90 %*','Run-Five-Round':'python -B "%~dp0run_five_round.py" start --approved-engine-hook --seconds 3600 %*','Stop-Five-Round':'python -B "%~dp0run_five_round.py" stop','Report-Five-Round':'python -B "%~dp0run_five_round.py" report'}
 for name,cmd in commands.items():files[name+'.cmd']=('@echo off\r\n'+cmd+'\r\npause\r\n').encode()
 commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 release=dict(format=1,version='0.2.0-five-round-candidate',source_commit=commit,pack_sha256={n:digest(files[n]) for n in [CORE,SUPP]},previous_core_hashes=['B0E51ABC7D1FC4FB0D1DE37CA106B72AD55C6DE230B19C309C3BF92AF2EA2280','1ABB8206F1B20677808500EB7FDA83C97A880883E0158BCE56D4F312D1A48F1B'],previous_suppression_hashes=['303C662A8B70B60A32E36E802CC8D84DDE59C61A25D8B854E5CE3D0D87F8A01B'],optional_shared_scope='Other units already assigned native Suppression Fire also receive its shared unlock and private suppressive ammunition.',gameplay_verified=False,runtime_required=True,confirmed_baseline_sha256=CONFIRMED,confirmed_source_tag='steel-sakura/confirmed-two-shot-20261025')
 files['release.json']=(json.dumps(release,indent=2)+'\n').encode()
 stable=ROOT/'build/type20-playable/iteration-02'
 for name in [CORE,SUPP]:files['supported/'+name]=(stable/name).read_bytes()
 files['supported/install_type20.py']=files['install_type20.py']
 stable_release={**release,'version':'0.1.0-supported-fallback','runtime_required':False,'pack_sha256':{n:digest(files['supported/'+n]) for n in [CORE,SUPP]},'previous_core_hashes':[release['pack_sha256'][CORE]]+release['previous_core_hashes']}
 files['supported/release.json']=(json.dumps(stable_release,indent=2)+'\n').encode()
 runtime_names=['Type20FiveRound.exe','engine-profile.json','run_five_round.py','scripts/five_round_log.py','scripts/tracked_files.py']
 runtime=dict(status='IMPLEMENTED_NATIVE_RUNTIME_GAME_TEST_REQUIRED',runtime_sha256={n:digest(files[n]) for n in runtime_names},pack_sha256=release['pack_sha256'],burst_size=5,primary_rearms=3,game_binary_changes=False,gameplay_verified=False)
 files['runtime-release.json']=(json.dumps(runtime,indent=2)+'\n').encode()
 if any(Path(n).name.lower() in ['shogun2.exe','shogun2.retail.exe','empire.retail.dll'] for n in files):raise ValueError('proprietary game binary in package')
 files['SHA256SUMS.txt']=''.join(digest(b)+'  '+n+'\n' for n,b in sorted(files.items())).encode()
 data=archive_bytes(files)
 if data!=archive_bytes(dict(reversed(list(files.items())))):raise ValueError('archive assembly not reproducible')
 with zipfile.ZipFile(io.BytesIO(data)) as z:
  if z.testzip() or any(z.read(n)!=b for n,b in files.items()):raise ValueError('archive differs')
 destination=ROOT/'dist/five_round/0.2.0'
 for name,raw in files.items():write_bytes(destination/name,raw,'Five-round release member '+name)
 archive=ROOT/'dist/five_round/steel-and-sakura-five-round-0.2.0-candidate.zip';write_bytes(archive,data,'Five-round publish installable native runtime candidate with supported fallback')
 result=dict(status='FIVE_ROUND_RUNTIME_IMPLEMENTED_NOT_GAME_VERIFIED',source_commit=commit,zip=str(archive),zip_sha256=digest(data),directory=str(destination),pack_sha256=latest['pack_sha256'],exe_sha256=latest['exe_sha256'],adapter_cases=v['adapter_cases'],assertions=v['adapter_assertions'],python_tests=load(session/'delivery-verification.json')['python_tests'],gameplay_build_iteration=3,game_attached=False,archive_byte_reproducible=True,confirmed_baseline_sha256=CONFIRMED,original_game_binaries_packaged=False)
 save(OUT/'release.json',result,'runtime release and validation provenance');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
