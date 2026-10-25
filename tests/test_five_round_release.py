"""Recovery exercises the real installer transaction; no game process is used."""
import contextlib,io,json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import install_type20_supported as installer
import restore_confirmed_type20 as recovery
import five_round_build as build

class ConfirmedRecoveryTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.game=self.root/'game';(self.game/'data').mkdir(parents=True);self.package=self.root/'package';(self.package/'fallback').mkdir(parents=True)
  self.env=patch.dict(os.environ,{'APPDATA':str(self.root/'profile')});self.env.start();self.verify=patch.object(installer,'verify_game',side_effect=lambda p:p.resolve());self.verify.start();self.closed=patch.object(installer,'ensure_closed');self.closed.start();self.silent=contextlib.redirect_stdout(io.StringIO());self.silent.__enter__()
  self.baseline=(ROOT/'build/type20-auto-cycle/confirmed-burst.pack').read_bytes();self.current=(ROOT/'build/type20-playable/iteration-02/steel_sakura_combined_test.pack').read_bytes();self.core=self.game/'data'/installer.CORE;self.core.write_bytes(self.current)
  (self.package/'fallback/confirmed_two_shot.pack').write_bytes(self.baseline)
  self.user=installer.user_script();self.user.parent.mkdir(parents=True);self.user.write_bytes(b'mod "mods_modern_units_otomo.pack";\r\nmod "steel_sakura_combined_test.pack";\r\n');(self.game/'mod_list.txt').write_bytes(self.user.read_bytes())
  for p in [self.game/'shogun2.exe',self.game/'empire.retail.dll',self.game/'data/mods_modern_units_otomo.pack']:p.write_bytes(b'untouched fixture')
  (self.package/'release.json').write_text(json.dumps({'pack_sha256':{installer.CORE:installer.sha(self.current),installer.SUPP:'optional'},'previous_core_hashes':[]}),encoding='utf-8')
  self.other=installer.preservation(self.game)
 def tearDown(self):
  self.silent.__exit__(None,None,None);self.closed.stop();self.verify.stop();self.env.stop();self.tmp.cleanup()
 def test_restore_confirmed_then_undo_restoration(self):
  r=recovery.restore(self.package,self.game);self.assertEqual(self.core.read_bytes(),self.baseline);self.assertEqual(installer.preservation(self.game),self.other)
  installer.rollback(Path(r['receipt']));self.assertEqual(self.core.read_bytes(),self.current);self.assertEqual(installer.preservation(self.game),self.other)
 def test_corrupt_archive_and_unknown_later_pack_refused(self):
  fallback=self.package/'fallback/confirmed_two_shot.pack';fallback.write_bytes(b'bad')
  with self.assertRaises(ValueError):recovery.restore(self.package,self.game)
  self.assertEqual(self.core.read_bytes(),self.current)
  fallback.write_bytes(self.baseline);self.core.write_bytes(b'later user changes')
  with self.assertRaises(ValueError):recovery.restore(self.package,self.game)
  self.assertEqual(self.core.read_bytes(),b'later user changes')
 def test_dry_run_creates_no_backup_and_changes_nothing(self):
  recovery.restore(self.package,self.game,True);self.assertFalse((self.package/'backups').exists());self.assertEqual(self.core.read_bytes(),self.current)

class RuntimeBuildSafetyTests(unittest.TestCase):
 def test_pack_generation_is_byte_reproducible(self):
  first,_=build.candidate();second,_=build.candidate();self.assertEqual(first,second);self.assertEqual(build.digest(first),build.load(build.OUT/'latest.json')['pack_sha256'])
 def test_native_profile_refuses_unsupported_dll(self):
  with tempfile.TemporaryDirectory() as d:
   game=Path(d);(game/'shogun2.exe').write_bytes((build.OUT/'binary-baseline/shogun2.exe').read_bytes());(game/'empire.retail.dll').write_bytes(b'unsupported binary')
   with patch.object(build,'GAME',game),self.assertRaisesRegex(ValueError,'unsupported engine binary: empire.retail.dll'):build.profile('not-a-supported-pack')
   (game/'shogun2.exe').write_bytes(b'unsupported executable')
   with patch.object(build,'GAME',game),self.assertRaisesRegex(ValueError,'unsupported engine binary: shogun2.exe'):build.profile('not-a-supported-pack')
 def test_runtime_source_has_no_completion_override_or_injection(self):
  source=build.host_source(build.load(build.OUT/'latest.json')['pack_sha256']);self.assertNotIn('c[176]&=',source);self.assertNotIn('CreateRemoteThread',source);self.assertNotIn('VirtualAllocEx',source)

if __name__=='__main__':unittest.main()
