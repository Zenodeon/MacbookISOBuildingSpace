from pathlib import Path

root = Path(r"I:\MacbookISOBuildingSpace\work\iso-root")
src = root / "$WinPEDriver$" / "IntelHDGraphics64" / "Graphics"
dst = root / "$WinPEDriver$" / "IntelIrisSetup"
dst.mkdir(parents=True, exist_ok=True)
files = [
    "igdkmd64.sys",
    "igd10iumd64.dll",
    "igd10idpp64.dll",
    "igd11dxva64.dll",
    "igd12umd64.dll",
    "igdumdim64.dll",
    "igdail64.dll",
    "igfxcmrt64.dll",
    "igfx11cmrt64.dll",
    "igfxcmjit64.dll",
    "igdde64.dll",
    "IntelCpHDCPSvc.exe",
    "igdusc64.dll",
    "igc64.dll",
    "igdmd64.dll",
]
total = 0
for name in files:
    data = (src / name).read_bytes()
    (dst / name).write_bytes(data)
    total += len(data)
    print(len(data), name)

inf_path = Path(r"I:\MacbookISOBuildingSpace\work\staging\igdiris64.inf")
raw = inf_path.read_bytes()
if raw[1:2] == b"\x00" or raw.startswith(b"\xff\xfe"):
    text = raw.decode("utf-16")
else:
    text = raw.decode("ascii")
out = text.replace("\r\n", "\n").replace("\n", "\r\n").encode("ascii")
(dst / "igdiris64.inf").write_bytes(out)
inf_path.write_bytes(out)
print("total", total)
print("inf", len(out), out[:3])
