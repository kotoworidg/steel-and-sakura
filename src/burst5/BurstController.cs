// Steel & Sakura Burst5 experiment. No game DLL patching or injected payload.
using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
namespace SteelSakura {
public interface IMemory { byte[] Read(uint address,int count); void Write(uint address,byte[] data); }
public static class Mem {
 public static uint U(IMemory m,uint p){return BitConverter.ToUInt32(m.Read(p,4),0);}
 public static float F(IMemory m,uint p){return BitConverter.ToSingle(m.Read(p,4),0);}
 public static bool Fin(float f){return !Single.IsNaN(f)&&!Single.IsInfinity(f);}
 public static bool Key(IMemory m,uint root,string expected){
  // Bounded direct record-header/string-wrapper discovery; no global memory search.
  if(root<0x10000)return false;
  var candidates=new HashSet<uint>(); candidates.Add(root);
  try{for(uint i=0;i<32;i+=4)candidates.Add(U(m,root+i));}catch{return false;}
  var first=new List<uint>(candidates);
  foreach(uint a in first){if(a<0x10000)continue;try{for(uint j=0;j<12;j+=4)candidates.Add(U(m,a+j));}catch{}}
  byte[] ascii=Encoding.ASCII.GetBytes(expected+"\0"), wide=Encoding.Unicode.GetBytes(expected+"\0");
  foreach(uint a in candidates){if(a<0x10000)continue;foreach(byte[] needle in new[]{ascii,wide}){try{var b=m.Read(a,needle.Length);bool same=true;for(int k=0;k<b.Length;k++)if(b[k]!=needle[k]){same=false;break;}if(same)return true;}catch{}}}
  return false;
 }
}
public sealed class Sample {
 public uint Action,Actor,Unit,UnitRecord,Battle,Animation,Target,Vtable,TargetVtable;
 public uint Tick,TimerVariant,EntityToken,TargetReferenceState; public float Ammo;
 public string Fingerprint {get{return String.Join(":",new[]{Actor,Unit,UnitRecord,Battle,Animation,Target,Vtable,TargetVtable,TimerVariant,EntityToken});}}
}
public sealed class BurstState {
 public uint Action; public Sample Last; public string Fingerprint;
 public int Shots,AmmoSamples,BeforeAttemptShots,LastHoldLogged=-1; public float LastAmmo; public uint Started,Due,LastTick;
 public bool Identity,Cancelled,Extended,Attempt,InOriginal; public string Reason="native baseline";
 public float[] Origin;
}
public sealed class BurstController {
 public const string UnitKey="steel_sakura_type20_suppressive_test";
 public const string BulletKey=UnitKey+"_bullet";
 public readonly Dictionary<uint,BurstState> States=new Dictionary<uint,BurstState>();
 readonly IMemory memory; readonly Action<string,object> log;
 readonly Dictionary<uint,float> passiveAmmo=new Dictionary<uint,float>(); int passivePairs;
 void ObserveNativeBefore(uint action,uint slot,uint record){
  if(passivePairs>=64||passiveAmmo.Count>=128)return;
  try{uint actor=Mem.U(memory,action+4),unit=Mem.U(memory,actor+0x214);float ammo=Mem.F(memory,unit+0xf78);passiveAmmo[action]=ammo;
   log("native-pre-debit-evidence",new{action=action,slot=slot,actor=actor,target=Probe(action+0x38),actorStateEvidence=Probe(actor+0x1b4),targetStateEvidence=Probe(Probe(action+0x38)+0x1b4),unit=unit,unitRecord=Probe(unit+0xb9c),projectileRecord=record,unitProof=Mem.Key(memory,Probe(unit+0xb9c),UnitKey),projectileProof=Mem.Key(memory,record,BulletKey),ammoCandidate=ammo});
  }catch{log("native-evidence-unreadable",new{action=action});}
 }
 void ObserveNativeAfter(uint action,uint slot){
  float before;if(!passiveAmmo.TryGetValue(action,out before))return;passiveAmmo.Remove(action);passivePairs++;
  try{uint actor=Mem.U(memory,action+4),unit=Mem.U(memory,actor+0x214);float after=Mem.F(memory,unit+0xf78);
   log("native-post-emission-evidence",new{action=action,slot=slot,ammoBeforeCandidate=before,ammoAfterCandidate=after,deltaCandidate=before-after,authorizesExtension=false});
  }catch{log("native-evidence-unreadable",new{action=action});}
 }
 public bool Writes; public bool VersionVerified; public bool Stopping; public uint ImageStart,ImageSize; public const uint Interval=100, MaxDuration=6000;
 public BurstController(IMemory m,bool writes,Action<string,object> logger){memory=m;Writes=writes;log=logger;}
 public uint Probe(uint address){try{return Mem.U(memory,address);}catch{return 0;}}
 public string Header(uint p){try{return BitConverter.ToString(memory.Read(p,64));}catch{return "unreadable";}}
 public Sample ReadSample(uint a){
  var x=new Sample();x.Action=a;x.Actor=Mem.U(memory,a+4);x.Unit=Mem.U(memory,x.Actor+0x214);
  x.Animation=Mem.U(memory,a+0x88);uint current=Mem.U(memory,x.Actor+0x474);
  if(current==0||Mem.U(memory,current)!=x.Animation)throw new InvalidDataException("native animation/action mismatch");
  x.EntityToken=Mem.U(memory,x.Actor+0x2c)&0xffff;uint rawTick=Mem.U(memory,x.Actor+0x1d8);if(rawTick>UInt32.MaxValue/100)throw new InvalidDataException("native clock overflow");x.Tick=rawTick*100;x.TimerVariant=Mem.U(memory,x.Actor+0x1f8);
  x.Target=Mem.U(memory,a+0x38);x.Vtable=Mem.U(memory,x.Actor);
  if(x.Target==0||x.Actor==0||x.Unit==0)throw new InvalidDataException("missing actor/unit/target");
  // RVA 3D44B4 passes action+2C, not the shooter, to helper 3A6630.
  // The helper reads wrapper+0C == action+38 (target), then target+1B4.
  // Its result is request metadata, not a native firing permission or health flag.
  // Retain a conservative target-reference filter; never apply it to the shooter.
  x.TargetReferenceState=Mem.U(memory,x.Target+0x1b4);
  if(x.TargetReferenceState!=0)throw new InvalidDataException("conservative target-reference predicate refused");
  x.TargetVtable=Mem.U(memory,x.Target);if(ImageSize==0||x.Vtable<ImageStart||(ulong)x.Vtable>=(ulong)ImageStart+ImageSize||x.TargetVtable<ImageStart||(ulong)x.TargetVtable>=(ulong)ImageStart+ImageSize)throw new InvalidDataException("entity vtable outside verified engine image");
  x.UnitRecord=Mem.U(memory,x.Unit+0xb9c);x.Battle=Mem.U(memory,Mem.U(memory,a+0x14)+8);
  x.Ammo=Mem.F(memory,x.Unit+0xf78);if(!Mem.Fin(x.Ammo)||x.Ammo<0||x.Ammo>1000000)throw new InvalidDataException("unverified ammo value");
  return x;
 }
 public void Cancel(BurstState s,string why){if(!s.Cancelled){s.Cancelled=true;s.Reason=why;log("cancel",new{action=s.Action,shots=s.Shots,reason=why});}}
 bool Valid(BurstState s,Sample x){
  if(s.Cancelled)return false;
  if(s.Fingerprint!=x.Fingerprint){Cancel(s,"identity/target/battle/generation fingerprint changed");return false;}
  if(x.Tick<s.LastTick||x.Tick-s.Started>MaxDuration){Cancel(s,"clock reset or burst deadline");return false;}
  s.LastTick=x.Tick;s.Last=x;return true;
 }
 bool Eligible(BurstState s,Sample x){return !Stopping&&Writes&&VersionVerified&&s.Identity&&!s.Cancelled&&s.AmmoSamples>=2&&s.Shots>=2&&s.Shots<5&&x.Ammo>=1&&Valid(s,x);}
 public BurstState Enter(uint action){
  Sample x;try{x=ReadSample(action);}catch(Exception e){BurstState old;if(States.TryGetValue(action,out old))Cancel(old,e.Message);uint actor=Probe(action+4);log("gate-refused",new{action=action,reason=e.Message,actor=actor,unit=Probe(actor+0x214),target=Probe(action+0x38),selected=Probe(action+0x88),current=Probe(Probe(actor+0x474)),actorStateEvidence=Probe(actor+0x1b4),targetStateEvidence=Probe(Probe(action+0x38)+0x1b4)});return null;}
  BurstState s;
  if(!States.TryGetValue(action,out s)){
   if(Stopping||States.Count>=512)return null;
   s=new BurstState{Action=action,Last=x,Fingerprint=x.Fingerprint,LastAmmo=x.Ammo,Started=x.Tick,LastTick=x.Tick};States[action]=s;
   log("actor",new{action=action,actor=x.Actor,unit=x.Unit,record=x.UnitRecord,target=x.Target,animation=x.Animation,ammo=x.Ammo});
  }
  if(s.InOriginal){Cancel(s,"reentrant original dispatch");return s;}
  if(!Valid(s,x))return s;
  // A unit-wide counter can change due to other men between callbacks. Rebaseline at entry.
  s.LastAmmo=x.Ammo;s.InOriginal=true;s.Attempt=false;
  if(Eligible(s,x)&&x.Tick>=s.Due){
   // The engine itself invoked this current action. Reuse its complete native pipeline.
   // Preserve slot one; clear only the primary fired flag and completion for one extra shot.
   memory.Write(action+0x6c,new byte[]{0,1,0});s.BeforeAttemptShots=s.Shots;s.Attempt=true;s.Extended=true;
   log("extra-attempt",new{action=action,next=s.Shots+1,clock=x.Tick});
  }
  return s;
 }
 public bool BeforeFire(uint action,uint slot,uint record=0,uint request=0){
  ObserveNativeBefore(action,slot,record);
  BurstState s;if(!States.TryGetValue(action,out s))return true;
  try{
   var x=ReadSample(action);
   // This breakpoint is AFTER native request validation, BEFORE ammo debit/spawn.
   // Rebaseline immediately before each native debit, even on the original pair.
   s.LastAmmo=x.Ammo;
   if(!s.Attempt)return true;
   if(!Eligible(s,x)||slot!=0||record==0||!Mem.Key(memory,record,BulletKey)){Cancel(s,"additional shot identity/accounting gate failed");return false;}
   if(request==0){Cancel(s,"fresh native request unavailable");return false;}
   float[] origin=new[]{Mem.F(memory,request+8),Mem.F(memory,request+12),Mem.F(memory,request+16)};
   double distance=0;for(int i=0;i<3;i++){if(!Mem.Fin(origin[i]))throw new InvalidDataException("invalid current origin");if(s.Origin!=null)distance+=(origin[i]-s.Origin[i])*(origin[i]-s.Origin[i]);}
   if(distance>.5625){Cancel(s,"movement/origin drift before ammo debit");return false;}
   return true;
  }catch(Exception e){if(!s.Attempt)return true;Cancel(s,e.Message);return false;}
 }
 public void AfterFire(uint action,uint slot,uint record,uint request){
  ObserveNativeAfter(action,slot);
  BurstState s;if(!States.TryGetValue(action,out s)||s.Cancelled)return;
  try{
   var x=ReadSample(action);if(!Valid(s,x))return;
   bool unitProof=Mem.Key(memory,x.UnitRecord,UnitKey),projectileProof=Mem.Key(memory,record,BulletKey);bool key=unitProof&&projectileProof;
   // Ability-switched projectiles are intentionally excluded from this five-shot test.
   if(!key){log("identity-refused",new{action=action,unitRecord=x.UnitRecord,projectileRecord=record,unitProof=unitProof,projectileProof=projectileProof,unitHeader=Header(x.UnitRecord),projectileHeader=Header(record)});Cancel(s,"exact unit/projectile key pair unresolved");return;}
   s.Identity=true;
   float delta=s.LastAmmo-x.Ammo;
   if(Math.Abs(delta-1.0f)>.001f){Cancel(s,"native ammo delta not exactly one");return;}
   float[] origin=new[]{Mem.F(memory,request+8),Mem.F(memory,request+12),Mem.F(memory,request+16)};
   foreach(float v in origin)if(!Mem.Fin(v))throw new InvalidDataException("invalid shot origin");
   if(s.Origin!=null){double d=0;for(int i=0;i<3;i++)d+=(origin[i]-s.Origin[i])*(origin[i]-s.Origin[i]);if(d>.5625){Cancel(s,"origin displacement: movement/animation ambiguity");return;}}
   s.Origin=origin;s.LastAmmo=x.Ammo;s.AmmoSamples++;s.Shots++;s.Due=x.Tick+Interval;
   log("shot",new{action=action,actor=x.Actor,slot=slot,shot=s.Shots,ammo=x.Ammo,delta=delta,clock=x.Tick,extra=s.Attempt});
   if(s.Shots>5)Cancel(s,"shot ceiling exceeded");
  }catch(Exception e){Cancel(s,"post-shot accounting: "+e.Message);}
 }
 // Returns whether to override AL to zero and retain this still-selected native action.
 public bool Leave(uint action,bool complete){
  BurstState s;if(!States.TryGetValue(action,out s))return false;s.InOriginal=false;
  try{
   Sample x=ReadSample(action);
   if(s.Attempt&&s.Shots==s.BeforeAttemptShots)Cancel(s,"no validated emission");
   if(complete&&Eligible(s,x)){
    memory.Write(action+0x6e,new byte[]{0});s.Extended=true;
    if(s.LastHoldLogged!=s.Shots){log("hold-native-action",new{action=action,shots=s.Shots,due=s.Due});s.LastHoldLogged=s.Shots;}return true;
   }
  }catch(Exception e){Cancel(s,e.Message);}
  if(s.Extended&&s.Cancelled){
   // Only at the live wrapper return, never through a stale timer callback.
   try{var x=ReadSample(action);if(x.Fingerprint==s.Fingerprint)memory.Write(action+0x6c,new byte[]{1,1,1});}catch{}
  }
  if(complete||s.Cancelled||s.Shots>=5){log("burst-end",new{action=action,shots=s.Shots,reason=s.Reason});States.Remove(action);}
  return false;
 }
 public void Expire(){Stopping=true;foreach(var s in States.Values)Cancel(s,"cease-fire/movement/death/battle/host stop: draining");}
 public bool ExtendedInFlight {get{foreach(var s in States.Values)if(s.Extended&&s.InOriginal)return true;return false;}}
}
}
