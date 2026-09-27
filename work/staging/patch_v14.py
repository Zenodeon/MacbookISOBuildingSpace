from pathlib import Path
p = Path(r"I:\MacbookISOBuildingSpace\work\staging\a1706.cmd")
text = p.read_bytes().decode("ascii")
repls = [
    ('set "MSG=A1706 setup log v13 %DATE% %TIME%"', 'set "MSG=A1706 setup log v14 %DATE% %TIME%"'),
    ('set "MSG=v13 restart iris only"', 'set "MSG=v14 restart iris only"'),
    ('set "MSG=v13 still problem 18, restart again"', 'set "MSG=v14 still problem 18, restart again"'),
    ('set "MSG=v13 display cycle"', 'set "MSG=v14 display cycle"'),
]
for a, b in repls:
    if a not in text:
        raise SystemExit("missing " + a)
    text = text.replace(a, b, 1)
old = (
    'call :cue done\r\n'
    'call :copysapi\r\n'
    'if exist X:\\sources\\setup.exe (\r\n'
    '  X:\\sources\\setup.exe\r\n'
    ') else (\r\n'
    '  %SYSTEMDRIVE%\\sources\\setup.exe\r\n'
    ')\r\n'
)
new = (
    'call :cue done\r\n'
    'call :copysapi\r\n'
    'set "MSG=v14 delete oem0 force"\r\n'
    'call :note\r\n'
    'pnputil /delete-driver oem0.inf /force >X:\\a1706-cmd-out.txt 2>&1\r\n'
    'set RC=!ERRORLEVEL!\r\n'
    'call :addfile X:\\a1706-cmd-out.txt\r\n'
    'set "MSG=delete-driver errorlevel=!RC!"\r\n'
    'call :note\r\n'
    'call :dump pnputil /enum-devices /class Display\r\n'
    'call :copysapi\r\n'
    'set "SRC="\r\n'
    'for %%L in (C D E F G H I J K L M N O P Q R S T U V W Y Z) do (\r\n'
    '  if exist "%%L:\\sources\\install.wim" (\r\n'
    '    vol %%L: >X:\\a1706-cmd-out.txt 2>&1\r\n'
    '    findstr /I /C:"ESD-ISO" X:\\a1706-cmd-out.txt >nul\r\n'
    '    if !ERRORLEVEL! equ 0 set "SRC=%%L:"\r\n'
    '  )\r\n'
    ')\r\n'
    'if not defined SRC (\r\n'
    '  set "MSG=ERROR missing ESD-ISO install.wim"\r\n'
    '  call :note\r\n'
    ') else (\r\n'
    '  set "MSG=installfrom !SRC!\\sources\\install.wim"\r\n'
    '  call :note\r\n'
    ')\r\n'
    'if exist X:\\sources\\setup.exe (\r\n'
    '  if defined SRC (\r\n'
    '    X:\\sources\\setup.exe /InstallFrom:!SRC!\\sources\\install.wim\r\n'
    '  ) else (\r\n'
    '    X:\\sources\\setup.exe\r\n'
    '  )\r\n'
    ') else (\r\n'
    '  if defined SRC (\r\n'
    '    %SYSTEMDRIVE%\\sources\\setup.exe /InstallFrom:!SRC!\\sources\\install.wim\r\n'
    '  ) else (\r\n'
    '    %SYSTEMDRIVE%\\sources\\setup.exe\r\n'
    '  )\r\n'
    ')\r\n'
)
if old not in text:
    raise SystemExit("setup block missing")
text = text.replace(old, new, 1)
if "uninstall" in text.lower():
    raise SystemExit("uninstall present")
if "v13" in text:
    raise SystemExit("v13 remains")
raw = text.encode("ascii")
if b"\x00" in raw:
    raise SystemExit("nulls")
p.write_bytes(raw)
print("bytes", len(raw))
