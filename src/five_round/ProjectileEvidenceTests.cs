// Offline native-layout fixtures for evidence classification. They do not run game code.
using System;
using System.Collections.Generic;
using System.IO;
namespace SteelSakura {
 public static class ProjectileEvidenceTests {
  sealed class Sample {
   public const uint Action=0x110000,Actor=0x220000,Unit=0x330000,Definition=0x440000,Request=0x550000;
   public const uint Context=0x660000,Battle=0x770000,Manager=0x880000,Array=0x990000;
   public const uint Object=0xaa0000,OtherObject=0xab0000,Component=0xbb0000,Victim=0xcc0000,ComponentArray=0xdd0000,Stack=0xee0000;
   public readonly FixtureMemory M=new FixtureMemory();
   public readonly List<string> Events=new List<string>();
   public readonly ProjectileEvidence Evidence;
   public Sample(){
    foreach(uint p in new[]{Action,Actor,Unit,Definition,Request,Context,Battle,Manager,Array,Object,OtherObject,Component,Victim,ComponentArray,Stack})M.Blocks[p]=new byte[0x2000];
    M.U(Action+4,Actor);M.U(Action+0x14,Context);M.U(Actor+0x214,Unit);M.U(Context+8,Battle);
    M.U(Battle+0xe8,Manager);M.U(Battle+0x50,1);M.U(Manager,Battle);M.U(Manager+0x14,Array);M.U(Manager+0x4c,17);
    M.U(Request,Battle);M.U(Request+4,Definition);M.U(Request+0x18,Actor);M.F(Request+0x34,1);
    Vector(Request+8,100,20,5);M.U(Definition+0x4c,1);M.F(Definition+0x78,3);M.F(Unit+0xf78,100);
    M.U(Component+0x24,Victim);M.U(Component+0x44,10);M.U(Victim+0x1194+0x14,1);M.U(Victim+0x1194+0x18,ComponentArray);M.U(ComponentArray,Component);
    Evidence=new ProjectileEvidence(M,(name,value)=>Events.Add(name));Samples.Add(this);
   }
   public void Vector(uint p,float x,float y,float z){M.F(p,x);M.F(p+4,y);M.F(p+8,z);}
   public PendingProjectile Begin(bool extra){return Evidence.Begin(Action,Actor,Unit,Definition,Request,extra);}
   public void Append(uint p){
    uint count=Mem.U(M,Manager+0x10),serial=Mem.U(M,Manager+0x4c);
    M.U(p,Battle);M.U(p+4,serial);M.U(p+8,Definition);M.U(p+0x1c,Actor);M.F(p+0x38,1);
    Vector(p+0x0c,100,20,5);Vector(p+0x74,100,20,5);Vector(p+0x80,100,20,5);Vector(p+0x8c,850,0,0);
    M.U(Array+count*4,p);M.U(Manager+0x10,count+1);M.U(Manager+0x4c,serial+1);
   }
   public void Register(bool extra,uint p){var pending=Begin(extra);Append(p);Assert(Evidence.Complete(pending),"valid native-layout object must register");}
   public void Move(uint p){Vector(p+0x80,185,20,5);M.U(Battle+0x50,Mem.U(M,Battle+0x50)+1);Evidence.Poll();}
   public void Store(uint p){Assert(Evidence.BeforeDamage(1,p,Component,3,7,Stack),"known object's valid damage store must be admitted");M.U(Component+0x44,7);Evidence.AfterDamage(1,p,Component,Stack);}
   public void NoDamage(){Assert(!Evidence.OrdinaryDamage&&!Evidence.AdditionalDamage,"no unproved damage credit");}
  }
  static readonly List<Sample> Samples=new List<Sample>();
  static int cases;
  static void Assert(bool value,string why){if(!value)throw new Exception("projectile evidence: "+why);}
  static void Test(string name,Action run){try{run();foreach(var s in Samples)Assert(s.M.Writes.Count==0,"evidence reader wrote game memory");cases++;}catch(Exception e){throw new Exception("ProjectileEvidenceTests: "+name,e);}}
  static void Invalid(Action run){try{run();}catch(InvalidDataException){return;}throw new Exception("expected InvalidDataException");}
  static void BadObject(string name,Action<Sample> corrupt){Test(name,()=>{var s=new Sample();var pending=s.Begin(false);s.Append(Sample.Object);corrupt(s);Assert(!s.Evidence.Complete(pending),"mismatched object credited");Assert(s.Events.Contains("projectile-registration-unconfirmed"),"missing failed-registration record");Assert(s.Evidence.SelectedActor==0,"failed registration selected actor");s.NoDamage();});}
  public static int Run(){
   Samples.Clear();cases=0;
   Test("ammo debit alone is not object creation",()=>{var s=new Sample();var pending=s.Begin(false);s.M.F(Sample.Unit+0xf78,99);Assert(!s.Evidence.Complete(pending),"debit without append counted");Assert(s.Events.Contains("projectile-registration-unconfirmed"),"no missing-object evidence");s.NoDamage();});
   Test("valid registration does not imply movement or damage",()=>{var s=new Sample();s.Register(false,Sample.Object);Assert(s.Evidence.SelectedActor==Sample.Actor,"sampled actor differs");Assert(s.Events.Contains("projectile-registered"),"registration not recorded");s.Evidence.Poll();Assert(!s.Events.Contains("projectile-moved"),"stationary object considered moving");s.NoDamage();});
   Test("request shooter identity is checked",()=>{var s=new Sample();s.M.U(Sample.Request+0x18,Sample.Victim);Invalid(()=>s.Begin(false));});
   Test("request definition identity is checked",()=>{var s=new Sample();s.M.U(Sample.Request+4,Sample.Definition+4);Invalid(()=>s.Begin(false));});
   Test("shotgun definition cannot pass single-projectile proof",()=>{var s=new Sample();s.M.U(Sample.Definition+0x4c,5);Invalid(()=>s.Begin(false));});
   Test("nonfinite request origin is rejected",()=>{var s=new Sample();s.M.F(Sample.Request+8,Single.NaN);Invalid(()=>s.Begin(false));});
   Test("zero request damage input is rejected",()=>{var s=new Sample();s.M.F(Sample.Request+0x34,0);Invalid(()=>s.Begin(false));});
   BadObject("wrong shooter",s=>s.M.U(Sample.Object+0x1c,Sample.Victim));
   BadObject("wrong definition",s=>s.M.U(Sample.Object+8,Sample.Definition+4));
   BadObject("serial outside constructor interval",s=>s.M.U(Sample.Object+4,16));
   BadObject("initial origin differs",s=>s.M.F(Sample.Object+0x0c,101));
   BadObject("nonfinite launch vector",s=>s.M.F(Sample.Object+0x8c,Single.PositiveInfinity));
   BadObject("zero launch vector",s=>s.Vector(Sample.Object+0x8c,0,0,0));
   Test("position may advance before the post checkpoint",()=>{var s=new Sample();var pending=s.Begin(false);s.Append(Sample.Object);s.M.F(Sample.Object+0x80,101);Assert(s.Evidence.Complete(pending),"already-moving native object rejected");Assert(s.Events.Contains("projectile-moved"),"early movement missing");s.NoDamage();});
   BadObject("object damage scale differs",s=>s.M.F(Sample.Object+0x38,2));
   Test("count advance without serial advance is rejected",()=>{var s=new Sample();var pending=s.Begin(false);s.Append(Sample.Object);s.M.U(Sample.Manager+0x4c,17);Assert(!s.Evidence.Complete(pending),"count alone credited");});
   Test("one uniquely matching object can coexist with unrelated append",()=>{var s=new Sample();var pending=s.Begin(false);s.Append(Sample.Object);s.M.U(Sample.Object+0x1c,Sample.Victim);s.Append(Sample.OtherObject);Assert(s.Evidence.Complete(pending),"unrelated native append confused matching");s.NoDamage();});
   Test("two matching objects are ambiguous",()=>{var s=new Sample();var pending=s.Begin(false);s.Append(Sample.Object);s.Append(Sample.OtherObject);Assert(!s.Evidence.Complete(pending),"ambiguous double creation accepted");});
   Test("duplicate completion cannot create another identity",()=>{var s=new Sample();var pending=s.Begin(false);s.Append(Sample.Object);Assert(s.Evidence.Complete(pending),"first registration");Assert(!s.Evidence.Complete(pending),"duplicate identity accepted");});
   Test("movement is separate from damage",()=>{var s=new Sample();s.Register(false,Sample.Object);s.Move(Sample.Object);Assert(s.Events.Contains("projectile-moved"),"movement missing");s.NoDamage();});
   Test("ordinary damage requires actual before and after store",()=>{var s=new Sample();s.Register(false,Sample.Object);s.Move(Sample.Object);s.Store(Sample.Object);Assert(s.Evidence.OrdinaryDamage&&!s.Evidence.AdditionalDamage,"ordinary damage classification");});
   Test("additional damage does not prove ordinary control",()=>{var s=new Sample();s.Register(false,Sample.Object);s.Register(true,Sample.OtherObject);s.Move(Sample.OtherObject);s.Store(Sample.OtherObject);Assert(s.Evidence.AdditionalDamage&&!s.Evidence.OrdinaryDamage,"additional damage classification");});
   Test("ordinary and additional identities can both be established",()=>{var s=new Sample();s.Register(false,Sample.Object);s.Move(Sample.Object);s.Store(Sample.Object);s.M.U(Sample.Component+0x44,10);s.Register(true,Sample.OtherObject);s.Move(Sample.OtherObject);s.Store(Sample.OtherObject);Assert(s.Evidence.OrdinaryDamage&&s.Evidence.AdditionalDamage,"paired control evidence missing");});
   Test("entry to damage routine without a store does not pass",()=>{var s=new Sample();s.Register(false,Sample.Object);s.Move(Sample.Object);Assert(s.Evidence.BeforeDamage(1,Sample.Object,Sample.Component,3,7,Sample.Stack),"valid before store");s.Evidence.AfterDamage(1,Sample.Object,Sample.Component,Sample.Stack);s.NoDamage();});
   Test("damage decrement without movement does not complete proof",()=>{var s=new Sample();s.Register(false,Sample.Object);s.Store(Sample.Object);s.NoDamage();});
   Test("zero computed damage is not damage credit",()=>{var s=new Sample();s.Register(false,Sample.Object);s.Move(Sample.Object);bool captured=s.Evidence.BeforeDamage(1,Sample.Object,Sample.Component,0,10,Sample.Stack);if(captured)s.Evidence.AfterDamage(1,Sample.Object,Sample.Component,Sample.Stack);s.NoDamage();});
   Test("incorrect native expected result is rejected",()=>{var s=new Sample();s.Register(false,Sample.Object);s.Move(Sample.Object);Assert(!s.Evidence.BeforeDamage(1,Sample.Object,Sample.Component,3,8,Sample.Stack),"invalid subtraction accepted");s.NoDamage();});
   Test("unregistered object cannot earn damage credit",()=>{var s=new Sample();s.Append(Sample.Object);Assert(!s.Evidence.BeforeDamage(1,Sample.Object,Sample.Component,3,7,Sample.Stack),"unregistered projectile accepted");s.NoDamage();});
   Test("projectile pointer reused before damage is rejected",()=>{var s=new Sample();s.Register(false,Sample.Object);s.Move(Sample.Object);s.M.U(Sample.Object+4,99);Assert(!s.Evidence.BeforeDamage(1,Sample.Object,Sample.Component,3,7,Sample.Stack),"reused pointer credited");s.NoDamage();});
   Test("projectile pointer reused across store cannot earn credit",()=>{var s=new Sample();s.Register(false,Sample.Object);s.Move(Sample.Object);Assert(s.Evidence.BeforeDamage(1,Sample.Object,Sample.Component,3,7,Sample.Stack),"before store");s.M.U(Sample.Object+4,99);s.M.U(Sample.Component+0x44,7);s.Evidence.AfterDamage(1,Sample.Object,Sample.Component,Sample.Stack);s.NoDamage();});
   Test("component owner reused across store cannot earn credit",()=>{var s=new Sample();s.Register(false,Sample.Object);s.Move(Sample.Object);Assert(s.Evidence.BeforeDamage(1,Sample.Object,Sample.Component,3,7,Sample.Stack),"before store");s.M.U(Sample.Component+0x24,Sample.Victim+4);s.M.U(Sample.Component+0x44,7);s.Evidence.AfterDamage(1,Sample.Object,Sample.Component,Sample.Stack);s.NoDamage();});
   Test("different stack cannot finish pending store",()=>{var s=new Sample();s.Register(false,Sample.Object);s.Move(Sample.Object);Assert(s.Evidence.BeforeDamage(1,Sample.Object,Sample.Component,3,7,Sample.Stack),"before store");s.M.U(Sample.Component+0x44,7);s.Evidence.AfterDamage(1,Sample.Object,Sample.Component,Sample.Stack+4);s.NoDamage();});
   Test("poll discards reused projectile identity",()=>{var s=new Sample();s.Register(false,Sample.Object);s.M.U(Sample.Object+4,99);s.Move(Sample.Object);Assert(s.Events.Contains("projectile-no-longer-correlatable"),"reuse was not recorded");Assert(!s.Evidence.BeforeDamage(1,Sample.Object,Sample.Component,3,7,Sample.Stack),"retired identity still admitted");s.NoDamage();});
   Test("extra cannot select the first observed actor",()=>{
    var s=new Sample();var pending=s.Begin(true);s.Append(Sample.Object);
    Assert(!s.Evidence.Complete(pending),"first extra selected a control actor");Assert(s.Evidence.SelectedActor==0&&s.Evidence.Registered==0,"extra committed sample identity");
   });
   Test("pending request cannot change the selected actor at completion",()=>{
    var s=new Sample();var first=s.Begin(false);uint otherAction=Sample.Action+0x100,otherRequest=Sample.Request+0x100;
    s.M.U(otherAction+4,Sample.Victim);s.M.U(otherAction+0x14,Sample.Context);s.M.U(Sample.Victim+0x214,Sample.Unit);
    s.M.Raw(otherRequest,s.M.Read(Sample.Request,0x80));s.M.U(otherRequest+0x18,Sample.Victim);
    var second=s.Evidence.Begin(otherAction,Sample.Victim,Sample.Unit,Sample.Definition,otherRequest,false);
    s.Append(Sample.Object);Assert(s.Evidence.Complete(first),"ordinary first object");
    s.Append(Sample.OtherObject);s.M.U(Sample.OtherObject+0x1c,Sample.Victim);
    Assert(!s.Evidence.Complete(second),"pending different actor admitted after selection");Assert(s.Evidence.SelectedActor==Sample.Actor&&s.Evidence.Registered==1,"sample crossed actors");
   });
   Test("pending completions cannot overrun the 32 object bound",()=>{
    var s=new Sample();var pending=new List<PendingProjectile>();
    for(int i=0;i<33;i++){
     uint obj=0x1000000+(uint)i*0x1000;s.M.Blocks[obj]=new byte[0x200];
     s.Vector(Sample.Request+8,100+i,20,5);pending.Add(s.Begin(false));s.Append(obj);
     s.Vector(obj+0x0c,100+i,20,5);s.Vector(obj+0x74,100+i,20,5);s.Vector(obj+0x80,100+i,20,5);
    }
    for(int i=0;i<32;i++)Assert(s.Evidence.Complete(pending[i]),"valid pending sample below bound");
    Assert(!s.Evidence.Complete(pending[32]),"pending object exceeded bound");Assert(s.Evidence.Registered==32,"sample exceeded 32 objects");
   });
   Test("live BurstController cancels extra re-arms after debit-only path",()=>{
    var f=new EngineFixture();const uint battle=0xa00000,manager=0xb00000,array=0xc00000,request=0xd00000,bulletKey=0xe00000;
    foreach(uint address in new[]{battle,manager,array,request,bulletKey})f.M.Blocks[address]=new byte[2048];
    f.M.Raw(EngineFixture.Record,new byte[2048]);f.M.U(EngineFixture.Record,bulletKey);
    f.M.Raw(bulletKey,System.Text.Encoding.Unicode.GetBytes(BurstController.BulletKey+"\0"));
    f.M.U(EngineFixture.Record+0x4c,1);f.M.F(EngineFixture.Record+0x78,3);
    f.M.U(battle+0xe8,manager);f.M.U(manager+0x14,array);f.M.U(manager+0x4c,17);
    f.M.U(request,battle);f.M.U(request+4,EngineFixture.Record);f.M.U(request+0x18,EngineFixture.Actor);f.M.F(request+0x34,1);
    f.M.F(request+8,100);f.M.F(request+12,20);f.M.F(request+16,5);
    var proof=new ProjectileEvidence(f.M,(name,value)=>f.Events.Add(name));
    var controller=new BurstController(f.M,true,(name,value)=>f.Events.Add(name),proof){VersionVerified=true};
    f.M.U(EngineFixture.Actor+0x1d8,1);controller.Enter(EngineFixture.Action,EngineFixture.Metadata);
    f.M.Raw(EngineFixture.Action+0x6c,new byte[]{1});
    Assert(controller.BeforeFire(EngineFixture.Action,0,EngineFixture.Record,request),"ordinary native path refused");
    f.M.F(EngineFixture.Unit+0xf78,39);controller.AfterFire(EngineFixture.Action,0,EngineFixture.Record,request);
    Assert(controller.States[EngineFixture.Action].Cancelled,"debit-only path did not cancel additions");controller.Leave(EngineFixture.Action,false);
    for(uint tick=2;tick<5;tick++){f.M.U(EngineFixture.Actor+0x1d8,tick);controller.Enter(EngineFixture.Action,EngineFixture.Metadata);controller.Leave(EngineFixture.Action,false);}
    Assert(f.M.Writes.Count==0&&!f.Events.Contains("primary-rearmed"),"debit-only path allowed another flag write");
    Assert(proof.Registered==0&&!proof.OrdinaryDamage&&!proof.AdditionalDamage,"debit-only path claimed projectile evidence");
    Assert(f.Events.Contains("projectile-registration-unconfirmed"),"missing registration failure evidence");
   });
   return cases;
  }
 }
}
