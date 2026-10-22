"""Controlled x32dbg console host. No engine patches or software breakpoints.
CLI prepare creates isolated, hash-tracked state and a ready-to-review launcher.
Worker accepts only bounded read/trace commands; no native function calls/writes.
"""
import argparse,ctypes,datetime,json,os,queue,re,subprocess,sys,threading,time
from pathlib import Path
from tracked_files import ROOT,write_text,digest
TOOL=ROOT/'tools/x64dbg/2026.05.27/release/x32/headless.exe'
BASE=ROOT/'build/engine-burst-research'
ALLOWED={'state','log','bph','bphc','bphd','bphs','run','detach','pause','sethardwarebreakpointcondition','sethardwarebreakpointlog','sethardwarebreakpointlogcondition','sethardwarebreakpointcommand','sethardwarebreakpointcommandcondition','sethardwarebreakpointsingleshoot','sethardwarebreakpointsilent','bplist'}
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def ps_script(path):
 p=subprocess.run(['powershell','-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',str(path)],capture_output=True,text=True,creationflags=0x08000000)
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 return p.stdout

def prepare(pid):
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
 session=BASE/('runtime-'+stamp);session.mkdir(parents=True,exist_ok=False)
 state=session/'debugger-state';state.mkdir();(state/'db').mkdir();(state/'memdumps').mkdir()
 (session/'inbox').mkdir();(session/'events').mkdir()
 write_text(session/'session.json',json.dumps({'pid':pid,'prepared':now(),'approval':'CONTROLLED_DEBUGGER_TRACE_ONLY','tool':str(TOOL),'no_patches':True,'no_native_calls':True,'no_software_breakpoints':True},indent=2)+'\n','Prepare authorized read/trace debugger session')
 ini='[Events]\nSystemBreakpoint=1\nEntryBreakpoint=0\nTlsCallbacks=0\nTlsCallbacksSystem=0\nDllEntry=0\nDllEntrySystem=0\nThreadEntry=0\nThreadStart=0\nThreadEnd=0\nDllLoad=0\nDllUnload=0\nDebugStrings=0\n[Engine]\nSaveDatabaseInProgramDirectory=0\nDisableDatabaseCompression=1\n[Misc]\nTransparentExceptionStepping=0\nQueryProcessCookie=0\n[Symbols]\nCachePath='+str(state/'symbols-blocked')+'\n'
 for name,data in [('headless.ini',ini),('notes.txt',''),('db/shogun2.exe.dd32','{}\n'),('db/shogun2.exe.dd32.bak','{}\n'),('db/shogun2.exe.dd32.cmdline',''),('symbols-blocked','Symbol downloads disabled for this trace.\n')]:
  write_text(state/name,data,'Seed isolated debugger state before write protection')
 # Export original ACL before applying a scoped deny rule. Only state is affected;
 # events/inbox remain writable through tracked_files. No original game ACL changes.
 quote=lambda x:str(x).replace("'","''")
 protect=f"$ErrorActionPreference='Stop'\n$statePath='{quote(state)}'\n$originalAcl=Get-Acl -LiteralPath $statePath\n$identity=[System.Security.Principal.WindowsIdentity]::GetCurrent().User\n$deny=[System.Security.AccessControl.FileSystemAccessRule]::new($identity,[System.Security.AccessControl.FileSystemRights]'Write,Delete,DeleteSubdirectoriesAndFiles',[System.Security.AccessControl.InheritanceFlags]'ContainerInherit,ObjectInherit',[System.Security.AccessControl.PropagationFlags]::None,[System.Security.AccessControl.AccessControlType]::Deny)\n$originalAcl.AddAccessRule($deny)\nSet-Acl -LiteralPath $statePath -AclObject $originalAcl\n"
 write_text(session/'protect-state.ps1',protect,'Prepare isolated debugger state write protection')
 # SDDL is captured in the worker immediately before protection through tracked_files.
 restore=f"$ErrorActionPreference='Stop'\n$statePath='{quote(state)}'\n$record=Get-Content -LiteralPath '{quote(session/'state-acl-before.json')}' -Raw | ConvertFrom-Json\n$originalAcl=[System.Security.AccessControl.DirectorySecurity]::new()\n$originalAcl.SetSecurityDescriptorSddlForm($record.sddl)\nSet-Acl -LiteralPath $statePath -AclObject $originalAcl\n"
 write_text(session/'restore-state-acl.ps1',restore,'Prepare exact isolated-state permission rollback')
 # Full named arguments and paths are fixed here; no shell command construction from input.
 launcher=f"$ErrorActionPreference='Stop'\n$pythonExe='{quote(sys.executable)}'\n$workerArgs='-B \"{ROOT/'scripts/trace_x32dbg.py'}\" worker --session \"{session}\"'\nStart-Process -FilePath $pythonExe -ArgumentList $workerArgs -Verb RunAs -WindowStyle Hidden\n"
 write_text(session/'launch-elevated.ps1',launcher,'Prepare UAC launcher for approved debugger trace, no game patch')
 print(json.dumps({'session':str(session),'launcher':str(session/'launch-elevated.ps1')}))

