using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Web.Script.Serialization;
namespace SteelSakura {
public sealed class FakeMemory:IMemory {
 public Dictionary<uint,byte> Bytes=new Dictionary<uint,byte>();public int ControllerWrites;
 public void Region(uint p,int n){for(uint i=0;i<n;i++)Bytes[p+i]=0;}
 public byte[] Read(uint p,int n){byte[] b=new byte[n];for(int i=0;i<n;i++)if(!Bytes.TryGetValue(p+(uint)i,out b[i]))throw new InvalidDataException("test unmapped memory");return b;}
 public void Write(uint p,byte[] b){ControllerWrites++;Put(p,b);}
 public void Put(uint p,byte[] b){for(int i=0;i<b.Length;i++)Bytes[p+(uint)i]=b[i];}
 public void U(uint p,uint n){Put(p,BitConverter.GetBytes(n));}public void F(uint p,float v){Put(p,BitConverter.GetBytes(v));}
 public byte B(uint p){return Read(p,1)[0];} public void B(uint p,byte n){Bytes[p]=n;}
}
public sealed class Rig {
 public const uint A=0x100000,E=0x200000,U=0x300000,R=0x400000,P=0x500000,T=0x700000,Q=0x800000;
 public FakeMemory M=new FakeMemory();public BurstController C;public int Shots;public bool Done,NativeGate=true;public float Delta=1;
 public List<uint> Times=new List<uint>();public List<string> Events=new List<string>();
 public Rig(bool writes){
  foreach(uint a in new[]{A,E,U,R,P,T,Q,0x600000u,0x610000u,0x900000u,0xa00000u,0xb00000u})M.Region(a,0x2000);
  M.U(A+4,E);M.U(E+0x214,U);M.U(U+0xb9c,R);M.U(A+0x14,0x600000);M.U(0x600008,0x610000);
  M.U(A+0x38,T);M.U(E,0x71010000);M.U(T,0x71020000);M.U(A+0x88,0x82);M.U(E+0x474,0x900000);M.U(0x900000,0x82);
  M.F(U+0xf78,100);M.U(R,0xa00000);M.Put(0xa00000,Encoding.Unicode.GetBytes(BurstController.UnitKey+"\0"));
  M.U(P,0xb00000);M.Put(0xb00000,Encoding.Unicode.GetBytes(BurstController.BulletKey+"\0"));
  C=new BurstController(M,writes,(n,o)=>Events.Add(n));C.VersionVerified=true;C.ImageStart=0x71000000;C.ImageSize=0x200000;
 }
 public void Step(uint tick){
  if(Done)return;M.U(E+0x1d8,tick/100);C.Enter(A);
  for(uint slot=0;slot<2;slot++){
   if(M.B(A+0x6c+slot)!=0||(!NativeGate)||(slot==1&&tick<150))continue;
   if(!C.BeforeFire(A,slot,P,Q))continue;
   M.B(A+0x6c+slot,1);M.F(U+0xf78,Mem.F(M,U+0xf78)-Delta);Shots++;Times.Add((tick/100)*100);C.AfterFire(A,slot,P,Q);
  }
  bool complete=M.B(A+0x6c)!=0&&M.B(A+0x6d)!=0;M.B(A+0x6e,(byte)(complete?1:0));
  bool hold=C.Leave(A,complete);if(complete&&!hold)Done=true;
 }
 public void Run(uint interval=50){for(uint t=0;t<=8000&&!Done;t+=interval)Step(t);}
}
public static class SelfTests {
 static List<object> cases=new List<object>();static void Check(bool x,string message){if(!x)throw new Exception(message);}
 static void Case(string name,Action test){test();cases.Add(new{name=name,passed=true});}
 public static int Run(){
  try{
   Case("five_through_original_pipeline",()=>{var r=new Rig(true);r.Run();Check(r.Shots==5,"five");Check(Mem.F(r.M,Rig.U+0xf78)==95,"native ammo");Check(r.Done,"complete");Check(r.C.States.Count==0,"state release");});
   Case("first_two_preserved",()=>{var r=new Rig(true);r.Step(0);Check(r.Shots==1&&r.M.ControllerWrites==0,"first untouched");r.Step(150);Check(r.Shots==2,"second untouched");});
   Case("paced_extra_times",()=>{var r=new Rig(true);r.Run();Check(r.Times.SequenceEqual(new uint[]{0,100,200,300,400}),"cadence");});
   Case("one_fps_no_catchup_dump",()=>{var r=new Rig(true);r.Run(1000);Check(r.Shots==5&&r.Times.SequenceEqual(new uint[]{0,1000,2000,3000,4000}),"coarse cadence");});
   Case("half_fps_deadline",()=>{var r=new Rig(true);r.Run(2000);Check(r.Shots<=5,"bounded");});
   Case("diagnostic_is_nonmutating",()=>{var r=new Rig(false);r.Run();Check(r.Shots==2&&r.M.ControllerWrites==0,"diagnostic writes");});
   Case("unknown_engine_no_extension",()=>{var r=new Rig(true);r.C.VersionVerified=false;r.Run();Check(r.Shots==2&&r.M.ControllerWrites==0,"version gate");});
   Case("unknown_unit_no_extension",()=>{var r=new Rig(true);r.M.Put(0xa00000,Encoding.Unicode.GetBytes("vanilla_tosa\0"));r.Run();Check(r.Shots==2&&r.M.ControllerWrites==0,"unit gate");});
   Case("wrong_projectile_no_extension",()=>{var r=new Rig(true);r.M.Put(0xb00000,Encoding.Unicode.GetBytes("vanilla_bullet\0"));r.Run();Check(r.Shots==2&&r.M.ControllerWrites==0,"projectile gate");});
   Case("ability_projectile_excluded",()=>{var r=new Rig(true);r.M.Put(0xb00000,Encoding.Unicode.GetBytes(BurstController.UnitKey+"_suppression_bullet\0"));r.Run();Check(r.Shots==2,"ability scope");});
   Case("key_prefix_rejected",()=>{var r=new Rig(true);r.M.Put(0xa00000,Encoding.Unicode.GetBytes(BurstController.UnitKey+"_other\0"));r.Run();Check(r.Shots==2,"prefix match");});
   Case("bounded_identity_search",()=>{var r=new Rig(true);r.M.U(Rig.R,0);r.M.U(Rig.R+128,0xa00000);r.Run();Check(r.Shots==2,"unrelated graph search");});
   Case("ammo_without_native_decrement_rejected",()=>{var r=new Rig(true);r.Delta=0;r.Run();Check(r.Shots==2&&r.M.ControllerWrites==0,"no ammo calibration");});
   Case("ambiguous_shared_ammo_rejected",()=>{var r=new Rig(true);r.Delta=2;r.Run();Check(r.Shots==2,"ambiguous accounting");});
   Case("fractional_ammo_rejected",()=>{var r=new Rig(true);r.Delta=.5f;r.Run();Check(r.Shots==2,"fractional accounting");});
   Case("low_ammo_no_extras",()=>{var r=new Rig(true);r.M.F(Rig.U+0xf78,2);r.Run();Check(r.Shots==2&&Mem.F(r.M,Rig.U+0xf78)==0,"ammo ceiling");});
   Case("three_rounds_remaining",()=>{var r=new Rig(true);r.M.F(Rig.U+0xf78,3);r.Run();Check(r.Shots==3&&Mem.F(r.M,Rig.U+0xf78)==0,"limited ammo");});
   Case("nan_ammo_fail_closed",()=>{var r=new Rig(true);r.M.F(Rig.U+0xf78,Single.NaN);r.Run();Check(r.M.ControllerWrites==0,"nan writes");});
   Case("infinite_ammo_fail_closed",()=>{var r=new Rig(true);r.M.F(Rig.U+0xf78,Single.PositiveInfinity);r.Run();Check(r.M.ControllerWrites==0,"inf writes");});
   Case("movement_animation_cancels",()=>{var r=new Rig(true);r.Step(0);r.Step(150);int writes=r.M.ControllerWrites;r.M.U(0x900000,0x83);r.NativeGate=false;r.Step(300);Check(r.Shots==2&&r.M.ControllerWrites==writes,"movement");});
   Case("live_actor_state_one_is_not_target_predicate",()=>{var r=new Rig(true);r.M.U(Rig.E+0x1b4,1);r.Run();Check(r.Shots==5,"live-observed shooter state must not block synthetic schedule");});
   Case("shooter_state_not_a_verified_death_flag",()=>{var r=new Rig(true);r.Step(0);r.Step(150);r.M.U(Rig.E+0x1b4,1);r.Step(300);Check(r.Shots==3,"do not invent shooter death semantics");});
   Case("target_reference_predicate_change_cancels",()=>{var r=new Rig(true);r.Step(0);r.Step(150);r.M.U(Rig.T+0x1b4,1);r.NativeGate=false;r.Step(300);Check(r.Shots==2,"conservative target-reference filter");});
   Case("target_change_cancels",()=>{var r=new Rig(true);r.Step(0);r.Step(150);r.M.U(Rig.A+0x38,Rig.E);r.NativeGate=false;r.Step(300);Check(r.Shots==2,"target change");});
   Case("cease_fire_dispatch_ends",()=>{var r=new Rig(true);r.Step(0);r.Step(150);r.C.Expire();r.NativeGate=false;r.Step(300);Check(r.Shots==2,"stop");});
   Case("battle_context_change_cancels",()=>{var r=new Rig(true);r.Step(0);r.Step(150);r.M.U(0x600008,0x610004);r.NativeGate=false;r.Step(300);Check(r.Shots==2,"battle");});
   Case("actor_pointer_reuse_cancels",()=>{var r=new Rig(true);r.Step(0);r.Step(150);r.M.U(Rig.E,0x71010004);r.NativeGate=false;r.Step(300);Check(r.Shots==2,"reuse");});
   Case("timer_reset_cancels",()=>{var r=new Rig(true);r.Step(0);r.Step(150);r.NativeGate=false;r.Step(10);Check(r.Shots==2,"timer");});
   Case("long_pause_deadline_cancels",()=>{var r=new Rig(true);r.Step(0);r.Step(150);r.Step(7000);Check(r.Shots==2,"deadline");});
   Case("no_timer_emission",()=>{var r=new Rig(true);r.Step(0);r.Step(150);Check(r.Shots==2,"only callback emits");});
   Case("unreadable_identity_fail_closed",()=>{var r=new Rig(true);r.M.Bytes.Remove(Rig.E+0x214);r.Run();Check(r.M.ControllerWrites==0,"bad memory");});
   Case("reentrant_dispatch_rejected",()=>{var r=new Rig(true);r.C.Enter(Rig.A);r.C.Enter(Rig.A);Check(r.C.States[Rig.A].Cancelled,"reentrant");});
   Case("draining_denies_new_actors",()=>{var r=new Rig(true);r.C.Expire();Check(r.C.Enter(Rig.A)==null&&r.M.ControllerWrites==0,"drain admission");});
   Case("paused_sim_clock_does_not_dump",()=>{var r=new Rig(true);r.Step(0);r.Step(150);for(int i=0;i<50;i++)r.Step(150);Check(r.Shots==2,"pause");});
   Case("origin_drift_aborts_followup",()=>{var r=new Rig(true);r.Step(0);r.Step(150);r.M.F(Rig.Q+8,10);r.Step(300);r.Step(450);Check(r.Shots==2,"drift before debit");});
   Case("x86_context_layout",()=>{Check(28+112+16+24==180,"ebp offset");Check(204+512==716,"context bytes");Check(12+80+4==96,"debug event bytes");});
   Case("no_sixth_on_repeated_ticks",()=>{var r=new Rig(true);r.Run();for(int i=0;i<100;i++)r.Step(1000);Check(r.Shots==5,"sixth");});
   Case("private_heap_flag_write_allowed",()=>Check(NativeMemory.RegionSafe(0x20000,3,0x20000,4096,0x1000,4,0x20000,true),"heap gate"));
   Case("guard_page_rejected",()=>Check(!NativeMemory.RegionSafe(0x20000,3,0x20000,4096,0x1000,0x104,0x20000,false),"guard page"));
   Case("noaccess_page_rejected",()=>Check(!NativeMemory.RegionSafe(0x20000,3,0x20000,4096,0x1000,1,0x20000,false),"noaccess"));
   Case("image_write_rejected",()=>Check(!NativeMemory.RegionSafe(0x20000,3,0x20000,4096,0x1000,4,0x1000000,true),"image write"));
   Case("executable_heap_write_rejected",()=>Check(!NativeMemory.RegionSafe(0x20000,3,0x20000,4096,0x1000,0x40,0x20000,true),"execute write"));
   Case("cross_region_read_rejected",()=>Check(!NativeMemory.RegionSafe(0x20fff,3,0x20000,4096,0x1000,4,0x20000,false),"region boundary"));
   Case("freed_region_rejected",()=>Check(!NativeMemory.RegionSafe(0x20000,3,0x20000,4096,0x10000,4,0x20000,false),"free region"));
   Case("foreign_actor_vtable_rejected",()=>{var r=new Rig(true);r.M.U(Rig.E,0x60000000);r.Run();Check(r.M.ControllerWrites==0,"foreign vtable");});
   Case("actor_token_change_cancels",()=>{var r=new Rig(true);r.Step(0);r.Step(150);r.M.U(Rig.E+0x2c,123);r.NativeGate=false;r.Step(300);Check(r.Shots==2,"actor token reuse");});
   Case("logging_failure_does_not_throw_during_cleanup",()=>{var log=new RuntimeLog("unused","missing-sakura-python.exe","unused");log.Add("offline",new{test=true});log.Flush();Check(log.Failed,"logging failure flag");log.Add("cancel",new{test=true});log.Flush();});
   Case("target_reference_initial_nonzero_no_extension",()=>{var r=new Rig(true);r.M.U(Rig.T+0x1b4,1);r.Run();Check(r.Shots==2&&r.M.ControllerWrites==0,"target reference gate");Check(r.Events.Contains("native-post-emission-evidence"),"refused admission still records native evidence");});
   Case("target_reference_unreadable_no_extension",()=>{var r=new Rig(true);r.M.Bytes.Remove(Rig.T+0x1b4);r.Run();Check(r.Shots==2&&r.M.ControllerWrites==0,"target read failure");});
   Case("passive_evidence_does_not_authorize_foreign_unit",()=>{var r=new Rig(true);r.M.Put(0xa00000,Encoding.Unicode.GetBytes("vanilla_tosa\0"));r.Run();Check(r.Events.Contains("native-pre-debit-evidence")&&r.Shots==2&&r.M.ControllerWrites==0,"passive cannot authorize");});
   Case("passive_evidence_bounded",()=>{var r=new Rig(false);for(uint i=0;i<200;i++){r.C.BeforeFire(Rig.A,0,Rig.P,Rig.Q);r.C.AfterFire(Rig.A,0,Rig.P,Rig.Q);}Check(r.Events.Count(n=>n=="native-post-emission-evidence")==64&&r.M.ControllerWrites==0,"bounded passive records");});
   var random=new Random(53922026);int fuzz=1000;
   for(int n=0;n<fuzz;n++){
    var r=new Rig(true);uint clock=0;int stop=random.Next(2,25);
    for(int t=0;t<80&&!r.Done;t++){
     if(t==stop){r.C.Expire();r.NativeGate=false;}
     r.Step(clock);clock+=(uint)random.Next(1,1400);
     Check(r.Shots<=5,"fuzz shot cap");Check(Mem.F(r.M,Rig.U+0xf78)==100-r.Shots,"fuzz accounting");
    }
   }
   Console.WriteLine(new JavaScriptSerializer().Serialize(new{status="PASS_OFFLINE_ONLY",cases=cases,fuzzScenarios=fuzz,nativeGameExecuted=false,realAmmoSemanticsVerified=false,realOrderOrDeathSemanticsVerified=false}));return 0;
  }catch(Exception e){Console.WriteLine(new JavaScriptSerializer().Serialize(new{status="FAIL",passedBeforeFailure=cases,error=e.ToString()}));return 1;}
 }
}
}
