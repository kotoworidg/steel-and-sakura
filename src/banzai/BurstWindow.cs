// Offline development core. No process access, native calls, or game-memory writes.
// Native lifecycle proof is mandatory. Unknown means NO additional shot.
using System;
using System.Collections.Generic;
namespace SteelSakura.Banzai {
 public enum Proof { Unknown, Rejected, Verified }
 public sealed class Frame {
  public ulong Actor, Unit, Action, Generation, Battle, Target, Weapon;
  public long TimeMs;
  public Proof Version, Identity, ActiveFireOrder, Alive, Stationary, BattleActive;
  public bool NativeDispatch, SameAnimation, SecondaryFired;
  public bool Permitted {
   get { return Actor!=0 && Unit!=0 && Action!=0 && Generation!=0 && Battle!=0 && Target!=0 && Weapon!=0 &&
    Version==Proof.Verified && Identity==Proof.Verified && ActiveFireOrder==Proof.Verified &&
    Alive==Proof.Verified && Stationary==Proof.Verified && BattleActive==Proof.Verified &&
    NativeDispatch && SameAnimation; }
  }
  public string IdentityToken { get { return String.Join(":",new[]{Actor,Unit,Action,Generation,Battle,Target,Weapon}); } }
 }
 public sealed class BurstWindow {
  // A future adapter must get these from a validated private animation, not a wall timer.
  readonly long first,second,spacing; readonly string identity;
  public int ConfirmedShots {get;private set;}
  public int ExtraAttempts {get;private set;}
  public bool Cancelled {get;private set;}
  public bool Complete {get;private set;}
  public string Reason {get;private set;}
  long lastTime, lastEmission=-1; bool pending;
  public BurstWindow(Frame f,long firstMarker,long secondMarker,long interval) {
   if(firstMarker<0 || interval<100 || secondMarker-firstMarker<interval*4 || secondMarker>6000)
    throw new ArgumentException("invalid bounded firing window");
   first=firstMarker;second=secondMarker;spacing=interval;identity=f.IdentityToken;lastTime=f.TimeMs;
   if(!f.Permitted)Cancel("unverified identity/lifecycle/compatibility");
  }
  public void Cancel(string reason){Cancelled=true;pending=false;Reason=reason;}
  bool Check(Frame f) {
   if(Cancelled||Complete)return false;
   if(!f.Permitted || f.IdentityToken!=identity){Cancel("identity, lifecycle, order or native dispatch changed");return false;}
   if(f.TimeMs<lastTime || f.TimeMs>second+1000){Cancel("clock rewind or firing window expired");return false;}
   lastTime=f.TimeMs;return true;
  }
  // Called only INSIDE a fresh invocation of the engine's original firing action.
  // A true result authorizes one primary-flag reset, never completion retention.
  // There is deliberately no method for overriding a return value or calling spawn.
  public bool TryPrimaryRepeat(Frame f,float ammo) {
   if(!Check(f))return false;
   if(pending){Cancel("previous emission has not been acknowledged");return false;}
   if(f.SecondaryFired || f.TimeMs>=second || ConfirmedShots<1 || ConfirmedShots>=4)return false;
   if(Single.IsNaN(ammo)||Single.IsInfinity(ammo)||ammo<1){Cancel("insufficient or invalid ammo");return false;}
   // No catch-up volley: at most one repeat per native simulation tick.
   if(f.TimeMs<first || f.TimeMs-lastEmission<spacing)return false;
   pending=true;ExtraAttempts++;return true;
  }
  // Called immediately around the original native debit/spawn on the same thread.
  // Never debit ammo here: the native pipeline owns it, including its side effects.
  public void Emitted(Frame f,int slot,float before,float after,bool nativeRequestValid) {
   if(!Check(f))return;
   if(!nativeRequestValid || Single.IsNaN(before)||Single.IsNaN(after)||Single.IsInfinity(before)||Single.IsInfinity(after)||
      before<1||after<0||Math.Abs((before-after)-1)>0.001f){Cancel("native debit/spawn evidence invalid");return;}
   if(slot==0) {
    if(ConfirmedShots==0) {if(pending||f.TimeMs<first){Cancel("invalid initial native shot");return;}}
    else if(!pending || ConfirmedShots>=4 || f.TimeMs>=second || f.TimeMs<=lastEmission){Cancel("unrequested or late repeat");return;}
   } else if(slot==1) {
    if(pending || f.TimeMs<second || ConfirmedShots==0){Cancel("invalid secondary marker");return;}
    Complete=true;
   } else {Cancel("unknown firing slot");return;}
   pending=false;ConfirmedShots++;lastEmission=f.TimeMs;
   if(ConfirmedShots>5){Cancel("shot ceiling");return;}
   if(Complete)Reason=ConfirmedShots==5?"five native emissions observed":"short burst; no catch-up or held action";
  }
  public void EndNativeInvocation() {if(pending)Cancel("native request rejected or emission missing");}
  public void EndAction(){if(!Complete)Cancel("native action ended");}
 }
}
