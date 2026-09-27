@echo off
set LOG=I:\MacbookISOBuildingSpace\work\staging\hive-inspect.txt
set HIV=I:\MacbookISOBuildingSpace\A1706Logs\SYSTEM.hiv
> "%LOG%" echo inspect
for %%A in ("%HIV%") do >> "%LOG%" echo size %%~zA
reg load HKLM\A1706HIV "%HIV%" >> "%LOG%" 2>&1
if errorlevel 1 exit /b 1
reg query HKLM\A1706HIV\Select >> "%LOG%" 2>&1
reg query "HKLM\A1706HIV\ControlSet001\Enum\PCI\VEN_8086&DEV_1927&SUBSYS_015D106B&REV_0A\3&11583659&0&10" >> "%LOG%" 2>&1
reg query "HKLM\A1706HIV\ControlSet001\Services\igfx" >> "%LOG%" 2>&1
reg unload HKLM\A1706HIV >> "%LOG%" 2>&1
echo SUCCESS>> "%LOG%"
