"""Prepare a bounded two-event infantry experiment; never edits the fallback.
Run extract_type20_research.ps1 first. Generated CA data stays under ignored build/.
"""
import copy,hashlib,json,re,shutil
from pathlib import Path
from inspect_anim_events import read_anim,event_bytes
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/type20-research"
UNIT="steel_sakura_type20_automatic_fire_test"
FALLBACK="SteelSakura_Automatic_Rifle_Squad"
EXPECTED="0A5CC547E5515CB813FB5341335E2A4D24E3596C7C9D7D3F32F39362FBB122F8"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def read(name,base=False):
 p=OUT/(("base_" if base else "installed_")+name+".json")
 return json.loads(p.read_text(encoding="utf-8-sig"))["DBRFileInfo"][0]["table"]
def obj(t,row):return dict(zip([f["name"] for f in t["definition"]["fields"]],[next(iter(x.values())) for x in row]))
def clone(t,predicate,changes):
 found=[r for r in t["table_data"] if predicate(obj(t,r))]
 if len(found)!=1:raise ValueError("Expected exactly one source row")
 r=copy.deepcopy(found[0]);fields=[f["name"] for f in t["definition"]["fields"]]
 for field,value in changes.items():
  i=fields.index(field);typ=next(iter(r[i]));r[i]={typ:value}
 return r
