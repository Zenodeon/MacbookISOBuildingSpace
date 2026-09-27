@echo off
set LOG=I:\MacbookISOBuildingSpace\work\staging\dism-v14.log
echo MOUNT>"%LOG%"
dism /Mount-Image /ImageFile:"I:\MacbookISOBuildingSpace\work\iso-root\sources\install.wim" /Index:1 /MountDir:"I:\MacbookISOBuildingSpace\work\mount-install" >>"%LOG%" 2>&1
if errorlevel 1 (
  echo MOUNT_FAIL>>"%LOG%"
  exit /b 1
)
echo ADD>>"%LOG%"
dism /Image:"I:\MacbookISOBuildingSpace\work\mount-install" /Add-Driver /Driver:"I:\MacbookISOBuildingSpace\work\iris-extract\signed" >>"%LOG%" 2>&1
if errorlevel 1 (
  echo ADD_FAIL>>"%LOG%"
  dism /Unmount-Image /MountDir:"I:\MacbookISOBuildingSpace\work\mount-install" /Discard >>"%LOG%" 2>&1
  exit /b 1
)
echo COMMIT>>"%LOG%"
dism /Unmount-Image /MountDir:"I:\MacbookISOBuildingSpace\work\mount-install" /Commit >>"%LOG%" 2>&1
echo DONE>>"%LOG%"
exit /b 0
