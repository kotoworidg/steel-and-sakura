"""Bounded PFH3/DB/LOC codec for the exact RPFM-decoded Shogun 2 tables used here.
No game execution, native memory access, or speculative animation/event handling.
"""
import math,struct

def pack_entries(raw):
 if len(raw)<32 or raw[:4]!=b'PFH3':raise ValueError('expected PFH3')
 flags,deps,depbytes,count,indexsize=struct.unpack_from('<5I',raw,4)
 if flags!=3 or deps or depbytes or count>10000 or indexsize>len(raw)-32:raise ValueError('unsupported pack header')
 pos,end,offset=32,32+indexsize,32+indexsize;out={};seen=set()
 for _ in range(count):
  if pos+4>end:raise ValueError('truncated pack index')
  size=struct.unpack_from('<I',raw,pos)[0];pos+=4
  stop=raw.index(b'\0',pos,end);name=raw[pos:stop].decode('utf-8').replace('\\','/');pos=stop+1
  if not name or name.startswith('/') or any(p in ['.','..'] for p in name.split('/')) or ':' in name or name.casefold() in seen or name.endswith('.rpfm_reserved'):raise ValueError('unsafe or duplicate packed path')
  if offset+size>len(raw):raise ValueError('truncated payload')
  seen.add(name.casefold());out[name]=raw[offset:offset+size];offset+=size
 if pos!=end or offset!=len(raw):raise ValueError('pack index/trailing bytes mismatch')
 return out

def pack_bytes(files):
 items=sorted(files.items());index=b''.join(struct.pack('<I',len(b))+n.replace('/','\\').encode()+b'\0' for n,b in items)
 raw=b'PFH3'+struct.pack('<7I',3,0,0,len(items),len(index),0,0)+index+b''.join(b for _,b in items)
 if pack_entries(raw)!=files:raise ValueError('pack encoder roundtrip')
 return raw

class Reader:
 def __init__(self,raw):self.raw=raw;self.pos=0
 def take(self,n):
  if n<0 or self.pos+n>len(self.raw):raise ValueError('truncated data')
  b=self.raw[self.pos:self.pos+n];self.pos+=n;return b
 def number(self,fmt):return struct.unpack('<'+fmt,self.take(struct.calcsize('<'+fmt)))[0]
 def text(self):return self.take(self.number('H')*2).decode('utf-16-le')

def text_bytes(s):
 raw=s.encode('utf-16-le')
 if len(raw)//2>65535:raise ValueError('string too long')
 return struct.pack('<H',len(raw)//2)+raw

def cell_read(r,t):
 if t=='StringU16':return r.text()
 if t=='OptionalStringU16':
  exists=r.number('B')
  if exists not in [0,1]:raise ValueError('invalid optional marker')
  return r.text() if exists else ''
 if t=='Boolean':
  v=r.number('B')
  if v not in [0,1]:raise ValueError('invalid Boolean')
  return bool(v)
 if t=='I32':return r.number('i')
 if t=='F32':
  v=r.number('f')
  if not math.isfinite(v):raise ValueError('non-finite field')
  return v
 raise ValueError('unsupported observed cell type '+t)

def cell_bytes(t,v):
 if t=='StringU16':return text_bytes(v)
 if t=='OptionalStringU16':return b'\1'+text_bytes(v) if v else b'\0'
 if t=='Boolean':
  if type(v) is not bool:raise ValueError('Boolean type mismatch')
  return bytes([int(v)])
 if t=='I32':
  if type(v) is not int:raise ValueError('I32 type mismatch')
  return struct.pack('<i',v)
 if t=='F32':
  if not math.isfinite(v):raise ValueError('non-finite field')
  return struct.pack('<f',v)
 raise ValueError('unsupported cell type '+t)

def db_read(raw,spec):
 r=Reader(raw)
 if r.take(4)!=bytes.fromhex('fdfefcff'):raise ValueError('unknown DB header')
 guid=r.text()
 if len(guid)!=36:raise ValueError('invalid GUID')
 version=0
 if r.raw[r.pos:r.pos+4]==bytes.fromhex('fcfdfeff'):r.take(4);version=r.number('i')
 if version!=spec['version'] or r.number('B')!=1:raise ValueError('DB version/flag mismatch')
 prefix=raw[:r.pos];count=r.number('I')
 if count>100000:raise ValueError('unreasonable row count')
 rows=[{f:cell_read(r,t) for f,t in spec['fields']} for _ in range(count)]
 if r.pos!=len(raw):raise ValueError('DB trailing bytes')
 return prefix,rows

def db_bytes(prefix,rows,spec):
 return prefix+struct.pack('<I',len(rows))+b''.join(cell_bytes(t,row[f]) for row in rows for f,t in spec['fields'])

def loc_read(raw):
 if raw[:10]!=b'\xff\xfeLOC\0\1\0\0\0':raise ValueError('unknown LOC header')
 r=Reader(raw);prefix=r.take(10);count=r.number('I')
 if count>100000:raise ValueError('unreasonable LOC rows')
 rows=[[r.text(),r.text(),cell_read(r,'Boolean')] for _ in range(count)]
 if r.pos!=len(raw):raise ValueError('LOC trailing bytes')
 return prefix,rows

def loc_bytes(prefix,rows):
 return prefix+struct.pack('<I',len(rows))+b''.join(text_bytes(k)+text_bytes(v)+cell_bytes('Boolean',flag) for k,v,flag in rows)
