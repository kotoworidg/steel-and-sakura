"""Read-only bounded disassembly at verified x86 instruction boundaries.
Never loads or executes the game DLL. Output remains ignored local research data.
"""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/python-research'))
import capstone,pefile
DLL=Path(r'D:\Games\Total War - SHOGUN 2\empire.retail.dll')
raw=DLL.read_bytes();sha=hashlib.sha256(raw).hexdigest().upper()
assert sha=='022FAE2E2DA92B59B8B1B8EE52887003C624E3C8ECA060B209F5D792A7F874F5'
pe=pefile.PE(data=raw);assert pe.FILE_HEADER.Machine==0x14c
cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
ranges={'manager_constructor':(0xd3b380,0x320),'directory_scan':(0xd5c670,0x210),'txt_enumeration':(0xd5ca50,0x250),'event_name_registration':(0xd39e91,0x190)}
out={}
for name,(rva,size) in ranges.items():
 offset=pe.get_offset_from_rva(rva)
 out[name]=[dict(address=hex(i.address),mnemonic=i.mnemonic,operands=i.op_str) for i in cs.disasm(raw[offset:offset+size],pe.OPTIONAL_HEADER.ImageBase+rva)]
strings={hex(va):raw[pe.get_offset_from_rva(va-pe.OPTIONAL_HEADER.ImageBase):].split(b'\0',1)[0].decode('ascii') for va in [0x1169d0c8,0x1169d0e8,0x116a23f0,0x115d3a40]}
result=dict(dll=str(DLL),sha256=sha,capstone_version=capstone.__version__,imagebase=hex(pe.OPTIONAL_HEADER.ImageBase),strings=strings,instructions=out,limits='Static x86 disassembly only; parser names and directory enumeration do not prove infantry runtime dispatch.')
p=ROOT/'build/engine-research/type20-disassembly.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(output=str(p),sha256=sha,strings=strings),indent=2))
