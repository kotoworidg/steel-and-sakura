"""Read-only audit of the observed two-shot animation/controller route.
No DLL patching, injection, game execution or speculative game entries.
"""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/python-research'))
import capstone,pefile
DLL=Path(r'D:\Games\Total War - SHOGUN 2\empire.retail.dll');raw=DLL.read_bytes();dll_sha=hashlib.sha256(raw).hexdigest().upper()
assert dll_sha=='022FAE2E2DA92B59B8B1B8EE52887003C624E3C8ECA060B209F5D792A7F874F5'
pe=pefile.PE(data=raw);base=pe.OPTIONAL_HEADER.ImageBase;assert pe.FILE_HEADER.Machine==0x14c
cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
ranges={'scalar_name_registry':(0xd39e86,0xd39fa4),'scalar_parse_store':(0xd3a189,0xd3a24c),'time_getter':(0x3d2ef0,0x3d2f1f),'dispatch_A':(0x38b600,0x38b93c),'dispatch_B':(0x3d4320,0x3d4603)}
code={}
for name,(start,end) in ranges.items():
 off=pe.get_offset_from_rva(start);body=raw[off:off+end-start];ins=list(cs.disasm(body,base+start));assert sum(i.size for i in ins)==len(body)
 code[name]=[dict(address=hex(i.address),bytes=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str) for i in ins]
def at(name,address,mnemonic,operands):
 row=next(i for i in code[name] if i['address']==address);assert row['mnemonic']==mnemonic and row['operands']==operands
at('scalar_parse_store','0x10d3a20d','fstp','dword ptr [eax]')
at('scalar_parse_store','0x10d3a239','add','ecx, 8')
at('scalar_parse_store','0x10d3a243','cmp','esi, 0xd')
at('time_getter','0x103d2f06','cmp','byte ptr [eax + ecx*8 + 0x94], 1')
at('time_getter','0x103d2f10','fld','dword ptr [eax + ecx*8 + 0x90]')
at('dispatch_A','0x1038b67b','setne','dl')
at('dispatch_A','0x1038b6f0','mov','byte ptr [ebx + edi + 0x74], 1')
at('dispatch_A','0x1038b8fc','cmp','ebp, 2')
at('dispatch_B','0x103d439b','setne','dl')
at('dispatch_B','0x103d4413','mov','byte ptr [ebx + esi + 0x6c], 1')
at('dispatch_B','0x103d45c3','cmp','ebp, 2')
vas=[0x116a257c,0x116a2588,0x116a2594,0x116a25a0,0x116a25ac,0x116a25b8,0x116a25c4,0x116a25d4,0x116a25e4,0x116a25f4,0x116a2604,0x116a2614,0x116a2624]
names=[]
for va in vas:
 off=pe.get_offset_from_rva(va-base);names.append(raw[off:].split(b'\0',1)[0].decode('ascii'))
assert [n for n in names if n.startswith('FIRE_TIME')]==['FIRE_TIME','FIRE_TIME_2']
# Model only the observed scalar-slot storage; not an engine runtime test.
duplicate_input=[['FIRE_TIME',0.0],['FIRE_TIME_2',.1],['FIRE_TIME',.2],['FIRE_TIME_2',.3],['FIRE_TIME',.4]]
slots={}
for key,value in duplicate_input:slots[key]=value
assert len(slots)==2
installed=Path(r'D:\Games\Total War - SHOGUN 2\data\steel_sakura_combined_test.pack');installed_sha=hashlib.sha256(installed.read_bytes()).hexdigest().upper();assert installed_sha=='1737D02D67F0C9100BBCC5255057C12B532F9805482D18ADC910542653D96DCD'
report=dict(status='STATIC_EVIDENCE_VERIFIED_NO_FIVE_SHOT_IMPLEMENTATION',date='2026-10-22',timezone='Asia/Singapore',dll=str(DLL),dll_sha256=dll_sha,installed_pack=str(installed),installed_pack_sha256=installed_sha,capstone_version=capstone.__version__,scalar_names=names,code=code,duplicate_event_storage_model=dict(runtime_test=False,input=duplicate_input,final_slots=slots),supported_conclusion='The recovered animation firing path has two named scalar shot-time slots and two dispatch iterations with two fired flags. Five timed shots are not expressible by merely adding markers, changing reload or changing the loop immediate.',limits=['No source symbols or instrumented runtime call trace identify every use of these two dispatch routines.','This is evidence about the recovered firing path, not a universal proof that every Shogun 2 controller is limited to two shots.','No verified alternative infantry controller, cross-state firing chain, or five-shot implementation exists in this project.','The executable and installed pack were not modified.'])
p=ROOT/'build/type20-five-shot/limit-audit.json';p.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(report=str(p),status=report['status'],scalar_names=names,dispatcher_limits=[2,2],installed_pack_sha256=installed_sha,game_modified=False),indent=2))
