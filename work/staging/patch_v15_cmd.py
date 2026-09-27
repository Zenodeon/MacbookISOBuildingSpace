from pathlib import Path
p = Path(r"I:\MacbookISOBuildingSpace\work\staging\a1706.cmd")
t = p.read_text(encoding="ascii")
t = t.replace("A1706 setup log v14", "A1706 setup log v15")
t = t.replace("v14 restart iris only", "v15 restart iris only")
t = t.replace("v14 still problem 18, restart again", "v15 still problem 18, restart again")
t = t.replace("v14 display cycle", "v15 display cycle")
old = """set \"MSG=v14 delete oem0 force\"
call :note
pnputil /delete-driver oem0.inf /force >X:\\a1706-cmd-out.txt 2>&1
set RC=!ERRORLEVEL!
call :addfile X:\\a1706-cmd-out.txt
set \"MSG=delete-driver errorlevel=!RC!\"
call :note
call :dump pnputil /enum-devices /class Display
call :copysapi
set \"SRC=\"
for %%L in (C D E F G H I J K L M N O P Q R S T U V W Y Z) do (
  if exist \"%%L:\\sources\\install.wim\" (
    vol %%L: >X:\\a1706-cmd-out.txt 2>&1
    findstr /I /C:\"ESD-ISO\" X:\\a1706-cmd-out.txt >nul
    if !ERRORLEVEL! equ 0 set \"SRC=%%L:\"
  )
)
if not defined SRC (
  set \"MSG=ERROR missing ESD-ISO install.wim\"
  call :note
) else (
  set \"MSG=installfrom !SRC!\\sources\\install.wim\"
  call :note
)
"""
new = """set \"SRC=\"
for %%L in (C D E F G H I J K L M N O P Q R S T U V W Y Z) do (
  if exist \"%%L:\\sources\\install.wim\" (
    if not defined SRC set \"SRC=%%L:\"
  )
)
if not defined SRC (
  set \"MSG=ERROR missing install.wim\"
  call :note
) else (
  set \"MSG=installfrom !SRC!\\sources\\install.wim\"
  call :note
)
"""
if old not in t:
    raise SystemExit("block missing")
t = t.replace(old, new, 1)
if "v14" in t or "delete-driver" in t or "ESD-ISO" in t:
    raise SystemExit("old text remains")
p.write_bytes(t.encode("ascii"))
print("ok", p.stat().st_size)
