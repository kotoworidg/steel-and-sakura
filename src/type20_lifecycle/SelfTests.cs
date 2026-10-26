using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Web.Script.Serialization;
using SteelSakura.CaptureAdapter;
namespace SteelSakura.ReadTrace {
 public static class LifecycleTests {
  sealed class Memory:IMemory {
   public readonly Dictionary<uint,byte[]> Blocks=new Dictionary<uint,byte[]>();
   public byte[] Read(uint p,int n){foreach(var b in Blocks)if(p>=b.Key&&(ulong)p+(uint)n<=(ulong)b.Key+(uint)b.Value.Length){byte[] r=new byte[n];Array.Copy(b.Value,(int)(p-b.Key),r,0,n);return r;}throw new IOException("unmapped");}
   public void Put(uint p,uint v){foreach(var b in Blocks)if(p>=b.Key&&(ulong)p+4<=(ulong)b.Key+(uint)b.Value.Length){Array.Copy(BitConverter.GetBytes(v),0,b.Value,(int)(p-b.Key),4);return;}throw new IOException("unmapped fixture");}
   public void Ammo(float f){Put(0x200f78,BitConverter.ToUInt32(BitConverter.GetBytes(f),0));}
  }
  static Memory Fixture(){var m=new Memory();m.Blocks[0x100000]=new byte[0x600];m.Blocks[0x200000]=new byte[4096];m.Blocks[0x300000]=Encoding.Unicode.GetBytes(IdentityReader.UnitKey+"\0");m.Blocks[0x400000]=new byte[256];m.Blocks[0x500000]=new byte[64];m.Blocks[0x600000]=new byte[64];m.Put(0x100214,0x200000);m.Put(0x200028,0x300000);m.Put(0x100474,0x500000);m.Put(0x400004,0x100000);m.Ammo(40);return m;}
  static void Assert(bool ok,string why){if(!ok)throw new Exception(why);}
  public static object Run(){var cases=new List<string>();var names=new List<string>();var details=new List<object>();Action<string,object> log=(n,d)=>{names.Add(n);details.Add(d);};
   var m=Fixture();var o=new LifecycleObserver(m,log,null);o.Before(1,0x400000,0,0);Assert(o.WatchActor==0x100000&&o.WatchCurrent==0x500000,"identity");cases.Add("exact observed identity chain selects one actor");
   m.Ammo(39);o.After(1,0x400000,0);Assert(names.Contains("native-after"),"pair");cases.Add("paired native observation");
   int count=names.Count;o.After(1,0x400000,0);o.After(2,0x400000,0);Assert(names.Count==count,"unpaired");cases.Add("unpaired or different thread acknowledgement ignored");
   m.Put(0x100474,0x600000);o.Watch(1,8,0x700000,0x700000);Assert(o.WatchCurrent==0x600000,"refresh");cases.Add("selected-animation pointer refreshed after synchronous write");
   string json=new JavaScriptSerializer().Serialize(details);Assert(json.Contains("\"lifeOrderMovementVerified\":false")&&json.Contains("\"authorizesExtraShots\":false"),"no fabricated proof");cases.Add("identity and raw changes never authorize extra shots");
   o.Before(1,0x400000,1,0);o.Before(1,0x400000,1,0);Assert(names.Contains("pair-incomplete"),"reentry");cases.Add("overlapping native pair is recorded as incomplete");
   m.Blocks[0x300000][0]=0;o.After(1,0x400000,1);Assert(names.Contains("binding-lost")&&o.WatchCurrent==0&&o.WatchActor==0,"binding loss");cases.Add("lost identity disarms observed fields");
   m=Fixture();m.Blocks[0x300000][m.Blocks[0x300000].Length-2]=1;names.Clear();o=new LifecycleObserver(m,log,null);o.Before(1,0x400000,0,0);Assert(names.Count==0&&o.WatchActor==0,"termination");cases.Add("unterminated key rejected");
   m=Fixture();m.Blocks.Remove(0x300000);o=new LifecycleObserver(m,log,null);o.Before(1,0x400000,0,0);Assert(o.WatchActor==0,"unmapped key");cases.Add("unreadable key rejected");
   m=Fixture();names.Clear();o=new LifecycleObserver(m,log,null);for(int i=0;i<405;i++){o.Before(1,0x400000,0,0);o.After(1,0x400000,0);}int pairs=names.FindAll(n=>n=="native-after").Count;Assert(pairs==400,"limit");cases.Add("bounded 400 native pair sample budget");
   return new{status="PASS_OBSERVER_FIXTURES_ONLY",cases=cases,gameExecution=false,extraShotsImplemented=false};
  }
 }
}
