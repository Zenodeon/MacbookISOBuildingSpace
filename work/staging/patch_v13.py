from pathlib import Path
p = Path(r"I:\MacbookISOBuildingSpace\work\staging\a1706.cmd")
text = p.read_bytes().decode("ascii")
old = '''set "MSG=A1706 setup log v12 %DATE% %TIME%"'''
new = '''set "MSG=A1706 setup log v13 %DATE% %TIME%"'''
if old not in text:
    raise SystemExit("banner missing")
text = text.replace(old, new, 1)
old = '''set "MSG=v12 2021 iris staged, no restart"\r\ncall :note\r\ncall :dump pnputil /enum-devices /class Display\r\ncall :dump pnputil /enum-devices /problem\r\ncall :copysapi\r\nset DRV='''
new = '''set "MSG=v13 restart iris only"\r\ncall :note\r\ncall :dump pnputil /enum-devices /class Display\r\ncall :dump pnputil /enum-devices /problem\r\ncall :copysapi\r\nset "GPU=PCI\\VEN_8086&DEV_1927&SUBSYS_015D106B&REV_0A\\3&11583659&0&10"\r\ncall :gpurestart\r\nfindstr /C:"CM_PROB_REINSTALL" X:\\a1706-cmd-out.txt >nul\r\nif !ERRORLEVEL! equ 0 (\r\n  set "MSG=v13 still problem 18, restart again"\r\n  call :note\r\n  call :gpurestart\r\n)\r\nset DRV='''
if old not in text:
    raise SystemExit("insert point missing")
text = text.replace(old, new, 1)
text = text.replace('set "MSG=v12 display cycle"', 'set "MSG=v13 display cycle"', 1)
label = ''':gpurestart\r\nset "MSG=pnputil restart-device"\r\ncall :note\r\npnputil /restart-device "!GPU!" >X:\\a1706-cmd-out.txt 2>&1\r\nset RC=!ERRORLEVEL!\r\ncall :addfile X:\\a1706-cmd-out.txt\r\nset "MSG=restart errorlevel=!RC!"\r\ncall :note\r\ncall :dump pnputil /enum-devices /class Display\r\ncall :dump pnputil /enum-devices /problem\r\ncall :copysapi\r\ngoto :eof\r\n'''
needle = ":dump\r\n"
if needle not in text:
    raise SystemExit("dump label missing")
text = text.replace(needle, label + needle, 1)
for bad in ("disable-device", "BasicDisplay", "v12"):
    if bad in text:
        raise SystemExit("unexpected " + bad)
raw = text.encode("ascii")
if b"\x00" in raw:
    raise SystemExit("nulls")
p.write_bytes(raw)
print("bytes", len(raw))
