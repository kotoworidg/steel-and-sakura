using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Web.Script.Serialization;
namespace SteelSakura {
public sealed class NativeMemory:IMemory {
 readonly IntPtr process;public NativeMemory(IntPtr h){process=h;}
 public static bool RegionSafe(uint start,uint count,uint regionBase,uint size,uint state,uint protect,uint type,bool write){return state==0x1000&&(protect&0x101)==0&&start>=regionBase&&(ulong)start+count<=(ulong)regionBase+size&&(!write||(type==0x20000&&(protect&0xc)!=0));}
 void Check(uint p,int n,bool write){IntPtr info=Marshal.AllocHGlobal(28);try{if(Native.VirtualQueryEx(process,new IntPtr(unchecked((int)p)),info,new UIntPtr(28))==UIntPtr.Zero||!RegionSafe(p,(uint)n,unchecked((uint)Marshal.ReadInt32(info)),unchecked((uint)Marshal.ReadInt32(info,12)),unchecked((uint)Marshal.ReadInt32(info,16)),unchecked((uint)Marshal.ReadInt32(info,20)),unchecked((uint)Marshal.ReadInt32(info,24)),write))throw new InvalidDataException("unreadable/guarded/non-private memory region");}finally{Marshal.FreeHGlobal(info);}}
 public byte[] Read(uint p,int n){if(p<0x10000||n<0||n>4096)throw new InvalidDataException("invalid bounded read");Check(p,n,false);byte[] b=new byte[n];IntPtr got;if(!Native.ReadProcessMemory(process,new IntPtr(unchecked((int)p)),b,n,out got)||got.ToInt32()!=n)throw new InvalidDataException("unreadable process data");return b;}
 public void Write(uint p,byte[] b){if(b.Length!=1||b[0]>1)throw new InvalidDataException("only one primary Boolean flag byte permitted");Check(p,b.Length,true);IntPtr n;if(!Native.WriteProcessMemory(process,new IntPtr(unchecked((int)p)),b,b.Length,out n)||n.ToInt32()!=b.Length)throw new InvalidDataException("action flag write failed");}
}
public static class Native {
 [DllImport("kernel32",SetLastError=true)]public static extern UIntPtr VirtualQueryEx(IntPtr process,IntPtr address,IntPtr info,UIntPtr size);
 [DllImport("kernel32",SetLastError=true)]public static extern bool DebugActiveProcess(uint pid);
 [DllImport("kernel32",SetLastError=true)]public static extern bool DebugBreakProcess(IntPtr process);
 [DllImport("kernel32",SetLastError=true)]public static extern bool DebugActiveProcessStop(uint pid);
 [DllImport("kernel32",SetLastError=true)]public static extern bool DebugSetProcessKillOnExit(bool kill);
 [DllImport("kernel32",SetLastError=true)]public static extern bool WaitForDebugEvent(IntPtr e,uint timeout);
 [DllImport("kernel32",SetLastError=true)]public static extern bool ContinueDebugEvent(uint p,uint t,uint status);
 [DllImport("kernel32",SetLastError=true)]public static extern bool GetThreadContext(IntPtr h,IntPtr c);
 [DllImport("kernel32",SetLastError=true)]public static extern bool SetThreadContext(IntPtr h,IntPtr c);
 [DllImport("kernel32",SetLastError=true)]public static extern IntPtr OpenThread(uint access,bool inherit,uint tid);
 [DllImport("kernel32",SetLastError=true)]public static extern bool CloseHandle(IntPtr h);
 [DllImport("kernel32",SetLastError=true)]public static extern bool GetExitCodeThread(IntPtr h,out uint code);
 [DllImport("kernel32",SetLastError=true)]public static extern uint SuspendThread(IntPtr h);
 [DllImport("kernel32",SetLastError=true)]public static extern uint ResumeThread(IntPtr h);
 [DllImport("kernel32",SetLastError=true)]public static extern bool ReadProcessMemory(IntPtr p,IntPtr a,byte[] b,int n,out IntPtr got);
 [DllImport("kernel32",SetLastError=true)]public static extern bool WriteProcessMemory(IntPtr p,IntPtr a,byte[] b,int n,out IntPtr put);
}
public sealed class Registers:IDisposable {
 public readonly byte[] Data=new byte[716];readonly IntPtr ptr=Marshal.AllocHGlobal(716);
 public uint this[int offset]{get{return BitConverter.ToUInt32(Data,offset);}set{Array.Copy(BitConverter.GetBytes(value),0,Data,offset,4);}}
 public Registers(IntPtr thread){this[0]=0x10017;Marshal.Copy(Data,0,ptr,Data.Length);if(!Native.GetThreadContext(thread,ptr))throw new InvalidOperationException("GetThreadContext "+Marshal.GetLastWin32Error());Marshal.Copy(ptr,Data,0,Data.Length);}
 public void Save(IntPtr thread){Marshal.Copy(Data,0,ptr,Data.Length);if(!Native.SetThreadContext(thread,ptr))throw new InvalidOperationException("SetThreadContext "+Marshal.GetLastWin32Error());}
 public void Dispose(){Marshal.FreeHGlobal(ptr);}
}
public sealed class RuntimeLog {
 readonly List<object> rows=new List<object>();readonly string workspace,python,session;int serial=0;public bool Failed;
 public RuntimeLog(string root,string py,string dir){workspace=root;python=py;session=dir;}
 public void Add(string name,object detail){if(Failed)return;rows.Add(new{utc=DateTime.UtcNow.ToString("o"),name=name,detail=detail});}
 public void Flush(){if(Failed||rows.Count==0)return;try{var text=new JavaScriptSerializer{MaxJsonLength=16*1024*1024}.Serialize(rows);rows.Clear();string path=Path.Combine(session,"log-"+(++serial).ToString("D5")+".json");
  var start=new ProcessStartInfo(python,"-B \""+Path.Combine(workspace,"scripts","five_round_log.py")+"\" \""+path+"\""){UseShellExecute=false,CreateNoWindow=true,RedirectStandardInput=true,RedirectStandardOutput=true,RedirectStandardError=true};
  using(var p=Process.Start(start)){p.StandardInput.Write(text);p.StandardInput.Close();string stdout=p.StandardOutput.ReadToEnd(),error=p.StandardError.ReadToEnd();p.WaitForExit();if(p.ExitCode!=0)throw new IOException("tracked runtime log failed "+stdout+error);}
  }catch(Exception e){Failed=true;Console.Error.WriteLine("Logging disabled; controller must drain: "+e.Message);}
 }
}
public sealed class HookHost {
 readonly uint pid;readonly bool mutate;readonly string root,python,session;readonly Dictionary<uint,uint[]> saved=new Dictionary<uint,uint[]>();
 readonly Dictionary<uint,Stack<uint>> frames=new Dictionary<uint,Stack<uint>>();
 Process processOwner;NativeMemory memory;BurstController controller;RuntimeLog log;uint image,imageSize;IntPtr process;bool draining,attached;int eventCount;double maxWallSeconds=90;
 readonly uint[] sites=new uint[]{0x3d438a,0x3b3042,0x3d453a,0x3d45b7};
 public HookHost(uint id,bool writes,string workspace,string py,string dir){pid=id;mutate=writes;root=workspace;python=py;session=dir;}
 static string Hash(string path){using(var s=SHA256.Create())using(var f=File.OpenRead(path))return BitConverter.ToString(s.ComputeHash(f)).Replace("-","");}
 public void Verify(){
  if(IntPtr.Size!=4)throw new InvalidOperationException("x86 host required");
  var p=Process.GetProcessById((int)pid);processOwner=p;if(!String.Equals(p.ProcessName,"shogun2",StringComparison.OrdinalIgnoreCase))throw new InvalidOperationException("not shogun2");
  if(Hash(p.MainModule.FileName)!="0AB284186E0BE3FBCDE34E2F800E3C0328008F3219490C7C25E822ADD837C4A9")throw new InvalidOperationException("unrecognized game executable hash");
  ProcessModule module=null;foreach(ProcessModule m in p.Modules)if(String.Equals(m.ModuleName,"empire.retail.dll",StringComparison.OrdinalIgnoreCase))module=m;
  if(module==null||Hash(module.FileName)!="022FAE2E2DA92B59B8B1B8EE52887003C624E3C8ECA060B209F5D792A7F874F5")throw new InvalidOperationException("unrecognized engine hash");
  string pack=Path.Combine(Path.GetDirectoryName(module.FileName),"data","steel_sakura_combined_test.pack");
  if(Hash(pack)!="__FIVE_ROUND_PACK_SHA256__")throw new InvalidOperationException("pack differs from calibrated baseline");
  var intent=new JavaScriptSerializer().Deserialize<Dictionary<string,object>>(File.ReadAllText(Path.Combine(session,"request.json")));maxWallSeconds=Convert.ToDouble(intent["duration_seconds"]);if(maxWallSeconds<10||maxWallSeconds>3600)throw new InvalidOperationException("invalid approved runtime duration");
  image=unchecked((uint)module.BaseAddress.ToInt32());imageSize=(uint)module.ModuleMemorySize;process=p.Handle;memory=new NativeMemory(process);
  // Whole controller/wrapper byte masks are generated from the pinned file; relocations masked.
  var profile=new JavaScriptSerializer().Deserialize<Dictionary<string,object>>(File.ReadAllText(Path.Combine(AppDomain.CurrentDomain.BaseDirectory,"engine-profile.json")));
  foreach(object obj in (System.Collections.IEnumerable)profile["code_checks"]){var d=(Dictionary<string,object>)obj;uint r=Convert.ToUInt32(d["rva"]);byte[] expected=Convert.FromBase64String((string)d["bytes"]),mask=Convert.FromBase64String((string)d["mask"]);var current=memory.Read(image+r,expected.Length);for(int i=0;i<expected.Length;i++)if(mask[i]!=0&&expected[i]!=current[i])throw new InvalidOperationException("live controller code mismatch");}
 }
 void Arm(uint tid){
  using(var h=new ThreadHandle(tid))using(var c=new Registers(h.Handle)){
   if(saved.ContainsKey(tid))return;
   if((c[24]&0xff)!=0)throw new InvalidOperationException("existing hardware debugger state; refuse overwrite");
   var old=new uint[6];for(int k=0;k<4;k++)old[k]=c[4+k*4];old[4]=c[20];old[5]=c[24];saved[tid]=old;
   for(int k=0;k<4;k++)c[4+k*4]=image+sites[k];c[20]=0;c[24]=0x455;c.Save(h.Handle);
  }
 }
 bool Restore(){
  controller.CleanupPaused();
  // Pending EXIT_THREAD events can temporarily deny SetThreadContext. Retain those
  // entries and drain events rather than pretending their registers were restored.
  foreach(uint tid in new List<uint>(saved.Keys)){
   try{using(var h=new ThreadHandle(tid)){
    uint exit;if(Native.GetExitCodeThread(h.Handle,out exit)&&exit!=259){saved.Remove(tid);continue;}
    uint[] old=saved[tid];using(var c=new Registers(h.Handle)){for(int k=0;k<4;k++)c[4+k*4]=old[k];c[20]=old[4];c[24]=old[5];c.Save(h.Handle);}
    using(var check=new Registers(h.Handle)){for(int k=0;k<4;k++)if(check[4+k*4]!=old[k])throw new InvalidOperationException("DR readback mismatch");if(check[24]!=old[5])throw new InvalidOperationException("DR7 readback mismatch");}
    saved.Remove(tid);
   }}catch{ /* Retry after the queued thread-exit/debug event; never silently discard. */ }
  }return saved.Count==0;
 }
 void Hit(uint tid){
  using(var h=new ThreadHandle(tid))using(var c=new Registers(h.Handle)){
   uint ip=c[184],rva=ip-image;Stack<uint> stack;if(!frames.TryGetValue(tid,out stack)){stack=new Stack<uint>();frames[tid]=stack;}
   if(rva==sites[0]){
    // Only the statically and dynamically recovered wrapper is admitted.
    uint ret=Mem.U(memory,c[196]+0xf4);if(ret==image+sites[1]){uint action=c[160];controller.Enter(action,c[176]);stack.Push(action);}
   }else if(rva==sites[1]){
    if(stack.Count>0){uint action=stack.Pop();controller.Leave(action,(c[176]&255)!=0);}
   }else if(stack.Count>0&&stack.Peek()==c[160]){
    uint action=c[160],slot=c[180];
    if(rva==sites[2]&&!controller.BeforeFire(action,slot,c[156],c[196]+0x74))c[184]=image+0x3d45be;
    if(rva==sites[3])controller.AfterFire(action,slot,c[156],c[196]+0x74);
   }
   c[20]=0;c[192]|=0x10000;c.Save(h.Handle); // RF resumes the original instruction once.
  }
 }
 public int Run(){
  log=new RuntimeLog(root,python,session);try{Verify();}catch(Exception e){log.Add("version-or-access-refused",e.ToString());log.Flush();return 1;}controller=new BurstController(memory,mutate,log.Add);controller.VersionVerified=true;controller.ImageStart=image;controller.ImageSize=imageSize;
  log.Add("start",new{hostPid=Process.GetCurrentProcess().Id,pid=pid,image=image,mode=mutate?"guarded-five-shot":"diagnostic-only",maxShots=5,intervalMs=100,maxBurstMs=BurstController.MaxDuration,unit=BurstController.UnitKey});
  IntPtr ev=Marshal.AllocHGlobal(96);bool processExited=false,firstBreak=true,restored=false,rollbackBreak=false,pending=false;uint pendingPid=0,pendingTid=0,pendingStatus=0x10002;double drainStarted=0,lastFlush=0;var timer=Stopwatch.StartNew();
  try{
   if(!Native.DebugActiveProcess(pid))throw new InvalidOperationException("attach denied "+Marshal.GetLastWin32Error());attached=true;log.Add("attached",new{pid=pid,temporaryPrimaryFlagWrites=true});
   if(!Native.DebugSetProcessKillOnExit(false))throw new InvalidOperationException("cannot disable kill-on-debugger-exit");
   while(!processExited){
    if(log.Failed||File.Exists(Path.Combine(session,"STOP"))||timer.Elapsed.TotalSeconds>maxWallSeconds||eventCount>maxWallSeconds*20000){if(!draining){draining=true;drainStarted=timer.Elapsed.TotalSeconds;controller.Expire();log.Add("drain",new{events=eventCount,seconds=timer.Elapsed.TotalSeconds});}}
    if(timer.Elapsed.TotalSeconds-lastFlush>2){log.Flush();lastFlush=timer.Elapsed.TotalSeconds;}
    bool got=Native.WaitForDebugEvent(ev,50);
    if(!got){int error=Marshal.GetLastWin32Error();if(error!=121&&error!=0)throw new InvalidOperationException("debug event wait "+error);if(draining&&!controller.ExtendedInFlight&&!rollbackBreak){if(!Native.DebugBreakProcess(process))throw new InvalidOperationException("rollback system break failed");rollbackBreak=true;}continue;}
    uint kind=unchecked((uint)Marshal.ReadInt32(ev,0)),epid=unchecked((uint)Marshal.ReadInt32(ev,4)),tid=unchecked((uint)Marshal.ReadInt32(ev,8));uint status=0x10002;bool stopAfter=false;pending=true;pendingPid=epid;pendingTid=tid;pendingStatus=status;
    try{
     eventCount++;
     if(kind==3){IntPtr file=Marshal.ReadIntPtr(ev,12);if(file!=IntPtr.Zero)Native.CloseHandle(file);if(!draining)Arm(tid);}
     else if(kind==2&&!draining)Arm(tid);
     else if(kind==4){saved.Remove(tid);Stack<uint> abandoned;if(frames.TryGetValue(tid,out abandoned))foreach(uint a in abandoned){BurstState state;if(controller.States.TryGetValue(a,out state)){controller.Cancel(state,"native thread exited");state.InOriginal=false;}}frames.Remove(tid);}
     else if(kind==5){controller.Expire();processExited=true;attached=false;stopAfter=true;}
     else if(kind==6){IntPtr file=Marshal.ReadIntPtr(ev,12);if(file!=IntPtr.Zero)Native.CloseHandle(file);}
     else if(kind==1){uint code=unchecked((uint)Marshal.ReadInt32(ev,12)),addr=unchecked((uint)Marshal.ReadInt32(ev,24));bool ours=false;foreach(uint r in sites)if(addr==image+r)ours=true;
      if(code==0x80000004&&ours)Hit(tid);
      else if(code==0x80000003&&(firstBreak||rollbackBreak)){firstBreak=false;rollbackBreak=false;}
      else {status=0x80010001;log.Add("native-exception",new{code=code,address=addr,firstChance=Marshal.ReadInt32(ev,92)});}
     }
    }catch(Exception e){controller.Expire();draining=true;drainStarted=timer.Elapsed.TotalSeconds;stopAfter=true;log.Add("fail-closed",e.ToString());}
    finally{if((stopAfter||draining&&!controller.ExtendedInFlight)&&!processExited){restored=Restore();}pendingStatus=status;if(!Native.ContinueDebugEvent(epid,tid,status))throw new InvalidOperationException("ContinueDebugEvent failed");pending=false;}
    if(processExited||restored)break;
   }
  }catch(Exception e){log.Add("runtime-error",e.ToString());return 1;}finally{
   if(attached){
    controller.Expire();
    // Never exit with our hardware sites armed, including unexpected wait/log errors.
    // Recovery performs no actor writes and only clears debug state we own.
    while(!restored&&saved.Count>0){
     if(!pending){
      Native.DebugBreakProcess(process);
      if(!Native.WaitForDebugEvent(ev,200)){System.Threading.Thread.Sleep(20);continue;}
      uint kind=(uint)Marshal.ReadInt32(ev);pendingPid=(uint)Marshal.ReadInt32(ev,4);pendingTid=(uint)Marshal.ReadInt32(ev,8);pendingStatus=0x10002;pending=true;
      if(kind==4){saved.Remove(pendingTid);frames.Remove(pendingTid);}
      if(kind==5){saved.Clear();processExited=true;attached=false;}
      if(kind==3||kind==6){IntPtr file=Marshal.ReadIntPtr(ev,12);if(file!=IntPtr.Zero)Native.CloseHandle(file);}
      if(kind==1){uint code=(uint)Marshal.ReadInt32(ev,12),address=(uint)Marshal.ReadInt32(ev,24);bool own=false;foreach(uint r in sites)if(address==image+r)own=true;if(code!=0x80000003&&!(code==0x80000004&&own))pendingStatus=0x80010001;}
     }
     restored=processExited||Restore();
     if(Native.ContinueDebugEvent(pendingPid,pendingTid,pendingStatus))pending=false;
    }
    if(pending){while(!Native.ContinueDebugEvent(pendingPid,pendingTid,pendingStatus))System.Threading.Thread.Sleep(20);pending=false;}
    if(attached){while(!Native.DebugActiveProcessStop(pid))System.Threading.Thread.Sleep(100);attached=false;log.Add("detached",new{pid=pid,engineFilesModified=false});}
   }
   Marshal.FreeHGlobal(ev);if(processOwner!=null)processOwner.Dispose();log.Add("end",new{events=eventCount,processExited=processExited});log.Flush();
  }
  return 0;
 }
}
public sealed class ThreadHandle:IDisposable {public IntPtr Handle;public ThreadHandle(uint tid){Handle=Native.OpenThread(0x5a,false,tid);if(Handle==IntPtr.Zero)throw new InvalidOperationException("OpenThread failed");}public void Dispose(){Native.CloseHandle(Handle);}}
public static class Program {
 public static int Main(string[] args){
  try{
   if(args.Length==2&&args[0]=="--check-profile"){var doc=new JavaScriptSerializer().Deserialize<Dictionary<string,object>>(File.ReadAllText(args[1]));int n=0;foreach(object x in (System.Collections.IEnumerable)doc["code_checks"]){var d=(Dictionary<string,object>)x;if(Convert.FromBase64String((string)d["bytes"]).Length!=Convert.FromBase64String((string)d["mask"]).Length)throw new Exception("mask size");n++;}Console.WriteLine("PROFILE_OK "+n);return 0;}
   if(args.Length==2&&args[0]=="--toy-child")return BridgeTests.Child(args[1]);
   if(args.Length==1&&args[0]=="--bridge-self-test")return BridgeTests.Run();
   if(args.Length==1&&args[0]=="--self-test")return SelfTests.Run();
   if(args.Length==6&&args[0]=="--run"&&args[1]=="--five-round-runtime-approved")return new HookHost(UInt32.Parse(args[2]),true,args[3],args[4],args[5]).Run();

   Console.WriteLine("Prepared experiment. No hook runs without explicit --run --five-round-runtime-approved. Use --self-test for offline tests.");return 2;
  }catch(Exception e){Console.Error.WriteLine(e.ToString());return 1;}
 }
}
}
