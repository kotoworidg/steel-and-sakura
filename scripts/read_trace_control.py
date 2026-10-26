"""Read-only trace status, safe detach request and evidence summary."""
import argparse,base64,collections,json,struct
from pathlib import Path
from tracked_files import ROOT,write_text,digest

def current():
 config=json.loads((ROOT/'build/read-trace/latest.json').read_text());session=Path(config['session']).resolve()
 if not session.is_relative_to(ROOT/'build/read-trace'):raise ValueError('session outside trace workspace')
 return config,session

def records(session):return [r for f in sorted(session.glob('log-*.json')) for r in json.loads(f.read_text())]
def summary(session):
 rows=records(session);names=collections.Counter(r['name'] for r in rows);identities=[];needle=('steel_sakura_type20_automatic_fire_test'+'\0').encode('utf-16-le')
 for r in rows:
  if r['name']!='unit-initial':continue
  d=r['detail'];matches=[]
  for p in d['pointers']:
   data=base64.b64decode(p['bytes']);position=data.find(needle)
   if position>=0:matches.append({'unit_offset':hex(p['offset']),'pointer':hex(p['pointer']),'string_offset':position,'exact_terminated_key':True})
  identities.append({'unit':hex(d['unit']),'matches':matches})
 after=[r['detail'] for r in rows if r['name']=='native-after'];polls=[r['detail'] for r in rows if r['name']=='poll-nonatomic']
 result={'session':str(session),'events':dict(names),'identity_candidates':identities,'paired_shots':len(after),'ammo_delta_histogram':dict(collections.Counter(str(x['delta']) for x in after)),
 'observed_unit_count':len(identities),'sampled_actors':sorted({hex(p['actor']) for p in polls}),'poll_time_range_ms':[min((p['elapsedMs'] for p in polls),default=0),max((p['elapsedMs'] for p in polls),default=0)],
 'native_exceptions':[r['detail'] for r in rows if r['name']=='native-exception'],'detached':bool(names['detached']),'finished':bool(names['end']),
 'game_data_writes':False,'order_move_death_semantics_verified':False,'five_shots_verified':False,'raw_logs':[{'path':str(f),'sha256':digest(f.read_bytes())} for f in sorted(session.glob('log-*.json'))]}
 return result

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['status','stop','report']);a=ap.parse_args();config,session=current()
 if a.action=='stop':
  if not (session/'STOP').exists():print(write_text(session/'STOP','Stop read-only observation; restore owned debug registers and detach.\n','Read trace graceful stop request'))
 elif a.action=='status':
  r=summary(session);print(json.dumps({k:v for k,v in r.items() if k not in ['identity_candidates','raw_logs']},indent=2))
 else:
  r=summary(session)
  if not r['detached'] or not r['finished']:raise RuntimeError('final report requires confirmed detach and end')
  print(write_text(session/'report.json',json.dumps(r,indent=2)+'\n','Read trace final evidence summary'))
  print(json.dumps({k:v for k,v in r.items() if k not in ['identity_candidates','raw_logs']},indent=2))
