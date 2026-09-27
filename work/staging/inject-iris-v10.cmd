@echo off
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
