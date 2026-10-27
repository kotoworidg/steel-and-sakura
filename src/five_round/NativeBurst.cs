// Live native-action adapter. Writes only the current action's primary fired byte.
// It neither retains completed actions nor calls a projectile emitter itself.
using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
namespace SteelSakura {
 public interface IMemory {byte[] Read(uint address,int count);void Write(uint address,byte[] data);}
 public static class Mem {
  public static uint U(IMemory m,uint p){return BitConverter.ToUInt32(m.Read(p,4),0);}
  public static float F(IMemory m,uint p){return BitConverter.ToSingle(m.Read(p,4),0);}
  public static bool Fin(float x){return !Single.IsNaN(x)&&!Single.IsInfinity(x);}
  public static bool ExactWide(IMemory m,uint p,string key){try{byte[] a=m.Read(p,Encoding.Unicode.GetByteCount(key+"\0")),b=Encoding.Unicode.GetBytes(key+"\0");if(a.Length!=b.Length)return false;for(int k=0;k<a.Length;k++)if(a[k]!=b[k])return false;return true;}catch{return false;}}
  public static bool Key(IMemory m,uint root,string key){
   if(root<0x10000)return false;var candidates=new HashSet<uint>{root};
   try{for(uint k=0;k<32;k+=4)candidates.Add(U(m,root+k));}catch{return false;}
   foreach(uint p in new List<uint>(candidates))if(p>=0x10000)try{for(uint k=0;k<12;k+=4)candidates.Add(U(m,p+k));}catch{}
   foreach(uint p in candidates)if(p>=0x10000&&ExactWide(m,p,key))return true;return false;
  }
 }
 public sealed class FireSnapshot {
  public uint Action,Actor,Unit,Key,Animation,Current,Variant,Target,Battle,Metadata,Tick;
  public byte Primary,Secondary,Complete;public float Ammo,First,Last;
  public string Token {get{return String.Join(":",new[]{Actor,Unit,Key,Animation,Current,Variant,Target,Battle,Metadata});}}
 }
 public sealed class BurstState {
  public uint Action;public FireSnapshot Last;public string Token;
  public int Shots,Extras,LastShot=-1,Due,ResetTick;public bool InOriginal,Cancelled,PendingExtra,PendingNative;
  public uint PendingSlot,Record;public float BeforeAmmo;public string Reason;public PendingProjectile Proof;
 }
 public sealed class BurstController {
  public const string UnitKey="steel_sakura_type20_automatic_fire_test";
  public const string BulletKey=UnitKey+"_bullet";
  public const string SuppressionKey="steel_sakura_type20_supported_suppression_bullet";
  public const int Interval=100,MaxDuration=1500;
  public readonly Dictionary<uint,BurstState> States=new Dictionary<uint,BurstState>();
  readonly IMemory memory;readonly Action<string,object> log;readonly ProjectileEvidence evidence;int refusals;
  public bool VersionVerified,Stopping;public uint ImageStart,ImageSize;
  public BurstController(IMemory m,bool writes,Action<string,object> l,ProjectileEvidence proof=null){memory=m;Writes=writes;log=l;evidence=proof;}
  public bool Writes;public bool ExtendedInFlight{get{return false;}}
  public bool TryIdentity(uint actor,out uint unit,out uint key){
   unit=key=0;try{
    if(actor<0x10000||(actor&3)!=0)return false;
    unit=Mem.U(memory,actor+0x214);if(unit<0x10000||(unit&3)!=0)return false;
    key=Mem.U(memory,unit+0x28);if(key<0x10000||(key&1)!=0||!Mem.ExactWide(memory,key,UnitKey))return false;
    return Mem.U(memory,actor+0x214)==unit&&Mem.U(memory,unit+0x28)==key;
   }catch{return false;}
  }
  byte[] Flags(uint a){return memory.Read(a+0x6c,3);}
  FireSnapshot Read(uint a,uint metadata){
   var x=new FireSnapshot{Action=a,Metadata=metadata};x.Actor=Mem.U(memory,a+4);
   if(!TryIdentity(x.Actor,out x.Unit,out x.Key))throw new InvalidDataException("exact actor/unit identity failed");
   x.Animation=Mem.U(memory,a+0x88);x.Current=Mem.U(memory,x.Actor+0x474);
   if(x.Current<0x10000||Mem.U(memory,x.Current)!=x.Animation)throw new InvalidDataException("native selected animation changed");
   x.Variant=Mem.U(memory,x.Actor+0x1f8);x.Target=Mem.U(memory,a+0x38);x.Battle=Mem.U(memory,Mem.U(memory,a+0x14)+8);
   if(x.Target<0x10000||x.Battle<0x10000)throw new InvalidDataException("target or battle context absent");
   x.Tick=Mem.U(memory,x.Actor+0x1d8);
   if(x.Tick>MaxDuration/100)throw new InvalidDataException("native firing window exceeded");
   x.Tick*=100;byte[] flags=Flags(a);x.Primary=flags[0];x.Secondary=flags[1];x.Complete=flags[2];
   if(x.Primary>1||x.Secondary>1||x.Complete>1)throw new InvalidDataException("unexpected native action flags");
   x.Ammo=Mem.F(memory,x.Unit+0xf78);if(!Mem.Fin(x.Ammo)||x.Ammo<0||x.Ammo>1000000)throw new InvalidDataException("invalid shared native ammunition");
   x.First=Mem.F(memory,metadata+0x90);x.Last=Mem.F(memory,metadata+0x98);
   if(memory.Read(metadata+0x94,1)[0]!=1||memory.Read(metadata+0x9c,1)[0]!=1||
      !Mem.Fin(x.First)||!Mem.Fin(x.Last)||Math.Abs(x.Last-.5f)>.001f||
      (Math.Abs(x.First)>.001f&&Math.Abs(x.First-.05f)>.001f))throw new InvalidDataException("private paired-window metadata differs");
   return x;
  }
  bool Same(BurstState s,FireSnapshot x){
   if(s.Token!=x.Token||x.Tick<s.Last.Tick){Cancel(s,"native identity/selection/target/clock changed");return false;}
   s.Last=x;return true;
  }
  bool Projectile(uint p){return Mem.Key(memory,p,BulletKey)||Mem.Key(memory,p,SuppressionKey);}
  public void Cancel(BurstState s,string why){if(!s.Cancelled){s.Cancelled=true;s.Reason=why;log("cancel",new{action=s.Action,shots=s.Shots,reason=why});}}
  public void Enter(uint action,uint metadata){
   // Called at RVA 3D438A, after the original completion/selection guards.
   FireSnapshot x;try{x=Read(action,metadata);}catch(Exception e){BurstState prior;if(States.TryGetValue(action,out prior))Cancel(prior,"current native firing frame no longer matches");try{uint u,k;if(refusals<8&&TryIdentity(Mem.U(memory,action+4),out u,out k)){refusals++;log("admission-refused",new{action=action,reason=e.Message});}}catch{}return;}
   if(evidence!=null){evidence.Poll();if(evidence.LimitReached||evidence.Finished)Stopping=true;if(evidence.SelectedActor!=0&&evidence.SelectedActor!=x.Actor)return;}
   if(Stopping||!VersionVerified||!Writes||x.Complete!=0)return;
   BurstState s;
   if(States.TryGetValue(action,out s)&&!s.InOriginal&&x.Primary==0&&x.Secondary==0&&(x.Tick<s.Last.Tick||s.Cancelled)){States.Remove(action);s=null;}
   if(!States.TryGetValue(action,out s)){
    // Attach midway through an existing burst cannot establish its shot count.
    if(x.Primary!=0||x.Secondary!=0||States.Count>=512)return;
    s=new BurstState{Action=action,Last=x,Token=x.Token};States[action]=s;
   }
   if(s.InOriginal){Cancel(s,"reentrant native action");return;}
   if(!Same(s,x)||s.Cancelled)return;s.InOriginal=true;s.PendingNative=false;
   if(s.Shots>=1&&s.Shots<4&&s.Extras<3&&x.Primary==1&&x.Secondary==0&&x.Complete==0&&
      x.Tick>=s.Due&&x.Tick<500&&x.Ammo>=1){
    // Only a one-byte reset. Native validation, debit, spawn and completion run next.
    memory.Write(action+0x6c,new byte[]{0});s.PendingExtra=true;s.ResetTick=(int)x.Tick;s.Extras++;
    log("primary-rearmed",new{action=action,shot=s.Shots+1,nativeMs=x.Tick});
   }
  }
  public bool BeforeFire(uint action,uint slot,uint record,uint request){
   BurstState s;if(!States.TryGetValue(action,out s)||!s.InOriginal)return true;
   bool extra=slot==0&&s.PendingExtra;
   try{
    var x=Read(action,s.Last.Metadata);
    if(!Same(s,x)||s.Cancelled||Stopping||!Projectile(record)||(s.Record!=0&&s.Record!=record))throw new InvalidDataException("native emission identity changed");
    if(slot>1||x.Ammo<1)throw new InvalidDataException("slot/ammunition unavailable");
    if(extra&&(x.Tick!=s.ResetTick||x.Tick>=500||s.Shots<1||s.Shots>=4))throw new InvalidDataException("extra shot selection/time gate failed");
    s.Proof=evidence==null?null:evidence.Begin(action,x.Actor,x.Unit,record,request,extra);
    s.BeforeAmmo=x.Ammo;s.PendingSlot=slot;s.PendingNative=true;
    if(s.Record==0)s.Record=record;
    return true;
   }catch(Exception e){Cancel(s,e.Message);s.PendingNative=false;return !extra;}
  }
  public void AfterFire(uint action,uint slot,uint record,uint request){
   BurstState s;if(!States.TryGetValue(action,out s)||!s.PendingNative||s.PendingSlot!=slot)return;s.PendingNative=false;
   try{
    var x=Read(action,s.Last.Metadata);
    if(evidence!=null&&!evidence.Complete(s.Proof))throw new InvalidDataException("projectile registration unconfirmed; additions cancelled");
    s.Proof=null;
    if(!Same(s,x)||s.Cancelled||record!=s.Record||Math.Abs((s.BeforeAmmo-x.Ammo)-1)>.001f)throw new InvalidDataException("native debit/spawn pair not confirmed");
    if((int)x.Tick<=s.LastShot)throw new InvalidDataException("multiple shots at one simulation time");
    bool extra=slot==0&&s.PendingExtra;
    if(slot==0&&s.Shots>0&&!extra)throw new InvalidDataException("unscheduled primary dispatch");
    s.PendingExtra=false;s.Shots++;s.LastShot=(int)x.Tick;s.Due=s.LastShot+Interval;
    log(evidence==null?"native-shot-confirmed":"native-path-ammo-debit",new{action=action,actor=x.Actor,unit=x.Unit,slot=slot,shot=s.Shots,nativeMs=x.Tick,extra=extra,ammo=x.Ammo,delta=s.BeforeAmmo-x.Ammo});
    if(s.Shots>5)throw new InvalidDataException("five-shot ceiling exceeded");
    if(slot==1)log(s.Shots==5?(evidence==null?"five-native-emissions-accounted":"five-registered-paths-damage-not-implied"):"short-native-burst",new{action=action,shots=s.Shots,extraAttempts=s.Extras});
   }catch(Exception e){Cancel(s,e.Message);}
  }
  void RestorePending(BurstState s){
   if(!s.PendingExtra)return;
   try{var x=Read(s.Action,s.Last.Metadata);
    if(x.Token==s.Token&&x.Tick==s.ResetTick&&x.Primary==0&&x.Secondary==0&&x.Complete==0){memory.Write(s.Action+0x6c,new byte[]{1});log("unconsumed-rearm-restored",new{action=s.Action});}
   }catch{log("pending-restore-unreadable",new{action=s.Action});}
   s.PendingExtra=false;
  }
  public bool Leave(uint action,bool completedReturn){
   BurstState s;if(!States.TryGetValue(action,out s))return false;
   if(s.PendingExtra){RestorePending(s);Cancel(s,"extra native request rejected or emission missing");}
   s.InOriginal=false;s.Proof=null;s.PendingNative=false;
   try{byte[] flags=Flags(action);if(flags[2]==1||s.Cancelled||s.Shots>=5){log("burst-end",new{action=action,shots=s.Shots,cancelled=s.Cancelled});States.Remove(action);}}
   catch{States.Remove(action);}
   // Never overrides AL or retains the action, even when a burst is short.
   return false;
  }
  public void CleanupPaused(){foreach(var s in States.Values)RestorePending(s);}
  public void Expire(){Stopping=true;foreach(var s in States.Values)Cancel(s,"runtime stop; native actions are not retained");}
 }
}
