from pathlib import Path

cmd_path = Path(r"I:\MacbookISOBuildingSpace\work\staging\a1706.cmd")
raw = cmd_path.read_bytes()
if b"\x00" in raw:
    raise SystemExit("a1706.cmd is not single-byte")
text = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
if b"A1706 setup log v8" not in text:
    raise SystemExit("banner missing")
text = text.replace(b"A1706 setup log v8", b"A1706 setup log v9", 1)

anchor = b"call :dump reg query HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers /s\n"
insert = anchor + b"call :dump sc query igfx\ncall :dump sc query BasicDisplay\n"
if anchor not in text:
    raise SystemExit("dump anchor missing")
text = text.replace(anchor, insert, 1)

old_hive = (
    b'set "MSG=booted saved SYSTEM hive, skip force-switch"\n'
    b"call :note\n"
    b'set "MSG=step save hive"\n'
    b"call :note\n"
    b"for %%D in (!LOGS!) do call :savehiv %%D\n"
)
new_hive = (
    b'set "MSG=v9 clean hive, iris boot-start, BasicDisplay disabled"\n'
    b"call :note\n"
)
if old_hive not in text:
    raise SystemExit("hive block missing")
text = text.replace(old_hive, new_hive, 1)

start = text.find(b":savehiv\n")
end = text.find(b":cue\n")
if start < 0 or end < 0 or end < start:
    raise SystemExit("savehiv bounds missing")
text = text[:start] + text[end:]

for bad in (b"remove-device", b"savehiv", b"SYSTEM.hiv", b"skip force-switch"):
    if bad in text:
        raise SystemExit("leftover " + bad.decode())
for good in (b"A1706 setup log v9", b"sc query igfx", b"sc query BasicDisplay", b"BasicDisplay disabled"):
    if good not in text:
        raise SystemExit("missing " + good.decode())
cmd_path.write_bytes(text.replace(b"\n", b"\r\n"))
print("a1706.cmd", cmd_path.stat().st_size)

inject = r"""@echo off
setlocal
set LOG=I:\MacbookISOBuildingSpace\work\staging\inject-iris-v9.log
set WIM=I:\MacbookISOBuildingSpace\work\iso-root\sources\boot.wim
set MNT=I:\MacbookISOBuildingSpace\work\mount-boot
set CMDFILE=I:\MacbookISOBuildingSpace\work\staging\a1706.cmd
set BCD1=I:\MacbookISOBuildingSpace\work\iso-root\efi\microsoft\boot\bcd
set BCD2=I:\MacbookISOBuildingSpace\work\iso-root\boot\bcd
> "%LOG%" echo start %DATE% %TIME%
attrib -R "%WIM%"
dism /Get-MountedImageInfo >> "%LOG%" 2>&1
if exist "%MNT%" (
  dism /Unmount-Image /MountDir:"%MNT%" /Discard >> "%LOG%" 2>&1
  rmdir /s /q "%MNT%"
)
mkdir "%MNT%"
dism /Mount-Image /ImageFile:"%WIM%" /Index:2 /MountDir:"%MNT%" >> "%LOG%" 2>&1
if errorlevel 1 goto fail
reg load HKLM\A1706V9 "%MNT%\Windows\System32\config\SYSTEM" >> "%LOG%" 2>&1
if errorlevel 1 goto failmnt
reg query "HKLM\A1706V9\Select" /v Current >> "%LOG%" 2>&1
reg query "HKLM\A1706V9\ControlSet001\Services\igfx" >> "%LOG%" 2>&1
if errorlevel 1 goto failreg
reg add "HKLM\A1706V9\ControlSet001\Services\igfx" /v Type /t REG_DWORD /d 1 /f >> "%LOG%" 2>&1
reg add "HKLM\A1706V9\ControlSet001\Services\igfx" /v Start /t REG_DWORD /d 0 /f >> "%LOG%" 2>&1
reg add "HKLM\A1706V9\ControlSet001\Services\igfx" /v ErrorControl /t REG_DWORD /d 0 /f >> "%LOG%" 2>&1
reg add "HKLM\A1706V9\ControlSet001\Services\igfx" /v Group /t REG_SZ /d Video /f >> "%LOG%" 2>&1
reg add "HKLM\A1706V9\ControlSet001\Services\igfx" /v ImagePath /t REG_EXPAND_SZ /d \SystemRoot\System32\drivers\igdkmd64.sys /f >> "%LOG%" 2>&1
reg add "HKLM\A1706V9\ControlSet001\Services\BasicDisplay" /v Start /t REG_DWORD /d 4 /f >> "%LOG%" 2>&1
if errorlevel 1 goto failreg
echo ----- igfx ----- >> "%LOG%"
reg query "HKLM\A1706V9\ControlSet001\Services\igfx" >> "%LOG%" 2>&1
echo ----- BasicDisplay Start ----- >> "%LOG%"
reg query "HKLM\A1706V9\ControlSet001\Services\BasicDisplay" /v Start >> "%LOG%" 2>&1
reg unload HKLM\A1706V9 >> "%LOG%" 2>&1
if errorlevel 1 goto failmnt
copy /y "%CMDFILE%" "%MNT%\Windows\System32\a1706.cmd" >> "%LOG%" 2>&1
if errorlevel 1 goto failmnt
dism /Unmount-Image /MountDir:"%MNT%" /Commit >> "%LOG%" 2>&1
if errorlevel 1 goto fail
attrib -R -S -H "%BCD1%"
attrib -R -S -H "%BCD2%"
echo ----- efi bcd ----- >> "%LOG%"
bcdedit /store "%BCD1%" /set {default} nointegritychecks on >> "%LOG%" 2>&1
if errorlevel 1 goto fail
bcdedit /store "%BCD1%" /enum {default} >> "%LOG%" 2>&1
echo ----- bios bcd ----- >> "%LOG%"
bcdedit /store "%BCD2%" /set {default} nointegritychecks on >> "%LOG%" 2>&1
if errorlevel 1 goto fail
bcdedit /store "%BCD2%" /enum {default} >> "%LOG%" 2>&1
echo SUCCESS>> "%LOG%"
exit /b 0
:failreg
echo FAIL>> "%LOG%"
reg unload HKLM\A1706V9 >> "%LOG%" 2>&1
goto failmnt
:failmnt
echo FAIL>> "%LOG%"
dism /Unmount-Image /MountDir:"%MNT%" /Discard >> "%LOG%" 2>&1
exit /b 1
:fail
echo FAIL>> "%LOG%"
exit /b 1
"""
inj = Path(r"I:\MacbookISOBuildingSpace\work\staging\inject-iris-v9.cmd")
data = inject.replace("\r\n", "\n").replace("\n", "\r\n").encode("ascii")
if b"\x00" in data:
    raise SystemExit("inject has nulls")
inj.write_bytes(data)
print("inject", inj.stat().st_size)
