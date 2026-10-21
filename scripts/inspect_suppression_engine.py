"""Read-only evidence for built-in suppression keys in this exact game version."""
from pathlib import Path
import hashlib,json,struct
import pefile
ROOT=Path(__file__).resolve().parents[1];DLL=Path(r'D:\Games\Total War - SHOGUN 2\empire.retail.dll');raw=DLL.read_bytes()
sha=hashlib.sha256(raw).hexdigest().upper();assert sha=='022FAE2E2DA92B59B8B1B8EE52887003C624E3C8ECA060B209F5D792A7F874F5'
pe=pefile.PE(data=raw);base=pe.OPTIONAL_HEADER.ImageBase
records=[]
for rva in [0x15b3d80,0x15b3d98,0x15b3db0]:
 off=pe.get_offset_from_rva(rva);ptr,number=struct.unpack_from('<II',raw,off);s=pe.get_offset_from_rva(ptr-base);name=raw[s:].split(b'\0',1)[0].decode('ascii');records.append(dict(table_entry_va=hex(base+rva),string_va=hex(ptr),name=name,numeric_value=number,raw_hex=raw[off:off+8].hex()))
assert [(r['name'],r['numeric_value']) for r in records]==[('suppression_fire',61),('tower_suppression_fire',64),('dummy_suppression_fire',67)]
r=dict(dll=str(DLL),sha256=sha,observed_string_numeric_pairs=records,inference='These are fixed built-in name/number mappings; using an existing name is better supported than inventing one.',limits=['No proof that dummy_suppression_fire supports a player-visible button or projectile switching.','No proof that it duplicates normal suppression buffs/debuffs.','No execution or modification of the DLL.'])
p=ROOT/'build/type20-suppression/engine-key-evidence.json';p.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
