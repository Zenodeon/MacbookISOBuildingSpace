import re
from pathlib import Path
inf = Path(r"I:\MacbookISOBuildingSpace\work\staging\iris1545\igdlh64.inf").read_text(encoding="utf-16")
# file is utf-16 le with bom, read_text utf-16 handles it
lines = inf.splitlines()
in_src = False
files = []
for line in lines:
    if line.strip().startswith("[") and in_src:
        break
    if line.strip().lower() == "[sourcedisksfiles]":
        in_src = True
        continue
    if not in_src:
        continue
    s = line.split(";")[0].strip()
    if not s or "=" not in s:
        continue
    name = s.split("=")[0].strip()
    files.append(name)
print("inf files", len(files), "unique", len(set(files)))

pemap = Path(r"I:\MacbookISOBuildingSpace\work\staging\iris1545\pemap.txt").read_text(encoding="utf-8", errors="replace").splitlines()
# a0\tigxpin.exe\tsize\tmachine
by_name = {}
for line in pemap:
    parts = line.split("\t")
    if len(parts) < 4:
        continue
    member, name, size, mach = parts[0], parts[1], parts[2], parts[3]
    if not name:
        continue
    by_name.setdefault(name.lower(), []).append((member, int(size), mach))

missing = []
multi = []
ok = 0
for name in files:
    hits = by_name.get(name.lower(), [])
    amd = [h for h in hits if h[2].lower() in ("0x8664", "0x8664 ")]
    if not hits:
        missing.append(name)
    elif len(amd) == 1:
        ok += 1
    elif len(amd) > 1:
        multi.append((name, amd))
    elif len(hits) == 1:
        ok += 1
    else:
        multi.append((name, hits))
print("matched", ok, "missing", len(missing), "multi", len(multi))
print("MISSING:")
for n in missing:
    print(" ", n)
print("MULTI:")
for n, hits in multi:
    print(" ", n, hits)
