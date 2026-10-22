"""Workspace-only engine research: static trampoline and scheduler contract.
Never loads a DLL, attaches to a process, injects, or installs anything.
"""
import argparse,dataclasses,datetime,hashlib,json,struct,sys
from pathlib import Path
from tracked_files import ROOT,write_bytes,write_text
sys.path.insert(0,str(ROOT/'tools/python-research'))
import capstone,pefile
DLL=Path(r'D:\Games\Total War - SHOGUN 2\empire.retail.dll')
SOURCE_SHA='022FAE2E2DA92B59B8B1B8EE52887003C624E3C8ECA060B209F5D792A7F874F5'
def sha(data):return hashlib.sha256(data).hexdigest().upper()
def align(value,step):return (value+step-1)//step*step
def instruction_rows(cs,data,va):return [dict(address=hex(i.address),bytes=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str) for i in cs.disasm(data,va)]
@dataclasses.dataclass
class IntentScheduler:
    """Original reference contract, not wired into any native game function.
    Native callback must own ammo consumption. Default at most one shot per update.
    identity must include an entity-generation value to prevent pointer reuse.
    """
    identity:tuple
    interval:float=.1
    burst_size:int|None=5
    next_due:float=0.
    emitted:int=0
    cancelled:bool=False
    last_now:float=-1.
    def tick(self,now,*,identity,experimental_unit,ability_active,alive,target_valid,moving,emit):
        if now<self.last_now:raise ValueError('Simulation time moved backwards')
        self.last_now=now
        if self.cancelled:return False
        if identity!=self.identity or not experimental_unit or not ability_active or not alive or not target_valid or moving:
            self.cancelled=True;return False
        if self.burst_size is not None and self.emitted>=self.burst_size:return False
        if now+1e-9<self.next_due:return False
        # Exactly one emission attempt per update; no instant low-FPS catch-up dump.
        if not emit():self.cancelled=True;return False
        self.emitted+=1;self.next_due=now+self.interval;return True

def contract_cases():
    cases=[]
    def replay(name,ticks,ammo=100,burst=5,gate=None):
        state=IntentScheduler((123,1),burst_size=burst);shots=[];remaining=[ammo]
        def emit():
            if remaining[0]<=0:return False
            remaining[0]-=1;shots.append(state.last_now);return True
        for t in ticks:
            args=dict(identity=(123,1),experimental_unit=True,ability_active=True,alive=True,target_valid=True,moving=False)
            if gate:args.update(gate(t))
            state.tick(t,emit=emit,**args)
        result=dict(name=name,shot_times=shots,shots=len(shots),ammo_remaining=remaining[0],cancelled=state.cancelled)
        cases.append(result);return result
    a=replay('finite_five', [i*.05 for i in range(30)]);assert a['shots']==5
    assert all(abs(x-y)<1e-8 for x,y in zip(a['shot_times'],[0,.1,.2,.3,.4]))
    assert replay('cancel_movement_after_two',[i*.1 for i in range(10)],gate=lambda t:dict(moving=t>=.2))['shots']==2
    assert replay('ammo_exhaustion', [i*.1 for i in range(10)],ammo=3)['shots']==3
    assert replay('unit_scope_denied',[0,.1],gate=lambda t:dict(experimental_unit=False))['shots']==0
    assert replay('entity_generation_changed',[0,.1],gate=lambda t:dict(identity=(123,2)))['shots']==0
    assert replay('target_lost',[i*.1 for i in range(10)],gate=lambda t:dict(target_valid=t<.2))['shots']==2
    assert replay('sustained_until_ability_expires',[i*.1 for i in range(20)],burst=None,gate=lambda t:dict(ability_active=t<.8))['shots']==8
    coarse=replay('one_hz_updates_no_catchup_dump',[0,1,2,3,4,5]);assert coarse['shots']==5 and coarse['shot_times']==[0,1,2,3,4]
    refused=replay('native_callback_refused',[0,.1],ammo=0);assert refused['shots']==0
    return dict(status='OFFLINE_REFERENCE_CONTRACT_ONLY',cases=cases,not_verified=['Native emission callback ABI/target/ammo behavior','Actual infantry controller identity','Native animation cancellation, sidecar lifetime and game-thread integration','Game simulation tick rate versus render FPS','In-game five shots or sustained fire'])

