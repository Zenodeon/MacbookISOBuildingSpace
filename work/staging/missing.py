from pathlib import Path
inf = Path(r"I:\MacbookISOBuildingSpace\work\iris-extract\signed\igdlh64.inf").read_text(encoding="utf-16")
lines = inf.splitlines()
in_src = False
wanted = []
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
    wanted.append(s.split("=")[0].strip())
have = {p.name.lower() for p in Path(r"I:\MacbookISOBuildingSpace\work\iris-extract\signed").iterdir()}
missing = [n for n in wanted if n.lower() not in have]
print("inf lists", len(wanted), "unique", len({n.lower() for n in wanted}), "missing", len(missing))
for n in missing:
    print(n)
