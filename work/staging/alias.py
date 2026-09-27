import shutil
from pathlib import Path
root = Path(r"I:\MacbookISOBuildingSpace\work\iris-extract\signed")
inf = (root/"igdlh64.inf").read_text(encoding="utf-16")
have = {p.name.lower(): p for p in root.iterdir()}
made = 0
for line in inf.splitlines():
    s = line.split(";")[0].strip()
    if "," not in s or s.startswith("[") or s.lower().startswith("hk"):
        continue
    parts = [p.strip() for p in s.split(",")]
    if len(parts) < 2:
        continue
    dest, src = parts[0], parts[1]
    if not dest or not src or "." not in dest or "." not in src:
        continue
    if src.lower() in have or dest.lower() not in have:
        continue
    target = root/src
    shutil.copyfile(have[dest.lower()], target)
    have[src.lower()] = target
    made += 1
print("copied aliases", made)
missing_left = []
in_src=False
for line in inf.splitlines():
    if line.strip().startswith("[") and in_src:
        break
    if line.strip().lower()=="[sourcedisksfiles]":
        in_src=True
        continue
    if not in_src:
        continue
    s=line.split(";")[0].strip()
    if "=" not in s:
        continue
    name=s.split("=")[0].strip()
    if name.lower() not in have:
        missing_left.append(name)
print("still missing", missing_left)
