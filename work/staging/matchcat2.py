import hashlib, os, struct
from pathlib import Path

cat = Path(r"I:\MacbookISOBuildingSpace\work\staging\iris1545\igdlh.cat").read_bytes()
marker = bytes.fromhex("2b0e03021a05000414")
exts = (".dll",".sys",".exe",".inf",".cat",".vp",".bin",".config",".txt",".ini",".rtl",".o",".json",".rtf",".wmv",".cpl",".cab",".cpa")

def utf16_strings(window):
    out = []
    j = 0
    n = len(window)
    while j < n - 4:
        if window[j+1] == 0 and 32 <= window[j] < 127:
            chars = []
            k = j
            while k < n - 1 and window[k+1] == 0 and 32 <= window[k] < 127:
                chars.append(chr(window[k]))
                k += 2
            s = "".join(chars)
            if len(s) > 4:
                out.append(s)
            j = k
        else:
            j += 1
    return out

entries = []
idx = 0
while True:
    i = cat.find(marker, idx)
    if i < 0:
        break
    start = i + len(marker)
    digest = cat[start:start+20]
    names = utf16_strings(cat[start:start+1200])
    pick = None
    for s in names:
        low = s.lower()
        if "," in s:
            continue
        if low.endswith(exts):
            pick = s
            break
    entries.append((digest, pick, names[:6]))
    idx = start + 20

named = sum(1 for _, n, _ in entries if n)
print("entries", len(entries), "named", named)
unnamed = [ns for _, n, ns in entries if not n]
print("unnamed samples", unnamed[:3])

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
    dd = opt + (112 if magic == 0x20B else 96)
    checksum = opt + 64
    cert_entry = dd + 32
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
        if raw and rsz:
            h.update(data[raw:raw+rsz])
            end = max(end, raw+rsz)
    cert_off = struct.unpack_from("<I", data, cert_entry)[0]
    tail_end = cert_off if cert_off else len(data)
    if end < tail_end:
        h.update(data[end:tail_end])
    return h.digest()

root = Path(r"I:\MacbookISOBuildingSpace\work\iris-extract\extracted")
digest_to_member = {}
for member in os.listdir(root):
    path = root / member
    if not path.is_file():
        continue
    data = path.read_bytes()
    for dig in (hashlib.sha1(data).digest(), pe_digest(data)):
        digest_to_member.setdefault(dig, member)

missing = []
used = {}
for dig, name, names in entries:
    member = digest_to_member.get(dig)
    if member is None:
        missing.append((name, names[:8]))
    else:
        used.setdefault(name, member)
print("missing", len(missing))
for item in missing:
    print(" MISS", item)
print("unique names", len(used), "none-name", sum(1 for n in used if n is None))
