import hashlib, os, struct
from pathlib import Path

cat = Path(r"I:\MacbookISOBuildingSpace\work\staging\iris1545\igdlh.cat").read_bytes()
marker = bytes.fromhex("2b0e03021a05000414")
hashes = []
idx = 0
while True:
    i = cat.find(marker, idx)
    if i < 0:
        break
    start = i + len(marker)
    digest = cat[start:start+20]
    window = cat[start:start+900]
    # utf-16le strings
    name = None
    j = 0
    while j < len(window)-4:
        if window[j+1] == 0 and 32 <= window[j] < 127:
            chars = []
            k = j
            while k < len(window)-1 and window[k+1] == 0 and 32 <= window[k] < 127:
                chars.append(chr(window[k]))
                k += 2
            s = "".join(chars)
            if "." in s and len(s) > 4 and " " not in s:
                name = s
                break
            j = k
        else:
            j += 1
    hashes.append((digest, name))
    idx = start + 20
print("catalog digests", len(hashes), "named", sum(1 for _, n in hashes if n))
print("sample", hashes[0][1], hashes[1][1], hashes[2][1])

def pe_digest(data):
    if data[:2] != b"MZ":
        return hashlib.sha1(data).digest()
    e = struct.unpack_from("<I", data, 0x3C)[0]
    if data[e:e+4] != b"PE\x00\x00":
        return hashlib.sha1(data).digest()
    coff = e + 4
    nsec = struct.unpack_from("<H", data, coff + 2)[0]
    optsz = struct.unpack_from("<H", data, coff + 16)[0]
    opt = coff + 20
    magic = struct.unpack_from("<H", data, opt)[0]
    if magic == 0x20B:
        dd = opt + 112
    elif magic == 0x10B:
        dd = opt + 96
    else:
        return hashlib.sha1(data).digest()
    checksum = opt + 64
    cert_entry = dd + 32
    cert_off, cert_sz = struct.unpack_from("<II", data, cert_entry)
    size_headers = struct.unpack_from("<I", data, opt + 60)[0]
    sec_off = opt + optsz
    sections = []
    for i in range(nsec):
        raw, rsz = struct.unpack_from("<II", data, sec_off + 40*i + 20)
        sections.append((raw, rsz))
    sections.sort()
    h = hashlib.sha1()
    h.update(data[:checksum])
    h.update(data[checksum+4:cert_entry])
    h.update(data[cert_entry+8:size_headers])
    end = size_headers
    for raw, rsz in sections:
        if raw == 0 or rsz == 0:
            continue
        h.update(data[raw:raw+rsz])
        if raw + rsz > end:
            end = raw + rsz
    tail_end = cert_off if cert_off else len(data)
    if end < tail_end:
        h.update(data[end:tail_end])
    # alignment: leftover after last section before cert, already included
    return h.digest()

root = Path(r"I:\MacbookISOBuildingSpace\work\iris-extract\extracted")
want = {d for d, _ in hashes}
found = {}
for member in os.listdir(root):
    path = root / member
    if not path.is_file():
        continue
    data = path.read_bytes()
    raw = hashlib.sha1(data).digest()
    auth = pe_digest(data)
    if raw in want and raw not in found:
        found[raw] = member
    if auth in want and auth not in found:
        found[auth] = member
print("matched digests", len(found), "of", len(want))
