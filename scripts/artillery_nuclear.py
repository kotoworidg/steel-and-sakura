"""Private high-blast artillery shell plus native ability test; rifle data preserved.
The shared shrapnel_shot relink requires exact-build human consent before install.
"""
import argparse,copy,hashlib,json
from pathlib import Path
from validate_free_fire_experiment import entries
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/artillery-nuclear-test';PACK=ROOT/'build/steel_sakura_artillery_nuclear_test.pack'
BASE='1737D02D67F0C9100BBCC5255057C12B532F9805482D18ADC910542653D96DCD'
UNIT='SteelSakura_Modern_Artillery';TITLE='FH70 BATTERY - NUCLEAR TEST';PROJ='steel_sakura_nuclear_projectile_v1';EXP='steel_sakura_nuclear_explosion_v1';CARD='steel_sakura_fh70_artillery_test'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def obj(fields,row):return dict(zip(fields,[next(iter(c.values())) for c in row]))
def put(t,row,field,value):
 i=t['fields'].index(field);kind=next(iter(t['rows'][row][i]));t['rows'][row][i]={kind:value}
def base_table(name):return json.loads((ROOT/'build/inventory'/('table_'+name+'.json')).read_text(encoding='utf-8-sig'))['DBRFileInfo'][0]['table']
def prepare():
 source=OUT/'working-rifle-baseline.pack';assert sha(source)==BASE
 audit=json.loads((ROOT/'build/artillery-nuclear-audit/decoded.json').read_text(encoding='utf-8-sig'))
 m=dict(source=str(source.resolve()),source_sha256=BASE,fallback=str(source.resolve()),fallback_sha256=BASE,unit=UNIT,title=TITLE,tables={},assets=[])
 t=audit['db/units_tables/steel_sakura_combined']['DBRFileInfo'][0]['table'];fields=[f['name'] for f in t['definition']['fields']]
 unit_t=dict(table='units_tables',version=t['definition']['version'],fields=fields,rows=copy.deepcopy(t['table_data']),new=False,path='db/units_tables/steel_sakura_combined')
 matches=[i for i,row in enumerate(unit_t['rows']) if obj(fields,row)['key']==UNIT];assert len(matches)==1
 for field,value in dict(on_screen_name=TITLE,icon_name=CARD,info_pic=CARD).items():put(unit_t,matches[0],field,value)
 m['tables']['units']=unit_t
 def clone(name,key,changes):
  source=base_table(name);fields=[f['name'] for f in source['definition']['fields']];rows=[r for r in source['table_data'] if obj(fields,r)[fields[0]]==key];assert len(rows)==1
  t=dict(table=name+'_tables',version=source['definition']['version'],fields=fields,rows=copy.deepcopy(rows),new=True,path='db/'+name+'_tables/steel_sakura_artillery_nuclear_test',source_key=key,source_row=copy.deepcopy(rows[0]))
  for f,v in changes.items():put(t,0,f,v)
  m['tables'][name]=t
 clone('projectiles','boshin_armstrong_gun_shell',dict(key=PROJ,explosion_type=EXP,effective_range=900,base_reload_time=60,calibration_area=10.0))
 clone('projectiles_explosions','boshin_armstrong_gun_shell',dict(key=EXP,detonation_radius=40.0,detonation_damage=100.0,explosion_particle_effect='Cannon_common_air_explosion_lrg',explosion_particle_effect_on_ground='Cannon_common_air_explosion_lrg'))
 clone('unit_special_abilities','shrapnel_shot',dict(activated_projectile=PROJ,active_time=15.0,num_uses=1))
 tooltip='Nuclear Shell (TEST)||One 15-second high-blast ammunition window per battle. Four-gun battery may fire a volley; exactly one shell is not guaranteed. Existing explosion visual; no mushroom cloud. Shared artillery ability test.'
 clone('unit_abilities','shrapnel_shot',dict(bullet_text='Nuclear Shell (TEST)',info_card_tooltip_text='Experimental large-blast ammunition. One activation per battle; Armstrong placeholder artillery.',button_tooltip_text=tooltip))
 # Assert private keys are absent in inspected vanilla, Otomo and the actual baseline.
 for name,key in [('projectiles',PROJ),('projectiles_explosions',EXP)]:
  assert key not in json.dumps(base_table(name))
  mod=ROOT/'build/inventory'/('existing_mod_'+name+'.json')
  if mod.exists():assert key not in mod.read_text(encoding='utf-8-sig')
  assert not any(key.encode('utf-16le') in data for path,data in entries(source).items() if path.startswith('db/'+name+'_tables/'))
 # Validate the selected effect is used by a real land bombardment explosion.
 native=base_table('projectiles_explosions');nf=[f['name'] for f in native['definition']['fields']];bomb=[obj(nf,row) for row in native['table_data'] if obj(nf,row)['key']=='boshin_bombardment_large'];assert len(bomb)==1 and bomb[0]['explosion_particle_effect_on_ground']=='Cannon_common_air_explosion_lrg'
 loc=json.loads((OUT/'base-localisation.json').read_text(encoding='utf-8-sig'))['LocRFileInfo'][0]['table']['table_data']
 m['localisation']=[dict(key=r[0]['StringU16'],text=r[1]['StringU16'],tooltip=r[2]['Boolean']) for r in loc]
 texts={'units_on_screen_name_'+UNIT:TITLE,'unit_description_texts_description_text_'+UNIT:'FH70-inspired four-gun test battery. Armstrong models. Nuclear Shell uses an existing large explosion effect.','unit_description_texts_long_description_text_'+UNIT:'TEST: forty crew and four Armstrong placeholder cannons. Normal shells remain conventional. Nuclear Shell offers one 15-second high-blast firing window, not a guaranteed single projectile. Radius 40 and damage 100 are experimental DB values. No mushroom cloud or fallout implemented.'}
 ability=obj(m['tables']['unit_abilities']['fields'],m['tables']['unit_abilities']['rows'][0])
 for f in ['bullet_text','info_card_tooltip_text','button_tooltip_text']:texts['unit_abilities_'+f+'_shrapnel_shot']=ability[f]
 for key,text in texts.items():
  found=[r for r in m['localisation'] if r['key']==key]
  if found:assert len(found)==1;found[0]['text']=text
  else:m['localisation'].append(dict(key=key,text=text,tooltip=key.startswith('unit_abilities_')))
 cards=json.loads((OUT/'card-source-paths.json').read_text(encoding='utf-8-sig'));assert len(cards)==5
 for source_path in cards:
  dest=source_path.replace('boshin_modern_art_armstrong_guns',CARD);src=OUT/'vanilla'/source_path;assert src.exists();m['assets'].append(dict(source=str(src.resolve()),destination=dest))
 j=base_table('unit_to_unit_abilities_junctions');jf=[f['name'] for f in j['definition']['fields']];m['other_native_users']=[obj(jf,row)['unit_name'] for row in j['table_data'] if obj(jf,row)['ability']=='shrapnel_shot']
 m['shared_scope']='All units assigned native shrapnel_shot use this Nuclear Shell test label, one activation, 15-second window and private high-blast projectile while the pack is enabled. Native suppression_fire and all infantry data are unchanged.'
 m['changed_loc_keys']=list(texts)
 (OUT/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('Prepared actual high-blast projectile/explosion and artillery cards; '+str(len(m['other_native_users']))+' other vanilla Shrapnel Shot assignments are affected by the shared key.')
def validate():
 m=json.loads((OUT/'manifest.json').read_text());before=entries(Path(m['source']));after=entries(PACK);assert sha(Path(m['source']))==BASE
 changed={k for k in before if before[k]!=after[k]};expected={'db/units_tables/steel_sakura_combined','text/db/steel_sakura_combined.loc'};assert changed==expected
 added={t['path'] for t in m['tables'].values() if t['new']}|{a['destination'] for a in m['assets']};assert set(after)-set(before)==added and not set(before)-set(after)
 assert all(after[k]==v for k,v in before.items() if k not in expected)
 decoded=json.loads((OUT/'rpfm-roundtrip.json').read_text(encoding='utf-8-sig'))
 for name,t in m['tables'].items():
  actual=decoded[name]['DBRFileInfo'][0]['table'];assert actual['table_data']==t['rows'] and [f['name'] for f in actual['definition']['fields']]==t['fields']
 old=json.loads((ROOT/'build/artillery-nuclear-audit/decoded.json').read_text(encoding='utf-8-sig'));oldunit=old['db/units_tables/steel_sakura_combined']['DBRFileInfo'][0]['table'];fields=m['tables']['units']['fields']
 for a,b in zip(oldunit['table_data'],m['tables']['units']['rows']):
  changes={f for f,x,y in zip(fields,a,b) if x!=y};assert changes==({'on_screen_name','icon_name','info_pic'} if obj(fields,a)['key']==UNIT else set())
 for a in m['assets']:assert after[a['destination']]==Path(a['source']).read_bytes()
 assert {a['destination'].split('/')[-2] for a in m['assets']}=={'icons','icons_square','info','recruitment_large','recruitment_small'}
 def row(name):t=m['tables'][name];return obj(t['fields'],t['rows'][0])
 p=row('projectiles');e=row('projectiles_explosions');ability=row('unit_special_abilities');assert p['key']==PROJ and p['explosion_type']==EXP and ability['key']=='shrapnel_shot' and ability['activated_projectile']==PROJ
 assert p['projectile_number']==1 and p['base_reload_time']==60 and e['detonation_radius']==40 and e['detonation_damage']==100 and e['particle_number']==4
 assert ability['active_time']==15 and ability['num_uses']==1
 for table,key in [('unit_stats_land','key'),('units_to_exclusive_faction_permissions','key'),('units_to_groupings_military_permissions','unit'),('unit_to_unit_abilities_junctions','unit_name')]:
  t=old['db/'+table+'_tables/steel_sakura_combined']['DBRFileInfo'][0]['table'];f=[x['name'] for x in t['definition']['fields']];rows=[obj(f,r) for r in t['table_data'] if obj(f,r)[key]==UNIT];assert rows
  if table=='unit_stats_land':assert rows[0]['guns']==4 and rows[0]['men']==40
  if table=='units_to_exclusive_faction_permissions':assert any(r['faction']=='oda' and r['allowed'] for r in rows)
  if table=='unit_to_unit_abilities_junctions':assert any(r['ability']=='shrapnel_shot' for r in rows)
 original_loc=json.loads((OUT/'base-localisation.json').read_text(encoding='utf-8-sig'))['LocRFileInfo'][0]['table']['table_data'];old_loc={r[0]['StringU16']:r[1]['StringU16'] for r in original_loc};new_loc={r['key']:r['text'] for r in m['localisation']};assert all(new_loc[k]==v for k,v in old_loc.items() if k not in m['changed_loc_keys'])
 r=dict(status='VERIFIED_OFFLINE_ONLY',runtime_status='PENDING_USER',pack=str(PACK.resolve()),pack_sha256=sha(PACK),manifest_sha256=sha(OUT/'manifest.json'),fallback=m['fallback'],fallback_sha256=BASE,failed_event_sha256=BASE,changed_payloads=sorted(changed),added_payloads=sorted(added),unchanged_payloads=len(before)-len(changed),title=TITLE,other_native_users=m['other_native_users'],shared_scope=m['shared_scope'],infantry_and_suppression_payloads_unchanged=True,nuclear_visual='EXISTING_LARGE_EXPLOSION_NO_MUSHROOM_CLOUD')
 (OUT/'validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k not in ['other_native_users','added_payloads']},indent=2))
def install(rollback=False):
 if not rollback:
  consent=json.loads((OUT/'shared-override-consent.json').read_text());report=json.loads((OUT/'validation.json').read_text());assert consent['approved'] is True and consent['pack_sha256']==report['pack_sha256']
 import type20_path_control as control
 control.OUT=OUT;control.install('fallback' if rollback else 'control')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['prepare','validate','install','rollback']);a=ap.parse_args();{'prepare':prepare,'validate':validate,'install':install,'rollback':lambda:install(True)}[a.action]()
