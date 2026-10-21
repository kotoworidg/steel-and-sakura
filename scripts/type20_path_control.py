"""Preserve the failed event experiment; build/verify/install a positive path control.
This control deliberately tests ONE delayed shot, never automatic fire.
"""
import argparse,copy,datetime,hashlib,json,os,re,shutil,struct,subprocess
from pathlib import Path
from inspect_anim_events import read_anim,event_bytes
from validate_free_fire_experiment import entries
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"build/type20-path-control"
UNIT="steel_sakura_type20_automatic_fire_test"
TITLE="TYPE20 ANIMATION CHECK - 4s HOLD / ONE SHOT"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def manifest():return json.loads((OUT/"manifest.json").read_text())
def prepare():
 old=json.loads((ROOT/"build/type20-research/event-test-validation.json").read_text())
 source=Path(old["test"]);assert sha(source)==old["test_sha256"]
 OUT.mkdir(parents=True,exist_ok=True)
 preserved=OUT/"failed-two-event.pack"
 if preserved.exists():assert sha(preserved)==old["test_sha256"]
 else:shutil.copy2(source,preserved)
 for name in ["event-test-validation.json","event-test-rpfm.json","event-test-manifest.json"]:
  dest=OUT/("failed-"+name)
  if not dest.exists():shutil.copy2(ROOT/"build/type20-research"/name,dest)
 packed=entries(preserved);assets=[];timelines=[]
 def asset(path,data):
  p=OUT/"generated"/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
  assets.append(dict(source=str(p.resolve()),destination=path))
 for mode,path in [("stand","men/musket/musket_poise/mus_fire.anim"),("kneel","men/musket/musket_kneel/mus_kneel_fire.anim")]:
  original=ROOT/"build/type20-research/vanilla/animations/shogun_animation/battle"/path
  raw=original.read_bytes();a=read_anim(raw);fps=a["fps"];hold=round(4*fps);stride=len(a["bones"])*28
  assert fps==20 and hold==80
  header=bytearray(raw[:a["frame_offset"]])
  struct.pack_into("<f",header,8,a["duration"]+4)
  struct.pack_into("<I",header,a["frame_offset"]-4,a["frame_count"]+hold)
  frame0=raw[a["frame_offset"]:a["frame_offset"]+stride]
  blocks=copy.deepcopy(a["event_blocks"])
  for block in blocks:
   for e in block:
    if e[0]=="FIRE_TIME":e[1]=f"{float(e[1])+4:.2f}"
  assert sum(e[0]=="FIRE_TIME" for b in blocks for e in b)==1
  edited=bytes(header)+frame0*hold+raw[a["frame_offset"]:a["event_offset"]]+event_bytes(blocks)
  read_anim(edited)
  dest="animations/steel_sakura/type20_event_test/"+mode+".anim";asset(dest,edited)
  timelines.append(dict(mode=mode,source=str(original.resolve()),delay_seconds=4,hold_frames=hold,first_shot=float(next(e[1] for e in blocks[0] if e[0]=="FIRE_TIME"))))
 frag=ROOT/"build/automatic-research/animations/battleconfiguration/shogun_man_musket_combat_fragment.txt"
 text=frag.read_text(encoding="utf-8-sig")
 for state,mode in [("FIRE","stand"),("KNEEL_FIRE","kneel")]:
  text,count=re.subn(r'(?m)^('+state+r'\s+filename\s*=\s*")[^"]+(")',lambda m:m[1]+"animations/steel_sakura/type20_event_test/"+mode+".anim"+m[2],text)
  assert count==1
 asset("animations/battleconfiguration/steel_sakura_type20_event_fragment.txt",text.encode())
 registry=packed["animations/animation_tables/animation_tables.txt"]
 original=(ROOT/"build/type20-research/vanilla/animations/animation_tables/animation_tables.txt").read_bytes()
 assert registry.startswith(original)
 private=registry[len(original):].decode()
 private,count=re.subn(r'(?m)^\tfragment steel_sakura_type20_event_fragment[^\n]*\n',"",private);assert count==1
 assert private.count("shogun_man_musket_combat_fragment")==1
 private=private.replace("shogun_man_musket_combat_fragment","steel_sakura_type20_event_fragment")
 asset("animations/animation_tables/animation_tables.txt",original+private.encode())
 m=dict(title=TITLE,unit=UNIT,status="POSITIVE_CONTROL_UNTESTED",failed_event=str(preserved.resolve()),failed_event_sha256=sha(preserved),fallback=old["fallback"],fallback_sha256=old["fallback_sha256"],assets=assets,timelines=timelines,original_fragment=str(frag.resolve()),purpose="Distinguish custom firing-path selection and event timing from ignored numbered markers; one shot only")
 (OUT/"manifest.json").write_text(json.dumps(m,indent=2)+"\n")
 print("Prepared 4-second animation/event path control; preserved failed experiment.")
