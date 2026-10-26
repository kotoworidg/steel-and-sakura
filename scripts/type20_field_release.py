"""Build a hook-free supported fallback; preserve the exhausted historical ledger."""
import argparse,io,json,subprocess,zipfile
from pathlib import Path
import type20_playable as supported
from tracked_files import ROOT,write_bytes,write_text,digest
from type20_pack_codec import pack_entries,pack_bytes,db_read
PROFILE=ROOT/'src/type20-field-release.json'
OUT=ROOT/'build/type20-field-release-20261027'
CANDIDATE_HASH='C89B3F9F48CCC07EB153576A264FF66AC8F63FE35F70609FD85736C043F2479A'
DELTA={'armour':8,'loose_formation_spacing_horizontal':3.0,'loose_formation_spacing_vertical':4.5}
FRAG='steel_sakura_frag_test'
SOURCES=['src/type20-field-release.json','src/type20-supported.json','scripts/type20_field_release.py',
         'scripts/type20_playable.py','scripts/type20_pack_codec.py','scripts/tracked_files.py',
         'scripts/install_type20_supported.py','scripts/validate_type20_rpfm.py',
         'tests/test_type20_field_release.py','docs/TYPE20_FIELD_RELEASE.md']

def save(path,value,reason):
    return write_text(path,json.dumps(value,indent=2)+'\n','Type20 field release: '+reason)

def load_profile():
    return supported.load(PROFILE)

def previous_builds():
    path=supported.OUT/'iterations.json'
    rows=supported.load(path)
    if len(rows)!=3 or rows[-1]['core_sha256']!=CANDIDATE_HASH:
        raise ValueError('Historical build ledger changed; review instead of resetting budget')
    return {'sha256':digest(path.read_bytes()),'builds':rows}

def check_iteration(iteration,rows):
    if iteration!=len(rows)+1 or not 1<=iteration<=3:
        raise ValueError('New session permits at most three sequential meaningful builds')

def extra_specs():
    table=supported.load(ROOT/'build/diagnostic/installed_projectiles_explosions.json')['DBRFileInfo'][0]['table']
    return {'projectiles_explosions':supported.schema(table)}

def validate_bytes(core,optional,profile=None):
    profile=profile or load_profile()
    original=supported.load(supported.PROFILE)
    editable={'version','title','stats','description','long_description','known_limits'}
    if any(profile.get(key)!=value for key,value in original.items() if key not in editable):
        raise ValueError('Unrelated source configuration changed')
    if profile['known_limits']!={**original['known_limits'],'grenade_damage_verified':False}:
        raise ValueError('Unsupported gameplay claim in profile')
    if profile['stats']!={**original['stats'],**DELTA}:
        raise ValueError('Unexpected unit changes outside protection/loose-formation contract')
    if profile['projectile']!=original['projectile'] or profile['suppression_projectile']!=original['suppression_projectile']:
        raise ValueError('Rifle ballistics/reload/ammunition must retain supported values')
    if profile.get('core_abilities')!=['rapid_volley','blinding_grenade']:
        raise ValueError('Expected native Rapid Volley and grenade assignment')
    result=supported.validate_bytes(core,optional,profile)
    entries=pack_entries(core)
    _,_,_,specs=supported.evidence();specs.update(extra_specs())
    rows=lambda table,path: db_read(entries['db/'+table+'_tables/'+path],specs[table])[1]
    stats=rows('unit_stats_land','steel_sakura_type20_burst')[0]
    if stats['armour']!=8 or stats['man_health']!=1 or stats['bulletproof'] or not stats['loose_formation']:
        raise ValueError('Native protection and selectable formation contract differs')
    ability=rows('unit_special_abilities',FRAG)[0]
    bullets={row['key']:row for row in rows('projectiles',FRAG)}
    grenade=bullets[ability['activated_projectile']]
    explosions={row['key']:row for row in rows('projectiles_explosions',FRAG)}
    explosion=explosions[grenade['explosion_type']]
    fragment=bullets[explosion['particle_type']]
    if ability['key']!='blinding_grenade' or grenade['shot_type']!='blinding_grenade' or grenade['projectile_number']!=1:
        raise ValueError('Native grenade linkage differs')
    if explosion['detonation_damage']<=0 or fragment['damage']<=0:
        raise ValueError('Inherited fragmentation damage chain is non-damaging')
    result.update(grenade_chain={'ability':ability['key'],'projectile':grenade['key'],
        'explosion':grenade['explosion_type'],'fragment':fragment['key'],
        'active_time':ability['active_time'],'recharge_time':ability['recharge_time'],
        'explosion_damage':explosion['detonation_damage'],'fragment_damage':fragment['damage']},
        grenade_damage_verified=False,runtime_required=False,stat_changes=DELTA,
        new_gameplay=['Type20 grenade ability assignment','armour 2 to 8','selectable loose spacing 2x3 to 3x4.5'])
    return result

