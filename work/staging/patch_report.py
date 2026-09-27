from pathlib import Path
p = Path(r"I:\MacbookISOBuildingSpace\WorkingReport.md")
text = p.read_text(encoding="utf-8")
old = """## What put a picture on HDMI

v13, `out\\Win10_Pro_A1706_SetupGUI_v13.iso`.
"""
new = """## What put a picture on HDMI

The file is named v13, `out\\Win10_Pro_A1706_SetupGUI_v13.iso`. That number is just where the filenames started keeping score. Another six or seven ISOs came before the count, and they never got a number. HDMI stayed dark through all of those.
"""
if old not in text:
    raise SystemExit("anchor missing")
text = text.replace(old, new, 1)
raw = text.encode("utf-8")
if b"\x00" in raw:
    raise SystemExit("nulls")
p.write_bytes(raw)
print("ok", len(raw))
