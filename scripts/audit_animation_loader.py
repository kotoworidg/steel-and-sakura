"""Read-only PE string/reference inventory; never modifies or executes game code.
Reference locations are investigation leads, not recovered controller semantics.
"""
import argparse,hashlib,json,re,struct
from pathlib import Path
import pefile
NEEDLES={"Animations/Animation_Tables/","Animations/Custom_Animation_Tables/",
         "Animations/BattleConfiguration/","FIRE_TIME","FIRE_TIME_2",
         "battle_entity_man_animation_tables","battle_entity_man_shogun_animation_tables"}
def audit(path):
 raw=path.read_bytes();pe=pefile.PE(data=raw,fast_load=True);base=pe.OPTIONAL_HEADER.ImageBase;rows=[]
 for match in re.finditer(rb"[ -~]{5,}",raw):
  text=match.group().decode()
  if text not in NEEDLES:continue
  off=match.start();rva=pe.get_rva_from_offset(off);va=base+rva
  refs=[]
  for hit in re.finditer(re.escape(struct.pack("<I",va)),raw):
   point=hit.start()
   try:rv=pe.get_rva_from_offset(point)
   except pefile.PEFormatError:continue
   section=next((s.Name.rstrip(b"\0").decode(errors="replace") for s in pe.sections if s.contains_rva(rv)),"unknown")
   refs.append(dict(file_offset=point,rva=hex(rv),section=section))
  rows.append(dict(text=text,file_offset=off,rva=hex(rva),va=hex(va),literal_address_references=refs))
 return dict(binary=str(path),sha256=hashlib.sha256(raw).hexdigest(),image_base=hex(base),machine=hex(pe.FILE_HEADER.Machine),method="Static ASCII strings and literal 32-bit address references; no execution/disassembly or runtime proof",findings=rows)
def main():
 p=argparse.ArgumentParser();p.add_argument("--output",type=Path);a=p.parse_args()
 result=audit(Path(r"D:\Games\Total War - SHOGUN 2\empire.retail.dll"))
 if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(result,indent=2))
if __name__=="__main__":main()