def main():
 installed=Path(r"D:\Games\Total War - SHOGUN 2\data\steel_sakura_combined_test.pack")
 known={EXPECTED}
 previous=OUT/"event-test-validation.json"
 if previous.exists():known.add(json.loads(previous.read_text())["test_sha256"])
 if sha(installed) not in known:raise ValueError("Installed baseline changed; inspect before preparing")
 preserved=OUT/"current-fallback.pack"
 if preserved.exists():
  if sha(preserved)!=EXPECTED:raise ValueError("Preserved fallback changed")
 else:shutil.copy2(installed,preserved)
 tables={}
 def add(name,predicate,changes,base=False):
  t=read(name,base);row=clone(t,predicate,changes)
  tables[name]=dict(table=name+"_tables",version=t["definition"]["version"],fields=[f["name"] for f in t["definition"]["fields"]],rows=[row])
 # Pick a free unit index from actual vanilla, installed, and Otomo rows.
 used=set()
 for p in [ROOT/"build/diagnostic/base_units.json",ROOT/"build/inventory/existing_mod_units.json",OUT/"installed_units.json"]:
  t=json.loads(p.read_text(encoding="utf-8-sig"))["DBRFileInfo"][0]["table"]
  used.update(obj(t,r)["unique_index"] for r in t["table_data"])
 index=max(used)+1
 title="Steel & Sakura \u2014 Type 20 Automatic Fire Test"
 add("units",lambda r:r["key"]==FALLBACK,dict(key=UNIT,on_screen_name=title,unit_description_text=UNIT,unique_index=index,icon_name=UNIT,info_pic=UNIT))
 add("unit_stats_land",lambda r:r["key"]==FALLBACK,dict(key=UNIT,man_animations_table=UNIT,equipment_theme=UNIT,default_missile_type=UNIT+"_bullet"))
 add("projectiles",lambda r:r["key"]=="steel_sakura_diag_rifle",dict(key=UNIT+"_bullet"))
 add("uniforms",lambda r:r["Unit"]==FALLBACK,dict(Unit=UNIT,Uniform_Name="Default_"+UNIT))
 add("units_to_groupings_military_permissions",lambda r:r["unit"]==FALLBACK,dict(unit=UNIT))
 add("units_to_exclusive_faction_permissions",lambda r:r["key"]==FALLBACK,dict(key=UNIT))
 add("warscape_equipment_themes",lambda r:r["theme"]=="boshin_spencer_bp_1",dict(theme=UNIT,primary_weapon=UNIT+"_weapon"),True)
 add("warscape_equipment_items",lambda r:r["equipment_key"]=="boshin_spencer",dict(equipment_key=UNIT+"_weapon"),True)
 assets=[]
 def asset(path,raw):
  p=OUT/"generated"/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
  assets.append(dict(source=str(p.resolve()),destination=path))
 timelines=[]
 for mode,observed in [("stand","men/musket/musket_poise/mus_fire.anim"),("kneel","men/musket/musket_kneel/mus_kneel_fire.anim")]:
  p=OUT/"vanilla/animations/shogun_animation/battle"/observed
  raw=p.read_bytes();a=read_anim(raw);blocks=copy.deepcopy(a["event_blocks"]);block=blocks[0]
  assert not any(e[0]=="FIRE_TIME_2" for e in block)
  pos=next(e for e in block if e[0]=="FIRE_POSITION")
  first=float(next(e[1] for e in block if e[0]=="FIRE_TIME"))
  block.append(["FIRE_TIME_2",f"{first+0.30:.2f}"])
  block.append(["FIRE_POSITION_2",*pos[1:]])
  edited=raw[:a["event_offset"]]+event_bytes(blocks)
  check=read_anim(edited)
  assert edited[:a["event_offset"]]==raw[:a["event_offset"]]
  asset("animations/steel_sakura/type20_event_test/"+mode+".anim",edited)
  timelines.append(dict(mode=mode,first=first,second=first+0.30,duration=a["duration"],frames_unchanged=True,bones=len(a["bones"])))
 fragment='version 1\n\n'
 for mode,state in [("stand","FIRE"),("kneel","KNEEL_FIRE")]:
  fragment+=f'{state}\tfilename = "animations/steel_sakura/type20_event_test/{mode}.anim"\tblend_in_time = 0.25\n'
 asset("animations/battleconfiguration/steel_sakura_type20_event_fragment.txt",fragment.encode())
 original=(OUT/"vanilla/animations/animation_tables/animation_tables.txt").read_bytes()
 text=original.decode("utf-8-sig")
 match=re.search(r"animation_table boshin_man_rifle_trained\s*\{[^}]*\}",text)
 if not match:raise ValueError("Actual rifle animation table not found")
 block=match.group().replace("animation_table boshin_man_rifle_trained","animation_table "+UNIT,1)
 block=block.replace('\tmount_table','\tfragment steel_sakura_type20_event_fragment default_equipment_display = primary_weapon, secondary_weapon, ambient\n\tmount_table',1)
 # Exact existing registry bytes preserved, one new table appended. This is a
 # shared registry path override, not an undocumented loader-directory guess.
 asset("animations/animation_tables/animation_tables.txt",original+b"\n\n"+block.encode()+b"\n")
 for folder in ["icons","icons_square","info","recruitment_large","recruitment_small"]:
  p=ROOT/"assets/infantry"/folder/"steel_sakura_automatic_rifle_squad.tga"
  asset(f"ui/units/{folder}/{UNIT}.tga",p.read_bytes())
 loc=[
 dict(key="units_on_screen_name_"+UNIT,text=title,tooltip=False),
 dict(key="unit_description_texts_description_text_"+UNIT,text="EXPERIMENT: two timed shot markers, 0.30 s apart. Spencer/Tosa visual placeholder. Automatic fire unconfirmed.",tooltip=False),
 dict(key="unit_description_texts_long_description_text_"+UNIT,text="Independent 40-man control: unchanged reload, range, damage and projectile count. Tests FIRE_TIME_2 on a human rifle animation. No custom Howa model or sustained-fire controller yet.",tooltip=False)]
 manifest=dict(unit=UNIT,title=title,status="UNTESTED_EVENT_HYPOTHESIS",fallback=str(preserved.resolve()),fallback_sha256=EXPECTED,tables=tables,assets=assets,localisation=loc,timelines=timelines,scope="No fallback, artillery, grenade or recruitment modifications",unique_index=index)
 (OUT/"event-test-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
 print("Prepared separate unit, independent weapon item/theme/projectile, two timed markers; reload unchanged.")
if __name__=="__main__":main()