def current():
    pointer=supported.load(OUT/'latest.json')
    session=Path(pointer['session'])
    result=validate_bytes((session/'steel_sakura_combined_test.pack').read_bytes(),
                          (session/'steel_sakura_type20_suppression.pack').read_bytes(),
                          supported.load(session/'profile.json'))
    if result['core_sha256']!=pointer['core_sha256'] or result['optional_sha256']!=pointer['optional_sha256']:
        raise ValueError('Built pack no longer matches iteration ledger')
    return session,result

def build(iteration):
    history=previous_builds()
    rows=supported.load(OUT/'iterations.json') if (OUT/'iterations.json').exists() else []
    check_iteration(iteration,rows)
    session=OUT/('iteration-%02d'%iteration)
    if session.exists():raise ValueError('Never overwrite a previous build iteration')
    profile=load_profile()
    _,base,r2,specs=supported.evidence()
    core,optional,_=supported.planned(profile,base,r2,specs)
    core_raw,optional_raw=pack_bytes(core),pack_bytes(optional)
    result=validate_bytes(core_raw,optional_raw,profile)
    record={'iteration':iteration,'core_sha256':digest(core_raw),'optional_sha256':digest(optional_raw),
            'profile_sha256':digest(PROFILE.read_bytes()),'session':str(session)}
    save(OUT/'iterations.json',rows+[record],'bounded NEW session ledger; historical three builds remain intact')
    save(session/'authorization.json',{'client_date':'2026-10-27','prior_session':history,
        'new_session_limit':3,'authorization':'Latest supplied TYPE 20 COMBAT IMPLEMENTATION request: mandatory supported fallback and maximum THREE meaningful build iterations; installation separate.',
        'installed_game_files_modified':False},'explicit continuation budget and no installation')
    for name,data in [('steel_sakura_combined_test.pack',core_raw),('steel_sakura_type20_suppression.pack',optional_raw)]:
        write_bytes(session/name,data,'Supported Type20 gameplay pack iteration '+str(iteration))
    save(session/'profile.json',profile,'frozen gameplay configuration')
    save(session/'schema-specs.json',{**specs,**extra_specs()},'observed table schemas')
    save(session/'validation.json',result,'offline links and exact baseline preservation')
    save(OUT/'latest.json',record,'new release build pointer without modifying old pointers')
    print(json.dumps({'session':str(session),'core_sha256':result['core_sha256'],'status':result['status']},indent=2))

def reopen():
    from validate_type20_rpfm import run
    session,result=current()
    paths=['db/'+table+'_tables/'+path for table,path in
           [('unit_abilities','steel_sakura_combined'),('unit_special_abilities',FRAG),
            ('projectiles',FRAG),('projectiles_explosions',FRAG)]]
    run(session=session,validation=result,additional_specs=extra_specs(),additional_paths=paths)

