from pathlib import Path

cmd_path = Path(r"I:\MacbookISOBuildingSpace\work\staging\a1706.cmd")
raw = cmd_path.read_bytes()
if b"\x00" in raw:
    raise SystemExit("a1706.cmd is not single-byte")
text = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
text = text.replace(b"A1706 setup log v9", b"A1706 setup log v10", 1)
old = (
    b'set "MSG=step after-wpeinit"\n'
    b"call :note\n"
    b'set "MSG=iris boot-start in image, skip drvload"\n'
    b"call :note\n"
)
new = (
    b'set "MSG=step after-wpeinit"\n'
    b"call :note\n"
    b'set "MSG=v10 BasicDisplay stays on, start igfx after log"\n'
    b"call :note\n"
    b"call :dump sc query igfx\n"
    b"call :dump sc query BasicDisplay\n"
    b'set "MSG=step start igfx"\n'
    b"call :note\n"
    b"call :dump sc start igfx\n"
    b"call :dump sc query igfx\n"
)
if old not in text:
    raise SystemExit("early block missing")
text = text.replace(old, new, 1)
old_msg = b'set "MSG=v9 clean hive, iris boot-start, BasicDisplay disabled"\n'
new_msg = b'set "MSG=v10 igfx demand-start, BasicDisplay left enabled"\n'
if old_msg not in text:
    raise SystemExit("late message missing")
text = text.replace(old_msg, new_msg, 1)
for bad in (b"remove-device", b"savehiv", b"SYSTEM.hiv", b"setup log v9", b"BasicDisplay disabled"):
    if bad in text:
        raise SystemExit("leftover " + bad.decode())
for good in (b"A1706 setup log v10", b"step start igfx", b"sc start igfx", b"BasicDisplay stays on"):
    if good not in text:
        raise SystemExit("missing " + good.decode())
cmd_path.write_bytes(text.replace(b"\n", b"\r\n"))
print("a1706.cmd", cmd_path.stat().st_size)

inject = r"""@echo off
setlocal
set LOG=I:\MacbookISOBuildingSpace\work\staging\inject-iris-v10.log
set WIM=I:\MacbookISOBuildingSpace\work\iso-root\sources\boot.wim
set MNT=I:\MacbookISOBuildingSpace\work\mount-boot
set CMDFILE=I:\MacbookISOBuildingSpace\work\staging\a1706.cmd
set BCD1=I:\MacbookISOBuildingSpace\work\iso-root\efi\microsoft\boot\bcd
set BCD2=I:\MacbookISOBuildingSpace\work\iso-root\boot\bcd
> "%LOG%" echo start %DATE% %TIME%
attrib -R "%WIM%"
if exist "%MNT%" (
  dism /Unmount-Image /MountDir:"%MNT%" /Discard >> "%LOG%" 2>&1
  rmdir /s /q "%MNT%"
)
mkdir "%MNT%"
dism /Mount-Image /ImageFile:"%WIM%" /Index:2 /MountDir:"%MNT%" >> "%LOG%" 2>&1
if errorlevel 1 goto fail
reg load HKLM\A1706V10 "%MNT%\Windows\System32\config\SYSTEM" >> "%LOG%" 2>&1
if errorlevel 1 goto failmnt
echo ----- before ----- >> "%LOG%"
reg query "HKLM\A1706V10\ControlSet001\Services\igfx" /v Start >> "%LOG%" 2>&1
reg query "HKLM\A1706V10\ControlSet001\Services\BasicDisplay" /v Start >> "%LOG%" 2>&1
reg add "HKLM\A1706V10\ControlSet001\Services\igfx" /v Start /t REG_DWORD /d 3 /f >> "%LOG%" 2>&1
if errorlevel 1 goto failreg
reg delete "HKLM\A1706V10\ControlSet001\Control\CriticalDeviceDatabase\pci#ven_8086&dev_1927" /f >> "%LOG%" 2>&1
if errorlevel 1 goto failreg
reg delete "HKLM\A1706V10\ControlSet001\Control\CriticalDeviceDatabase\pci#ven_8086&dev_1927&subsys_015d106b&rev_0a" /f >> "%LOG%" 2>&1
if errorlevel 1 goto failreg
echo ----- after ----- >> "%LOG%"
reg query "HKLM\A1706V10\ControlSet001\Services\igfx" >> "%LOG%" 2>&1
reg query "HKLM\A1706V10\ControlSet001\Services\BasicDisplay" /v Start >> "%LOG%" 2>&1
reg unload HKLM\A1706V10 >> "%LOG%" 2>&1
if errorlevel 1 goto failmnt
copy /y "%CMDFILE%" "%MNT%\Windows\System32\a1706.cmd" >> "%LOG%" 2>&1
if errorlevel 1 goto failmnt
dism /Unmount-Image /MountDir:"%MNT%" /Commit >> "%LOG%" 2>&1
if errorlevel 1 goto fail
attrib -R -S -H "%BCD1%"
attrib -R -S -H "%BCD2%"
bcdedit /store "%BCD1%" /set {default} nointegritychecks on >> "%LOG%" 2>&1
bcdedit /store "%BCD2%" /set {default} nointegritychecks on >> "%LOG%" 2>&1
bcdedit /store "%BCD1%" /enum {default} >> "%LOG%" 2>&1
bcdedit /store "%BCD2%" /enum {default} >> "%LOG%" 2>&1
echo SUCCESS>> "%LOG%"
exit /b 0
:failreg
echo FAIL>> "%LOG%"
reg unload HKLM\A1706V10 >> "%LOG%" 2>&1
goto failmnt
:failmnt
echo FAIL>> "%LOG%"
dism /Unmount-Image /MountDir:"%MNT%" /Discard >> "%LOG%" 2>&1
exit /b 1
:fail
echo FAIL>> "%LOG%"
exit /b 1
"""
inj = Path(r"I:\MacbookISOBuildingSpace\work\staging\inject-iris-v10.cmd")
data = inject.replace("\r\n", "\n").replace("\n", "\r\n").encode("ascii")
inj.write_bytes(data)
print("inject", inj.stat().st_size)
