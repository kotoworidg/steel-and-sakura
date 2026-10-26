// Strict read-only identity decoder for the observed engine/pack pair.
// A matching identity is NOT proof of life, active orders, generation or stationary state.
using System;
using System.Text;
namespace SteelSakura.CaptureAdapter {
 public interface IReadMemory {byte[] Read(uint address,int length);}
 public sealed class Identity {
  public uint Actor,Unit,KeyPointer;
  public bool AuthorizesExtraShots {get{return false;}}
 }
 public static class IdentityReader {
  public const string EngineHash="022FAE2E2DA92B59B8B1B8EE52887003C624E3C8ECA060B209F5D792A7F874F5";
  public const string PackHash="0B497A435F4E28C2C068D7C90B60BA9D0C0FFA353BABD46242EF2FED2222D270";
  public const string UnitKey="steel_sakura_type20_automatic_fire_test";
  static readonly byte[] Key=Encoding.Unicode.GetBytes(UnitKey+"\0");
  static uint At(uint p,uint offset){if(p<0x10000||(p&3)!=0)throw new ArgumentException("invalid object address");return checked(p+offset);}
  static byte[] Read(IReadMemory m,uint p,int length){byte[] b=m.Read(p,length);if(b==null||b.Length!=length)throw new ArgumentException("partial read");return b;}
  static uint U(IReadMemory m,uint p){return BitConverter.ToUInt32(Read(m,p,4),0);}
  public static bool TryUnit(IReadMemory m,uint unit,string engineHash,string packHash,out Identity result){
   result=null;if(engineHash!=EngineHash||packHash!=PackHash)return false;
   try{uint field=At(unit,0x28),key=U(m,field);At(key,0);byte[] bytes=Read(m,key,Key.Length);
    for(int i=0;i<Key.Length;i++)if(bytes[i]!=Key[i])return false;
    if(U(m,field)!=key)return false;
    result=new Identity{Unit=unit,KeyPointer=key};return true;
   }catch{return false;}
  }
  public static bool TryActor(IReadMemory m,uint actor,string engineHash,string packHash,out Identity result){
   result=null;
   try{uint field=At(actor,0x214),unit=U(m,field);Identity match;
    if(!TryUnit(m,unit,engineHash,packHash,out match)||U(m,field)!=unit)return false;
    match.Actor=actor;result=match;return true;
   }catch{return false;}
  }
 }
}
