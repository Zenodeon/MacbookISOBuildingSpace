from pathlib import Path
p = Path(r"I:\MacbookISOBuildingSpace\work\staging\a1706.cmd")
raw = p.read_bytes()
if raw[:2] == b"\xff\xfe":
    text = raw.decode("utf-16")
else:
    text = raw.decode("ascii")
text = text.replace("\r\n", "\n")
old_banner = "setup log v4 "
new_banner = "setup log v5 "
if old_banner not in text:
    raise SystemExit("banner missing")
text = text.replace(old_banner, new_banner, 1)
anchor = 'set "MSG=step after-wpeinit"\ncall :note\n'
insert = anchor + 'set "MSG=iris preinstalled in boot image, skip drvload"\ncall :note\n'
if anchor not in text:
    raise SystemExit("anchor missing")
text = text.replace(anchor, insert, 1)
block = 'set "TAG=iris"\nset "ONE=!DRV!\\IntelIrisSetup\\igdiris64.inf"\ncall :loadone\n'
if block not in text:
    raise SystemExit("iris load block missing")
text = text.replace(block, "", 1)
out = text.replace("\n", "\r\n").encode("ascii")
p.write_bytes(out)
print("cmd bytes", len(out), "nul", out.count(0))