def make_passthrough(raw,out):
    """A derived DLL copy with a behavior-preserving entry detour, not a burst patch.
    The candidate entry is not confirmed as the active foot-rifle routine.
    """
    pe=pefile.PE(data=raw,fast_load=True);cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
    entry=0x38b600;old_offset=pe.get_offset_from_rva(entry);stolen=raw[old_offset:old_offset+6]
    assert stolen==bytes.fromhex('81ecf0000000')
    assert instruction_rows(cs,stolen,pe.OPTIONAL_HEADER.ImageBase+entry)==[dict(address=hex(pe.OPTIONAL_HEADER.ImageBase+entry),bytes=stolen.hex(),mnemonic='sub',operands='esp, 0xf0')]
    assert pe.FILE_HEADER.Machine==0x14c
    header=pe.sections[0].get_file_offset()+pe.FILE_HEADER.NumberOfSections*40
    assert header+40<=min(s.PointerToRawData for s in pe.sections if s.PointerToRawData)
    assert raw[header:header+40]==bytes(40),'Do not overwrite nonzero header padding'
    new_rva=align(max(s.VirtualAddress+max(s.Misc_VirtualSize,s.SizeOfRawData) for s in pe.sections),pe.OPTIONAL_HEADER.SectionAlignment)
    new_raw=align(len(raw),pe.OPTIONAL_HEADER.FileAlignment)
    trampoline=stolen+b'\xe9'+struct.pack('<i',entry+6-(new_rva+6+5))
    branch=b'\xe9'+struct.pack('<i',new_rva-(entry+5))+b'\x90'
    size_raw=align(len(trampoline),pe.OPTIONAL_HEADER.FileAlignment)
    patched=bytearray(raw);patched+=bytes(new_raw-len(patched));patched+=trampoline+bytes(size_raw-len(trampoline))
    # Standard PE fields only; original game image remains untouched on disk.
    section=struct.pack('<8sIIIIIIHHI',b'.sslab\0\0',len(trampoline),new_rva,size_raw,new_raw,0,0,0,0,0x60000020)
    patched[header:header+40]=section
    struct.pack_into('<H',patched,pe.FILE_HEADER.get_field_absolute_offset('NumberOfSections'),pe.FILE_HEADER.NumberOfSections+1)
    struct.pack_into('<I',patched,pe.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),align(new_rva+len(trampoline),pe.OPTIONAL_HEADER.SectionAlignment))
    struct.pack_into('<I',patched,pe.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfCode'),pe.OPTIONAL_HEADER.SizeOfCode+size_raw)
    patched[old_offset:old_offset+6]=branch
    check=pefile.PE(data=bytes(patched),fast_load=True)
    struct.pack_into('<I',patched,pe.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),check.generate_checksum())
    result=bytes(patched);parsed=pefile.PE(data=result,fast_load=True)
    assert parsed.FILE_HEADER.NumberOfSections==pe.FILE_HEADER.NumberOfSections+1
    assert parsed.OPTIONAL_HEADER.AddressOfEntryPoint==pe.OPTIONAL_HEADER.AddressOfEntryPoint
    assert parsed.OPTIONAL_HEADER.DATA_DIRECTORY[1].VirtualAddress==pe.OPTIONAL_HEADER.DATA_DIRECTORY[1].VirtualAddress
    assert parsed.OPTIONAL_HEADER.DATA_DIRECTORY[5].VirtualAddress==pe.OPTIONAL_HEADER.DATA_DIRECTORY[5].VirtualAddress
    assert parsed.sections[-1].Name.rstrip(b'\0')==b'.sslab'
    # Verify both branches and rebasing arithmetically; no code execution.
    assert entry+5+struct.unpack('<i',branch[1:5])[0]==new_rva
    assert new_rva+11+struct.unpack('<i',trampoline[7:11])[0]==entry+6
    rebases=[]
    for imagebase in [0x10000000,0x20000000,0x30000000]:
        assert imagebase+entry+5+struct.unpack('<i',branch[1:5])[0]==imagebase+new_rva
        assert imagebase+new_rva+11+struct.unpack('<i',trampoline[7:11])[0]==imagebase+entry+6
        rebases.append(hex(imagebase))
    changes=[];i=0
    while i<len(raw):
        if raw[i]==result[i]:i+=1;continue
        start=i
        while i<len(raw) and raw[i]!=result[i]:i+=1
        changes.append(dict(offset=start,original_hex=raw[start:i].hex(),patched_hex=result[start:i].hex()))
    # All changes in the original file are header edits or the six-byte detour.
    assert all(c['offset']<pe.OPTIONAL_HEADER.SizeOfHeaders or old_offset<=c['offset']<old_offset+6 for c in changes)
    restored=bytearray(result[:len(raw)])
    for c in changes:restored[c['offset']:c['offset']+len(bytes.fromhex(c['original_hex']))]=bytes.fromhex(c['original_hex'])
    assert bytes(restored)==raw
    output=out/'empire.retail.PASSTHROUGH_ONLY_NOT_FOR_INSTALL.dll'
    backup=write_bytes(output,result,'Create workspace-only pass-through detour copy; not a functional burst patch; never installed or loaded')
    plan=dict(status='STATIC_PASSTHROUGH_ONLY_NOT_RUNTIME_READY',output=str(output),source_sha256=SOURCE_SHA,output_sha256=sha(result),original_length=len(raw),original_file_changes=changes,appended_bytes=len(result)-len(raw),entry_rva=hex(entry),trampoline_rva=hex(new_rva),trampoline_bytes=trampoline.hex(),entry_patch=branch.hex(),entry_disassembly=instruction_rows(cs,branch,pe.OPTIONAL_HEADER.ImageBase+entry),trampoline_disassembly=instruction_rows(cs,trampoline,pe.OPTIONAL_HEADER.ImageBase+new_rva),checked_image_bases=rebases,creation_backup_manifest=backup,rollback_command='python -B scripts/engine_burst_lab.py restore "'+str(out/'passthrough-plan.json')+'"',limitations=['Only preserves the original entry sequence and branches back. No scheduler is connected.','Candidate routine is not established as foot-infantry firing.','PE parsing/branch checks do not prove Windows loader or runtime compatibility.','Signature/trust policies, loader checks and interference with other hooks are untested.','No install, injection, process access, or executable/DLL loading has been attempted.'])
    write_text(out/'passthrough-plan.json',json.dumps(plan,indent=2)+'\n','Record static workspace-copy patch and byte-exact restoration plan')
    return plan

