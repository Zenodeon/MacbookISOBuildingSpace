from pathlib import Path
p = Path(r"I:\MacbookISOBuildingSpace\work\staging\a1706.cmd")
raw = p.read_bytes()
if b"\x00" in raw:
    raise SystemExit("not single-byte")
text = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
text = text.replace(b"A1706 setup log v11", b"A1706 setup log v12", 1)
old = (
    b'set "MSG=v11 log first, pnputil restart igfx, then disable BasicDisplay"\n'
    b"call :note\n"
    b'set "GPU=PCI\\VEN_8086&DEV_1927&SUBSYS_015D106B&REV_0A\\3&11583659&0&10"\n'
    b'set "BASIC=ROOT\\BasicDisplay\\0000"\n'
    b'set "TAG=restart-igfx"\n'
    b"call :pnpdev /restart-device\n"
    b"call :dump pnputil /enum-devices /class Display\n"
    b"call :dump pnputil /enum-devices /problem\n"
    b'set "TAG=disable-basicdisplay"\n'
    b"call :pnpbasic /disable-device\n"
    b'set "TAG=restart-igfx-after-basic"\n'
    b"call :pnpdev /restart-device\n"
    b"call :dump pnputil /enum-devices /class Display\n"
    b"call :copysapi\n"
)
new = (
    b'set "MSG=v12 2021 iris staged, no restart"\n'
    b"call :note\n"
    b"call :dump pnputil /enum-devices /class Display\n"
    b"call :dump pnputil /enum-devices /problem\n"
    b"call :copysapi\n"
)
if old not in text:
    raise SystemExit("restart block missing")
text = text.replace(old, new, 1)
old_find = b'if exist "%~1:\\$WinPEDriver$\\IntelIrisSetup\\igdiris64.inf" ('
new_find = b'if exist "%~1:\\$WinPEDriver$\\AppleSPIKeyboard\\AppleSPIKeyboard.inf" ('
if old_find not in text:
    raise SystemExit("finddrv missing")
text = text.replace(old_find, new_find, 1)
text = text.replace(b"set \"MSG=iris-inf-on %~1\"", b"set \"MSG=winpedriver-on %~1\"", 1)
text = text.replace(
    b'set "MSG=v11 pnputil restart done, display cycle"\n',
    b'set "MSG=v12 display cycle"\n',
    1,
)
start = text.find(b":pnpdev\n")
end = text.find(b":cue\n")
if start < 0 or end < 0 or end < start:
    raise SystemExit("pnp bounds missing")
text = text[:start] + text[end:]
for bad in (b"restart-device", b"/disable-device", b":pnpdev", b"igdiris64.inf", b"setup log v11"):
    if bad in text:
        raise SystemExit("leftover " + bad.decode())
for good in (b"A1706 setup log v12", b"2021 iris staged", b"AppleSPIKeyboard.inf", b"enum-devices /class Display"):
    if good not in text:
        raise SystemExit("missing " + good.decode())
p.write_bytes(text.replace(b"\n", b"\r\n"))
print("a1706.cmd", p.stat().st_size)
