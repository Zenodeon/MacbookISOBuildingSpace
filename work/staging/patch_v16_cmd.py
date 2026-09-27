from pathlib import Path
p = Path(r"I:\MacbookISOBuildingSpace\work\staging\a1706.cmd")
lines = p.read_text(encoding="ascii").splitlines(keepends=True)
out = []
skip = 0
for line in lines:
    if skip:
        skip -= 1
        continue
    if "TAG=thunderbolt" in line or "TAG=cirrus4206" in line:
        skip = 2
        continue
    out.append(line.replace("v15", "v16"))
text = "".join(out)
if "v15" in text or "thunderbolt" in text or "cirrus4206" in text:
    raise SystemExit("old text remains")
if "cirrus4208" not in text or "setup log v16" not in text:
    raise SystemExit("required text missing")
p.write_bytes(text.encode("ascii"))
print("ok", p.stat().st_size)
