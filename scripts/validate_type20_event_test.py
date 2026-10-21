"""Check the bounded event experiment, including byte preservation of all prior data."""
import hashlib,json,re
from pathlib import Path
from validate_free_fire_experiment import entries
from inspect_anim_events import read_anim
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"build/type20-research"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def main():
 m=json.loads((OUT/"event-test-manifest.json").read_text())
 before=entries(Path(m["fallback"]));pack=ROOT/"build/steel_sakura_type20_event_test.pack";after=entries(pack)
 assert sha(Path(m["fallback"]))==m["fallback_sha256"]
 assert before.keys()<=after.keys()
 assert all(after[k]==v for k,v in before.items()),"An existing payload changed"
 name="steel_sakura_type20_event_test"
 expected={"db/"+t["table"]+"/"+name for t in m["tables"].values()}|{"text/db/"+name+".loc"}|{a["destination"] for a in m["assets"]}
 assert set(after)-set(before)==expected
 for a in m["assets"]:assert after[a["destination"]]==Path(a["source"]).read_bytes()
 evidence=json.loads((OUT/"event-test-rpfm.json").read_text(encoding="utf-8-sig"))
 data={}
 for n,t in m["tables"].items():
  actual=evidence[n]["DBRFileInfo"][0]["table"]
  assert actual["definition"]["version"]==t["version"]
  assert actual["table_data"]==t["rows"]
  data[n]=dict(zip(t["fields"],[next(iter(c.values())) for c in t["rows"][0]]))
  # Compare actual composite primary keys against installed and vanilla tables.
  key_fields=[i for i,f in enumerate(actual["definition"]["fields"]) if f["is_key"]]
  new_key=tuple(next(iter(t["rows"][0][i].values())) for i in key_fields)
  assert key_fields
  for p in [OUT/("installed_"+n+".json"),OUT/("base_"+n+".json"),ROOT/("build/diagnostic/base_"+n+".json"),ROOT/("build/inventory/table_"+n+".json"),ROOT/("build/inventory/existing_mod_"+n+".json")]:
   if p.exists():
    other=json.loads(p.read_text(encoding="utf-8-sig"))["DBRFileInfo"][0]["table"]
    assert new_key not in {tuple(next(iter(r[i].values())) for i in key_fields) for r in other["table_data"]},("Key collision",n,new_key)
 u=m["unit"];s=data["unit_stats_land"];p=data["projectiles"]
 assert s["key"]==u and data["units"]["key"]==u and s["men"]==40
 assert s["man_animations_table"]==u and s["equipment_theme"]==data["warscape_equipment_themes"]["theme"]
 assert data["warscape_equipment_themes"]["primary_weapon"]==data["warscape_equipment_items"]["equipment_key"]
 assert data["warscape_equipment_items"]["equipment_item"]=="spencer" # honest visual placeholder
 assert s["default_missile_type"]==p["key"]==u+"_bullet"
 assert data["uniforms"]["Unit"]==u and data["units_to_exclusive_faction_permissions"]==dict(key=u,faction="oda",allowed=True)
 assert data["units_to_groupings_military_permissions"]==dict(unit=u,military_group="japan")
 base=json.loads((OUT/"installed_unit_stats_land.json").read_text(encoding="utf-8-sig"))["DBRFileInfo"][0]["table"]
 fields=[f["name"] for f in base["definition"]["fields"]]
 old=next(dict(zip(fields,[next(iter(c.values())) for c in r])) for r in base["table_data"] if next(iter(r[0].values()))=="SteelSakura_Automatic_Rifle_Squad")
 diff={k for k in s if s[k]!=old[k]}
 assert diff=={"key","equipment_theme","man_animations_table","default_missile_type"}
 basep=json.loads((OUT/"installed_projectiles.json").read_text(encoding="utf-8-sig"))["DBRFileInfo"][0]["table"]
 fields=[f["name"] for f in basep["definition"]["fields"]]
 oldp=next(dict(zip(fields,[next(iter(c.values())) for c in r])) for r in basep["table_data"] if next(iter(r[0].values()))=="steel_sakura_diag_rifle")
 assert {k for k in p if p[k]!=oldp[k]}=={"key"}
 registry=after["animations/animation_tables/animation_tables.txt"]
 original=(OUT/"vanilla/animations/animation_tables/animation_tables.txt").read_bytes()
 assert registry.startswith(original)
 assert registry.decode("utf-8-sig").count("animation_table "+u)==1
 custom=registry[len(original):].decode()
 assert custom.index("fragment steel_sakura_type20_event_fragment") < custom.index("mount_table")
 fragment=after["animations/battleconfiguration/steel_sakura_type20_event_fragment.txt"].decode()
 for path in re.findall(r'filename = "([^"]+)"',fragment):assert path in after
 for mode,source in [("stand","men/musket/musket_poise/mus_fire.anim"),("kneel","men/musket/musket_kneel/mus_kneel_fire.anim")]:
  raw=after["animations/steel_sakura/type20_event_test/"+mode+".anim"];a=read_anim(raw)
  original=(OUT/"vanilla/animations/shogun_animation/battle"/source).read_bytes();b=read_anim(original)
  assert raw[:a["event_offset"]]==original[:b["event_offset"]]
  ev=a["event_blocks"][0];times={e[0]:float(e[1]) for e in ev if e[0].startswith("FIRE_TIME")}
  assert set(times)=={"FIRE_TIME","FIRE_TIME_2"} and abs(times["FIRE_TIME_2"]-times["FIRE_TIME"]-0.3)<1e-6
  assert 0<=times["FIRE_TIME"]<times["FIRE_TIME_2"]<a["duration"]
  assert a["bones"]==b["bones"]
 report=dict(status="VERIFIED_OFFLINE_ONLY",runtime_status="PENDING_USER_TEST",automatic_fire="NOT_CONFIRMED",unit=u,title=m["title"],test=str(pack),test_sha256=sha(pack),fallback=m["fallback"],fallback_sha256=m["fallback_sha256"],manifest_sha256=sha(OUT/"event-test-manifest.json"),prior_payloads_preserved=len(before),new_payloads=len(expected),db_roundtrips=len(data),unchanged="All existing rifle, artillery, grenade, ability and recruitment payloads; rifle reload/damage/range/count",hypothesis="FIRE_TIME_2 might cause a delayed second rifle projectile; pistol-only dispatch remains possible")
 (OUT/"event-test-validation.json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
