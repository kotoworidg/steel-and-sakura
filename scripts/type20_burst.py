"""Prepare and validate an isolated two-event human-rig burst hypothesis.
No reload/stat edits, shared animation registry overrides, or runtime success claims.
"""
import argparse,copy,datetime,hashlib,json,re,shutil,struct
from pathlib import Path
from inspect_anim_events import read_anim,event_bytes
from validate_free_fire_experiment import entries
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'build/type20-burst'
UNIT='steel_sakura_type20_automatic_fire_test'
TITLE='TYPE20 BURST TEST - two timed shots'
PACK=ROOT/'build/steel_sakura_type20_burst.pack'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def prepare():
 OUT.mkdir(parents=True,exist_ok=True)
 old=json.loads((ROOT/'build/type20-research/event-test-manifest.json').read_text())
 m=copy.deepcopy(old);m.update(title=TITLE,status='BURST_HYPOTHESIS_RUNTIME_UNCONFIRMED',assets=[],timelines=[])
 assert sha(Path(m['fallback']))==m['fallback_sha256']
 for t in m['tables'].values():
  if t['table']=='units_tables':t['rows'][0][t['fields'].index('on_screen_name')]={'StringU16':TITLE}
 m['localisation'][0]['text']=TITLE
 m['localisation'][1]['text']='Experimental two-shot animation, 0.15 seconds between markers. Actual second bullet requires in-game confirmation.'
 m['localisation'][2]['text']='Private human animation registry and recoil pulses. Unchanged reload, range, damage and bullet count. Spencer visual placeholder; no modern magazine animation.'
 def asset(path,data):
  p=OUT/'generated'/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
  m['assets'].append(dict(source=str(p.resolve()),destination=path))
 for mode,path in [('stand','musket_poise/mus_fire.anim'),('kneel','musket_kneel/mus_kneel_fire.anim')]:
  source=ROOT/'build/type20-research/vanilla/animations/shogun_animation/battle/men/musket'/path
  raw=source.read_bytes();a=read_anim(raw);assert a['fps']==20 and len(a['bones'])==48
  # Repeat the first three sampled recoil poses, then finish the source recovery.
  indices=[0,2,4,0,2,4]+list(range(5,a['frame_count']))
  stride=len(a['bones'])*28
  frames=[raw[a['frame_offset']+i*stride:a['frame_offset']+(i+1)*stride] for i in indices]
  head=bytearray(raw[:a['frame_offset']]);struct.pack_into('<I',head,a['frame_offset']-4,len(indices));struct.pack_into('<f',head,8,(len(indices)-1)/a['fps'])
  blocks=copy.deepcopy(a['event_blocks']);first=next(e for b in blocks for e in b if e[0]=='FIRE_TIME');time=float(first[1])
  assert not any(e[0]=='FIRE_TIME_2' for b in blocks for e in b)
  pos=next(e for b in blocks for e in b if e[0]=='FIRE_POSITION')
  blocks[0]+=[['FIRE_TIME_2',f'{time+.15:.2f}'],['FIRE_POSITION_2',*pos[1:]]]
  dest='animations/steel_sakura/type20_burst/'+mode+'.anim'
  asset(dest,bytes(head)+b''.join(frames)+event_bytes(blocks))
  m['timelines'].append(dict(mode=mode,source=str(source.resolve()),source_sha256=sha(source),frame_indices=indices,first_shot=time,second_shot=time+.15,destination=dest))
 fragments=ROOT/'build/automatic-research/animations/battleconfiguration'
 fire=(fragments/'shogun_man_musket_combat_fragment.txt').read_text(encoding='utf-8-sig')
 for state,mode in [('FIRE','stand'),('KNEEL_FIRE','kneel')]:
  fire,n=re.subn(r'(?m)^('+state+r'\s+filename\s*=\s*")[^"]+(")',lambda x:x[1]+'animations/steel_sakura/type20_burst/'+mode+'.anim'+x[2],fire);assert n==1
 asset('animations/battleconfiguration/steel_sakura_type20_burst_fire.txt',fire.encode())
 reload=(fragments/'boshin_man_rifle_combat_fragment.txt').read_text(encoding='utf-8-sig')
 inventory=set(p.lower().replace('\\','/') for p in json.loads((ROOT/'build/inventory/all_data_local_paths.json').read_text()))
 poise='animations/shogun_animation/battle/men/musket/musket_poise/mus_poise.anim'
 kneel='animations/shogun_animation/battle/men/musket/musket_kneel/mus_kneel_poise.anim'
 assert poise in inventory and kneel in inventory
 # Keep the actual database reload timer; use existing aim clips instead of lever cycling.
 count=0
 def aimed(x):
  nonlocal count
  count+=1
  return x[1]+(kneel if 'KNEEL' in x[1] else poise)+x[3]
 reload=re.sub(r'(?m)^([^\n]*filename\s*=\s*")([^"]+)(")',aimed,reload);assert count==8
 asset('animations/battleconfiguration/steel_sakura_type20_burst_reload.txt',reload.encode())
 registry=(ROOT/'build/type20-research/vanilla/animations/animation_tables/animation_tables.txt').read_text(encoding='utf-8-sig')
 block=re.search(r'animation_table boshin_man_rifle_trained\s*\{[^}]*\}',registry).group()
 block=block.replace('animation_table boshin_man_rifle_trained','animation_table '+UNIT).replace('shogun_man_musket_combat_fragment','steel_sakura_type20_burst_fire').replace('boshin_man_rifle_combat_fragment','steel_sakura_type20_burst_reload')
 asset('animations/animation_tables/steel_sakura_type20_burst.txt',('version 1\n'+block+'\n').encode())
 for a in old['assets']:
  if a['destination'].startswith('ui/'):asset(a['destination'],Path(a['source']).read_bytes())
 m['scope']='Isolated burst and aimed recovery hypothesis. Original rifle, grenade, artillery payloads unchanged.'
 (OUT/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 print('Prepared unique registry, two-event recoil clips, and aimed recovery; no combat stat changes.')
def validate():
 m=json.loads((OUT/'manifest.json').read_text());base=entries(Path(m['fallback']));p=entries(PACK)
 assert all(p[k]==v for k,v in base.items())
 assert 'animations/animation_tables/animation_tables.txt' not in p
 for a in m['assets']:assert p[a['destination']]==Path(a['source']).read_bytes()
 expected=set(base)|{a['destination'] for a in m['assets']}|{'db/'+t['table']+'/steel_sakura_type20_burst' for t in m['tables'].values()}|{'text/db/steel_sakura_type20_burst.loc'}
 assert set(p)==expected
 inv=set(x.lower().replace('\\','/') for x in json.loads((ROOT/'build/inventory/all_data_local_paths.json').read_text()))
 for path,data in p.items():
  if path.startswith('animations/battleconfiguration/'):
   for ref in re.findall(r'filename\s*=\s*"([^"]+)"',data.decode()):assert ref.lower().replace('\\','/') in inv or ref.lower().replace('\\','/') in p,ref
 for t in m['timelines']:
  raw=p[t['destination']];a=read_anim(raw);src=Path(t['source']).read_bytes();b=read_anim(src);stride=len(b['bones'])*28
  assert sha(Path(t['source']))==t['source_sha256'] and a['bones']==b['bones'] and a['fps']==b['fps']
  assert a['frame_count']==len(t['frame_indices']) and abs(a['duration']-(a['frame_count']-1)/a['fps'])<1e-5
  assert raw[a['frame_offset']:a['event_offset']]==b''.join(src[b['frame_offset']+i*stride:b['frame_offset']+(i+1)*stride] for i in t['frame_indices'])
  events=[e for block in a['event_blocks'] for e in block]
  assert sum(e[0]=='FIRE_TIME' for e in events)==sum(e[0]=='FIRE_TIME_2' for e in events)==1
  assert abs(float(next(e[1] for e in events if e[0]=='FIRE_TIME_2'))-t['second_shot'])<1e-5
  assert all(0<=float(e[1])<=a['duration'] for e in events if e[0] in ['FIRE_TIME','FIRE_TIME_2'])
  values=struct.unpack('<'+'f'*((a['event_offset']-a['frame_offset'])//4),raw[a['frame_offset']:a['event_offset']]);import math;assert all(math.isfinite(v) for v in values)
 decoded=json.loads((OUT/'rpfm-roundtrip.json').read_text(encoding='utf-8-sig'))
 for name,t in m['tables'].items():
  actual=decoded[name]['DBRFileInfo'][0]['table']
  assert actual['table_data']==t['rows']
  assert [f['name'] for f in actual['definition']['fields']]==t['fields']
 registry=p['animations/animation_tables/steel_sakura_type20_burst.txt'].decode()
 assert registry.count('animation_table ')==1 and ('animation_table '+UNIT) in registry
 assert re.search(r'fragment\s+steel_sakura_type20_burst_fire\b',registry) and re.search(r'fragment\s+steel_sakura_type20_burst_reload\b',registry)
 assert not re.search(r'fragment\s+shogun_man_musket_combat_fragment\b',registry)
 for fragment in re.findall(r'fragment\s+(\S+)',registry):
  ref='animations/battleconfiguration/'+fragment.lower()+'.txt'
  assert ref in inv or ref in p,ref
 stats=m['tables']['unit_stats_land']; row=dict(zip(stats['fields'],[next(iter(c.values())) for c in stats['rows'][0]]))
 assert row['man_animations_table']==UNIT and row['equipment_theme']==UNIT and row['default_missile_type']==UNIT+'_bullet'
 assert row['firing_mechanism']=='none'
 original=json.loads((ROOT/'build/type20-research/event-test-manifest.json').read_text())
 for n,t in m['tables'].items():
  if n!='units':assert t==original['tables'][n]
  else:
   delta=[f for f,a,b in zip(t['fields'],t['rows'][0],original['tables'][n]['rows'][0]) if a!=b]
   assert delta==['on_screen_name']
 r=dict(status='VERIFIED_OFFLINE_ONLY',runtime_status='PENDING_USER',automatic_fire='UNCONFIRMED_TWO_EVENT_HYPOTHESIS',pack=str(PACK.resolve()),pack_sha256=sha(PACK),manifest_sha256=sha(OUT/'manifest.json'),fallback=m['fallback'],fallback_sha256=m['fallback_sha256'],failed_event_sha256='3CDF8ADF3DDEC46FDD9E3379D37530B353DD8DCC5A55827E11FF9DF5B870768C',preserved_base_payloads=len(base),title=TITLE,payloads=len(p))
 (OUT/'validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
def install(rollback=False):
 import type20_path_control as control
 control.OUT=OUT
 control.install('fallback' if rollback else 'control')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['prepare','validate','install','rollback']);a=ap.parse_args()
 {'prepare':prepare,'validate':validate,'install':install,'rollback':lambda:install(True)}[a.action]()

