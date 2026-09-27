@echo off
setlocal
set LOG=I:\MacbookISOBuildingSpace\work\staging\inject-hive-v8.log
set WIM=I:\MacbookISOBuildingSpace\work\iso-root\sources\boot.wim
set MNT=I:\MacbookISOBuildingSpace\work\mount-boot
set HIV=I:\MacbookISOBuildingSpace\work\staging\SYSTEM.v8.hiv
set CMDFILE=I:\MacbookISOBuildingSpace\work\staging\a1706.cmd
> "%LOG%" echo start %DATE% %TIME%
reg load HKLM\A1706V8 "%HIV%" >> "%LOG%" 2>&1
if errorlevel 1 goto fail
reg add "HKLM\A1706V8\ControlSet001\Services\igfx" /v ImagePath /t REG_EXPAND_SZ /d \SystemRoot\System32\drivers\igdkmd64.sys /f >> "%LOG%" 2>&1
if errorlevel 1 goto failreg
reg unload HKLM\A1706V8 >> "%LOG%" 2>&1
if errorlevel 1 goto fail
attrib -R "%WIM%"
if exist "%MNT%" rmdir /s /q "%MNT%"
mkdir "%MNT%"
dism /Mount-Image /ImageFile:"%WIM%" /Index:2 /MountDir:"%MNT%" >> "%LOG%" 2>&1
if errorlevel 1 goto fail
copy /y "%HIV%" "%MNT%\Windows\System32\config\SYSTEM" >> "%LOG%" 2>&1
if errorlevel 1 goto failmnt
del /q "%MNT%\Windows\System32\config\SYSTEM.LOG" "%MNT%\Windows\System32\config\SYSTEM.LOG1" "%MNT%\Windows\System32\config\SYSTEM.LOG2" >> "%LOG%" 2>&1
copy /y "%CMDFILE%" "%MNT%\Windows\System32\a1706.cmd" >> "%LOG%" 2>&1
if errorlevel 1 goto failmnt
dism /Unmount-Image /MountDir:"%MNT%" /Commit >> "%LOG%" 2>&1
if errorlevel 1 goto fail
echo SUCCESS>> "%LOG%"
exit /b 0
:failreg
reg unload HKLM\A1706V8 >> "%LOG%" 2>&1
goto fail
:failmnt
echo FAIL>> "%LOG%"
dism /Unmount-Image /MountDir:"%MNT%" /Discard >> "%LOG%" 2>&1
exit /b 1
:fail
echo FAIL>> "%LOG%"
exit /b 1
