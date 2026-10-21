"""Safely switch the one active combined pack; all prior payloads are preserved.
Usage: python scripts/select_type20_event_test.py test|fallback [--dry-run]
"""
import argparse,datetime,hashlib,json,os,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"build/type20-research"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def main():
 ap=argparse.ArgumentParser();ap.add_argument("mode",choices=["test","fallback"]);ap.add_argument("--dry-run",action="store_true");a=ap.parse_args()
 r=json.loads((OUT/"event-test-validation.json").read_text());source=Path(r[a.mode]);expected=r[a.mode+"_sha256"]
 if sha(source)!=expected:raise ValueError("Source changed after validation")
 if sha(OUT/"event-test-manifest.json")!=r["manifest_sha256"]:raise ValueError("Manifest changed after validation")
 config=json.loads((ROOT/"src/install_config.json").read_text());game=Path(config["game_root"]).resolve();data=game/"data"
 target=data/"steel_sakura_combined_test.pack"
 known={r["fallback_sha256"],r["test_sha256"]}
 previous=OUT/"installation-report.json"
 if previous.exists():
  old_report=json.loads(previous.read_text())
  if old_report.get("fallback_sha256")==r["fallback_sha256"] and old_report.get("installed")==str(target):known.add(old_report["sha256"])
 if sha(target) not in known:raise ValueError("Unknown installed version; inspect first")
 extras=[p for folder in [data,data/"MyMods"] for p in folder.glob("steel_sakura*.pack") if p!=target]
 if extras:raise ValueError("Other Steel Sakura packs present: "+str(extras))
 if a.dry_run:print("Verified plan:",source,"->",target,expected);return
 running=subprocess.run(["powershell","-NoProfile","-Command","@(Get-Process shogun* -ErrorAction SilentlyContinue).Count"],capture_output=True,text=True,check=True)
 if running.stdout.strip()!="0":raise ValueError("Close Shogun 2 before changing its mod")
 if sha(target)==expected:print("Already installed and hash verified:",target,expected);return
 backup=ROOT/"backups"/("type20-events-"+datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f"));backup.mkdir(parents=True)
 configs=[game/"mod_list.txt",Path(os.environ["APPDATA"])/"The Creative Assembly/Shogun2/scripts/user.script.txt"]
 originals={p:p.read_bytes() for p in configs}
 shutil.copy2(target,backup/target.name)
 for p,raw in originals.items():(backup/p.name).write_bytes(raw)
 old=sha(target)
 try:
  shutil.copy2(source,target)
  if sha(target)!=expected:raise ValueError("Installed hash mismatch")
  if any(p.read_bytes()!=raw for p,raw in originals.items()):raise ValueError("Loading configuration unexpectedly changed")
 except Exception:
  shutil.copy2(backup/target.name,target)
  raise
 report=dict(mode=a.mode,installed=str(target),sha256=expected,previous_sha256=old,fallback_sha256=r["fallback_sha256"],backup=str(backup),configs_unchanged=True,only_active_steel_sakura_pack=True,runtime_status="PENDING_USER_TEST")
 (OUT/"installation-report.json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
