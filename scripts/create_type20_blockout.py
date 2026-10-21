"""Create an original coarse rifle blockout; export to the locally verified VMPF v3.
NOT included in the firing test pack: attachment lookup, textures, grip and
rendering must be proven separately. Geometry is original cuboids, no game mesh.
Requires the reviewed GPL writer in build/type20-research/tool-reference.
"""
from pathlib import Path
import hashlib,importlib.util,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def main():
 writer=ROOT/"build/type20-research/tool-reference/vmpf_format.py"
 if hashlib.sha256(writer.read_bytes()).hexdigest()!="bb95cac7c3ca526d39892114d6c438a36887910aebe6bf73deee719ac36fff1e":
  raise ValueError("The reviewed, pinned format writer is required")
 spec=importlib.util.spec_from_file_location("ss_vmpf_reference",writer);v=importlib.util.module_from_spec(spec);sys.modules[spec.name]=v;spec.loader.exec_module(v)
 # X follows the observed weapon bone's rifle-length direction. Dimensions
 # below are an original silhouette study, not measured Howa specifications.
 boxes=[(-.12,.03,-.025,.20,.12,.025), # receiver
        (.20,.045,-.02,.42,.105,.02), # handguard
        (.42,.065,-.009,.55,.082,.009), # barrel
        (-.35,.035,-.018,-.12,.10,.018), # stock
        (-.08,-.075,-.018,-.025,.035,.018), # grip
        (.045,-.115,-.018,.105,.04,.018)] # magazine
 faces=[((0,3,2,1),(0,0,-1)),((4,5,6,7),(0,0,1)),
        ((0,4,7,3),(-1,0,0)),((1,2,6,5),(1,0,0)),
        ((0,1,5,4),(0,-1,0)),((3,7,6,2),(0,1,0))]
 pos=[];norm=[];tan=[];bitan=[];uv=[];indices=[]
 for x0,y0,z0,x1,y1,z1 in boxes:
  c=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
  for corners,n in faces:
   start=len(pos);t=(0,1,0) if abs(n[0])==1 else (1,0,0)
   pos.extend(c[i] for i in corners);norm.extend([n]*4);tan.extend([t]*4);bitan.extend([tuple(np.cross(n,t))]*4);uv.extend([(0,0),(1,0),(1,1),(0,1)])
   indices.extend([start,start+1,start+2,start,start+2,start+3])
 raw=v.encode_rigid_vertices(np.array(pos),np.array(norm),np.array(tan),np.array(bitan),np.array(uv),np.zeros((len(pos),2)),np.ones((len(pos),4)))
 model=v.VmpfFile(version=3,vertex_format=2,skeleton_name="man_shogun",float_params=[("light_scale",1.0)])
 for lod in range(1,5):
  model.parts.append(v.VmpfPart(vertices=raw.copy(),indices=np.array(indices,dtype=np.uint16),name=f"rigid_equip_ss_type20_blockout_lod{lod}",material_names=["default"]*3,bone_index=1))
 native=ROOT/"build/type20-research/original-model/type20_blockout.variant_part_mesh";native.parent.mkdir(parents=True,exist_ok=True);native.write_bytes(v.save(model))
 decoded=v.load(native.read_bytes());assert v.save(decoded)==native.read_bytes()
 assert np.allclose(v.decode_vertices(decoded,decoded.parts[0])["position0"],pos)
 obj=ROOT/"assets/type20/type20_blockout.obj";obj.parent.mkdir(parents=True,exist_ok=True)
 lines=["# Steel & Sakura original coarse rifle blockout; no third-party geometry.","# Not a dimensionally accurate Howa Type 20. Not installed in the event test."]
 lines+=["v %.6f %.6f %.6f"%tuple(p) for p in pos]
 lines+=["f %d %d %d"%tuple(i+1 for i in indices[j:j+3]) for j in range(0,len(indices),3)]
 obj.write_text("\n".join(lines)+"\n")
 report=dict(status="FORMAT_ROUNDTRIP_ONLY_NOT_RENDER_VERIFIED",original_geometry=True,obj=str(obj),native=str(native),native_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),version=3,vertex_format=2,bone=1,lods=4,vertices_per_lod=len(pos),triangles_per_lod=len(indices)//3,included_in_firing_pack=False)
 (native.parent/"report.json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
