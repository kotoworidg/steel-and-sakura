"""Prepare the bounded projectile evidence mode of the existing adapter.
No pack build, installation, game launch or game attachment. This is not a combat release.
"""
import argparse,base64,datetime,json,struct,subprocess,uuid
from pathlib import Path
from tracked_files import ROOT,write_text,write_bytes,digest
from five_round_build import ENGINE,CSC,host_source
PACK='C89B3F9F48CCC07EB153576A264FF66AC8F63FE35F70609FD85736C043F2479A'
BASE=ROOT/'build/five_round/build-20261025T083327.514537Z/engine-profile.json'
BASE_HASH='C5193820979DD7F6E9F494E8BBB79535BF5B52B257F7A013F035FE592E941875'
OUT=ROOT/'build/five_round'

def stamp():return datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
def save(path,obj,why):return write_text(path,json.dumps(obj,indent=2)+'\n','Projectile evidence: '+why)

def profile():
    if digest(BASE.read_bytes())!=BASE_HASH:raise ValueError('preserved profile differs')
    p=json.loads(BASE.read_text());raw=(OUT/'binary-baseline/empire.retail.dll').read_bytes()
    if digest(raw)!=ENGINE:raise ValueError('pinned development DLL differs')
    pe=struct.unpack_from('<I',raw,0x3c)[0];opt=pe+24
    count=struct.unpack_from('<H',raw,pe+6)[0];opt_size=struct.unpack_from('<H',raw,pe+20)[0]
    if struct.unpack_from('<H',raw,opt)[0]!=0x10b:raise ValueError('expected x86 PE')
    sections=[struct.unpack_from('<IIII',raw,opt+opt_size+40*i+8) for i in range(count)]
    def data(rva,size):
        for vs,va,rs,offset in sections:
            if va<=rva and rva+size<=va+rs:return raw[offset+rva-va:offset+rva-va+size]
        raise ValueError('RVA outside backed file section: '+hex(rva))
    anchors={0x424f4f:'894344',0x424f52:'e819300400',0x481010:'558bec83e4f0',0x483da4:'e867d2ffff',0x38f368:'e853620900',0x425951:'e8caf3ffff',0x481c07:'e89424ffff',0x3ea970:'8b8194030000'}
    for r,b in anchors.items():
        if data(r,len(bytes.fromhex(b)))!=bytes.fromhex(b):raise ValueError('new native anchor mismatch: '+hex(r))
    rr,rs=struct.unpack_from('<II',raw,opt+96+5*8);relocs=[];pos=0
    while pos<rs:
        page,size=struct.unpack('<II',data(rr+pos,8))
        if size<8 or size%2 or pos+size>rs:raise ValueError('invalid relocation block')
        for entry, in struct.iter_unpack('<H',data(rr+pos+8,size-8)):
            if entry>>12==3:relocs.append(page+(entry&0xfff))
        pos+=size
    checks=p['code_checks']
    for start,size in [(0x40e2f0,0x3c6),(0x41c760,0x160),(0x424d20,0x600),(0x481010,0x2340),(0x483d40,0x90),(0x38f340,0x180),(0x4255c0,0x480)]:
        for delta in range(0,size,4096):
            r=start+delta;b=data(r,min(4096,size-delta));mask=bytearray(b'\xff'*len(b))
            for loc in relocs:
                for k in range(4):
                    if r<=loc+k<r+len(b):mask[loc+k-r]=0
            checks.append(dict(rva=r,bytes=base64.b64encode(b).decode(),mask=base64.b64encode(mask).decode()))
    p.update(runtime_mode='bounded-projectile-evidence',pack_sha256=PACK,max_duration_seconds=90,sample_actors=1,max_registered_projectiles=32,gameplay_verified=False,new_gameplay_build=False,
      scope='Existing primary re-arm algorithm for a bounded comparison; registered object, movement and component-integrity writes are independent observations. No full-auto or five-damaging-projectile claim.',
      approval_token='--projectile-evidence-approved',native_sites={hex(k):v for k,v in anchors.items()},
      runtime_changes=[dict(location='selected current action +0x6C',purpose='Existing reproduction only, max3 re-arms per action; cancelled if native creation unconfirmed',restore='Existing owner/tick-guarded restoration of unconsumed reset'),dict(location='owned DR0/DR1/DR2/DR3',purpose='Entry/return, per-thread pre↔post, per-thread component store before↔after',sites=['3D438A','3B3042','3D453A↔3D45B7','424F4F↔424F52'],restore='Saved DR0..DR3/DR6/DR7 with readback before detach'),dict(location='thread EIP at3D453A',purpose='Existing skip to3D45BE for refused extra before ammo debit',restore='No persistent code patch')])
    return p