def validate():
 m=manifest();source=Path(m["failed_event"]);pack=ROOT/"build/steel_sakura_type20_path_control.pack"
 before,after=entries(source),entries(pack);assert before.keys()==after.keys()
 changes={k for k in before if before[k]!=after[k]}
 expected={a["destination"] for a in m["assets"]}|{"db/units_tables/steel_sakura_type20_event_test","text/db/steel_sakura_type20_event_test.loc"}
 assert changes==expected
 base=entries(Path(m["fallback"]));assert all(after[k]==v for k,v in base.items())
 for a in m["assets"]:assert after[a["destination"]]==Path(a["source"]).read_bytes()
 for t in m["timelines"]:
  mode=t["mode"];raw=after["animations/steel_sakura/type20_event_test/"+mode+".anim"];a=read_anim(raw)
  vanilla=Path(t["source"]).read_bytes();b=read_anim(vanilla);stride=len(b["bones"])*28;hold=t["hold_frames"]
  assert a["bones"]==b["bones"] and a["fps"]==b["fps"] and a["frame_count"]==b["frame_count"]+hold
  assert abs(a["duration"]-b["duration"]-4)<1e-5
  assert raw[a["frame_offset"]:a["frame_offset"]+hold*stride]==vanilla[b["frame_offset"]:b["frame_offset"]+stride]*hold
  assert raw[a["frame_offset"]+hold*stride:a["event_offset"]]==vanilla[b["frame_offset"]:b["event_offset"]]
  blocks=copy.deepcopy(b["event_blocks"])
  for block in blocks:
   for e in block:
    if e[0]=="FIRE_TIME":e[1]=f"{float(e[1])+4:.2f}"
  assert a["event_blocks"]==blocks
  assert not any(e[0]=="FIRE_TIME_2" for block in a["event_blocks"] for e in block)
 registry=after["animations/animation_tables/animation_tables.txt"]
 vanilla=(ROOT/"build/type20-research/vanilla/animations/animation_tables/animation_tables.txt").read_bytes()
 assert registry.startswith(vanilla)
 private=registry[len(vanilla):].decode()
 assert "shogun_man_musket_combat_fragment" not in private and len(re.findall(r"fragment\s+steel_sakura_type20_event_fragment\b",private))==1
 frag=after["animations/battleconfiguration/steel_sakura_type20_event_fragment.txt"].decode()
 states=re.findall(r'(?m)^(FIRE|KNEEL_FIRE)\s+filename',frag);assert sorted(states)==["FIRE","KNEEL_FIRE"]
 for path in re.findall(r'filename\s*=\s*"([^"]+)"',frag):
  if "steel_sakura" in path:assert path in after
 e=json.loads((OUT/"rpfm-evidence.json").read_text(encoding="utf-8-sig"))
 old=e["before_units"]["DBRFileInfo"][0]["table"];new=e["after_units"]["DBRFileInfo"][0]["table"]
 fields=[f["name"] for f in old["definition"]["fields"]];diff=[]
 for x,y in zip(old["table_data"],new["table_data"]):
  for f,a,b in zip(fields,x,y):
   if a!=b:diff.append((f,a,b))
 assert diff==[("on_screen_name",{"StringU16":"Steel & Sakura \u2014 Type 20 Automatic Fire Test"},{"StringU16":TITLE})]
 assert len(old["table_data"])==len(new["table_data"])==1
 loc=e["after_loc"]["LocRFileInfo"][0]["table"]["table_data"]
 assert any(row[0]["StringU16"]=="units_on_screen_name_"+UNIT and row[1]["StringU16"]==TITLE for row in loc)
 assert len(loc)==3 and all(UNIT in row[0]["StringU16"] for row in loc)
 r=dict(status="VERIFIED_OFFLINE_ONLY",runtime_status="PENDING_USER",automatic_fire="NOT_IMPLEMENTED_CONTROL_ONLY",pack=str(pack.resolve()),pack_sha256=sha(pack),manifest_sha256=sha(OUT/"manifest.json"),failed_event=m["failed_event"],failed_event_sha256=m["failed_event_sha256"],fallback=m["fallback"],fallback_sha256=m["fallback_sha256"],changed_payloads=sorted(changes),preserved_base_payloads=len(base),title=TITLE)
 (OUT/"validation.json").write_text(json.dumps(r,indent=2)+"\n");print(json.dumps(r,indent=2))
