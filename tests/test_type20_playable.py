"""Gameplay-pack corruption checks and real install/undo fixtures; no game runtime."""
import contextlib,io,json,os,struct,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import type20_playable as playable
import install_type20_supported as installer
from type20_pack_codec import pack_entries,pack_bytes,db_read,db_bytes

class PlayablePackTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.profile,cls.base,cls.r2,cls.specs=playable.evidence();cls.core,cls.optional,_=playable.planned(cls.profile,cls.base,cls.r2,cls.specs)
 def check(self,core=None,optional=None):return playable.validate_bytes(pack_bytes(core or self.core),pack_bytes(optional or self.optional))
 def test_supported_pack_and_exact_baseline_preservation(self):
  r=self.check();self.assertEqual(r['unchanged_baseline_payloads'],35);self.assertEqual(r['core_entries'],40);self.assertFalse(r['in_game_verified']);self.assertFalse(r['five_shot']);self.assertFalse(r['full_auto']);self.assertFalse(r['magazine_model'])
  for p,b in self.base.items():
   if p not in set(playable.PATHS.values())|{playable.LOC}:self.assertEqual(self.core[p],b,p)
 def test_every_new_db_payload_uses_observed_schema_and_roundtrips(self):
  for pack in [self.core,self.optional]:
   for p,b in pack.items():
    if p not in self.base or p in playable.PATHS.values():
     if p.startswith('db/'):
      spec=self.specs[p.split('/')[1].removesuffix('_tables')];prefix,rows=db_read(b,spec);self.assertEqual(db_bytes(prefix,rows,spec),b)
 def test_rejects_modified_firing_animation(self):
  core=dict(self.core);p=next(p for p in core if p.endswith('.anim'));core[p]=core[p][:-1]+bytes([core[p][-1]^1])
  with self.assertRaises(ValueError):self.check(core)
 def test_rejects_zero_damage_multi_projectile_and_broken_reference(self):
  for field,value in [('damage',0.0),('projectile_number',5),('key','missing')]:
   core=dict(self.core);p=playable.PATHS['projectiles'];spec=self.specs['projectiles'];prefix,rows=db_read(core[p],spec);rows[0][field]=value;core[p]=db_bytes(prefix,rows,spec)
   with self.subTest(field=field),self.assertRaises(ValueError):self.check(core)
 def test_rejects_infinite_ammo_or_skirmish_regression(self):
  for field,value in [('ammo',0),('ammo',-1),('skirmish',True),('all_ranks_fire',False)]:
   core=dict(self.core);p=playable.PATHS['unit_stats_land'];spec=self.specs['unit_stats_land'];prefix,rows=db_read(core[p],spec);rows[0][field]=value;core[p]=db_bytes(prefix,rows,spec)
   with self.subTest(field=field,value=value),self.assertRaises(ValueError):self.check(core)
 def test_rejects_changed_unrelated_artillery(self):
  core=dict(self.core);p='db/gun_types_tables/steel_sakura_combined';core[p]+=b'\0'
  with self.assertRaises(ValueError):self.check(core)
 def test_rejects_broken_optional_projectile_and_duration(self):
  for field,value in [('activated_projectile','missing'),('active_time',300.0)]:
   optional=dict(self.optional);p='db/unit_special_abilities_tables/'+playable.OPTIONAL;spec=self.specs['unit_special_abilities'];prefix,rows=db_read(optional[p],spec);rows[0][field]=value;optional[p]=db_bytes(prefix,rows,spec)
   with self.subTest(field=field),self.assertRaises(ValueError):self.check(optional=optional)
 def test_pack_rejects_truncation_trailing_data_and_case_collision(self):
  raw=pack_bytes({'a':b'x'})
  for damaged in [raw[:-1],raw+b'x']:
   with self.assertRaises(ValueError):pack_entries(damaged)
  with self.assertRaises(ValueError):pack_bytes({'a':b'x','A':b'y'})

class InstallTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.game=self.root/'game';(self.game/'data/MyMods').mkdir(parents=True)
  self.package=self.root/'package';self.package.mkdir();self.env=patch.dict(os.environ,{'APPDATA':str(self.root/'profile')});self.env.start()
  self.fake_game=patch.object(installer,'verify_game',side_effect=lambda p:p.resolve());self.fake_game.start();self.closed=patch.object(installer,'ensure_closed');self.closed.start()
  self.silent=contextlib.redirect_stdout(io.StringIO());self.silent.__enter__()
  pointer=playable.load(playable.OUT/'latest.json');self.build=Path(pointer['session'])
  self.main=self.game/'data'/installer.CORE;self.main.write_bytes(playable.BASE.read_bytes());self.modlist=self.game/'mod_list.txt';self.modlist.write_bytes(b'mod "otomo_fots_expanded.pack";\r\nmod "steel_sakura_combined_test.pack";\r\n')
  self.user=installer.user_script();self.user.parent.mkdir(parents=True);self.user.write_bytes(b'\xff\xfe'+('mod "mods_modern_units_otomo.pack";\r\nmod "steel_sakura_combined_test.pack";\r\n').encode('utf-16-le'))
  for p in [self.game/'shogun2.exe',self.game/'empire.retail.dll',self.game/'data/mods_modern_units_otomo.pack',self.game/'data/MyMods/mods_modern_units_otomo.pack']:p.write_bytes(b'UNRELATED FIXTURE '+p.name.encode())
  for name in [installer.CORE,installer.SUPP]:(self.package/name).write_bytes((self.build/name).read_bytes())
  release=dict(format=1,version='fixture',pack_sha256={n:installer.hashpath(self.package/n) for n in [installer.CORE,installer.SUPP]},optional_shared_scope='explicit shared native ability override')
  (self.package/'release.json').write_text(json.dumps(release));self.original={p:p.read_bytes() for p in [self.main,self.modlist,self.user]};self.preserved=installer.preservation(self.game)
 def tearDown(self):
  self.silent.__exit__(None,None,None);self.closed.stop();self.fake_game.stop();self.env.stop();self.tmp.cleanup()
 def test_install_and_real_rollback_restore_original_bytes_and_otomo(self):
  result=installer.install(self.package,self.game,True);self.assertEqual(self.main.read_bytes(),(self.package/installer.CORE).read_bytes());self.assertIn(b'steel_sakura_type20_suppression.pack',self.modlist.read_bytes())
  self.assertTrue(self.user.read_bytes().startswith(b'\xff\xfe'));self.assertEqual(self.preserved,installer.preservation(self.game))
  installer.rollback(Path(result['receipt']));self.assertFalse((self.game/'data'/installer.SUPP).exists())
  for p,b in self.original.items():self.assertEqual(p.read_bytes(),b)
  self.assertEqual(self.preserved,installer.preservation(self.game))
 def test_dry_run_does_not_write_or_create_backup(self):
  installer.install(self.package,self.game,True,True);self.assertFalse((self.package/'backups').exists())
  for p,b in self.original.items():self.assertEqual(p.read_bytes(),b)
 def test_unknown_installed_pack_and_package_corruption_refused(self):
  self.main.write_bytes(b'later user build')
  with self.assertRaises(ValueError):installer.install(self.package,self.game)
  self.main.write_bytes(self.original[self.main]);(self.package/installer.CORE).write_bytes(b'corrupt')
  with self.assertRaises(ValueError):installer.install(self.package,self.game)
  self.assertFalse((self.package/'backups').exists())
 def test_rollback_refuses_later_configuration_edits(self):
  result=installer.install(self.package,self.game);later=self.user.read_bytes()+b'\0\0';self.user.write_bytes(later);before=self.main.read_bytes()
  with self.assertRaises(ValueError):installer.rollback(Path(result['receipt']))
  self.assertEqual(self.user.read_bytes(),later);self.assertEqual(self.main.read_bytes(),before)
 def test_rollback_rejects_tampered_original_backup(self):
  result=installer.install(self.package,self.game);receipt=Path(result['receipt']);r=json.loads(receipt.read_text());Path(r['records'][0]['backup_path']).write_bytes(b'tampered');before=self.main.read_bytes()
  with self.assertRaises(ValueError):installer.rollback(receipt)
  self.assertEqual(self.main.read_bytes(),before)
 def test_failure_restores_original_files_with_fresh_backups(self):
  replace=installer.os.replace;calls=[0]
  def fail_once(a,b):
   calls[0]+=1
   if calls[0]==1:raise OSError('simulated write failure')
   return replace(a,b)
  with patch.object(installer.os,'replace',side_effect=fail_once),self.assertRaises(RuntimeError):installer.install(self.package,self.game,True)
  for p,b in self.original.items():self.assertEqual(p.read_bytes(),b)
  self.assertFalse((self.game/'data'/installer.SUPP).exists());self.assertEqual(self.preserved,installer.preservation(self.game))
 def test_core_install_removes_previous_optional_module_and_can_undo(self):
  first=installer.install(self.package,self.game,True);optional=(self.game/'data'/installer.SUPP).read_bytes();configs={p:p.read_bytes() for p in [self.modlist,self.user]}
  second=installer.install(self.package,self.game,False);self.assertFalse((self.game/'data'/installer.SUPP).exists());self.assertNotIn(b'mod "steel_sakura_type20_suppression.pack";',self.modlist.read_bytes())
  installer.rollback(Path(second['receipt']));self.assertEqual((self.game/'data'/installer.SUPP).read_bytes(),optional)
  for p,b in configs.items():self.assertEqual(p.read_bytes(),b)
 def test_loading_encodings_and_unrelated_entries_preserved(self):
  for enc,bom in [('utf-8',b''),('utf-8',b'\xef\xbb\xbf'),('utf-16-le',b'\xff\xfe'),('utf-16-be',b'\xfe\xff'),('cp1252',b'')]:
   text='mod "otomo_fots_expanded.pack";\r\n# caf\u00e9\r\n';raw=bom+text.encode(enc);edited=installer.edit_list(raw,True)
   self.assertTrue(edited.startswith(raw));self.assertEqual(installer.edit_list(edited,True),edited)
   disabled=installer.edit_list(edited,False);self.assertTrue(disabled.startswith(raw))
 def test_rejects_unexpected_target_in_transaction_and_receipt(self):
  outside=self.root/'unrelated.txt';outside.write_text('preserve')
  with self.assertRaises(ValueError):installer.transaction(self.game,{outside:b'bad'},self.package/'backups','reject')
  self.assertEqual(outside.read_text(),'preserve')

if __name__=='__main__':unittest.main()
