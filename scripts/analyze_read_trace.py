"""Analyze saved observations only; never opens a game process."""
import base64,collections,json,struct
from pathlib import Path
from tracked_files import ROOT,write_text,digest
from read_trace_control import current,records,summary

def main():
 _,session=current();rows=records(session);state=summary(session)
 if not state['finished'] or not state['detached']:raise RuntimeError('Wait for confirmed safe detach before final analysis')
 needle=('steel_sakura_type20_automatic_fire_test'+'\0').encode('utf-16-le');identities={};proof=[]
 for row in rows:
  if row['name']!='unit-initial':continue
  d=row['detail'];raw=base64.b64decode(d['bytes0']);pointer=struct.unpack_from('<I',raw,0x28)[0]
  matches=[p for p in d['pointers'] if p['offset']==0x28 and p['pointer']==pointer]
  ok=len(matches)==1 and base64.b64decode(matches[0]['bytes']).startswith(needle)
  if not ok:raise AssertionError('unit +28 identity was not an exact terminated match')
  identities[d['unit']]=pointer;proof.append({'unit':hex(d['unit']),'key_pointer':hex(pointer),'offset':'0x28','encoding':'UTF-16LE','terminator_verified':True})
 seen=set();native_actor_checks=0
 for row in rows:
  if row['name']!='native-before':continue
  d=row['detail'];assert d['unit'] in identities
  if d.get('actorBytes'):
   raw=base64.b64decode(d['actorBytes']);assert struct.unpack_from('<I',raw,0x214)[0]==d['unit'];native_actor_checks+=1;seen.add(d['actor'])
 bins={};changes=[];prior={}
 for row in rows:
  if row['name']!='poll-nonatomic':continue
  d=row['detail'];raw=base64.b64decode(d['actorBytes']) if d['actorBytes'] else None
  if raw is None:continue
  # These are observed raw fields; no unverified health/order names assigned.
  vals={hex(off):struct.unpack_from('<I',raw,off)[0] for off in [0x1b4,0x1d8,0x1f8,0x214,0x2d8,0x474]}
  k=str(d['actor']);label=str(d['elapsedMs']//5000*5)+'s'
  bucket=bins.setdefault(label,{'count':0,'clock_values':[],'selected_animation_values':set(),'ammo_values':[]})
  bucket['count']+=1;bucket['clock_values'].append(vals['0x1d8']);bucket['selected_animation_values'].add(vals['0x2d8'])
  if d['unitBytes0']:bucket['ammo_values'].append(struct.unpack_from('<f',base64.b64decode(d['unitBytes0']),0xf78)[0])
  fields_now={k:v for k,v in vals.items() if k!='0x1d8'}
  if k in prior and fields_now!=prior[k]:changes.append({'elapsedMs':d['elapsedMs'],'actor':hex(d['actor']),'changed':{a:[prior[k][a],b] for a,b in fields_now.items() if prior[k][a]!=b}})
  prior[k]=fields_now
 timeline=[]
 for label,d in bins.items():timeline.append({'window':label,'samples':d['count'],'raw_native_tick_minmax':[min(d['clock_values']),max(d['clock_values'])],'raw_selected_animation_values':sorted(d['selected_animation_values']),'ammo_minmax':[min(d['ammo_values']),max(d['ammo_values'])] if d['ammo_values'] else None})
 result={'status':'OBSERVED_IDENTITY_AND_AMMO_ONLY','session':str(session),'unit_identity_path':'actor+0x214 -> unit; unit+0x28 -> exact NUL-terminated UTF-16 key','unit_identity_snapshot_checks':len(proof),'actor_to_unit_snapshot_checks':native_actor_checks,'sampled_actor_count':len(seen),'identities':proof,'raw_timeline':timeline,'raw_field_changes':changes,
 'ammo':state['ammo_delta_histogram'],'limits':['One engine/pack/battle only; key ownership/generation on deallocation is not proved.','Twelve custom unit objects observed; only first two firing actors were polled.','Only first 400 paired shot events were recorded; polling continued afterwards.','Polling is nonatomic. Stop/Move timing was not marked automatically; native order/death semantics remain unverified.','No five-shot controller was run.'],'source_logs':state['raw_logs']}
 print(write_text(session/'identity-analysis.json',json.dumps(result,indent=2)+'\n','Read trace exact unit identity regression and unlabelled state timeline'))
 print(json.dumps({k:v for k,v in result.items() if k not in ['identities','raw_timeline','raw_field_changes','source_logs']},indent=2))
if __name__=='__main__':main()
