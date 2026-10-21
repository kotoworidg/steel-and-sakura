"""Replace the failed dummy assignment with native Suppression Fire.
Shared native changes are explicit and require recorded user consent before install.
No firing statistics/animations are altered by this revision.
"""
import argparse,copy,hashlib,json
from pathlib import Path
from validate_free_fire_experiment import entries
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/type20-native-suppression';PACK=ROOT/'build/steel_sakura_type20_native_suppression.pack'
UNIT='steel_sakura_type20_suppressive_test';TITLE='TYPE20 SUPPRESSION FIX R2'
SOURCE='11B6BF8D14B868C31327495AD8E29CA35513DFFD3EA805DCF288D7E81B90BBD1';FALLBACK='56CCB4B44FC1520C379045ED3EC30D3EA13D6B3FB5BCF701A7259CC19EAD1299'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def put(t,f,v):
 i=t['fields'].index(f);k=next(iter(t['rows'][0][i]));t['rows'][0][i]={k:v}
def obj(t,r):return dict(zip(t['fields'],[next(iter(c.values())) for c in r]))
def prepare():
 source=OUT/'failed-dummy-ability.pack';assert sha(source)==SOURCE
 old=json.loads((ROOT/'build/type20-suppression/manifest.json').read_text());m=dict(source=str(source.resolve()),source_sha256=SOURCE,unit=UNIT,title=TITLE,tables={},localisation=copy.deepcopy(old['localisation']),fallback=old['fallback'],fallback_sha256=FALLBACK)
 assert sha(Path(m['fallback']))==FALLBACK
 for name in ['units','unit_to_unit_abilities_junctions']:
  t=copy.deepcopy(old['tables'][name]);t['path']='db/'+t['table']+'/steel_sakura_type20_suppression';t['new']=False;m['tables'][name]=t
 put(m['tables']['units'],'on_screen_name',TITLE);put(m['tables']['unit_to_unit_abilities_junctions'],'ability','suppression_fire')
 for name,changes in [('unit_abilities',{'requires_effect_enabling':False}),('unit_special_abilities',{'activated_projectile':UNIT+'_suppression_bullet'})]:
  source_t=json.loads((ROOT/'build/diagnostic'/('base_'+name+'.json')).read_text(encoding='utf-8-sig'))['DBRFileInfo'][0]['table'];fs=[f['name'] for f in source_t['definition']['fields']];rows=[r for r in source_t['table_data'] if next(iter(r[fs.index('key')].values()))=='suppression_fire'];assert len(rows)==1
  t=dict(table=name+'_tables',version=source_t['definition']['version'],fields=fs,rows=copy.deepcopy(rows),new=True,path='db/'+name+'_tables/steel_sakura_type20_native_suppression');t['vanilla_row']=copy.deepcopy(rows[0])
  for f,v in changes.items():put(t,f,v)
  m['tables'][name]=t
 for row in m['localisation']:
  if row['key']=='units_on_screen_name_'+UNIT:row['text']=TITLE
  elif row['key'].startswith('unit_description_texts_description_text_'):row['text']='Native Suppression Fire button test. Existing two-shot firing unchanged. The shared ability is temporarily unlocked and linked to our private suppressive projectile.'
  elif row['key'].startswith('unit_description_texts_long_description_text_'):row['text']='R2 replaces the failed dummy key with suppression_fire. Native 30-second activation and 120-second recharge retained. Shared-key changes affect all native Suppression Fire users while enabled. Continuous fire remains unconfirmed.'
 j=json.loads((ROOT/'build/diagnostic/base_unit_to_unit_abilities_junctions.json').read_text(encoding='utf-8-sig'))['DBRFileInfo'][0]['table'];fields=[f['name'] for f in j['definition']['fields']];m['other_native_users']=[dict(zip(fields,[next(iter(c.values())) for c in r]))['unit_name'] for r in j['table_data'] if next(iter(r[fields.index('ability')].values()))=='suppression_fire']
 m['shared_changes']={'unit_abilities.suppression_fire.requires_effect_enabling':{'vanilla':True,'test':False},'unit_special_abilities.suppression_fire.activated_projectile':{'vanilla':'boshin_rifle_suppressive','test':UNIT+'_suppression_bullet'}}
 m['scope_warning']='These definitions are shared by the native ability key. Other assigned users can gain the unlocked ability and use the private zero-reload/range900/damage3 projectile during activation. Native effects, active time 30 and recharge120 remain unchanged.'
 (OUT/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('Prepared native-key R2; shared impact recorded for '+str(len(m['other_native_users']))+' vanilla assignments.')
def validate():
 m=json.loads((OUT/'manifest.json').read_text());before=entries(Path(m['source']));after=entries(PACK);assert sha(Path(m['source']))==SOURCE
 changed={k for k in before if before[k]!=after[k]};expected={'db/units_tables/steel_sakura_type20_suppression','db/unit_to_unit_abilities_junctions_tables/steel_sakura_type20_suppression','text/db/steel_sakura_type20_suppression.loc'};assert changed==expected
 added={t['path'] for t in m['tables'].values() if t['new']};assert set(after)-set(before)==added
 assert len(after)==len(before)+2 and not set(before)-set(after)
 decoded=json.loads((OUT/'rpfm-roundtrip.json').read_text(encoding='utf-8-sig'))
 for name,t in m['tables'].items():
  actual=decoded[name]['DBRFileInfo'][0]['table'];assert actual['table_data']==t['rows'] and [f['name'] for f in actual['definition']['fields']]==t['fields']
  if t['new']:
   diffs=[f for f,a,b in zip(t['fields'],t['rows'][0],t['vanilla_row']) if a!=b];assert diffs==(['requires_effect_enabling'] if name=='unit_abilities' else ['activated_projectile'])
 assignment=obj(m['tables']['unit_to_unit_abilities_junctions'],m['tables']['unit_to_unit_abilities_junctions']['rows'][0]);assert assignment==dict(unit_name=UNIT,ability='suppression_fire')
 native=obj(m['tables']['unit_special_abilities'],m['tables']['unit_special_abilities']['rows'][0]);assert native['active_time']==30 and native['recharge_time']==120
 old=json.loads((ROOT/'build/type20-suppression/manifest.json').read_text());projectile=old['tables']['projectiles'];rows=[obj(projectile,r) for r in projectile['rows']];assert any(r['key']==native['activated_projectile'] and r['base_reload_time']==0 and r['shot_type']=='suppression_shot' for r in rows)
 assert all(after[k]==v for k,v in before.items() if k not in expected)
 r=dict(status='VERIFIED_OFFLINE_ONLY_NOT_GAMEPLAY_PROOF',runtime_status='PENDING_USER',pack=str(PACK.resolve()),pack_sha256=sha(PACK),manifest_sha256=sha(OUT/'manifest.json'),source=m['source'],source_sha256=SOURCE,fallback=m['fallback'],fallback_sha256=FALLBACK,failed_event_sha256=SOURCE,changed_payloads=sorted(changed),added_payloads=sorted(added),unchanged_payloads=len(before)-len(changed),shared_changes=m['shared_changes'],other_native_users=m['other_native_users'],automatic_fire='NOT_ESTABLISHED_ANIMATIONS_UNCHANGED')
 (OUT/'validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='other_native_users'},indent=2))
def install(rollback=False):
 if not rollback:
  consent=json.loads((OUT/'shared-override-consent.json').read_text());report=json.loads((OUT/'validation.json').read_text());assert consent['approved'] is True and consent['pack_sha256']==report['pack_sha256']
 import type20_path_control as control
 control.OUT=OUT;control.install('fallback' if rollback else 'control')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['prepare','validate','install','rollback']);a=ap.parse_args();{'prepare':prepare,'validate':validate,'install':install,'rollback':lambda:install(True)}[a.action]()
