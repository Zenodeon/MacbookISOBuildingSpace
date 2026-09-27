from pathlib import Path
p = Path(r"I:\MacbookISOBuildingSpace\work\staging\a1706.cmd")
raw = p.read_bytes()
if b"\x00" in raw:
    raise SystemExit("not single-byte")
text = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
text = text.replace(b"A1706 setup log v10", b"A1706 setup log v11", 1)
old = (
    b'set "MSG=v10 BasicDisplay stays on, start igfx after log"\n'
    b"call :note\n"
    b"call :dump sc query igfx\n"
    b"call :dump sc query BasicDisplay\n"
    b'set "MSG=step start igfx"\n'
    b"call :note\n"
    b"call :dump sc start igfx\n"
    b"call :dump sc query igfx\n"
)
new = (
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
if old not in text:
    raise SystemExit("sc block missing")
text = text.replace(old, new, 1)
text = text.replace(b"call :dump sc query igfx\ncall :dump sc query BasicDisplay\n", b"", 1)
old_msg = b'set "MSG=v10 igfx demand-start, BasicDisplay left enabled"\n'
new_msg = b'set "MSG=v11 pnputil restart done, display cycle"\n'
if old_msg not in text:
    raise SystemExit("late message missing")
text = text.replace(old_msg, new_msg, 1)
sub = (
    b":pnpdev\n"
    b'set "MSG=step !TAG! %~1"\n'
    b"call :note\n"
    b'pnputil %~1 "!GPU!" >X:\\a1706-cmd-out.txt 2>&1\n'
    b"set RC=!ERRORLEVEL!\n"
    b"call :addfile X:\\a1706-cmd-out.txt\n"
    b"if !RC! equ 0 (\n"
    b'  set "MSG=errorlevel=!RC! !TAG!"\n'
    b") else (\n"
    b'  set "MSG=ERROR errorlevel=!RC! !TAG!"\n'
    b")\n"
    b"call :note\n"
    b"goto :eof\n"
    b":pnpbasic\n"
    b'set "MSG=step !TAG! %~1"\n'
    b"call :note\n"
    b'pnputil %~1 "!BASIC!" >X:\\a1706-cmd-out.txt 2>&1\n'
    b"set RC=!ERRORLEVEL!\n"
    b"call :addfile X:\\a1706-cmd-out.txt\n"
    b"if !RC! equ 0 (\n"
    b'  set "MSG=errorlevel=!RC! !TAG!"\n'
    b") else (\n"
    b'  set "MSG=ERROR errorlevel=!RC! !TAG!"\n'
    b")\n"
    b"call :note\n"
    b"goto :eof\n"
)
mark = b":cue\n"
if mark not in text:
    raise SystemExit("cue missing")
text = text.replace(mark, sub + mark, 1)
for bad in (b"\nsc ", b"sc query", b"sc start", b"setup log v10"):
    if bad in text:
        raise SystemExit("leftover " + bad.decode())
for good in (b"A1706 setup log v11", b"restart-igfx", b"/disable-device", b"restart-igfx-after-basic", b":pnpdev"):
    if good not in text:
        raise SystemExit("missing " + good.decode())
p.write_bytes(text.replace(b"\n", b"\r\n"))
print("a1706.cmd", p.stat().st_size)
