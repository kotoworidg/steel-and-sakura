// Offline Win32 transport test against our own synthetic x86 child ONLY.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.IO.Pipes;
using System.Runtime.InteropServices;
using System.Threading;
using System.Web.Script.Serialization;
namespace SteelSakura {
public static class BridgeTests {
 [DllImport("kernel32")]static extern IntPtr VirtualAlloc(IntPtr p,UIntPtr n,uint flags,uint protect);
 [DllImport("kernel32")]static extern bool VirtualProtect(IntPtr p,UIntPtr n,uint protect,out uint previous);
 [DllImport("kernel32")]static extern bool VirtualFree(IntPtr p,UIntPtr n,uint how);
 [UnmanagedFunctionPointer(CallingConvention.Cdecl)]delegate int Toy();
 public static int Child(string name){
  IntPtr block=VirtualAlloc(IntPtr.Zero,new UIntPtr(4096),0x3000,4);if(block==IntPtr.Zero)return 1;
  try{
   var calls=new Toy[4];for(int i=0;i<4;i++){byte[] code=new byte[]{0xb8,(byte)(i+1),0,0,0,0xc3};IntPtr address=IntPtr.Add(block,i*16);Marshal.Copy(code,0,address,code.Length);calls[i]=(Toy)Marshal.GetDelegateForFunctionPointer(address,typeof(Toy));}
   uint old;if(!VirtualProtect(block,new UIntPtr(4096),0x20,out old))return 2;
   using(var pipe=new NamedPipeClientStream(".",name,PipeDirection.InOut)){pipe.Connect(10000);var reader=new StreamReader(pipe);var writer=new StreamWriter(pipe){AutoFlush=true};writer.WriteLine(block.ToInt32().ToString());bool stop=false;
    var thread=new Thread(()=>{reader.ReadLine();stop=true;});thread.IsBackground=true;thread.Start();var clock=Stopwatch.StartNew();
    while(!stop&&clock.Elapsed.TotalSeconds<25){for(int i=0;i<4;i++)if(calls[i]()!=i+1)return 3;Thread.Sleep(10);}
   }return 0;
  }finally{VirtualFree(block,UIntPtr.Zero,0x8000);}
 }
 public static int Run(){
  string name="ss-burst5-toy-"+Guid.NewGuid().ToString("N");var original=new Dictionary<uint,uint[]>();var hits=new HashSet<uint>();bool attached=false;Process child=null;IntPtr ev=Marshal.AllocHGlobal(96);int events=0;bool restored=false;
  using(var pipe=new NamedPipeServerStream(name,PipeDirection.InOut,1,PipeTransmissionMode.Byte,PipeOptions.Asynchronous)){
   try{
    child=Process.Start(new ProcessStartInfo(Process.GetCurrentProcess().MainModule.FileName,"--toy-child "+name){UseShellExecute=false,CreateNoWindow=true});
    var connected=pipe.BeginWaitForConnection(null,null);if(!connected.AsyncWaitHandle.WaitOne(10000))throw new Exception("toy pipe timeout");pipe.EndWaitForConnection(connected);
    var reader=new StreamReader(pipe);var writer=new StreamWriter(pipe){AutoFlush=true};uint address=unchecked((uint)Int32.Parse(reader.ReadLine()));uint pid=(uint)child.Id;
    var memory=new NativeMemory(child.Handle);if(memory.Read(address,6)[0]!=0xb8)throw new Exception("toy process read");bool blocked=false;try{memory.Write(address,new byte[]{0x90});}catch(InvalidDataException){blocked=true;}if(!blocked||memory.Read(address,6)[0]!=0xb8)throw new Exception("toy executable write guard");
    if(!Native.DebugActiveProcess(pid))throw new Exception("toy attach "+Marshal.GetLastWin32Error());attached=true;
    if(!Native.DebugSetProcessKillOnExit(false))throw new Exception("toy kill-on-exit");bool first=true;var clock=Stopwatch.StartNew();
    while(!restored&&clock.Elapsed.TotalSeconds<12){
     if(!Native.WaitForDebugEvent(ev,100))continue;uint kind=(uint)Marshal.ReadInt32(ev),epid=(uint)Marshal.ReadInt32(ev,4),tid=(uint)Marshal.ReadInt32(ev,8),status=0x10002;events++;
     try{
      if(kind==2||kind==3){
       using(var h=new ThreadHandle(tid))using(var c=new Registers(h.Handle)){
        if((c[24]&255)!=0)throw new Exception("toy unexpected debug registers");var saved=new uint[6];for(int i=0;i<4;i++){saved[i]=c[4+4*i];c[4+4*i]=address+(uint)i*16;}saved[4]=c[20];saved[5]=c[24];original[tid]=saved;c[20]=0;c[24]=0x455;c.Save(h.Handle);
       }
      }
      if(kind==3||kind==6){IntPtr f=Marshal.ReadIntPtr(ev,12);if(f!=IntPtr.Zero)Native.CloseHandle(f);}
      if(kind==4)original.Remove(tid);
      if(kind==1){uint code=(uint)Marshal.ReadInt32(ev,12),ip=(uint)Marshal.ReadInt32(ev,24);
       if(code==0x80000004&&ip>=address&&ip<address+64){using(var h=new ThreadHandle(tid))using(var c=new Registers(h.Handle)){hits.Add(c[184]);c[20]=0;c[192]|=0x10000;c.Save(h.Handle);}}
       else if(code==0x80000003&&first)first=false;else status=0x80010001;
      }
      if(hits.Count==4){
       foreach(uint id in new List<uint>(original.Keys)){
        try{using(var h=new ThreadHandle(id)){
         uint exitCode;if(Native.GetExitCodeThread(h.Handle,out exitCode)&&exitCode!=259){original.Remove(id);continue;}
         uint[] old=original[id];using(var c=new Registers(h.Handle)){for(int i=0;i<4;i++)c[4+4*i]=old[i];c[20]=old[4];c[24]=old[5];c.Save(h.Handle);}
         using(var c=new Registers(h.Handle)){for(int i=0;i<4;i++)if(c[4+4*i]!=old[i])throw new Exception("toy register readback");if(c[24]!=old[5])throw new Exception("toy DR7 readback");}
         original.Remove(id);
        }}catch{ /* The queued EXIT_THREAD event resolves terminating threads. */ }
       }
       restored=original.Count==0;
      }
     }finally{if(!Native.ContinueDebugEvent(epid,tid,status))throw new Exception("toy continue");}
    }
    if(hits.Count!=4)throw new Exception("toy four hardware sites not all reached");
    if(!Native.DebugActiveProcessStop(pid))throw new Exception("toy detach");attached=false;
    writer.WriteLine("STOP");if(!child.WaitForExit(5000)||child.ExitCode!=0)throw new Exception("toy failed after detach");
    if(!restored)throw new Exception("toy debug register restoration mismatch");
    Console.WriteLine(new JavaScriptSerializer().Serialize(new{status="PASS_SYNTHETIC_PROCESS_ONLY",hardwareSites=hits.Count,liveMemoryReadVerified=true,executableWriteRejected=true,debugEvents=events,debugRegistersRestored=restored,detached=true,childExitedNormally=true,shogun2Attached=false,engineHookExecuted=false}));return 0;
   }catch(Exception e){Console.WriteLine(new JavaScriptSerializer().Serialize(new{status="FAIL",error=e.ToString(),shogun2Attached=false}));return 1;}
   finally{
    if(attached&&child!=null)Native.DebugActiveProcessStop((uint)child.Id);
    if(child!=null){if(!child.HasExited){try{child.Kill();child.WaitForExit(2000);}catch{}}child.Dispose();}
    Marshal.FreeHGlobal(ev);
   }
  }
 }
}
}