def install(mode):
 r=json.loads((OUT/"validation.json").read_text());m=manifest()
 source=Path(r["pack"] if mode=="control" else r["fallback"]);expected=r["pack_sha256"] if mode=="control" else r["fallback_sha256"]
 assert sha(source)==expected and sha(OUT/"manifest.json")==r["manifest_sha256"]
 game=Path(json.loads((ROOT/"src/install_config.json").read_text())["game_root"]).resolve();target=game/"data/steel_sakura_combined_test.pack"
 allowed={r["pack_sha256"],r["failed_event_sha256"],r["fallback_sha256"]}
 prior=OUT/"installation.json"
 if prior.exists():
  p=json.loads(prior.read_text())
  if p["fallback_sha256"]==r["fallback_sha256"]:allowed.add(p["installed_sha256"])
 if sha(target) not in allowed:raise ValueError("Unknown installed pack; inspect first")
 extra=[p for folder in [game/"data",game/"data/MyMods"] for p in folder.glob("steel_sakura*.pack") if p!=target]
 if extra:raise ValueError("Unexpected other Steel Sakura pack")
 running=subprocess.run(["powershell","-NoProfile","-Command","@(Get-Process shogun* -ErrorAction SilentlyContinue).Count"],capture_output=True,text=True,check=True)
 if running.stdout.strip()!="0":raise ValueError("Close Shogun 2 before installation")
 backup=ROOT/"backups"/("type20-path-control-"+datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f"));backup.mkdir(parents=True)
 shutil.copy2(target,backup/target.name)
 configs=[game/"mod_list.txt",Path(os.environ["APPDATA"])/"The Creative Assembly/Shogun2/scripts/user.script.txt"]
 original={p:p.read_bytes() for p in configs}
 for p,b in original.items():(backup/p.name).write_bytes(b)
 try:
  shutil.copy2(source,target)
  assert sha(target)==expected and all(p.read_bytes()==b for p,b in original.items())
 except Exception:
  shutil.copy2(backup/target.name,target);raise
 result=dict(mode=mode,installed=str(target),installed_sha256=expected,fallback_sha256=r["fallback_sha256"],backup=str(backup),configs_unchanged=True,runtime_status="PENDING_USER")
 (OUT/"installation.json").write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result,indent=2))
if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("action",choices=["prepare","validate","install","rollback"]);a=ap.parse_args()
 if a.action=="prepare":prepare()
 elif a.action=="validate":validate()
 else:install("control" if a.action=="install" else "fallback")
