"""Try repeated two-shot human firing cycles; runtime continuity remains unproven.
Confirmed burst payloads are carried forward byte-identically for direct comparison.
"""
import argparse,copy,hashlib,json,math,re,struct
from pathlib import Path
from inspect_anim_events import read_anim,event_bytes
from validate_free_fire_experiment import entries
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/type20-auto-cycle'
UNIT='steel_sakura_type20_auto_cycle_test';OLD='steel_sakura_type20_automatic_fire_test'
TITLE='TYPE20 AUTO CYCLE TEST - continuous trial'
PACK=ROOT/'build/steel_sakura_type20_auto_cycle.pack'
CONFIRMED='0B497A435F4E28C2C068D7C90B60BA9D0C0FFA353BABD46242EF2FED2222D270'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def read_manifest():return json.loads((OUT/'manifest.json').read_text())
def obj(t):return dict(zip(t['fields'],[next(iter(c.values())) for c in t['rows'][0]]))
def prepare():
 OUT.mkdir(parents=True,exist_ok=True);base=OUT/'confirmed-burst.pack';assert sha(base)==CONFIRMED
 original=json.loads((ROOT/'build/type20-burst/manifest.json').read_text());m=copy.deepcopy(original)
 # Only copied new rows are renamed; existing payloads are never edited.
 m['tables']=json.loads(json.dumps(original['tables']).replace(OLD,UNIT))
 t=m['tables']['units'];t['rows'][0][t['fields'].index('on_screen_name')]={'StringU16':TITLE};t['rows'][0][t['fields'].index('unique_index')]={'I32':obj(original['tables']['units'])['unique_index']+1}
 p=m['tables']['projectiles'];p['rows'][0][p['fields'].index('base_reload_time')]={'I32':0}
 m.update(unit=UNIT,title=TITLE,status='CONTINUOUS_CYCLE_HYPOTHESIS_UNTESTED',fallback=str(base.resolve()),fallback_sha256=CONFIRMED,assets=[],timelines=[])
 m['localisation']=json.loads(json.dumps(original['localisation']).replace(OLD,UNIT))
 for row in m['localisation']:
  if row['key'].startswith('units_on_screen_name_'):row['text']=TITLE
  elif 'long_description' in row['key']:row['text']='Separate 40-man automatic-cycle experiment. Repeats the confirmed two-shot human firing path with short aimed transitions and zero projectile reload timer. Continuous fire and ammo accounting require gameplay testing. No magazine reload simulation; Spencer visual placeholder.'
  else:row['text']='EXPERIMENT: two timed shots in a short firing cycle, with aimed recovery. Sustained automatic fire unconfirmed. Compare the unchanged TYPE20 BURST TEST.'
 def asset(path,data):
  p=OUT/'generated'/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);m['assets'].append(dict(source=str(p.resolve()),destination=path))
 for mode,observed in [('stand','musket_poise/mus_fire.anim'),('kneel','musket_kneel/mus_kneel_fire.anim')]:
  source=ROOT/'build/type20-research/vanilla/animations/shogun_animation/battle/men/musket'/observed
  raw=source.read_bytes();a=read_anim(raw);assert a['fps']==20 and len(a['bones'])==48
  stride=len(a['bones'])*28
  for kind,indices in [('fire',[0,2,4,0,2,4,0]),('ready',[0,0])]:
   head=bytearray(raw[:a['frame_offset']]);struct.pack_into('<I',head,a['frame_offset']-4,len(indices));struct.pack_into('<f',head,8,(len(indices)-1)/a['fps'])
   if kind=='fire':
    blocks=copy.deepcopy(a['event_blocks']);pos=next(e for block in blocks for e in block if e[0]=='FIRE_POSITION')
    for block in blocks:
     for event in block:
      if event[0]=='FIRE_TIME':event[1]='0.05'
    blocks[0]+=[['FIRE_TIME_2','0.20'],['FIRE_POSITION_2',*pos[1:]]]
   else:blocks=[[]]
   frames=b''.join(raw[a['frame_offset']+i*stride:a['frame_offset']+(i+1)*stride] for i in indices)
   dest='animations/steel_sakura/type20_auto_cycle/'+mode+'_'+kind+'.anim'
   asset(dest,bytes(head)+frames+event_bytes(blocks))
   m['timelines'].append(dict(source=str(source.resolve()),source_sha256=sha(source),destination=dest,mode=mode,kind=kind,frame_indices=indices,duration=(len(indices)-1)/a['fps']))
 source_frag=ROOT/'build/automatic-research/animations/battleconfiguration'
 standing={'AIM','COMBAT_READY','COMBAT_READY_TO_RELOAD_1','COMBAT_READY_TO_RELOAD_2','RELOAD_1','RELOAD_2','RELOAD_TO_COMBAT_READY','AIM_TO_COMBAT_READY','COMBAT_READY_TO_AIM'}
 kneeling={'COMBAT_READY_KNEEL','COMBAT_READY_KNEEL_TO_KNEEL_AIM','KNEEL_AIM','KNEEL_AIM_TO_COMBAT_READY_KNEEL','COMBAT_READY_KNEEL_TO_KNEEL_RELOAD','KNEEL_RELOAD','KNEEL_RELOAD_TO_COMBAT_READY_KNEEL'}
 m['state_remaps']={}
 for name,source in [('fire','shogun_man_musket_combat_fragment.txt'),('reload','boshin_man_rifle_combat_fragment.txt')]:
  txt=(source_frag/source).read_text(encoding='utf-8-sig');changed=[]
  def edit(line):
   match=re.match(r'(\w+)\s+filename\s*=\s*"([^"]+)"',line)
   if not match:return line
   state=match[1]
   if state in ['FIRE','KNEEL_FIRE']:mode='kneel' if state=='KNEEL_FIRE' else 'stand';kind='fire'
   elif state in standing:mode='stand';kind='ready'
   elif state in kneeling:mode='kneel';kind='ready'
   else:return line
   path='animations/steel_sakura/type20_auto_cycle/'+mode+'_'+kind+'.anim';changed.append(dict(state=state,path=path,source_path=match[2]))
   # blend_in_time=0.0 is observed in vanilla fragments. No new syntax or state names.
   return state+'\tfilename = "'+path+'"\tblend_in_time = 0.0'
  txt='\n'.join(edit(line) for line in txt.splitlines())+'\n'
  asset('animations/battleconfiguration/steel_sakura_type20_auto_cycle_'+name+'.txt',txt.encode());m['state_remaps'][name]=changed
 assert len(m['state_remaps']['fire'])==18 and len(m['state_remaps']['reload'])==8
 registry=(ROOT/'build/type20-burst/generated/animations/animation_tables/steel_sakura_type20_burst.txt').read_text()
 registry=registry.replace(OLD,UNIT).replace('steel_sakura_type20_burst_fire','steel_sakura_type20_auto_cycle_fire').replace('steel_sakura_type20_burst_reload','steel_sakura_type20_auto_cycle_reload')
 asset('animations/animation_tables/steel_sakura_type20_auto_cycle.txt',registry.encode())
 for a in original['assets']:
  if a['destination'].startswith('ui/'):asset(a['destination'].replace(OLD,UNIT),Path(a['source']).read_bytes())
 # Record the zero-timer evidence without claiming that grenade/fragment behavior proves rifle safety.
 vanilla=json.loads((ROOT/'build/diagnostic/base_projectiles.json').read_text(encoding='utf-8-sig'))['DBRFileInfo'][0]['table'];fields=[f['name'] for f in vanilla['definition']['fields']]
 zero=[dict(zip(fields,[next(iter(c.values())) for c in row])) for row in vanilla['table_data']]
 m['zero_reload_evidence']=[r['key'] for r in zero if r['base_reload_time']==0]
 assert 'blinding_grenade' in m['zero_reload_evidence']
 m['limitations']=['Zero reload is present on vanilla grenades/fragments; rifle behavior is untested.','The infantry state machine remains in use; it may impose an irreducible pause.','Two registered shot times only; no invented additional markers or infantry loop state.','No magazine/ammo-per-bullet accounting established; runtime rate is unmeasured.']
 (OUT/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('Prepared separate short-cycle two-event experiment; confirmed burst untouched.')
def validate():
 m=read_manifest();before=entries(Path(m['fallback']));packed=entries(PACK);assert sha(Path(m['fallback']))==CONFIRMED
 assert all(packed[k]==v for k,v in before.items())
 assert 'animations/animation_tables/animation_tables.txt' not in packed
 expected=set(before)|{a['destination'] for a in m['assets']}|{'db/'+t['table']+'/steel_sakura_type20_auto_cycle' for t in m['tables'].values()}|{'text/db/steel_sakura_type20_auto_cycle.loc'};assert set(packed)==expected
 for a in m['assets']:assert packed[a['destination']]==Path(a['source']).read_bytes()
 decoded=json.loads((OUT/'rpfm-roundtrip.json').read_text(encoding='utf-8-sig'))
 old=json.loads((ROOT/'build/type20-burst/manifest.json').read_text());renamed=json.loads(json.dumps(old['tables']).replace(OLD,UNIT))
 for name,t in m['tables'].items():
  actual=decoded[name]['DBRFileInfo'][0]['table'];assert actual['table_data']==t['rows'] and [f['name'] for f in actual['definition']['fields']]==t['fields']
  delta={f:(a,b) for f,a,b in zip(t['fields'],t['rows'][0],renamed[name]['rows'][0]) if a!=b}
  assert set(delta)==({'on_screen_name','unique_index'} if name=='units' else {'base_reload_time'} if name=='projectiles' else set()),(name,delta)
 assert obj(m['tables']['projectiles'])['projectile_number']==1 and obj(m['tables']['projectiles'])['base_reload_time']==0
 stats=obj(m['tables']['unit_stats_land']);assert stats['key']==stats['man_animations_table']==stats['equipment_theme']==UNIT
 assert stats['default_missile_type']==UNIT+'_bullet' and stats['men']==40 and stats['firing_mechanism']=='none'
 assert obj(m['tables']['units_to_exclusive_faction_permissions'])['faction']=='oda'
 loc=decoded['localisation']['LocRFileInfo'][0]['table']['table_data'];assert len(loc)==3
 assert any(r[0]['StringU16']=='units_on_screen_name_'+UNIT and r[1]['StringU16']==TITLE for r in loc)
 inventory=set(p.lower().replace('\\','/') for p in json.loads((ROOT/'build/inventory/all_data_local_paths.json').read_text()))
 for name in ['fire','reload']:
  txt=packed['animations/battleconfiguration/steel_sakura_type20_auto_cycle_'+name+'.txt'].decode()
  for ref in re.findall(r'filename\s*=\s*"([^"]+)"',txt):assert ref.lower().replace('\\','/') in inventory or ref.lower().replace('\\','/') in packed,ref
  for entry in m['state_remaps'][name]:assert entry['state']+'\tfilename = "'+entry['path']+'"\tblend_in_time = 0.0' in txt
 registry=packed['animations/animation_tables/steel_sakura_type20_auto_cycle.txt'].decode();assert ('animation_table '+UNIT) in registry and registry.count('animation_table ')==1
 for frag in re.findall(r'fragment\s+(\S+)',registry):assert 'animations/battleconfiguration/'+frag.lower()+'.txt' in inventory or 'animations/battleconfiguration/'+frag.lower()+'.txt' in packed
 for t in m['timelines']:
  raw=packed[t['destination']];a=read_anim(raw);src=Path(t['source']).read_bytes();b=read_anim(src);stride=len(b['bones'])*28
  assert sha(Path(t['source']))==t['source_sha256'] and a['bones']==b['bones'] and a['fps']==20 and a['frame_count']==len(t['frame_indices'])
  assert abs(a['duration']-t['duration'])<1e-5
  assert raw[a['frame_offset']:a['event_offset']]==b''.join(src[b['frame_offset']+i*stride:b['frame_offset']+(i+1)*stride] for i in t['frame_indices'])
  values=struct.unpack('<'+'f'*((a['event_offset']-a['frame_offset'])//4),raw[a['frame_offset']:a['event_offset']]);assert all(math.isfinite(v) for v in values)
  events=[e for block in a['event_blocks'] for e in block]
  if t['kind']=='ready':assert not events
  else:
   assert [(e[0],float(e[1])) for e in events if e[0].startswith('FIRE_TIME')]==[('FIRE_TIME',.05),('FIRE_TIME_2',.20)]
   assert not any(e[0]=='FIRE_TIME_3' for e in events)
   assert all(0<=float(e[1])<a['duration'] for e in events if e[0].startswith('FIRE_TIME'))
 report=dict(status='VERIFIED_OFFLINE_ONLY',runtime_status='PENDING_USER',automatic_fire='UNCONFIRMED_SHORT_REPEAT_CYCLE',pack=str(PACK.resolve()),pack_sha256=sha(PACK),manifest_sha256=sha(OUT/'manifest.json'),fallback=m['fallback'],fallback_sha256=CONFIRMED,failed_event_sha256=CONFIRMED,preserved_base_payloads=len(before),payloads=len(packed),title=TITLE)
 (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
def install(rollback=False):
 import type20_path_control as control
 control.OUT=OUT;control.install('fallback' if rollback else 'control')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','validate','install','rollback']);a=p.parse_args();{'prepare':prepare,'validate':validate,'install':install,'rollback':lambda:install(True)}[a.action]()
