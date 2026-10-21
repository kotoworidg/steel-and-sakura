"""Remove empty RPFM editor metadata from supported PFH3 Mod release packs.

Retains every game file byte-for-byte. Rejects dependencies, unknown metadata,
compression/flag variants and malformed indices rather than guessing.
"""
import argparse
import hashlib
import struct
from pathlib import Path


def clean(path):
    raw = path.read_bytes()
    if len(raw) < 32 or raw[:4] != b"PFH3":
        raise ValueError("Only PFH3 is supported")
    flags, dependencies, dependency_bytes, count, index_bytes = struct.unpack_from("<5I", raw, 4)
    if flags != 3 or dependencies or dependency_bytes:
        raise ValueError("Only uncompressed Mod packs without dependencies are supported")
    cursor, offset = 32, 32 + index_bytes
    entries = []
    for _ in range(count):
        if cursor + 4 > 32 + index_bytes:
            raise ValueError("Truncated index")
        size = struct.unpack_from("<I", raw, cursor)[0]
        cursor += 4
        end = raw.index(b"\0", cursor, 32 + index_bytes)
        name = raw[cursor:end]
        cursor = end + 1
        if offset + size > len(raw):
            raise ValueError("Truncated payload")
        entries.append((name, raw[offset:offset + size]))
        offset += size
    if cursor != 32 + index_bytes or offset != len(raw):
        raise ValueError("Unexpected index or trailing bytes")
    import json
    allowed = {b"notes.rpfm_reserved", b"settings.rpfm_reserved", b"dependencies_manager_v2.rpfm_reserved"}
    retained, removed = [], []
    for name, payload in entries:
        if name.endswith(b".rpfm_reserved"):
            if name not in allowed:
                raise ValueError("Unknown editor metadata")
            metadata = json.loads(payload)
            if name == b"notes.rpfm_reserved" and metadata != {"pack_notes": "", "file_notes": {}}:
                raise ValueError("Refusing to drop nonempty notes")
            if name == b"dependencies_manager_v2.rpfm_reserved" and metadata != []:
                raise ValueError("Refusing to drop nonempty dependencies")
            removed.append(name.decode())
        else:
            retained.append((name, payload))
    if not removed:
        print(f"{path}: no editor metadata")
        return
    index = b"".join(struct.pack("<I", len(payload)) + name + b"\0" for name, payload in retained)
    header = bytearray(raw[:32])
    struct.pack_into("<II", header, 16, len(retained), len(index))
    output = bytes(header) + index + b"".join(payload for _, payload in retained)
    # Prove every retained payload remains identical before replacing the build.
    cursor, offset = 32, 32 + len(index)
    for name, payload in retained:
        size = struct.unpack_from("<I", output, cursor)[0]
        end = output.index(b"\0", cursor + 4)
        if output[cursor + 4:end] != name or output[offset:offset + size] != payload:
            raise ValueError("Retained data mismatch")
        cursor, offset = end + 1, offset + size
    path.write_bytes(output)
    print(f"{path}: removed {len(removed)} editor entries; {len(retained)} game files unchanged; SHA256 {hashlib.sha256(output).hexdigest().upper()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pack", type=Path)
    clean(parser.parse_args().pack)
