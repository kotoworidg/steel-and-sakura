"""Build and validate a supported-mechanics playable Type 20 upgrade.
Preserves the confirmed firing animations and unrelated baseline payloads.
"""
import argparse,copy,datetime,hashlib,io,json,struct,zipfile
from pathlib import Path
from tracked_files import ROOT,write_bytes,write_text,digest
from type20_pack_codec import pack_entries,pack_bytes,db_read,db_bytes,loc_read,loc_bytes
PROFILE=ROOT/'src/type20-supported.json'
BASE=ROOT/'build/type20-auto-cycle/confirmed-burst.pack'
R2=ROOT/'build/type20-five-shot/confirmed-suppression-r2.pack'
OUT=ROOT/'build/type20-playable'
TYPE20='steel_sakura_type20_automatic_fire_test'
PATHS={n:'db/'+n+'_tables/steel_sakura_type20_burst' for n in ['units','unit_stats_land','projectiles']}
LOC='text/db/steel_sakura_type20_burst.loc'
JUNCTION='db/unit_to_unit_abilities_junctions_tables/steel_sakura_type20_playable'
OPTIONAL='zz_steel_sakura_type20_suppression'

def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,obj,why):return write_text(p,json.dumps(obj,indent=2)+'\n','Type20 playable '+why)
def schema(table):return dict(version=table['definition']['version'],fields=[(f['name'],f['field_type']) for f in table['definition']['fields']])

def evidence():
 profile=load(PROFILE)
 if digest(BASE.read_bytes())!=profile['baseline_sha256']:raise ValueError('confirmed baseline differs')
 if digest(R2.read_bytes())!='1737D02D67F0C9100BBCC5255057C12B532F9805482D18ADC910542653D96DCD':raise ValueError('preserved native suppression baseline differs')
 decoded=load(ROOT/'build/type20-burst/rpfm-roundtrip.json');native=load(ROOT/'build/type20-native-suppression/rpfm-roundtrip.json')
 specs={n:schema(decoded[n]['DBRFileInfo'][0]['table']) for n in PATHS}
 for n in ['unit_abilities','unit_special_abilities','unit_to_unit_abilities_junctions']:specs[n]=schema(native[n]['DBRFileInfo'][0]['table'])
 return profile,pack_entries(BASE.read_bytes()),pack_entries(R2.read_bytes()),specs

def decode_lossless(raw,spec):
 prefix,rows=db_read(raw,spec)
 if db_bytes(prefix,rows,spec)!=raw:raise ValueError('existing RPFM payload does not roundtrip')
 return prefix,rows

def planned(profile,base,r2,specs):
 core=dict(base);before={};after={};modified=[]
 for name,path in PATHS.items():
  prefix,rows=decode_lossless(base[path],specs[name])
  if len(rows)!=1:raise ValueError('ambiguous Type20 source row')
  before[name]=copy.deepcopy(rows[0]);row=rows[0]
  if name=='units':row.update(profile['costs']);row['on_screen_name']=profile['title']
  if name=='unit_stats_land':row.update(profile['stats'])
  if name=='projectiles':
   row.update(profile['projectile']);secondary=copy.deepcopy(row);secondary.update(profile['suppression_projectile']);rows.append(secondary)
  after[name]=copy.deepcopy(rows)
  core[path]=db_bytes(prefix,rows,specs[name]);modified.append(path)
 prefix,loc=loc_read(base[LOC])
 if loc_bytes(prefix,loc)!=base[LOC] or len(loc)!=3:raise ValueError('source localization differs')
 values=[profile['title'],profile['description'],profile['long_description']]
 for row,value in zip(loc,values):row[1]=value
 core[LOC]=loc_bytes(prefix,loc);modified.append(LOC)
 spec=specs['unit_to_unit_abilities_junctions'];template='db/unit_to_unit_abilities_junctions_tables/steel_sakura_combined'
 prefix,_=decode_lossless(base[template],spec)
 core[JUNCTION]=db_bytes(prefix,[{'unit_name':TYPE20,'ability':profile['core_ability']}],spec)
 optional={}
 optional[JUNCTION.replace('steel_sakura_type20_playable',OPTIONAL)]=db_bytes(prefix,[{'unit_name':TYPE20,'ability':profile['optional_ability']}],spec)
 for n in ['unit_abilities','unit_special_abilities']:
  path='db/'+n+'_tables/steel_sakura_type20_native_suppression';prefix,rows=decode_lossless(r2[path],specs[n])
  if len(rows)!=1 or rows[0]['key']!='suppression_fire':raise ValueError('native suppression template differs')
  if n=='unit_special_abilities':rows[0]['activated_projectile']=profile['suppression_projectile']['key']
  optional['db/'+n+'_tables/'+OPTIONAL]=db_bytes(prefix,rows,specs[n])
 return core,optional,dict(before=before,after=after,modified_payloads=modified,added_payloads=[JUNCTION],optional_shared_scope='Native suppression_fire unlock and activated projectile apply to every unit already assigned this ability. Core-only installation has no shared ability overrides.')

