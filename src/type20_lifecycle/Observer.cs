// Observes one exact Type 20 actor. Never grants permission for extra shots.
using System;
using System.Collections.Generic;
using System.IO;
using System.Web.Script.Serialization;
using SteelSakura.CaptureAdapter;
namespace SteelSakura.ReadTrace {
 public sealed class LifecycleObserver {
  public const string UnitKey=IdentityReader.UnitKey;
  readonly IMemory mem;readonly Action<string,object> log;readonly string session;
  readonly HashSet<string> markers=new HashSet<string>();
  readonly Dictionary<uint,Pending> pending=new Dictionary<uint,Pending>();
  uint actor,unit,key,current;int nativeSamples,watchSamples;bool stopped;
  sealed class Pending {public uint Action,Slot;public float Ammo;}
  sealed class Adapter:IReadMemory {readonly IMemory m;public Adapter(IMemory x){m=x;}public byte[] Read(uint p,int n){return m.Read(p,n);}}
  public uint WatchActor {get{return stopped?0:actor;}}
  public uint WatchCurrent {get{return current;}}
  public bool ExtendedInFlight {get{return false;}}
  public LifecycleObserver(IMemory m,Action<string,object> l,string dir){mem=m;log=l;session=dir;}
  uint U(uint p){byte[] b=mem.Read(p,4);if(b==null||b.Length!=4)throw new IOException("partial read");return BitConverter.ToUInt32(b,0);}
  float F(uint p){return BitConverter.ToSingle(mem.Read(p,4),0);}
  string Block(uint p,int n){try{return Convert.ToBase64String(mem.Read(p,n));}catch{return null;}}
  bool Matches(uint a,out Identity id){return IdentityReader.TryActor(new Adapter(mem),a,IdentityReader.EngineHash,IdentityReader.PackHash,out id);}
  bool StillBound(){Identity id;return actor!=0&&Matches(actor,out id)&&id.Unit==unit&&id.KeyPointer==key;}
  object Snapshot(uint action,uint ip){
   uint selected=U(actor+0x474);current=selected>=0x10000&&(selected&3)==0?selected:0;
   return new{actor=actor,unit=unit,keyPointer=key,instruction=ip,current=current,
    actorBytes=Block(actor,0x600),unitBytes=Block(unit,4096),action=action,
    actionBytes=action==0?null:Block(action,0x100),currentBytes=current==0?null:Block(current,64),
    ammo=F(unit+0xf78),actorStateRaw=U(actor+0x1b4),
    synchronizedDebugBoundary=true,lifeOrderMovementVerified=false};
  }
  public void Before(uint tid,uint action,uint slot,uint record){
   if(stopped||nativeSamples>=400)return;
   uint a=U(action+4);Identity id;if(!Matches(a,out id))return;
   if(actor==0){actor=a;unit=id.Unit;key=id.KeyPointer;log("actor-bound",new{tid=tid,actor=actor,unit=unit,keyPointer=key,identity=UnitKey,authorizesExtraShots=false});}
   if(a!=actor)return;
   if(!StillBound()){Expire();log("binding-lost",new{actor=actor,unit=unit});return;}
   if(pending.ContainsKey(tid)){pending.Remove(tid);log("pair-incomplete",new{tid=tid,action=action,reason="another pre-debit arrived before acknowledgement"});}
   pending[tid]=new Pending{Action=action,Slot=slot,Ammo=F(unit+0xf78)};
   log("native-before",new{tid=tid,slot=slot,projectile=record,snapshot=Snapshot(action,0)});
  }
  public void After(uint tid,uint action,uint slot){
   Pending p;if(!pending.TryGetValue(tid,out p)||p.Action!=action||p.Slot!=slot)return;
   pending.Remove(tid);if(!StillBound()){Expire();log("binding-lost",new{actor=actor,unit=unit});return;}
   float after=F(unit+0xf78);nativeSamples++;
   log("native-after",new{tid=tid,slot=slot,before=p.Ammo,after=after,delta=p.Ammo-after,snapshot=Snapshot(action,0),
    accountingLimit="shared unit counter; other engine threads can run between the two debug stops"});
  }
  public void Watch(uint tid,uint mask,uint ip,uint image){
   if(stopped||watchSamples++>=1000)return;
   if(!StillBound()){Expire();log("binding-lost",new{actor=actor,unit=unit});return;}
   log("watched-write",new{tid=tid,debugStatusMask=mask,writerNextInstruction=ip,writerNextRva=ip>=image?ip-image:0,
    nearbyCode=ip>=16?Block(ip-16,48):null,snapshot=Snapshot(0,ip),
    observation="hardware write watchpoint; raw change, no inferred Stop/Move/death label"});
  }
  public void Poll(){
   // Markers label command intent only. They do not prove native order semantics.
   if(String.IsNullOrEmpty(session)||!Directory.Exists(Path.Combine(session,"markers")))return;
   foreach(string p in Directory.GetFiles(Path.Combine(session,"markers"),"*.json"))if(markers.Add(p)){
    string raw=File.ReadAllText(p);if(raw.Length>4096)throw new IOException("oversized marker");
    object value=new JavaScriptSerializer().DeserializeObject(raw);log("command-intent-marker",value);
   }
  }
  public void Expire(){stopped=true;current=0;}
 }
}
