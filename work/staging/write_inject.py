from pathlib import Path
text = r"""@echo off
setlocal
set LOG=I:\MacbookISOBuildingSpace\work\staging\inject-iris-v5.log
set WIM=I:\MacbookISOBuildingSpace\work\iso-root\sources\boot.wim
set MNT=I:\MacbookISOBuildingSpace\work\mount-boot
set INF=I:\MacbookISOBuildingSpace\work\iso-root\$WinPEDriver$\IntelIrisSetup\igdiris64.inf
set CMDFILE=I:\MacbookISOBuildingSpace\work\staging\a1706.cmd
set BCD1=I:\MacbookISOBuildingSpace\work\iso-root\efi\microsoft\boot\bcd
set BCD2=I:\MacbookISOBuildingSpace\work\iso-root\boot\bcd
> "%LOG%" echo start %DATE% %TIME%
attrib -R "%WIM%"
dism /Get-MountedImageInfo >> "%LOG%" 2>&1
if exist "%MNT%" rmdir /s /q "%MNT%"
mkdir "%MNT%"
dism /Mount-Image /ImageFile:"%WIM%" /Index:2 /MountDir:"%MNT%" >> "%LOG%" 2>&1
if errorlevel 1 goto fail
dism /Image:"%MNT%" /Add-Driver /Driver:"%INF%" /ForceUnsigned >> "%LOG%" 2>&1
if errorlevel 1 goto fail
copy /y "%CMDFILE%" "%MNT%\Windows\System32\a1706.cmd" >> "%LOG%" 2>&1
if errorlevel 1 goto fail
dism /Unmount-Image /MountDir:"%MNT%" /Commit >> "%LOG%" 2>&1
if errorlevel 1 goto fail
attrib -R -S -H "%BCD1%"
attrib -R -S -H "%BCD2%"
echo ----- efi bcd ----- >> "%LOG%"
bcdedit /store "%BCD1%" /enum {default} >> "%LOG%" 2>&1
bcdedit /store "%BCD1%" /set {default} testsigning on >> "%LOG%" 2>&1
echo ----- bios bcd ----- >> "%LOG%"
bcdedit /store "%BCD2%" /enum {default} >> "%LOG%" 2>&1
bcdedit /store "%BCD2%" /set {default} testsigning on >> "%LOG%" 2>&1
echo SUCCESS>> "%LOG%"
exit /b 0
:fail
echo FAIL>> "%LOG%"
dism /Unmount-Image /MountDir:"%MNT%" /Discard >> "%LOG%" 2>&1
exit /b 1
"""
p = Path(r"I:\MacbookISOBuildingSpace\work\staging\inject-iris-v5.cmd")
p.write_bytes(text.replace("\n", "\r\n").encode("ascii"))
print("wrote", p, p.stat().st_size)