def validate_bytes(core_raw,optional_raw,profile=None):
 p,base,r2,specs=evidence();profile=profile or p
 core=pack_entries(core_raw);optional=pack_entries(optional_raw);expected,expected_optional,changes=planned(profile,base,r2,specs)
 if core!=expected or optional!=expected_optional:raise ValueError('unexpected payload or field changes')
 if set(core)-set(base)!={JUNCTION} or set(base)-set(core):raise ValueError('baseline roster payloads missing')
 allowed=set(PATHS.values())|{LOC}
 changed={k for k in base if core[k]!=base[k]}
 if changed!=allowed:raise ValueError('unexpected baseline change footprint')
 for path,raw in base.items():
  if path not in allowed and core[path]!=raw:raise ValueError('unrelated payload changed')
 for name in ['units','unit_stats_land','projectiles']:
  _,rows=db_read(core[PATHS[name]],specs[name]);keys=[r['key'] for r in rows]
  if len(set(keys))!=len(keys):raise ValueError('duplicate DB key')
 _,stats=db_read(core[PATHS['unit_stats_land']],specs['unit_stats_land']);stats=stats[0]
 if stats['key']!=TYPE20 or stats['men']!=40 or stats['man_health']!=1 or stats['firing_mechanism']!='none':raise ValueError('native unit/controller foundation changed')
 if not 1<=stats['ammo']<=1000 or stats['ammo']!=210:raise ValueError('invalid finite native ammunition reserve')
 if stats['skirmish'] or not stats['guard_mode'] or not stats['all_ranks_fire']:raise ValueError('fire control regression')
 _,bullets=db_read(core[PATHS['projectiles']],specs['projectiles'])
 if len(bullets)!=2 or stats['default_missile_type']!=bullets[0]['key']:raise ValueError('normal projectile reference broken')
 for b in bullets:
  if b['projectile_number']!=1 or b['damage']<=0 or b['explosion_type'] or b['base_reload_time']!=1 or b['penetration']!='ap' or b['effective_range']!=450 or b['muzzle_velocity']!=850:raise ValueError('damage, single-projectile or supported reload contract failed')
 if bullets[1]['key']!=profile['suppression_projectile']['key'] or bullets[1]['shot_type']!='suppression_shot':raise ValueError('suppression projectile broken')
 _,ability=db_read(optional['db/unit_abilities_tables/'+OPTIONAL],specs['unit_abilities'])
 _,special=db_read(optional['db/unit_special_abilities_tables/'+OPTIONAL],specs['unit_special_abilities'])
 if ability[0]['requires_effect_enabling'] or special[0]['activated_projectile']!=bullets[1]['key'] or special[0]['active_time']!=30 or special[0]['recharge_time']!=120 or special[0]['can_autotrigger']:raise ValueError('native timed suppression contract failed')
 # Core modifies only private Type20 keys; optional shared definitions are explicit.
 if any(k.startswith(('db/unit_abilities_tables/','db/unit_special_abilities_tables/')) and k not in base for k in core):raise ValueError('core acquired shared ability overrides')
 from inspect_anim_events import read_anim
 clips=[]
 for path in [k for k in core if k.endswith('.anim')]:
  if core[path]!=base[path]:raise ValueError('confirmed animation changed')
  a=read_anim(core[path]);events=[e for b in a['event_blocks'] for e in b if e[0] in ['FIRE_TIME','FIRE_TIME_2']]
  if len(a['bones'])!=48 or [e[0] for e in events]!=['FIRE_TIME','FIRE_TIME_2']:raise ValueError('confirmed firing clip structure differs')
  clips.append({'path':path,'sha256':digest(core[path]),'markers':events})
 if len(clips)!=2:raise ValueError('confirmed firing clips missing')
 return dict(status='PASS_OFFLINE_DATA_AND_PRESERVATION',core_sha256=digest(core_raw),optional_sha256=digest(optional_raw),core_entries=len(core),optional_entries=len(optional),
  unchanged_baseline_payloads=len(base)-len(changed),changed_baseline_payloads=sorted(changed),added_core_payloads=[JUNCTION],
  known_good_firing_clips_preserved=clips,normal_projectile=bullets[0],suppression_projectile=bullets[1],
  native_reload_timer=1,native_ammo=210,finite_ammunition=True,magazine_model=False,five_shot=False,full_auto=False,
  core_new_shared_ability_overrides=False,optional_shared_ability_overrides=['suppression_fire.requires_effect_enabling','suppression_fire.activated_projectile'],
  in_game_verified=False,changes=changes)

