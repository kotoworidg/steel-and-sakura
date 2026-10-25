"""Exercise the launcher acknowledgement and failure path without a game attach."""
import json,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import run_five_round as launcher

class LauncherStartupTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(dir=ROOT/'build/five_round');self.session=Path(self.temp.name)
 def tearDown(self):self.temp.cleanup()
 def log(self,rows):
  (self.session/'log-00001.json').write_text(json.dumps([{'name':n,'detail':d} for n,d in rows]),encoding='utf-8')
 def test_spawn_is_not_success_without_actual_attached_log(self):
  self.log([('start',{})]);proc=SimpleNamespace(pid=123,poll=Mock(side_effect=lambda:self.log([('start',{}),('attached',{})])))
  with patch.object(launcher.time,'sleep') as sleeping:result=launcher.await_attachment(proc,self.session)
  self.assertEqual(result['status'],'ATTACHED_GAMEPLAY_NOT_VERIFIED');self.assertTrue(result['attached']);sleeping.assert_called_once()
 def test_access_denied_is_visible_and_requests_admin(self):
  self.log([('version-or-access-refused','System.ComponentModel.Win32Exception: Access is denied')]);proc=SimpleNamespace(pid=123,poll=Mock(return_value=1))
  with self.assertRaisesRegex(RuntimeError,'Run as administrator'):launcher.await_attachment(proc,self.session)
  self.assertFalse((self.session/'STOP').exists())
 def test_early_exit_and_already_detached_never_report_active(self):
  proc=SimpleNamespace(pid=123,poll=Mock(return_value=7))
  with self.assertRaisesRegex(RuntimeError,'before attachment, exit code 7'):launcher.await_attachment(proc,self.session)
  self.log([('attached',{}),('detached',{}),('end',{})])
  with self.assertRaisesRegex(RuntimeError,'already stopped'):launcher.await_attachment(proc,self.session)
 def test_timeout_requests_graceful_stop_instead_of_success(self):
  proc=SimpleNamespace(pid=123,poll=Mock(return_value=None))
  with self.assertRaisesRegex(RuntimeError,'graceful stop requested'):launcher.await_attachment(proc,self.session,timeout=0)
  self.assertTrue((self.session/'STOP').is_file());self.assertIn('No attachment acknowledgement',(self.session/'STOP').read_text(encoding='utf-8'))
 def test_native_call_counters_never_imply_projectile_verification(self):
  self.log([('native-shot-confirmed',{'extra':True}),('five-native-emissions-accounted',{}),('admission-refused',{'reason':'private paired-window metadata differs'})]);r=launcher.report(self.session)
  self.assertEqual(r['firing_path_ammo_debit_pairs'],1);self.assertEqual(r['five_count_groups'],1);self.assertFalse(r['projectile_count_verified']);self.assertFalse(r['visual_projectile_damage_verification']);self.assertEqual(r['runtime_errors'],[]);self.assertEqual(len(r['guard_refusals']),1)

if __name__=='__main__':unittest.main()
