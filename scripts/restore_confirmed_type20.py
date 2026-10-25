"""One-command restoration of the preserved, user-confirmed two-shot pack.
The installer supplies hash checks, immutable backups, allowlisted writes and undo.
"""
import argparse,json
from pathlib import Path
try:import install_type20_supported as installer
except ImportError:import install_type20 as installer
CONFIRMED='0B497A435F4E28C2C068D7C90B60BA9D0C0FFA353BABD46242EF2FED2222D270'

def restore(package,game,dry=False):
 package=package.resolve();game=installer.verify_game(game.resolve());installer.ensure_closed()
 baseline=package/'fallback/confirmed_two_shot.pack';raw=baseline.read_bytes()
 if installer.sha(raw)!=CONFIRMED:raise ValueError('Confirmed fallback archive differs; no files changed')
 release=json.loads((package/'release.json').read_text(encoding='utf-8'))
 core=(game/'data'/installer.CORE).resolve();supp=(game/'data'/installer.SUPP).resolve()
 known={None,CONFIRMED,release['pack_sha256'][installer.CORE]}|set(release.get('previous_core_hashes',[]))
 if installer.hashpath(core) not in known:raise ValueError('Installed pack has later or unknown edits; refusing restoration')
 if installer.hashpath(supp) not in {None,release['pack_sha256'][installer.SUPP]}|set(release.get('previous_suppression_hashes',[])):raise ValueError('Optional module has unknown edits')
 configs=[(game/'mod_list.txt').resolve(),installer.user_script()]
 changes={core:raw,supp:None};changes.update({p:installer.edit_list(p.read_bytes() if p.exists() else b'',False) for p in configs})
 result={'status':'CONFIRMED_BASELINE_DRY_RUN' if dry else 'CONFIRMED_BASELINE_RESTORED','restored_sha256':CONFIRMED}
 if not dry:
  before=installer.preservation(game);receipt=installer.transaction(game,changes,package/'backups','Restore preserved confirmed two-shot baseline')
  if installer.hashpath(core)!=CONFIRMED or installer.preservation(game)!=before:raise RuntimeError('Restoration verification failed; preserve receipt '+str(receipt))
  result.update(receipt=str(receipt),unrelated_mods_and_binaries_unchanged=True)
 print(json.dumps(result,indent=2));return result

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--game-root',type=Path,default=Path('D:/Games/Total War - SHOGUN 2'));p.add_argument('--dry-run',action='store_true');a=p.parse_args();restore(Path(__file__).resolve().parent,a.game_root,a.dry_run)