def build(iteration):
 state=load(OUT/'iterations.json') if (OUT/'iterations.json').exists() else []
 if iteration!=len(state)+1 or not 1<=iteration<=3:raise ValueError('next meaningful iteration must be 1..3 in order')
 profile,base,r2,specs=evidence();core,optional,changes=planned(profile,base,r2,specs)
 core_raw=pack_bytes(core);optional_raw=pack_bytes(optional);validation=validate_bytes(core_raw,optional_raw,profile)
 session=OUT/('iteration-%02d'%iteration)
 if session.exists():raise ValueError('iteration directory already exists')
 save(OUT/'iterations.json',state+[dict(iteration=iteration,profile_sha256=digest(PROFILE.read_bytes()),core_sha256=digest(core_raw),status='BUILT')],'bounded iteration ledger')
 write_bytes(session/'steel_sakura_combined_test.pack',core_raw,'Type20 playable build core gameplay pack, iteration '+str(iteration))
 write_bytes(session/'steel_sakura_type20_suppression.pack',optional_raw,'Type20 playable build optional native suppression module, iteration '+str(iteration))
 save(session/'validation.json',validation,'exact gameplay deltas, finite ammunition and baseline preservation evidence')
 save(session/'schema-specs.json',specs,'observed RPFM table versions and scalar types')
 save(session/'profile.json',profile,'frozen own tuning profile')
 save(OUT/'latest.json',{'iteration':iteration,'session':str(session),'core_sha256':digest(core_raw),'optional_sha256':digest(optional_raw)},'current playable build pointer')
 print(json.dumps({k:v for k,v in validation.items() if k not in ['normal_projectile','suppression_projectile','changes']},indent=2))

def validate():
 pointer=load(OUT/'latest.json');session=Path(pointer['session']);r=validate_bytes((session/'steel_sakura_combined_test.pack').read_bytes(),(session/'steel_sakura_type20_suppression.pack').read_bytes(),load(session/'profile.json'))
 if r['core_sha256']!=pointer['core_sha256'] or r['optional_sha256']!=pointer['optional_sha256']:raise ValueError('build pointer differs')
 return r

if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('action',choices=['build','validate']);ap.add_argument('--iteration',type=int,default=1);a=ap.parse_args()
 if a.action=='build':build(a.iteration)
 else:print(json.dumps(validate(),indent=2))
