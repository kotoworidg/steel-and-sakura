using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Text;
namespace SteelSakura.ReadTrace {
 public sealed class Observer {
  public const string UnitKey="steel_sakura_type20_automatic_fire_test";
  readonly NativeMemory mem;readonly Action<string,object> log;readonly Stopwatch clock=Stopwatch.StartNew();
  readonly Dictionary<uint,ulong> pairs=new Dictionary<uint,ulong>();
  readonly Dictionary<uint,float> ammo=new Dictionary<uint,float>();
  readonly Dictionary<uint,uint> tracked=new Dictionary<uint,uint>();
  readonly HashSet<uint> capturedUnits=new HashSet<uint>();
  long sampled;int shots,samples;bool stopped;
  public bool ExtendedInFlight{get{return false;}}
  public Observer(NativeMemory m,Action<string,object> l){mem=m;log=l;}
  uint U(uint p){return BitConverter.ToUInt32(mem.Read(p,4),0);}
  float F(uint p){return BitConverter.ToSingle(mem.Read(p,4),0);}
  uint Probe(uint p){try{return U(p);}catch{return 0;}}
  string Block(uint p,int n){try{return Convert.ToBase64String(mem.Read(p,n));}catch{return null;}}
  bool Key(uint root){
   var candidates=new HashSet<uint>();candidates.Add(root);
   for(uint k=0;k<32;k+=4)candidates.Add(Probe(root+k));
   foreach(uint p in new List<uint>(candidates))if(p>=0x10000)for(uint k=0;k<12;k+=4)candidates.Add(Probe(p+k));
   foreach(uint p in candidates)if(p>=0x10000)foreach(var enc in new[]{Encoding.ASCII,Encoding.Unicode}){
    try{byte[] expected=enc.GetBytes(UnitKey+"_bullet\0"),actual=mem.Read(p,expected.Length);bool same=true;for(int k=0;k<actual.Length;k++)if(actual[k]!=expected[k]){same=false;break;}if(same)return true;}catch{}
   }return false;
  }
  // Bounded, game-object-only pointer hints, captured once per identified unit.
  object Pointers(uint unit){var rows=new List<object>();for(uint offset=0;offset<0x1200;offset+=4){uint p=Probe(unit+offset);if(p<0x10000||p>0x7fff0000||(p&3)!=0)continue;string bytes=Block(p,128);if(bytes!=null)rows.Add(new{offset=offset,pointer=p,bytes=bytes});if(rows.Count>=256)break;}return rows;}
  public void Before(uint tid,uint action,uint slot,uint record){
   if(stopped||shots>=400||!Key(record))return;
   uint actor=U(action+4),unit=U(actor+0x214);if(unit==0)return;
   if(tracked.Count<2&&!tracked.ContainsKey(actor))tracked[actor]=unit;
   if(capturedUnits.Add(unit))log("unit-initial",new{elapsedMs=clock.ElapsedMilliseconds,unit=unit,bytes0=Block(unit,4096),bytes1=Block(unit+4096,512),pointers=Pointers(unit),projectile=record,projectileHeader=Block(record,192),identityBasis="exact private projectile key; unit key still unresolved"});
   pairs[tid]=((ulong)action<<32)|unit;ammo[tid]=F(unit+0xf78);
   log("native-before",new{elapsedMs=clock.ElapsedMilliseconds,tid=tid,action=action,actor=actor,unit=unit,slot=slot,projectile=record,ammo=ammo[tid],actorBytes=tracked.ContainsKey(actor)?Block(actor,0x600):null});
  }
  public void After(uint tid,uint action,uint slot){
   ulong pair;if(!pairs.TryGetValue(tid,out pair)||(uint)(pair>>32)!=action)return;
   uint unit=(uint)pair;float after=F(unit+0xf78);log("native-after",new{elapsedMs=clock.ElapsedMilliseconds,tid=tid,action=action,slot=slot,before=ammo[tid],after=after,delta=ammo[tid]-after});pairs.Remove(tid);ammo.Remove(tid);shots++;
  }
  public void Poll(){
   if(stopped||samples>=750||clock.ElapsedMilliseconds-sampled<200)return;sampled=clock.ElapsedMilliseconds;samples++;
   foreach(var actor in tracked){try{
    if(U(actor.Key+0x214)!=actor.Value){log("actor-mapping-changed",new{actor=actor.Key,elapsedMs=sampled});continue;}
    log("poll-nonatomic",new{elapsedMs=sampled,actor=actor.Key,unit=actor.Value,actorBytes=Block(actor.Key,0x600),unitBytes0=Block(actor.Value,4096),unitBytes1=Block(actor.Value+4096,512),mappingStillSame=Probe(actor.Key+0x214)==actor.Value});
   }catch(Exception e){log("poll-unreadable",new{actor=actor.Key,elapsedMs=sampled,error=e.Message});}}
  }
  public void Expire(){stopped=true;}
 }
}
