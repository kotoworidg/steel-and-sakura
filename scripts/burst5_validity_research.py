"""Read-only native target-reference trace; all output uses tracked backups."""
import json,sys,collections
from pathlib import Path
from tracked_files import ROOT,write_text,digest
sys.path.insert(0,str(ROOT/'tools/python-research'))
import capstone,pefile

def investigate():
 game=Path('D:/Games/Total War - SHOGUN 2/empire.retail.dll');raw=game.read_bytes()
 assert digest(raw)=='022FAE2E2DA92B59B8B1B8EE52887003C624E3C8ECA060B209F5D792A7F874F5'
 pe=pefile.PE(data=raw);dis=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
 ranges=[(0x3a6630,0x16),(0x3d44b4,0x10),(0x3d451b,0x24),(0x420d00,0x6c),(0x1a9290,0x12d)]
 decoded={r:list(dis.disasm(pe.get_data(r,n),r)) for r,n in ranges}
 ins={i.address:i for listing in decoded.values() for i in listing}
 def expect(r,mnemonic,operand):
  i=ins[r];assert i.mnemonic==mnemonic and i.op_str==operand,(hex(r),i.mnemonic,i.op_str)
 checks=[(0x3a6630,'mov','eax, dword ptr [ecx + 0xc]'),(0x3a6637,'cmp','dword ptr [eax + 0x1b4], 0'),(0x3d44b4,'lea','ebx, [esi + 0x2c]'),(0x3d44b7,'mov','ecx, ebx'),(0x3d44b9,'call','0x3a6630'),(0x3d44be,'mov','byte ptr [esp + 0x60], al'),(0x3d4520,'call','0x420d00'),(0x3d4525,'cmp','al, 1'),(0x3d4527,'jne','0x3d45be'),(0x3d453a,'call','0x1a9290'),(0x1a92c7,'movss','dword ptr [ebx + 0xf78], xmm0')]
 for item in checks:expect(*item)
 # 2C + C resolves action+38, NOT action+4 (shooter).
 assert 0x2c+0xc==0x38 and 0x38!=4
 session=ROOT/'build/burst5/runtime/20261022T101927.563542Z'
 records=[x for p in sorted(session.glob('log-*.json')) for x in json.loads(p.read_text())]
 refused=[r for r in records if r['name']=='gate-refused' and r['detail']['reason']=='native entity validity predicate refused']
 observed=collections.Counter(str(r['detail'].get('validity')) for r in refused)
 assert len(refused)==703 and observed=={'1':703}
 result={'status':'PASS_STATIC_AND_CAPTURED_LOG_ONLY','dll_sha256':digest(raw),'instruction_assertions':len(checks),'wrapper_offset_arithmetic_verified':True,'source_live_session':str(session),'live_actor_field_values':dict(observed),'target_field_logged_in_old_session':False,'findings':['Native helper receives action+2C, dereferences +C, and tests target+1B4.','Shooter+1B4 was wrongly added to the experiment admission predicate.','Helper AL is stored in request metadata; no immediate helper-result branch rejects the shot.','A separate validator at 420D00 is checked before the existing pre-debit hook.','Target predicate semantics, unit key mapping, cancellation and live ammo behavior remain unverified.'],'game_attached':False,'five_shots_verified':False,'ranges':[{'rva':hex(r),'bytes':pe.get_data(r,n).hex(),'instructions':[{'rva':hex(i.address),'mnemonic':i.mnemonic,'operands':i.op_str} for i in decoded[r]]} for r,n in ranges]}
 write_text(ROOT/'build/burst5/validity-research.json',json.dumps(result,indent=2)+'\n','Burst5 reproducible native predicate evidence and captured-value comparison')
 return result
if __name__=='__main__':
 r=investigate();print(json.dumps({k:v for k,v in r.items() if k!='ranges'},indent=2))
