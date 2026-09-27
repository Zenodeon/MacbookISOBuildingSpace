from pathlib import Path
inf = Path(r"I:\MacbookISOBuildingSpace\work\iris-extract\signed\igdlh64.inf").read_text(encoding="utf-16")
# dest,source pairs
pairs = []
for line in inf.splitlines():
    s = line.split(";")[0].strip()
    if "," not in s or s.startswith("[") or "=" in s.split(",")[0] and s.strip().endswith("="):
        continue
    if "=" in s and not s.lower().startswith("hk"):
        # skip source disks and directives that aren't copy lines
        pass
    left = s.split(",")
    if len(left) >= 2 and left[0] and left[1] and " " not in left[0] and "\\" not in left[0]:
        dest, src = left[0].strip(), left[1].strip()
        if src and "." in src and "." in dest and not dest.startswith("%"):
            pairs.append((dest, src))
print("pairs", len(pairs))
# unique src for missing
have = {p.name.lower(): p.name for p in Path(r"I:\MacbookISOBuildingSpace\work\iris-extract\signed").iterdir()}
shown=set()
for dest, src in pairs:
    if src.lower() not in have and src.lower() not in shown:
        shown.add(src.lower())
        print(f"{src}  <=  {dest}  dest_present={dest.lower() in have}")
