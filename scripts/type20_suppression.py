"""Single-button suppressive-fire experiment using an unused registered engine key.
No vanilla ability/projectile rows are overridden. Runtime activation unconfirmed.
"""
import argparse,copy,hashlib,json,math,re,struct
from pathlib import Path
from inspect_anim_events import read_anim
from validate_free_fire_experiment import entries
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/type20-suppression';PACK=ROOT/'build/steel_sakura_type20_suppression.pack'
OLD='steel_sakura_type20_auto_cycle_test';UNIT='steel_sakura_type20_suppressive_test';ABILITY='dummy_suppression_fire'
TITLE='TYPE20 SUPPRESSIVE AUTO TEST';BASE='56CCB4B44FC1520C379045ED3EC30D3EA13D6B3FB5BCF701A7259CC19EAD1299'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def obj(t,row=None):return dict(zip(t['fields'],[next(iter(c.values())) for c in (row or t['rows'][0])]))
def put(t,field,value,row=0):
 i=t['fields'].index(field);typ=next(iter(t['rows'][row][i]));t['rows'][row][i]={typ:value}
def source_table(name):return json.loads((ROOT/'build/diagnostic'/('base_'+name+'.json')).read_text(encoding='utf-8-sig'))['DBRFileInfo'][0]['table']
def prepare():
 base=OUT/'confirmed-no-reload-bursts.pack';assert sha(base)==BASE
 old=json.loads((ROOT/'build/type20-auto-cycle/manifest.json').read_text());m=copy.deepcopy(old);m['tables']=json.loads(json.dumps(old['tables']).replace(OLD,UNIT))
 m.update(unit=UNIT,title=TITLE,status='ABILITY_AND_HIGHER_CADENCE_UNTESTED',fallback=str(base.resolve()),fallback_sha256=BASE,assets=[],timelines=[],ability=ABILITY)
 put(m['tables']['units'],'on_screen_name',TITLE);put(m['tables']['units'],'unique_index',obj(old['tables']['units'])['unique_index']+1)
 # One ordinary projectile and one private activated projectile, one bullet per timed event.
 p=m['tables']['projectiles'];put(p,'base_reload_time',1)
 p['rows'].append(copy.deepcopy(p['rows'][0]));put(p,'key',UNIT+'_suppression_bullet',1);put(p,'base_reload_time',0,1);put(p,'shot_type','suppression_shot',1);put(p,'calibration_area',2.0,1)
 def clone(name,predicate,changes):
  source=source_table(name);fields=[f['name'] for f in source['definition']['fields']]
  rows=[r for r in source['table_data'] if predicate(dict(zip(fields,[next(iter(c.values())) for c in r])))]
  assert len(rows)==1
  t=dict(table=name+'_tables',version=source['definition']['version'],fields=fields,rows=[copy.deepcopy(rows[0])])
  for f,v in changes.items():put(t,f,v)
  m['tables'][name]=t
 clone('unit_abilities',lambda r:r['key']=='suppression_fire',dict(key=ABILITY,requires_effect_enabling=False,bullet_text='Suppressive Fire',info_card_tooltip_text='Experimental higher-cadence suppressive fire for this test unit.',button_tooltip_text='Suppressive Fire||Attempts higher-cadence repeated two-shot fire for 10 seconds. Continuous automatic fire unconfirmed.'))
 clone('unit_special_abilities',lambda r:r['key']=='suppression_fire',dict(key=ABILITY,active_time=10.0,recharge_time=30.0,activated_projectile=UNIT+'_suppression_bullet',initial_recharge=-1.0,can_autotrigger=False))
 clone('unit_to_unit_abilities_junctions',lambda r:r['unit_name']=='Boshin_Inf_Light_Tosa_Riflemen' and r['ability']=='suppression_fire',dict(unit_name=UNIT,ability=ABILITY))
 # Verify this registered key has no rows in inspected vanilla/Otomo sources.
 for name in ['unit_abilities','unit_special_abilities','unit_to_unit_abilities_junctions']:
  assert ABILITY not in json.dumps(source_table(name))
  p=ROOT/'build/inventory'/('existing_mod_'+name+'.json')
  if p.exists():assert ABILITY not in p.read_text(encoding='utf-8-sig')
 m['localisation']=json.loads(json.dumps(old['localisation']).replace(OLD,UNIT))
 m['localisation'][0]['text']=TITLE;m['localisation'][1]['text']='EXPERIMENT: one Suppressive Fire button, private projectile switch, shorter two-shot cycles. Full automatic fire unconfirmed.';m['localisation'][2]['text']='Default two-shot bursts. Suppressive Fire attempts higher cadence for 10 seconds, followed by 30-second recharge. One bullet per event; no verified longer burst or magazine simulation. Compare unchanged burst units.'
 for field in ['bullet_text','info_card_tooltip_text','button_tooltip_text']:
  m['localisation'].append(dict(key='unit_abilities_'+field+'_'+ABILITY,text=obj(m['tables']['unit_abilities'])[field],tooltip=True))
 def asset(path,data):
  p=OUT/'generated'/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);m['assets'].append(dict(source=str(p.resolve()),destination=path))
 for a in old['assets']:
  path=a['destination'].replace(OLD,UNIT).replace('type20_auto_cycle','type20_suppression')
  raw=Path(a['source']).read_bytes()
  if a['destination'].endswith('.anim'):
   source=read_anim(raw)
   if '_fire.anim' in a['destination']:
    # Keep two existing marker names; retime to 0.00/0.10 and finish after 0.20.
    stride=len(source['bones'])*28;indices=[0,2,3,5,6]
    header=bytearray(raw[:source['frame_offset']]);struct.pack_into('<I',header,source['frame_offset']-4,5);struct.pack_into('<f',header,8,.20)
    from inspect_anim_events import event_bytes
    blocks=copy.deepcopy(source['event_blocks'])
    for block in blocks:
     for event in block:
      if event[0]=='FIRE_TIME':event[1]='0.00'
      if event[0]=='FIRE_TIME_2':event[1]='0.10'
    raw=bytes(header)+b''.join(raw[source['frame_offset']+i*stride:source['frame_offset']+(i+1)*stride] for i in indices)+event_bytes(blocks)
   else:indices=list(range(source['frame_count']))
   m['timelines'].append(dict(source=a['source'],source_sha256=sha(Path(a['source'])),destination=path,source_frame_indices=indices))
  elif a['destination'].endswith('.txt'):
   raw=raw.decode().replace(OLD,UNIT).replace('type20_auto_cycle','type20_suppression').encode()
  asset(path,raw)
 for path in json.loads((OUT/'ui-source-paths.json').read_text(encoding='utf-8-sig')):
  asset(path.replace('suppression_fire',ABILITY),(OUT/'vanilla'/path).read_bytes())
 m['runtime_limits']=['Only two shot events are established; longer individual bursts are not implemented.','A fixed engine key does not establish its active behavior or UI visibility.','No evidence yet shows that an ability can switch the infantry animation controller.','Suppressive shot effects, projectile switching, expiry and ammo accounting need gameplay confirmation.']
 (OUT/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('Prepared single-button supported-key diagnostic; no shared vanilla row overrides.')
def validate():
 m=json.loads((OUT/'manifest.json').read_text());base=entries(Path(m['fallback']));p=entries(PACK);assert sha(Path(m['fallback']))==BASE
 assert all(p[k]==v for k,v in base.items())
 expected=set(base)|{a['destination'] for a in m['assets']}|{'db/'+t['table']+'/steel_sakura_type20_suppression' for t in m['tables'].values()}|{'text/db/steel_sakura_type20_suppression.loc'};assert set(p)==expected
 for a in m['assets']:assert p[a['destination']]==Path(a['source']).read_bytes()
 decoded=json.loads((OUT/'rpfm-roundtrip.json').read_text(encoding='utf-8-sig'))
 for name,t in m['tables'].items():
  dt=decoded[name]['DBRFileInfo'][0]['table'];assert dt['table_data']==t['rows'] and [f['name'] for f in dt['definition']['fields']]==t['fields']
 assert obj(m['tables']['unit_abilities'])['key']==ABILITY and obj(m['tables']['unit_abilities'])['requires_effect_enabling'] is False
 ability=obj(m['tables']['unit_special_abilities']);assert ability['key']==ABILITY and ability['activated_projectile']==UNIT+'_suppression_bullet' and ability['active_time']==10
 assert obj(m['tables']['unit_to_unit_abilities_junctions'])==dict(unit_name=UNIT,ability=ABILITY)
 bullets=[obj(m['tables']['projectiles'],row) for row in m['tables']['projectiles']['rows']];assert [r['base_reload_time'] for r in bullets]==[1,0] and all(r['projectile_number']==1 for r in bullets) and bullets[1]['shot_type']=='suppression_shot'
 stats=obj(m['tables']['unit_stats_land']);assert stats['key']==stats['man_animations_table']==stats['equipment_theme']==UNIT and stats['default_missile_type']==bullets[0]['key']
 assert obj(m['tables']['units_to_exclusive_faction_permissions'])['faction']=='oda'
 inventory=set(x.lower().replace('\\','/') for x in json.loads((ROOT/'build/inventory/all_data_local_paths.json').read_text()))
 for a in m['assets']:
  path=a['destination']
  if path.endswith('.txt'):
   text=p[path].decode()
   if '/battleconfiguration/' in path:
    for ref in re.findall(r'filename\s*=\s*"([^"]+)"',text):assert ref.lower().replace('\\','/') in p or ref.lower().replace('\\','/') in inventory,ref
   else:
    assert ('animation_table '+UNIT) in text
    for f in re.findall(r'fragment\s+(\S+)',text):assert 'animations/battleconfiguration/'+f.lower()+'.txt' in p or 'animations/battleconfiguration/'+f.lower()+'.txt' in inventory
 for a in m['assets']:
  if a['destination'].startswith('ui/units/'):assert a['destination'].endswith('/'+UNIT+'.tga')
 for t in m['timelines']:
  raw=p[t['destination']];a=read_anim(raw);src=Path(t['source']).read_bytes();b=read_anim(src);stride=len(b['bones'])*28;assert sha(Path(t['source']))==t['source_sha256'] and a['bones']==b['bones']
  assert raw[a['frame_offset']:a['event_offset']]==b''.join(src[b['frame_offset']+i*stride:b['frame_offset']+(i+1)*stride] for i in t['source_frame_indices'])
  assert a['frame_count']==len(t['source_frame_indices']) and abs(a['duration']-(a['frame_count']-1)/a['fps'])<1e-5
  vals=struct.unpack('<'+'f'*((a['event_offset']-a['frame_offset'])//4),raw[a['frame_offset']:a['event_offset']]);assert all(math.isfinite(v) for v in vals)
  ev=[e for block in a['event_blocks'] for e in block]
  if '_fire.anim' in t['destination']:assert [(e[0],float(e[1])) for e in ev if e[0].startswith('FIRE_TIME')]==[('FIRE_TIME',0.),('FIRE_TIME_2',.1)]
  else:assert not ev
 r=dict(status='VERIFIED_OFFLINE_ONLY',runtime_status='PENDING_USER',pack=str(PACK.resolve()),pack_sha256=sha(PACK),manifest_sha256=sha(OUT/'manifest.json'),fallback=m['fallback'],fallback_sha256=BASE,failed_event_sha256=BASE,preserved_base_payloads=len(base),payloads=len(p),title=TITLE,ability=ABILITY,continuous_fire='UNCONFIRMED',longer_individual_burst='NOT_IMPLEMENTED_TWO_EVENTS_ONLY')
 (OUT/'validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
def install(rollback=False):
 import type20_path_control as control
 control.OUT=OUT;control.install('fallback' if rollback else 'control')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['prepare','validate','install','rollback']);a=ap.parse_args();{'prepare':prepare,'validate':validate,'install':install,'rollback':lambda:install(True)}[a.action]()
