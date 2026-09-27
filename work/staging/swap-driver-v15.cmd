@echo off
setlocal
set LOG=I:\MacbookISOBuildingSpace\work\staging\dism-v15-boot.log
set WIM=I:\MacbookISOBuildingSpace\work\iso-root\sources\boot.wim
set MNT=I:\MacbookISOBuildingSpace\work\mount-boot
set SIGNED=I:\MacbookISOBuildingSpace\work\iris-extract\signed
set LIST=I:\MacbookISOBuildingSpace\work\staging\drivers-v15-before.txt
set AFTER=I:\MacbookISOBuildingSpace\work\staging\drivers-v15-after.txt
echo MOUNT>"%LOG%"
dism /Mount-Image /ImageFile:"%WIM%" /Index:2 /MountDir:"%MNT%" >>"%LOG%" 2>&1
if errorlevel 1 (
  echo MOUNT_FAIL>>"%LOG%"
  exit /b 1
)
echo GET>>"%LOG%"
dism /Image:"%MNT%" /Get-Drivers /Format:List >"%LIST%" 2>&1
python I:\MacbookISOBuildingSpace\work\staging\find_slim_oem.py "%LIST%" >I:\MacbookISOBuildingSpace\work\staging\slim-oem.txt
set /p OEM=<I:\MacbookISOBuildingSpace\work\staging\slim-oem.txt
echo OEM=%OEM%>>"%LOG%"
if "%OEM%"=="" (
  echo NO_SLIM>>"%LOG%"
  dism /Unmount-Image /MountDir:"%MNT%" /Discard >>"%LOG%" 2>&1
  exit /b 1
)
if "%OEM%"=="MISSING" (
  echo NO_SLIM>>"%LOG%"
  dism /Unmount-Image /MountDir:"%MNT%" /Discard >>"%LOG%" 2>&1
  exit /b 1
)
echo REMOVE>>"%LOG%"
dism /Image:"%MNT%" /Remove-Driver /Driver:%OEM% >>"%LOG%" 2>&1
if errorlevel 1 (
  echo REMOVE_FAIL>>"%LOG%"
  dism /Unmount-Image /MountDir:"%MNT%" /Discard >>"%LOG%" 2>&1
  exit /b 1
)
echo ADD>>"%LOG%"
dism /Image:"%MNT%" /Add-Driver /Driver:"%SIGNED%" >>"%LOG%" 2>&1
if errorlevel 1 (
  echo ADD_FAIL>>"%LOG%"
  dism /Unmount-Image /MountDir:"%MNT%" /Discard >>"%LOG%" 2>&1
  exit /b 1
)
echo GET_AFTER>>"%LOG%"
dism /Image:"%MNT%" /Get-Drivers /Format:List >"%AFTER%" 2>&1
python I:\MacbookISOBuildingSpace\work\staging\check_drivers_v15.py "%AFTER%" >>"%LOG%" 2>&1
if errorlevel 1 (
  echo CHECK_FAIL>>"%LOG%"
  dism /Unmount-Image /MountDir:"%MNT%" /Discard >>"%LOG%" 2>&1
  exit /b 1
)
echo BASIC>>"%LOG%"
reg load HKLM\A1706V15 "%MNT%\Windows\System32\config\SYSTEM" >>"%LOG%" 2>&1
reg query HKLM\A1706V15\ControlSet001\Services\BasicDisplay /v Start >>"%LOG%" 2>&1
reg query HKLM\A1706V15\ControlSet001\Services\igfx /v Start >>"%LOG%" 2>&1
reg unload HKLM\A1706V15 >>"%LOG%" 2>&1
echo COMMIT>>"%LOG%"
dism /Unmount-Image /MountDir:"%MNT%" /Commit >>"%LOG%" 2>&1
if errorlevel 1 (
  echo COMMIT_FAIL>>"%LOG%"
  exit /b 1
)
echo DONE>>"%LOG%"
exit /b 0
