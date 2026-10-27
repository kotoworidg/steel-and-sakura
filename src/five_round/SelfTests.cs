// Tests the same memory adapter used by the native host. Never runs the game.
using System;
using System.Collections.Generic;
using System.IO;
using System.Web.Script.Serialization;
namespace SteelSakura {
 public sealed class FixtureMemory:IMemory {
  public readonly Dictionary<uint,byte[]> Blocks=new Dictionary<uint,byte[]>();
  public readonly List<uint> Writes=new List<uint>();
  public byte[] Read(uint p,int n){foreach(var b in Blocks)if(p>=b.Key&&(ulong)p+(uint)n<=(ulong)b.Key+(uint)b.Value.Length){byte[] r=new byte[n];Array.Copy(b.Value,(int)(p-b.Key),r,0,n);return r;}throw new IOException("unmapped fixture read "+p.ToString("X"));}
  public void Raw(uint p,byte[] data){foreach(var b in Blocks)if(p>=b.Key&&(ulong)p+(uint)data.Length<=(ulong)b.Key+(uint)b.Value.Length){Array.Copy(data,0,b.Value,(int)(p-b.Key),data.Length);return;}throw new IOException("unmapped fixture write");}
  public void U(uint p,uint value){Raw(p,BitConverter.GetBytes(value));}
  public void F(uint p,float value){Raw(p,BitConverter.GetBytes(value));}
  public void Write(uint p,byte[] data){if(data.Length!=1||data[0]>1)throw new Exception("adapter exceeded one Boolean byte");Writes.Add(p);Raw(p,data);}
 }
 public sealed class EngineFixture {
  public const uint Action=0x100000,Actor=0x200000,Unit=0x300000,Key=0x400000,Current=0x500000,Context=0x600000,Metadata=0x700000,Record=0x800000;
  public readonly FixtureMemory M=new FixtureMemory();public readonly List<string> Events=new List<string>();public readonly List<int> NativeTimes=new List<int>();
  public readonly BurstController C;public bool RejectNextExtra,NoDebit;
  public EngineFixture(bool kneel=false){
   foreach(uint p in new[]{Action,Actor,Unit,Key,Current,Context,Metadata,Record})M.Blocks[p]=new byte[p==Unit?4096:2048];
   M.U(Action+4,Actor);M.U(Action+0x14,Context);M.U(Action+0x38,0x900000);M.U(Action+0x88,7);
   M.U(Actor+0x214,Unit);M.U(Actor+0x474,Current);M.U(Actor+0x1f8,3);M.U(Current,7);M.U(Context+8,0xa00000);
   M.U(Unit+0x28,Key);M.Raw(Key,System.Text.Encoding.Unicode.GetBytes(BurstController.UnitKey+"\0"));M.Raw(Record,System.Text.Encoding.Unicode.GetBytes(BurstController.BulletKey+"\0"));M.F(Unit+0xf78,40);
   M.F(Metadata+0x90,kneel?0:.05f);M.F(Metadata+0x98,.5f);M.Raw(Metadata+0x94,new byte[]{1});M.Raw(Metadata+0x9c,new byte[]{1});
   C=new BurstController(M,true,(name,value)=>Events.Add(name)){VersionVerified=true};
  }
  public float Ammo{get{return Mem.F(M,Unit+0xf78);}}
  public void Tick(int ms){
   M.U(Actor+0x1d8,(uint)(ms/100));C.Enter(Action,Metadata);
   for(uint slot=0;slot<2;slot++){
    byte flag=M.Read(Action+0x6c+slot,1)[0];float marker=Mem.F(M,Metadata+0x90+slot*8);
    if(flag!=0||ms+0.001<marker*1000||Ammo<1)continue;
    M.Raw(Action+0x6c+slot,new byte[]{1});
    // Native request construction/validation happens before the pre-debit boundary.
    if(slot==0&&RejectNextExtra&&NativeTimes.Count>0){RejectNextExtra=false;continue;}
    if(C.BeforeFire(Action,slot,Record,0)){
     if(!NoDebit)M.F(Unit+0xf78,Ammo-1);NativeTimes.Add(ms);C.AfterFire(Action,slot,Record,0);
    }
   }
   byte[] flags=M.Read(Action+0x6c,3);M.Raw(Action+0x6e,new byte[]{(byte)(flags[0]==1&&flags[1]==1?1:0)});C.Leave(Action,flags[0]==1&&flags[1]==1);
  }
  public void Run(){foreach(int ms in new[]{100,200,300,400,500})Tick(ms);}
 }
 public static class SelfTests {
  static readonly List<string> Cases=new List<string>();static int assertions;
  static void Assert(bool value,string why){assertions++;if(!value)throw new Exception(why);}
  static void Test(string name,Action test){test();Cases.Add(name);}
  static void OnlyPrimaryWrites(EngineFixture f){foreach(uint p in f.M.Writes)Assert(p==EngineFixture.Action+0x6c,"write outside primary flag");}
  public static int Run(){try{
   Test("five native emissions with actual adapter flag writes",()=>{var f=new EngineFixture();f.Run();Assert(f.NativeTimes.Count==5&&f.Ammo==35,"five/debit");Assert(f.Events.Contains("five-native-emissions-accounted"),"native five record");Assert(f.M.Writes.Count==3,"exactly three re-arms");OnlyPrimaryWrites(f);});
   Test("kneeling first marker",()=>{var f=new EngineFixture(true);foreach(int ms in new[]{0,100,200,300,500})f.Tick(ms);Assert(f.NativeTimes.Count==5&&f.Ammo==35,"kneeling five");OnlyPrimaryWrites(f);});
   Test("repeating native actions",()=>{var f=new EngineFixture();f.Run();f.M.Raw(EngineFixture.Action+0x6c,new byte[]{0,0,0});f.Run();Assert(f.NativeTimes.Count==10&&f.Ammo==30,"two five-round cycles");OnlyPrimaryWrites(f);});
   Test("correct identity does not use obsolete unit+B9C",()=>{var f=new EngineFixture();f.M.U(EngineFixture.Unit+0xb9c,0xdeadbeef);f.Run();Assert(f.NativeTimes.Count==5,"observed identity path");});
   Test("foreign unit remains native two-shot",()=>{var f=new EngineFixture();f.M.Raw(EngineFixture.Key,new byte[]{0});f.Run();Assert(f.NativeTimes.Count==2&&f.M.Writes.Count==0,"foreign scope");});
   Test("wrong private projectile remains native",()=>{var f=new EngineFixture();f.M.Raw(EngineFixture.Record,new byte[]{0});f.Run();Assert(f.NativeTimes.Count==2&&f.M.Writes.Count==0,"projectile scope");});
   Test("unknown private marker window cannot activate",()=>{var f=new EngineFixture();f.M.F(EngineFixture.Metadata+0x98,.7f);f.Run();Assert(f.M.Writes.Count==0,"marker compatibility");});
   Test("no callback means no timer emission",()=>{var f=new EngineFixture();f.Tick(100);Assert(f.NativeTimes.Count==1&&f.M.Writes.Count==0,"no off-thread scheduler");});
   Test("selected animation change cancels additions",()=>{var f=new EngineFixture();f.Tick(100);f.M.U(EngineFixture.Current,8);f.Run();Assert(f.M.Writes.Count==0,"animation changed");});
   Test("target change cancels additions",()=>{var f=new EngineFixture();f.Tick(100);f.M.U(EngineFixture.Action+0x38,0xb00000);f.Tick(200);f.Tick(500);Assert(f.M.Writes.Count==0,"target changed");});
   Test("clock rewind without fresh native action cancels",()=>{var f=new EngineFixture();f.Tick(100);f.Tick(0);f.Tick(200);f.Tick(500);Assert(f.M.Writes.Count==0,"clock rewind");});
   Test("native request rejection is not retried",()=>{var f=new EngineFixture();f.Tick(100);f.RejectNextExtra=true;foreach(int ms in new[]{200,300,400,500})f.Tick(ms);Assert(f.NativeTimes.Count==2&&f.M.Writes.Count==1,"no rejected-request retry");OnlyPrimaryWrites(f);});
   Test("unexpected ammunition debit stops additions",()=>{var f=new EngineFixture();f.NoDebit=true;f.Run();Assert(f.M.Writes.Count==0&&!f.Events.Contains("five-native-emissions-accounted"),"no invented accounting proof");});
   Test("ammunition exhaustion",()=>{var f=new EngineFixture();f.M.F(EngineFixture.Unit+0xf78,1);f.Run();Assert(f.NativeTimes.Count==1&&f.Ammo==0&&f.M.Writes.Count==0,"finite native ammo");});
   Test("coarse native updates do not dump catch-up shots",()=>{var f=new EngineFixture();f.Tick(100);f.Tick(500);Assert(f.NativeTimes.Count==2&&!f.Events.Contains("five-native-emissions-accounted"),"coarse update short burst");});
   Test("attach midway through burst waits for fresh action",()=>{var f=new EngineFixture();f.M.Raw(EngineFixture.Action+0x6c,new byte[]{1});f.Run();Assert(f.NativeTimes.Count==1&&f.M.Writes.Count==0,"no assumed earlier shots");});
   Test("controller stop preserves normal native action lifetime",()=>{var f=new EngineFixture();f.Tick(100);f.C.Expire();f.Run();Assert(f.NativeTimes.Count==2&&f.M.Writes.Count==0,"stop no additions");});
   Test("pending unconsumed reset restored at paused cleanup",()=>{var f=new EngineFixture();f.Tick(100);f.M.U(EngineFixture.Actor+0x1d8,2);f.C.Enter(EngineFixture.Action,EngineFixture.Metadata);Assert(f.M.Read(EngineFixture.Action+0x6c,1)[0]==0,"rearmed");f.C.Expire();f.C.CleanupPaused();Assert(f.M.Read(EngineFixture.Action+0x6c,3)[0]==1&&f.M.Read(EngineFixture.Action+0x6e,1)[0]==0,"only primary restored");OnlyPrimaryWrites(f);});
   Test("version mismatch",()=>{var f=new EngineFixture();f.C.VersionVerified=false;f.Run();Assert(f.NativeTimes.Count==2&&f.M.Writes.Count==0,"version guard");});
   Test("explicit mutation switch off",()=>{var f=new EngineFixture();f.C.Writes=false;f.Run();Assert(f.NativeTimes.Count==2&&f.M.Writes.Count==0,"mutation guard");});
   Test("unterminated identity key",()=>{var f=new EngineFixture();int length=System.Text.Encoding.Unicode.GetByteCount(BurstController.UnitKey);f.M.Raw(EngineFixture.Key+(uint)length,new byte[]{1});f.Run();Assert(f.M.Writes.Count==0,"exact terminated identity");});
   Test("many independent firing actions stay bounded",()=>{for(int i=0;i<200;i++){var f=new EngineFixture();f.Run();Assert(f.NativeTimes.Count==5&&f.C.States.Count==0,"independent native action cleanup");OnlyPrimaryWrites(f);}});
   int projectileCases=ProjectileEvidenceTests.Run();
   Console.WriteLine(new JavaScriptSerializer().Serialize(new{projectileEvidenceCases=projectileCases,status="PASS_SHARED_LIVE_ADAPTER_FIXTURES_GAME_NOT_RUN",cases=Cases,assertions=assertions,gameAttached=false,gameplayVerified=false,onlyPrimaryFlagWritten=true}));return 0;
  }catch(Exception e){Console.Error.WriteLine(e.ToString());return 1;}}
 }
}
