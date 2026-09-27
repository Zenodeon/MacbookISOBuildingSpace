@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
if errorlevel 1 exit /b 1
cl /nologo /O1 /MT /W3 /Fe:I:\MacbookISOBuildingSpace\work\staging\a1706dlg.exe I:\MacbookISOBuildingSpace\work\staging\a1706dlg.c /link /SUBSYSTEM:WINDOWS user32.lib
if errorlevel 1 exit /b 1
echo CL_OK