def worker(session):
 session=Path(session).resolve();config=json.loads((session/'session.json').read_text());pid=config['pid'];state=session/'debugger-state'
 if not session.is_relative_to(BASE):raise ValueError('Invalid session')
 output=queue.Queue();serial=0;child=None;seen=set();detached=False;attached=False;exit_requested=False
 def event(kind,payload):
  nonlocal serial
  serial+=1
  write_text(session/'events'/f'{serial:06d}-{kind}.json',json.dumps({'utc':now(),'kind':kind,'payload':payload},indent=2)+'\n','Record debugger trace event without untracked log append')
 expected={str(p.relative_to(state)):digest(p.read_bytes()) for p in state.rglob('*') if p.is_file()}
 acl_code="(Get-Acl -LiteralPath '"+str(state).replace("'","''")+"').Sddl"
 acl=subprocess.run(['powershell','-NoProfile','-NonInteractive','-Command',acl_code],capture_output=True,text=True,check=True,creationflags=0x08000000).stdout.strip()
 write_text(session/'state-acl-before.json',json.dumps({'path':str(state),'sddl':acl,'rollback':'powershell -NoProfile -File "'+str(session/'restore-state-acl.ps1')+'"'},indent=2)+'\n','Back up exact isolated-state ACL before deny-write protection')
 ps_script(session/'protect-state.ps1')
 try:
  # Demonstrate that writes/creation are blocked before launching the debugger.
  blocked=[]
  for path in [state/'headless.ini',state/'must-not-be-created.tmp']:
   try:
    with path.open('ab'):pass
   except PermissionError:blocked.append(str(path))
   else:raise RuntimeError('State write protection failed: '+str(path))
  event('state-protection',{'blocked_write_checks':blocked,'hashes':expected})
  # Filesystem changes are denied in state, including automatic saves and symbols.
  child=subprocess.Popen([str(TOOL),'-userdir',str(state)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,cwd=str(TOOL.parent),creationflags=0x08000000)
  def reader():
   for line in iter(child.stdout.readline,b''):output.put(line.decode('utf-8',errors='replace'))
  threading.Thread(target=reader,daemon=True).start()
  event('started',{'debugger_pid':child.pid,'target_pid':pid,'admin':bool(ctypes.windll.shell32.IsUserAnAdmin())})
  deadline=time.monotonic()+240
  while child.poll() is None:
   lines=[]
   while not output.empty():lines.append(output.get_nowait())
   if lines:
    text=''.join(lines);event('stdout',text)
    if 'Attached to process' in text or 'attached to process' in text:attached=True
    if 'Detached!' in text:detached=True;attached=False
   for path in sorted((session/'inbox').glob('*.json')):
    if path.name in seen:continue
    item=json.loads(path.read_text(encoding='utf-8'));command=item['command'];seen.add(path.name)
    if command=='HOST_EXIT':
     if attached and not detached:raise RuntimeError('Detach must be confirmed before HOST_EXIT')
     exit_requested=True;wire='exit'
    elif command=='HOST_ATTACH':
     wire='attach .'+str(pid);attached=True;detached=False
    else:
     verb=command.split(' ',1)[0].lower()
     if verb not in ALLOWED or '\n' in command or '\r' in command or ';' in command:raise ValueError('Forbidden command')
     if verb=='attach':raise ValueError('Use HOST_ATTACH for the pinned process only')
     wire=command
    if command=='HOST_ATTACH':wire='attach .'+str(pid);attached=True;detached=False
    event('command',wire)
    child.stdin.write((wire+'\n').encode());child.stdin.flush();deadline=time.monotonic()+240
   if time.monotonic()>deadline:
    if attached and not detached:
     child.stdin.write(b'detach\n');child.stdin.flush();event('watchdog','Requested detach after 240 seconds without a command');deadline=time.monotonic()+30
    else:
     child.stdin.write(b'exit\n');child.stdin.flush();deadline=time.monotonic()+30
   time.sleep(.15)
  time.sleep(.2)
  lines=[]
  while not output.empty():lines.append(output.get_nowait())
  if lines:event('stdout',''.join(lines))
  event('exit',{'returncode':child.returncode,'explicit_detach_confirmed':detached})
 except Exception as e:
  event('host-error',repr(e))
  if child and child.poll() is None:
   # Do not terminate the debugger while it might own a live game process.
   try:child.stdin.write(b'detach\n');child.stdin.flush()
   except Exception:pass
   event('recovery','Detach requested. Debugger retained; do not terminate until state is checked.')
 finally:
  # Restore only directory permissions; seeded files should never have changed.
  if child is None or child.poll() is not None:
   ps_script(session/'restore-state-acl.ps1')
  else:
   event('protection-retained','Debugger still running: state ACL remains protected. Restore only after debugger exits.')
  actual={str(p.relative_to(state)):digest(p.read_bytes()) for p in state.rglob('*') if p.is_file()}
  event('state-audit',{'unchanged':actual==expected,'expected':expected,'actual':actual})

def command(session,text):
 p=Path(session).resolve()
 if not p.is_relative_to(BASE):raise ValueError('Invalid session')
 # Host-only attach is pinned to the prepared PID. Engine write commands rejected.
 if text not in ('HOST_ATTACH','HOST_EXIT') and text.split(' ',1)[0].lower() not in ALLOWED:raise ValueError('Forbidden command')
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
 print(write_text(p/'inbox'/(stamp+'.json'),json.dumps({'command':text,'utc':now()})+'\n','Queue approved bounded debugger read/trace command'))
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=['prepare','worker','command']);parser.add_argument('--pid',type=int);parser.add_argument('--session');parser.add_argument('--text');a=parser.parse_args()
 if a.action=='prepare':prepare(a.pid)
 elif a.action=='worker':worker(a.session)
 else:command(a.session,a.text)