def restore(planpath):
    p=Path(planpath).resolve();allowed=ROOT/'build/engine-burst-research'
    if not p.is_relative_to(allowed):raise ValueError('Refuse plan outside research workspace')
    plan=json.loads(p.read_text());target=Path(plan['output']).resolve()
    if not target.is_relative_to(allowed):raise ValueError('Refuse write outside research workspace')
    data=target.read_bytes()
    if sha(data)!=plan['output_sha256']:raise ValueError('Derived copy changed; refusing to discard later work')
    restored=bytearray(data[:plan['original_length']])
    for c in plan['original_file_changes']:
        original=bytes.fromhex(c['original_hex']);restored[c['offset']:c['offset']+len(original)]=original
    if sha(restored)!=plan['source_sha256']:raise ValueError('Restored hash mismatch')
    print(write_bytes(target,restored,'Undo workspace-only pass-through scaffold with exact original-byte restoration'))

def research():
    raw=DLL.read_bytes();assert sha(raw)==SOURCE_SHA
    installed=Path(r'D:\Games\Total War - SHOGUN 2\data\steel_sakura_combined_test.pack');pack_before=sha(installed.read_bytes())
    out=ROOT/'build/engine-burst-research'/('lab-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    contract=contract_cases();write_text(out/'scheduler-contract.json',json.dumps(contract,indent=2)+'\n','Offline original scheduler contract checks; no game integration')
    plan=make_passthrough(raw,out)
    assert sha(DLL.read_bytes())==SOURCE_SHA and sha(installed.read_bytes())==pack_before
    report=dict(status='WORKSPACE_RESEARCH_ONLY_GAME_UNCHANGED',directory=str(out),original_dll_sha256=SOURCE_SHA,installed_pack_sha256=pack_before,contract_cases=len(contract['cases']),pass_through_copy=plan['output'],not_five_shot_game_patch=True,correction='Prior two-shot dispatchers are not yet proven to be the foot-infantry controller; adjacent binding context points toward naval/grenade actions. Metadata two-time-slot finding remains supported.',next_gate='Resolve actual infantry caller, native emitter ABI, unit scoping, ammo/target lifetime and cancellation before wiring any scheduler or requesting a runtime patch test.')
    write_text(out/'summary.json',json.dumps(report,indent=2)+'\n','Final research summary and original game/pack unchanged hashes')
    print(json.dumps(report,indent=2))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['research','restore']);parser.add_argument('plan',nargs='?');args=parser.parse_args()
    if args.action=='research':research()
    else:
        if not args.plan:parser.error('restore requires a workspace plan')
        restore(args.plan)
