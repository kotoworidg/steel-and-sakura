// Native projectile evidence. Reads real request/manager/object fields; never writes game memory.
// Registration, movement and component-integrity damage are deliberately separate observations.
using System;
using System.Collections.Generic;
using System.IO;
namespace SteelSakura {
 public sealed class PendingProjectile {
  public uint Action,Actor,Unit,Definition,Request,Battle,Manager,Count,Serial;
  public bool Extra;public float[] Origin;public float Scale;
 }
 public sealed class ObservedProjectile {
  public uint Pointer,Serial,Definition,Actor,Manager,Battle;public bool Extra,Moved;
  public float[] Origin;public float Scale;
 }
 sealed class PendingDamage {
  public ObservedProjectile Shot;public uint Component,Stack,Before,Expected,Computed,Owner;
 }
 public sealed class ProjectileEvidence {
  readonly IMemory memory;readonly Action<string,object> log;
  readonly Dictionary<uint,ObservedProjectile> objects=new Dictionary<uint,ObservedProjectile>();
  readonly Dictionary<uint,PendingDamage> damage=new Dictionary<uint,PendingDamage>();
  uint lastTick=UInt32.MaxValue;public uint SelectedActor;public int Registered,Attempts;
  public bool OrdinaryDamage,AdditionalDamage;
  public const int Limit=32;
  public bool Finished {get{return OrdinaryDamage&&AdditionalDamage;}}
  public bool LimitReached {get{return Registered>=Limit||Attempts>=64;}}
  public ProjectileEvidence(IMemory m,Action<string,object> l){memory=m;log=l;}
  uint U(uint p){return Mem.U(memory,p);}float F(uint p){return Mem.F(memory,p);}
  static void Require(bool ok,string why){if(!ok)throw new InvalidDataException(why);}
  static bool Pointer(uint p){return p>=0x10000&&(p&3)==0;}
  float[] Vector(uint p){var v=new[]{F(p),F(p+4),F(p+8)};foreach(float x in v)Require(Mem.Fin(x),"nonfinite vector");return v;}
  static double Distance(float[] a,float[] b){double n=0;for(int i=0;i<3;i++){double d=(double)a[i]-b[i];n+=d*d;}return n;}
  public PendingProjectile Begin(uint action,uint actor,uint unit,uint definition,uint request,bool extra){
   Require(!LimitReached,"bounded projectile sample is full");Attempts++;
   Require(Pointer(action)&&Pointer(actor)&&Pointer(unit)&&Pointer(definition)&&Pointer(request),"invalid native request pointer");
   Require(SelectedActor==0||SelectedActor==actor,"different sampled actor");
   var p=new PendingProjectile{Action=action,Actor=actor,Unit=unit,Definition=definition,Request=request,Extra=extra};
   Require(U(request+4)==definition&&U(request+0x18)==actor,"request definition/shooter mismatch");
   Require(U(definition+0x4c)==1,"native definition is not a single projectile");
   p.Scale=F(request+0x34);float baseDamage=F(definition+0x78);
   Require(Mem.Fin(p.Scale)&&p.Scale>0&&Mem.Fin(baseDamage)&&baseDamage>=1,"request has no positive native damage input");
   p.Origin=Vector(request+8);uint context=U(action+0x14);Require(Pointer(context),"missing action context");
   p.Battle=U(context+8);Require(Pointer(p.Battle),"missing battle");p.Manager=U(p.Battle+0xe8);Require(Pointer(p.Manager),"missing native projectile manager");
   p.Count=U(p.Manager+0x10);p.Serial=U(p.Manager+0x4c);Require(p.Count<=65536&&p.Serial<UInt32.MaxValue-64,"manager bounds/serial wrap");
   log("projectile-request",new{action=action,actor=actor,extra=extra,request=request,definition=definition,battle=p.Battle,manager=p.Manager,beforeCount=p.Count,beforeSerial=p.Serial,origin=p.Origin,damageScale=p.Scale,baseDamage=baseDamage});
   return p;
  }
  public bool Complete(PendingProjectile p){
   if(p==null)return false;
   try{
    Require(Registered<Limit,"registered projectile sample is full");
    Require((SelectedActor==0&&!p.Extra)||SelectedActor==p.Actor,"first sample must be ordinary and subsequent samples must share its actor");
    Require(U(U(p.Action+0x14)+8)==p.Battle&&U(p.Battle+0xe8)==p.Manager,"native manager ownership changed");
    uint count=U(p.Manager+0x10),serial=U(p.Manager+0x4c),array=U(p.Manager+0x14);
    Require(count>=p.Count&&count-p.Count<=64&&serial>=p.Serial&&serial-p.Serial<=64,"ambiguous native vector/serial change");
    Require(count>p.Count&&serial>p.Serial&&Pointer(array),"no registered projectile after firing path");
    ObservedProjectile match=null;int matches=0;
    for(uint i=p.Count;i<count;i++){
     uint obj=U(array+i*4);Require(Pointer(obj),"invalid appended object");uint id=U(obj+4);
     if(id<p.Serial||id>=serial||U(obj+8)!=p.Definition||U(obj+0x1c)!=p.Actor)continue;
     var origin=Vector(obj+0x0c);if(Distance(origin,p.Origin)>0.000001)continue;
     var velocity=Vector(obj+0x8c);Require(Distance(velocity,new float[3])>0.000001,"registered projectile has zero launch velocity");
     float scale=F(obj+0x38);Require(Mem.Fin(scale)&&scale>0&&Math.Abs(scale-p.Scale)<0.0001,"registered damage input differs");
     Vector(obj+0x80); // It may already have moved after native registration; immutable origin is the identity check.
     matches++;match=new ObservedProjectile{Pointer=obj,Serial=id,Definition=p.Definition,Actor=p.Actor,Manager=p.Manager,Battle=p.Battle,Extra=p.Extra,Origin=origin,Scale=scale};
    }
    Require(matches==1,"expected one uniquely matched native projectile, found "+matches);
    ObservedProjectile prior;Require(!objects.TryGetValue(match.Pointer,out prior)||prior.Serial!=match.Serial,"duplicate projectile identity");
    objects[match.Pointer]=match;Registered++;if(SelectedActor==0)SelectedActor=p.Actor;
    log("projectile-registered",new{action=p.Action,actor=p.Actor,extra=p.Extra,pointer=match.Pointer,serial=match.Serial,definition=match.Definition,manager=p.Manager,origin=match.Origin,velocity=Vector(match.Pointer+0x8c),damageScale=match.Scale,registered=Registered,damageVerified=false});ObservePosition(match);return true;
   }catch(Exception e){log("projectile-registration-unconfirmed",new{action=p.Action,actor=p.Actor,extra=p.Extra,reason=e.Message});return false;}
  }
  bool Same(ObservedProjectile s){
   return U(s.Battle+0xe8)==s.Manager&&U(s.Pointer+4)==s.Serial&&U(s.Pointer+8)==s.Definition&&U(s.Pointer+0x1c)==s.Actor&&Distance(Vector(s.Pointer+0x0c),s.Origin)<0.000001;
  }
  void ObservePosition(ObservedProjectile s){
   var now=Vector(s.Pointer+0x80);if(!s.Moved&&Distance(now,s.Origin)>0.000001){s.Moved=true;log("projectile-moved",new{pointer=s.Pointer,serial=s.Serial,extra=s.Extra,origin=s.Origin,position=now,retirementByte=memory.Read(s.Pointer+0xc1,1)[0],damageVerified=false});}
  }
  public void Poll(){
   if(objects.Count==0)return;
   var snapshot=new List<ObservedProjectile>(objects.Values);
   try{uint tick=U(snapshot[0].Battle+0x50);if(tick==lastTick)return;lastTick=tick;}catch{return;}
   foreach(var s in snapshot)try{if(!Same(s)){objects.Remove(s.Pointer);log("projectile-no-longer-correlatable",new{pointer=s.Pointer,serial=s.Serial,reason="identity changed; cause unknown"});continue;}ObservePosition(s);}catch{objects.Remove(s.Pointer);log("projectile-no-longer-correlatable",new{pointer=s.Pointer,serial=s.Serial,reason="memory unreadable; cause unknown"});}
  }
  public bool BeforeDamage(uint thread,uint projectile,uint component,uint computedDamage,uint expectedValue,uint stack){
   if(damage.ContainsKey(thread)){Abandon(thread,"nested damage store");return false;}
   ObservedProjectile shot;if(!objects.TryGetValue(projectile,out shot))return false;
   try{
    Require(Same(shot)&&Pointer(component),"damage projectile/component identity changed");ObservePosition(shot);
    uint before=U(component+0x44);Require(before<=Int32.MaxValue&&computedDamage<=Int32.MaxValue,"damage counter out of signed range");
    uint expected=(uint)Math.Max(0,(long)before-computedDamage);Require(expectedValue==expected,"native damage result does not match clamped subtraction");
    // +24 is a candidate owner reference. Do not label this whole-soldier health.
    var pending=new PendingDamage{Shot=shot,Component=component,Stack=stack,Before=before,Expected=expected,Computed=computedDamage,Owner=U(component+0x24)};damage[thread]=pending;
    log("projectile-damage-store-before",new{thread=thread,pointer=projectile,serial=shot.Serial,extra=shot.Extra,component=component,componentOwner=pending.Owner,before=before,computedDamage=computedDamage,expected=expected,moved=shot.Moved});return true;
   }catch(Exception e){log("projectile-damage-unconfirmed",new{pointer=projectile,reason=e.Message});return false;}
  }
  public void AfterDamage(uint thread,uint projectile,uint component,uint stack){
   PendingDamage p;if(!damage.TryGetValue(thread,out p))return;damage.Remove(thread);
   try{
    Require(p.Shot.Pointer==projectile&&p.Component==component&&p.Stack==stack&&Same(p.Shot)&&U(component+0x24)==p.Owner,"damage store owner/stack changed");
    uint after=U(component+0x44);Require(after==p.Expected,"native component counter did not match expected store");
    bool decreased=after<p.Before;
    log("projectile-damage-store-after",new{thread=thread,pointer=projectile,serial=p.Shot.Serial,extra=p.Shot.Extra,component=component,componentOwner=p.Owner,before=p.Before,after=after,decrease=p.Before-after,moved=p.Shot.Moved,componentIntegrityDecreased=decreased,wholeSoldierHealthVerified=false});
    if(decreased&&p.Shot.Moved){if(p.Shot.Extra)AdditionalDamage=true;else OrdinaryDamage=true;}
   }catch(Exception e){log("projectile-damage-unconfirmed",new{pointer=projectile,reason=e.Message});}
  }
  public void Abandon(uint thread,string why){if(damage.Remove(thread))log("projectile-damage-unconfirmed",new{thread=thread,reason=why});}
 }
}
