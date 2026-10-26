using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Web.Script.Serialization;
namespace SteelSakura.Banzai {
 public static class Offline {
  static int checks;static List<string> cases=new List<string>();
  static void Assert(bool v,string name){checks++;if(!v)throw new Exception(name);}
  static Frame Good(long t=0){return new Frame{Actor=1,Unit=2,Action=3,Generation=4,Battle=5,Target=6,Weapon=7,TimeMs=t,
   Version=Proof.Verified,Identity=Proof.Verified,ActiveFireOrder=Proof.Verified,Alive=Proof.Verified,
   Stationary=Proof.Verified,BattleActive=Proof.Verified,NativeDispatch=true,SameAnimation=true};}
  static BurstWindow Start(Frame f){var b=new BurstWindow(f,100,900,200);f.TimeMs=100;b.Emitted(f,0,40,39,true);return b;}
  static void Test(string name,Action body){body();cases.Add(name);}
  static void RunTests(){
   Test("five sequential native-debit observations; no completion hold",()=>{
    var f=Good();var b=Start(f);float ammo=39;
    foreach(long t in new long[]{300,500,700}){f.TimeMs=t;Assert(b.TryPrimaryRepeat(f,ammo),"repeat due");b.Emitted(f,0,ammo,ammo-1,true);ammo--;b.EndNativeInvocation();}
    f.TimeMs=900;Assert(!b.TryPrimaryRepeat(f,ammo),"final marker must own slot one");b.Emitted(f,1,ammo,ammo-1,true);
    Assert(b.Complete&&!b.Cancelled&&b.ConfirmedShots==5&&b.ExtraAttempts==3,"exact five");
   });
   var changes=new Dictionary<string,Action<Frame>> {
    {"cease-fire",f=>f.ActiveFireOrder=Proof.Rejected},{"unmapped order",f=>f.ActiveFireOrder=Proof.Unknown},
    {"movement",f=>f.Stationary=Proof.Rejected},{"unmapped movement",f=>f.Stationary=Proof.Unknown},
    {"death",f=>f.Alive=Proof.Rejected},{"unmapped life",f=>f.Alive=Proof.Unknown},
    {"battle ended",f=>f.BattleActive=Proof.Rejected},{"identity unknown",f=>f.Identity=Proof.Unknown},
    {"version mismatch",f=>f.Version=Proof.Rejected},{"animation changed",f=>f.SameAnimation=false},
    {"no native callback",f=>f.NativeDispatch=false},{"pointer reused",f=>f.Generation++},
    {"actor changed",f=>f.Actor++},{"unit changed",f=>f.Unit++},{"action changed",f=>f.Action++},
    {"target changed",f=>f.Target++},{"battle changed",f=>f.Battle++},{"weapon changed",f=>f.Weapon++}
   };
   foreach(var item in changes){var change=item;Test(change.Key,()=>{var f=Good();var b=Start(f);f.TimeMs=300;change.Value(f);Assert(!b.TryPrimaryRepeat(f,39)&&b.Cancelled&&b.ExtraAttempts==0,change.Key);});}
   Test("low FPS skips shots rather than catching up",()=>{var f=Good();var b=Start(f);f.TimeMs=900;Assert(!b.TryPrimaryRepeat(f,39),"no overdue volley");b.Emitted(f,1,39,38,true);Assert(b.Complete&&b.ConfirmedShots==2,"short native pair");});
   Test("paused simulation does not emit",()=>{var f=Good();var b=Start(f);for(int i=0;i<200;i++)Assert(!b.TryPrimaryRepeat(f,39),"paused");});
   Test("clock rewind",()=>{var f=Good();var b=Start(f);f.TimeMs=0;Assert(!b.TryPrimaryRepeat(f,39)&&b.Cancelled,"rewind");});
   Test("native rejection cancels remaining extras",()=>{var f=Good();var b=Start(f);f.TimeMs=300;Assert(b.TryPrimaryRepeat(f,39),"armed");b.EndNativeInvocation();f.TimeMs=500;Assert(!b.TryPrimaryRepeat(f,39)&&b.Cancelled,"rejection");});
   Test("action ends without stale timers",()=>{var f=Good();var b=Start(f);b.EndAction();f.TimeMs=300;Assert(!b.TryPrimaryRepeat(f,39),"no after-action shot");});
   Test("ammo zero NaN infinity negative",()=>{foreach(float ammo in new[]{0f,-1f,float.NaN,float.PositiveInfinity}){var f=Good();var b=Start(f);f.TimeMs=300;Assert(!b.TryPrimaryRepeat(f,ammo)&&b.Cancelled,"ammo invalid");}});
   Test("wrong native debit stops further work",()=>{foreach(float after in new[]{39f,37f,float.NaN,float.PositiveInfinity}){var f=Good();var b=Start(f);f.TimeMs=300;Assert(b.TryPrimaryRepeat(f,39),"armed");b.Emitted(f,0,39,after,true);Assert(b.Cancelled,"bad debit");}});
   Test("two soldiers share native unit ammo without double debit",()=>{var a=Good();var z=Good();z.Actor=20;z.Action=30;var ba=Start(a);var bz=Start(z);float ammo=78;foreach(long t in new long[]{300,500,700}){a.TimeMs=z.TimeMs=t;Assert(ba.TryPrimaryRepeat(a,ammo),"a");ba.Emitted(a,0,ammo,ammo-1,true);ammo--;Assert(bz.TryPrimaryRepeat(z,ammo),"b");bz.Emitted(z,0,ammo,ammo-1,true);ammo--;}a.TimeMs=z.TimeMs=900;ba.Emitted(a,1,ammo,ammo-1,true);ammo--;bz.Emitted(z,1,ammo,ammo-1,true);ammo--;Assert(ammo==70&&ba.ConfirmedShots==5&&bz.ConfirmedShots==5,"shared total ten");});
   Test("unknown proof cannot be approved by scheduler",()=>{var f=Good();f.Identity=Proof.Unknown;var b=Start(f);f.TimeMs=300;Assert(!b.TryPrimaryRepeat(f,39)&&b.Cancelled,"unknown proof");});
   var random=new Random(20261024);
   for(int run=0;run<1000;run++){
    var f=Good();var b=Start(f);float ammo=39;long time=100;long prior=100;bool cancel=false;
    while(time<900){time+=random.Next(1,250);f.TimeMs=time;
     if(random.Next(20)==0){f.ActiveFireOrder=Proof.Rejected;cancel=true;}
     bool repeat=b.TryPrimaryRepeat(f,ammo);if(repeat){Assert(!cancel&&time-prior>=200&&time<900,"property spacing/cancel");b.Emitted(f,0,ammo,ammo-1,true);ammo--;prior=time;}
     b.EndNativeInvocation();
    }
    if(!b.Cancelled)b.Emitted(f,1,ammo,ammo-1,true);
    Assert(b.ExtraAttempts<=3&&b.ConfirmedShots<=5,"bounded random schedule");
   }
  }
  static object Replay(string dir){
   var serializer=new JavaScriptSerializer{MaxJsonLength=16*1024*1024};int pairs=0,privateKeys=0,unitKeys=0;var pending=new Dictionary<long,Dictionary<string,object>>();var hashes=new List<object>();
   foreach(string path in Directory.GetFiles(dir,"log-*.json").OrderBy(x=>x)){
    byte[] raw=File.ReadAllBytes(path);using(var sha=System.Security.Cryptography.SHA256.Create())hashes.Add(new{file=path,sha256=BitConverter.ToString(sha.ComputeHash(raw)).Replace("-","")});
    foreach(object value in (object[])serializer.DeserializeObject(System.Text.Encoding.UTF8.GetString(raw))){var row=(Dictionary<string,object>)value;string name=(string)row["name"];
     if(name!="native-pre-debit-evidence"&&name!="native-post-emission-evidence")continue;
     var detail=(Dictionary<string,object>)row["detail"];long action=Convert.ToInt64(detail["action"]);
     if(name=="native-pre-debit-evidence"){pending[action]=detail;if(Convert.ToBoolean(detail["projectileProof"]))privateKeys++;if(Convert.ToBoolean(detail["unitProof"]))unitKeys++;}
     else {Dictionary<string,object> before;if(!pending.TryGetValue(action,out before))throw new Exception("unpaired native sample");pending.Remove(action);
      if(Convert.ToDouble(before["ammoCandidate"])-Convert.ToDouble(detail["ammoAfterCandidate"])!=1)throw new Exception("native delta mismatch");pairs++;
     }
    }
   }
   if(pairs!=64||privateKeys!=64||unitKeys!=0||pending.Count!=0)throw new Exception("captured evidence changed; review required");
   return new{status="CAPTURED_EVIDENCE_ONLY",pairedNativeDebits=pairs,privateProjectileMatches=privateKeys,unitIdentityMatches=unitKeys,liveExtensionAuthorized=false,
    blockedBy=new[]{"unit identity not resolved","active order, life and movement semantics not captured","no native adapter supplied"},sources=hashes};
  }
  public static int Main(string[] args){try{
   object output;if(args.Length==1&&args[0]=="--self-test"){RunTests();output=new{status="PASS_OFFLINE_MODEL_ONLY",cases=cases,assertions=checks,randomSchedules=1000,liveAdapter=false};}
   else if(args.Length==2&&args[0]=="--replay")output=Replay(args[1]);
   else {Console.Error.WriteLine("OFFLINE ONLY. --self-test | --replay <saved session>. This executable cannot attach to or modify the game.");return 2;}
   Console.WriteLine(new JavaScriptSerializer{MaxJsonLength=16*1024*1024}.Serialize(output));return 0;
  }catch(Exception e){Console.Error.WriteLine(e.ToString());return 1;}}
 }
}
