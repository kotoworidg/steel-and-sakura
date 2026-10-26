"""Release data/compatibility tests; these do not simulate or prove combat."""
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import type20_field_release as release
import type20_playable as supported
from type20_pack_codec import pack_bytes,db_read,db_bytes

class FieldReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile=release.load_profile()
        _,cls.base,cls.r2,cls.specs=supported.evidence()
        cls.core,cls.optional,_=supported.planned(cls.profile,cls.base,cls.r2,cls.specs)

    def validate(self,core=None,profile=None):
        return release.validate_bytes(pack_bytes(self.core if core is None else core),pack_bytes(self.optional),profile or self.profile)

    def test_real_type20_receives_existing_grenade_chain_and_rapid_volley(self):
        _,rows=db_read(self.core[supported.JUNCTION],self.specs['unit_to_unit_abilities_junctions'])
        self.assertEqual({(r['unit_name'],r['ability']) for r in rows},
            {(supported.TYPE20,'rapid_volley'),(supported.TYPE20,'blinding_grenade')})
        result=self.validate()
        self.assertEqual(result['grenade_chain']['explosion'],'steel_sakura_frag_explosion_v1')
        self.assertFalse(result['grenade_damage_verified'])

    def test_armour_and_selectable_dispersion_change_without_invulnerability(self):
        _,rows=db_read(self.core[supported.PATHS['unit_stats_land']],self.specs['unit_stats_land'])
        row=rows[0]
        self.assertEqual((row['armour'],row['man_health'],row['bulletproof']),(8,1,False))
        self.assertEqual((row['loose_formation_spacing_horizontal'],row['loose_formation_spacing_vertical']),(3,4.5))
        self.assertTrue(row['loose_formation'])
        self.assertTrue(row['guard_mode'])
        self.assertFalse(row['skirmish'])

    def test_preserves_engine_damage_ammo_clips_and_every_unrelated_payload(self):
        result=self.validate()
        self.assertEqual(result['unchanged_baseline_payloads'],35)
        self.assertEqual(result['normal_projectile']['damage'],3)
        self.assertEqual(result['normal_projectile']['projectile_number'],1)
        self.assertEqual(result['native_ammo'],210)
        for p in self.base:
            if p not in set(supported.PATHS.values())|{supported.LOC}:
                self.assertEqual(self.core[p],self.base[p],p)
        for flag in ['five_shot','full_auto','magazine_model','in_game_verified']:
            self.assertFalse(result[flag])

    def test_rejects_reverting_grenade_link_and_collateral_edits(self):
        core=dict(self.core)
        path=supported.JUNCTION
        prefix,rows=db_read(core[path],self.specs['unit_to_unit_abilities_junctions'])
        core[path]=db_bytes(prefix,rows[:1],self.specs['unit_to_unit_abilities_junctions'])
        with self.assertRaises(ValueError):self.validate(core)
        core=dict(self.core)
        path='db/unit_special_abilities_tables/steel_sakura_frag_test'
        core[path]=core[path][:-1]+bytes([core[path][-1]^1])
        with self.assertRaises(ValueError):self.validate(core)

    def test_contract_rejects_disguised_balance_or_fake_burst_changes(self):
        for section,key,value in [('stats','man_health',10),('stats','ammo',999),
                                  ('stats','armour',100),('costs','upkeep_cost',0),('projectile','projectile_number',5),
                                  ('projectile','damage',0),('stats','loose_formation_spacing_horizontal',2)]:
            p=copy.deepcopy(self.profile);p[section][key]=value
            core,optional,_=supported.planned(p,self.base,self.r2,self.specs)
            with self.subTest(key=key),self.assertRaises(ValueError):
                release.validate_bytes(pack_bytes(core),pack_bytes(optional),p)

    def test_previous_build_ledger_is_preserved_and_new_budget_is_bounded(self):
        history=release.previous_builds()
        self.assertEqual(len(history['builds']),3)
        self.assertEqual(history['builds'][-1]['core_sha256'],release.CANDIDATE_HASH)
        with self.assertRaises(ValueError):release.check_iteration(4,[])
        with self.assertRaises(ValueError):release.check_iteration(1,[{'iteration':1}])


# Exercise the actual new/recovery pack bytes with the existing transactional
# install/rollback fixture suite; writes are confined to TemporaryDirectory.
import test_type20_playable as legacy_tests
import install_type20_supported as installer

class FieldInstallTests(legacy_tests.InstallTests):
    def setUp(self):
        super().setUp()
        self.build,_=release.current()
        for name in [installer.CORE,installer.SUPP]:
            (self.package/name).write_bytes((self.build/name).read_bytes())
        candidate=ROOT/'dist/five_round/0.2.0-launcher-fix/steel_sakura_combined_test.pack'
        self.assertEqual(installer.hashpath(candidate),release.CANDIDATE_HASH)
        self.main.write_bytes(candidate.read_bytes())
        self.original[self.main]=self.main.read_bytes()
        self.manifest={'format':1,'version':'0.3.0-fixture',
            'pack_sha256':{n:installer.hashpath(self.package/n) for n in [installer.CORE,installer.SUPP]},
            'previous_core_hashes':[release.CANDIDATE_HASH],
            'optional_shared_scope':'existing shared suppression option'}
        (self.package/'release.json').write_text(json.dumps(self.manifest))

    def test_confirmed_recovery_and_inverse_restore_new_then_candidate(self):
        first=installer.install(self.package,self.game)
        new_bytes=self.main.read_bytes()
        self.assertNotEqual(new_bytes,self.original[self.main])
        recovery=self.root/'recovery';recovery.mkdir()
        (recovery/installer.CORE).write_bytes(supported.BASE.read_bytes())
        (recovery/installer.SUPP).write_bytes((self.package/installer.SUPP).read_bytes())
        manifest={**self.manifest,'supports_suppression':False,
                  'previous_core_hashes':[installer.sha(new_bytes)],
                  'pack_sha256':{n:installer.hashpath(recovery/n) for n in [installer.CORE,installer.SUPP]}}
        (recovery/'release.json').write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError,'does not contain'):
            installer.install(recovery,self.game,True)
        self.assertFalse((recovery/'backups').exists())
        self.assertEqual(self.main.read_bytes(),new_bytes)
        second=installer.install(recovery,self.game)
        self.assertEqual(installer.hashpath(self.main),installer.BASELINE)
        installer.rollback(Path(second['receipt']))
        self.assertEqual(self.main.read_bytes(),new_bytes)
        installer.rollback(Path(first['receipt']))
        self.assertEqual(installer.hashpath(self.main),release.CANDIDATE_HASH)
        for p,b in self.original.items():self.assertEqual(p.read_bytes(),b)
        self.assertEqual(installer.preservation(self.game),self.preserved)

if __name__=='__main__':unittest.main()