def package():
    session,validation=current()
    tests=supported.load(session/'test-results.json')
    rpfm=supported.load(session/'rpfm-validation.json')
    source_hashes={name:digest((ROOT/name).read_bytes()) for name in SOURCES}
    if not tests['successful'] or tests['failures'] or tests['errors'] or tests['skipped'] or tests['source_sha256']!=source_hashes:
        raise ValueError('Passing tests for current source required')
    if rpfm['status']!='PASS_RPFM_INDEPENDENT_REOPEN' or any(rpfm[k]!=validation[k] for k in ['core_sha256','optional_sha256']):
        raise ValueError('Matching independent pack reopening required')
    if supported.load(session/'profile.json')!=load_profile():raise ValueError('Profile changed after build')
    history=previous_builds()
    files={name:(session/name).read_bytes() for name in
           ['steel_sakura_combined_test.pack','steel_sakura_type20_suppression.pack','validation.json',
            'rpfm-validation.json','test-results.json','profile.json','authorization.json']}
    files.update({'install_type20.py':(ROOT/'scripts/install_type20_supported.py').read_bytes(),
                  'README.md':(ROOT/'docs/TYPE20_FIELD_RELEASE.md').read_bytes()})
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    release={'format':1,'version':'0.3.0','source_commit':commit,'source_sha256':source_hashes,
             'pack_sha256':{n:digest(files[n]) for n in ['steel_sakura_combined_test.pack','steel_sakura_type20_suppression.pack']},
             'previous_core_hashes':[r['core_sha256'] for r in history['builds']],
             'previous_suppression_hashes':[r['optional_sha256'] for r in history['builds'] if 'optional_sha256' in r],
             'optional_shared_scope':validation['changes']['optional_shared_scope'],
             'runtime_required':False,'five_round_bursts':False,'true_full_auto':False,
             'per_soldier_magazine_reload':False,'in_game_verified':False}
    files['release.json']=(json.dumps(release,indent=2)+'\n').encode()
    files['Preview-Install.cmd']=b'@echo off\r\npython -B "%~dp0install_type20.py" install --dry-run\r\npause\r\n'
    files['Install-Core.cmd']=b'@echo off\r\npython -B "%~dp0install_type20.py" install %*\r\npause\r\n'
    # Include original confirmed recovery and its guarded installer as a separate option.
    recovery=dict(release,version='confirmed-two-shot-recovery',supports_suppression=False)
    recovery['pack_sha256']={**release['pack_sha256'],'steel_sakura_combined_test.pack':digest(supported.BASE.read_bytes())}
    recovery['previous_core_hashes']=[*release['previous_core_hashes'],release['pack_sha256']['steel_sakura_combined_test.pack']]
    files.update({'recovery/steel_sakura_combined_test.pack':supported.BASE.read_bytes(),
                  'recovery/steel_sakura_type20_suppression.pack':files['steel_sakura_type20_suppression.pack'],
                  'recovery/install_type20.py':files['install_type20.py'],
                  'recovery/release.json':(json.dumps(recovery,indent=2)+'\n').encode()})
    files['Restore-Confirmed.cmd']=b'@echo off\r\npython -B "%~dp0recovery\\install_type20.py" install %*\r\npause\r\n'
    files['SHA256SUMS.txt']=''.join(digest(data)+'  '+name+'\n' for name,data in sorted(files.items())).encode()
    target=ROOT/'dist/type20-field-release/0.3.0'
    for name,data in files.items():write_bytes(target/name,data,'Type20 release package '+name)
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in sorted(files.items()):
            entry=zipfile.ZipInfo(name,date_time=(2026,10,27,0,0,0));entry.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(entry,data)
    raw=buf.getvalue()
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if z.testzip() or any(z.read(n)!=data for n,data in files.items()):raise ValueError('ZIP verification failed')
    path=target.parent/'steel-and-sakura-type20-0.3.0.zip'
    write_bytes(path,raw,'Verified installable supported Type20 ZIP without runtime binaries')
    report={'zip':str(path),'zip_sha256':digest(raw),'release_directory':str(target),'source_commit':commit,
            'core_sha256':validation['core_sha256'],'installed':False,'in_game_verified':False}
    save(OUT/'release.json',report,'release provenance')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('action',choices=['build','validate','reopen','package'])
    ap.add_argument('--iteration',type=int,default=1)
    args=ap.parse_args()
    if args.action=='build':build(args.iteration)
    elif args.action=='validate':print(json.dumps(current()[1],indent=2))
    elif args.action=='reopen':reopen()
    else:package()