def prepare():
    session=OUT/('projectile-evidence-'+stamp());transactions=[]
    def text(path,body,why):transactions.append(write_text(path,body,why))
    def copy(path,src,why):transactions.append(write_bytes(path,src.read_bytes(),why))
    ep=profile();text(session/'NativeHost.cs',host_source(PACK),'Bounded projectile evidence host from current source')
    transactions.append(save(session/'engine-profile.json',ep,'verified native object/damage ABI and changed hook layout'))
    for name in ['NativeBurst.cs','ProjectileEvidence.cs','SelfTests.cs','ProjectileEvidenceTests.cs','BridgeTests.cs']:
        copy(session/name,ROOT/'src/five_round'/name,'Freeze evidence runtime/test source for reproducible compilation')
    exe=session/'Type20FiveRound.exe';transactions.append(write_bytes(exe,b'','Reserve evidence-only compiler output'))
    archive=ROOT/'backups'/('projectile-evidence-compiler-'+stamp()+'-'+uuid.uuid4().hex[:8]);archive.mkdir(parents=True,exist_ok=False)
    original=archive/'original.bin';original.write_bytes(exe.read_bytes());record=dict(original_path=str(exe),original_exists=True,original_sha256=digest(exe.read_bytes()),backup_path=str(original),operation='external_pending',expected_new_sha256=None)
    (archive/'pending.json').write_text(json.dumps(record,indent=2)+'\n')
    sources=[session/name for name in ['NativeHost.cs','NativeBurst.cs','ProjectileEvidence.cs','SelfTests.cs','ProjectileEvidenceTests.cs','BridgeTests.cs']]
    result=subprocess.run([str(CSC),'/nologo','/noconfig','/platform:x86','/target:exe','/debug-','/optimize+','/r:System.dll','/r:System.Core.dll','/r:System.Web.Extensions.dll','/out:'+str(exe),*map(str,sources)],capture_output=True,text=True,timeout=45)
    record.update(operation='write',expected_new_sha256=digest(exe.read_bytes()),rollback_command='python -B scripts/tracked_files.py rollback "'+str(archive/'manifest.json')+'"');(archive/'manifest.json').write_text(json.dumps(record,indent=2)+'\n');transactions.append(str(archive/'manifest.json'))
    save(session/'compiler.json',dict(exit_code=result.returncode,stdout=result.stdout,stderr=result.stderr),'compiler output')
    if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    results={}
    for name,args in [('fixtures',['--self-test']),('multiplexed_transport',['--bridge-self-test']),('profile',['--check-profile',str(session/'engine-profile.json')])]:
        r=subprocess.run([str(exe),*args],capture_output=True,text=True,timeout=45);results[name]=dict(exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr)
        save(session/(name+'.json'),results[name],'offline '+name+' result; not game evidence')
        if r.returncode:raise RuntimeError(name+': '+r.stdout+r.stderr)
    # Fail-safe entry point regression: historical scope must not activate new sites.
    r=subprocess.run([str(exe),'--run','--five-round-runtime-approved','0',str(session),'python',str(session)],capture_output=True,text=True,timeout=5)
    if r.returncode!=2:raise RuntimeError('old approval scope accepted by changed runtime')
    copy(session/'run_five_round.py',ROOT/'scripts/run_five_round.py','Copy existing guarded launcher with distinct evidence approval scope')
    for name in ['tracked_files.py','five_round_log.py']:copy(session/'scripts'/name,ROOT/'scripts'/name,'Runtime logger preserves hash-backed rollback')
    protected=[ROOT/'build/type20-playable/iterations.json',ROOT/'build/type20-field-release-20261027/iterations.json',ROOT/'build/type20-auto-cycle/confirmed-burst.pack']
    manifest=dict(status='OFFLINE_PREPARED_EVIDENCE_ONLY_NOT_COMBAT_RELEASE',gameplay_verified=False,game_attached=False,pack_installed=False,runtime_sha256={str(p.relative_to(session)).replace('\\','/'):digest(p.read_bytes()) for p in [exe,session/'engine-profile.json',session/'run_five_round.py',session/'scripts/tracked_files.py',session/'scripts/five_round_log.py']},protected_sha256={str(p):digest(p.read_bytes()) for p in protected},transactions=transactions,requires_new_explicit_approval=True,build_iterations_consumed=0)
    save(session/'runtime-release.json',manifest,'bounded evidence package; no gameplay release or new pack')
    save(OUT/'projectile-evidence-latest.json',dict(session=str(session),exe_sha256=digest(exe.read_bytes()),status=manifest['status']),'latest evidence preparation only; historical combat build pointer unchanged')
    print(json.dumps(dict(session=str(session),status=manifest['status'],offline_checks=list(results),old_approval_token_rejected=True,game_attached=False),indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['prepare']);p.parse_args();prepare()
