from pathlib import Path
p = Path(r"I:\MacbookISOBuildingSpace\work\staging\a1706.cmd")
text = p.read_bytes().decode("ascii")
old = "if exist X:\\sources\\setup.exe (\r\n"
new = (
    "set \"MSG=after-setup log a1706-after-setup.txt\"\r\n"
    "call :note\r\n"
    "if exist %SystemRoot%\\System32\\a1706dlg.exe (\r\n"
    "  start \"\" %SystemRoot%\\System32\\a1706dlg.exe\r\n"
    ") else (\r\n"
    "  set \"MSG=ERROR missing a1706dlg.exe\"\r\n"
    "  call :note\r\n"
    ")\r\n"
    "if exist X:\\sources\\setup.exe (\r\n"
)
if old not in text:
    raise SystemExit("anchor missing")
text = text.replace(old, new, 1)
raw = text.encode("ascii")
if b"\x00" in raw:
    raise SystemExit("nulls")
p.write_bytes(raw)
print("cmd", len(raw), "has watcher", "a1706dlg.exe" in text)
