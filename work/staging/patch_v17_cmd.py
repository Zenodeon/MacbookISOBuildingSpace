from pathlib import Path
p = Path(r"I:\MacbookISOBuildingSpace\work\staging\a1706.cmd")
lines = p.read_text(encoding="ascii").splitlines(keepends=True)
out = []
i = 0
while i < len(lines):
    if 'findstr /C:"CM_PROB_REINSTALL"' in lines[i]:
        while i < len(lines) and not lines[i].startswith("set DRV="):
            i += 1
        continue
    if "Narrator.exe" in lines[i]:
        break
    out.append(lines[i].replace("v16", "v17"))
    i += 1
tail = """if exist %SystemRoot%\\System32\\Narrator.exe start "" %SystemRoot%\\System32\\Narrator.exe
set "N=0"
set "IRISOK=0"
:waitiris
set /a N+=1
pnputil /enum-devices /class Display >X:\\a1706-cmd-out.txt 2>&1
call :addfile X:\\a1706-cmd-out.txt
set "MSG=iris wait !N! %TIME%"
call :note
if not exist %SystemRoot%\\System32\\a1706iris.exe (
  set "MSG=ERROR missing a1706iris.exe"
  call :note
  goto :irisdone
)
%SystemRoot%\\System32\\a1706iris.exe
if !ERRORLEVEL! equ 0 (
  set "MSG=iris started %TIME%"
  call :note
  set "IRISOK=1"
  goto :irisdone
)
if !N! geq 30 goto :irisdone
ping -n 3 127.0.0.1 >nul
goto :waitiris
:irisdone
if not "!IRISOK!"=="1" (
  set "MSG=ERROR iris not started"
  call :note
  goto :eof
)
if exist %SystemRoot%\\System32\\DisplaySwitch.exe (
  %SystemRoot%\\System32\\DisplaySwitch.exe /external
)
set "SRC="
for %%L in (C D E F G H I J K L M N O P Q R S T U V W Y Z) do (
  if exist "%%L:\\sources\\install.wim" (
    if not defined SRC set "SRC=%%L:"
  )
)
if not defined SRC (
  set "MSG=ERROR missing install.wim"
  call :note
) else (
  set "MSG=installfrom !SRC!\\sources\\install.wim"
  call :note
)
set "MSG=after-setup log a1706-after-setup.txt"
call :note
if exist %SystemRoot%\\System32\\a1706dlg.exe (
  start "" %SystemRoot%\\System32\\a1706dlg.exe
) else (
  set "MSG=ERROR missing a1706dlg.exe"
  call :note
)
set "MSG=launching setup %TIME%"
call :note
if exist X:\\sources\\setup.exe (
  if defined SRC (
    X:\\sources\\setup.exe /InstallFrom:!SRC!\\sources\\install.wim
  ) else (
    X:\\sources\\setup.exe
  )
) else (
  if defined SRC (
    %SYSTEMDRIVE%\\sources\\setup.exe /InstallFrom:!SRC!\\sources\\install.wim
  ) else (
    %SYSTEMDRIVE%\\sources\\setup.exe
  )
)
goto :eof
"""
# keep subroutines from :try onward
rest = []
while i < len(lines):
    if lines[i].startswith(":try"):
        rest = lines[i:]
        break
    i += 1
if not rest:
    raise SystemExit("missing :try")
text = "".join(out) + tail.replace("\n", "\r\n") + "".join(rest)
if "v16" in text or "CM_PROB_REINSTALL" in text or "display cycle" in text or "/clone" in text:
    raise SystemExit("old text remains")
for need in ("v17", "iris started", "iris wait", "ERROR iris not started", "launching setup", "a1706iris.exe", "/external", "cirrus4208"):
    if need not in text:
        raise SystemExit("missing " + need)
p.write_bytes(text.encode("ascii"))
print("ok", p.stat().st_size)
