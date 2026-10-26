using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Web.Script.Serialization;
using SteelSakura.Banzai;
namespace SteelSakura.CaptureAdapter {
 public sealed class Memory:IReadMemory {
  public Dictionary<uint,byte[]> Blocks=new Dictionary<uint,byte[]>();public bool Partial;public uint FlipAddress;int flipReads;
  public byte[] Read(uint p,int n){if(p==FlipAddress&&++flipReads>1)return new byte[n];
   foreach(var block in Blocks)if(p>=block.Key&&(ulong)p+(uint)n<=(ulong)block.Key+(uint)block.Value.Length){byte[] b=new byte[Partial?n-1:n];Array.Copy(block.Value,(int)(p-block.Key),b,0,b.Length);return b;}
   throw new IOException("unmapped snapshot");
  }
 }
 public static class Runner {
  static int checks;static List<string> cases=new List<string>();
  static void Assert(bool ok,string label){checks++;if(!ok)throw new Exception(label);}
  static Memory Fixture(){var m=new Memory();m.Blocks[0x100000]=new byte[0x600];m.Blocks[0x200000]=new byte[0x1000];m.Blocks[0x300000]=Encoding.Unicode.GetBytes(IdentityReader.UnitKey+"\0");Put(m.Blocks[0x100000],0x214,0x200000);Put(m.Blocks[0x200000],0x28,0x300000);return m;}
  static void Put(byte[] b,int off,uint value){Array.Copy(BitConverter.GetBytes(value),0,b,off,4);}
  static bool Actor(Memory m,out Identity id){return IdentityReader.TryActor(m,0x100000,IdentityReader.EngineHash,IdentityReader.PackHash,out id);}
  static object Tests(){
   Identity id;var good=Fixture();Assert(Actor(good,out id)&&id.Unit==0x200000&&!id.AuthorizesExtraShots,"correct chain");cases.Add("exact positive chain without extra-shot authority");
   var changes=new Dictionary<string,Action<Memory>>{
    {"wrong unit key",m=>m.Blocks[0x300000][0]=0},
    {"unterminated key",m=>m.Blocks[0x300000][m.Blocks[0x300000].Length-2]=1},
    {"null unit",m=>Put(m.Blocks[0x100000],0x214,0)},
    {"null key",m=>Put(m.Blocks[0x200000],0x28,0)},
    {"unit address overflow",m=>Put(m.Blocks[0x100000],0x214,0xfffffff0)},
    {"unaligned unit",m=>Put(m.Blocks[0x100000],0x214,0x200001)},
    {"partial read",m=>m.Partial=true},
    {"unit pointer changes",m=>m.FlipAddress=0x100214},
    {"key pointer changes",m=>m.FlipAddress=0x200028},
    {"unmapped key",m=>m.Blocks.Remove(0x300000)}
   };
   foreach(var c in changes){var m=Fixture();c.Value(m);Assert(!Actor(m,out id)&&id==null,c.Key);cases.Add(c.Key);}
   Assert(!IdentityReader.TryActor(good,0x100000,"wrong",IdentityReader.PackHash,out id),"wrong engine");cases.Add("engine hash mismatch");
   Assert(!IdentityReader.TryActor(good,0x100000,IdentityReader.EngineHash,"wrong",out id),"wrong pack");cases.Add("pack hash mismatch");
   Assert(Actor(good,out id),"positive again");
   var frame=new Frame{Actor=id.Actor,Unit=id.Unit,Action=1,Generation=1,Battle=1,Target=1,Weapon=1,Version=Proof.Verified,Identity=Proof.Verified,NativeDispatch=true,SameAnimation=true};
   var burst=new BurstWindow(frame,100,900,200);frame.TimeMs=300;Assert(!burst.TryPrimaryRepeat(frame,40)&&burst.Cancelled,"identity cannot bypass unknown lifecycle");cases.Add("identity success cannot authorize unknown order/life/movement");
   return new{cases=cases,assertions=checks,status="PASS_OFFLINE_ONLY"};
  }
  static object Replay(string path){var json=new JavaScriptSerializer{MaxJsonLength=32*1024*1024};var units=new Dictionary<uint,Memory>();int count=0,actors=0;
   foreach(string f in Directory.GetFiles(path,"log-*.json").OrderBy(x=>x))foreach(object item in (object[])json.DeserializeObject(File.ReadAllText(f))){
    var row=(Dictionary<string,object>)item;var d=row["detail"] as Dictionary<string,object>;string name=(string)row["name"];if(d==null)continue;
    if(name=="unit-initial"){
     uint u=Convert.ToUInt32(d["unit"]);var m=new Memory();m.Blocks[u]=Convert.FromBase64String((string)d["bytes0"]);
     foreach(object x in (object[])d["pointers"]){var p=(Dictionary<string,object>)x;if(Convert.ToUInt32(p["offset"])==0x28)m.Blocks[Convert.ToUInt32(p["pointer"])]=Convert.FromBase64String((string)p["bytes"]);}
     Identity id;Assert(IdentityReader.TryUnit(m,u,IdentityReader.EngineHash,IdentityReader.PackHash,out id),"captured unit match");count++;units[u]=m;
    }else if(name=="native-before"&&d["actorBytes"]!=null){uint u=Convert.ToUInt32(d["unit"]),a=Convert.ToUInt32(d["actor"]);Memory m=units[u];m.Blocks[a]=Convert.FromBase64String((string)d["actorBytes"]);Identity id;Assert(IdentityReader.TryActor(m,a,IdentityReader.EngineHash,IdentityReader.PackHash,out id)&&id.Unit==u,"captured actor chain");actors++;}
   }
   Assert(count==12&&actors==4,"pinned sample coverage");return new{unitMatches=count,actorSnapshotMatches=actors,gameExecution=false,lifeOrderMovementVerified=false};
  }
  public static int Main(string[] args){try{if(args.Length!=2||args[0]!="--verify-capture"){Console.WriteLine("Offline snapshot decoder only. --verify-capture <saved session>");return 2;}
   object tests=Tests(),capture=Replay(args[1]);Console.WriteLine(new JavaScriptSerializer().Serialize(new{tests=tests,capture=capture}));return 0;
  }catch(Exception e){Console.Error.WriteLine(e.ToString());return 1;}}
 }
}
