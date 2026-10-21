"""Read Shogun 2 v1 animation frames and event blocks without changing game data.
Layout cross-check: robert-d-schultz/rmv2_anim_blender_import_export,
commit 28c2f47ba12cf3e5d02df75cf65579a1111b3deb, anim_format.py.
Independent narrow implementation; no Blender or third-party dependencies.
"""
import argparse, hashlib, json, struct
from pathlib import Path

def read_anim(data):
    version, fps, duration, bones = struct.unpack_from("<IffI", data)
    if version != 1 or not 0 < fps < 1000 or not 0 < bones < 1000:
        raise ValueError("Only observed Shogun 2 v1 clips are supported")
    offset = 16
    def string():
        nonlocal offset
        count, = struct.unpack_from("<H", data, offset)
        offset += 2
        end = offset + count * 2
        if end > len(data): raise ValueError("Truncated string")
        text = data[offset:end].decode("utf-16le"); offset = end
        return text
    rig = []
    for i in range(bones):
        name = string()
        parent, = struct.unpack_from("<i", data, offset); offset += 4
        if not -1 <= parent < bones: raise ValueError("Invalid parent")
        rig.append([name, parent])
    frame_count, = struct.unpack_from("<I", data, offset); offset += 4
    frame_offset = offset
    offset += frame_count * bones * 28
    if offset > len(data): raise ValueError("Truncated frames")
    event_offset = offset
    blocks = []
    while offset < len(data):
        count, = struct.unpack_from("<I", data, offset); offset += 4
        if count > 10000: raise ValueError("Invalid event count")
        block = []
        for _ in range(count):
            strings, = struct.unpack_from("<I", data, offset); offset += 4
            if strings > 100: raise ValueError("Invalid event width")
            block.append([string() for _ in range(strings)])
        blocks.append(block)
    if offset != len(data): raise ValueError("Trailing partial data")
    return dict(version=version, fps=fps, duration=duration, bones=rig,
                frame_count=frame_count, frame_offset=frame_offset,
                event_offset=event_offset, event_blocks=blocks)

def event_bytes(blocks):
    out = bytearray()
    for block in blocks:
        out += struct.pack("<I", len(block))
        for event in block:
            out += struct.pack("<I", len(event))
            for text in event:
                raw = text.encode("utf-16le")
                out += struct.pack("<H", len(raw)//2) + raw
    return bytes(out)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = []
    for p in sorted(args.root.rglob("*.anim")):
        raw = p.read_bytes(); row = read_anim(raw)
        assert raw[:row["event_offset"]] + event_bytes(row["event_blocks"]) == raw
        row.update(path=str(p), sha256=hashlib.sha256(raw).hexdigest(),
                   size=len(raw), event_roundtrip_identical=True)
        rows.append(row)
    text = json.dumps(rows, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(json.dumps([dict(path=r["path"],duration=r["duration"],
          frames=r["frame_count"],bones=len(r["bones"]),events=r["event_blocks"],
          roundtrip=r["event_roundtrip_identical"]) for r in rows],indent=2))
if __name__ == "__main__": main()
