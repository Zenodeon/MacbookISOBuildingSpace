@echo off
mkdir I:\MacbookISOBuildingSpace\work\staging\iris-test 2>nul
subst X: I:\MacbookISOBuildingSpace\work\staging\iris-test
>X:\a1706-cmd-out.txt echo Device Description: Intel(R) Iris(TM) Graphics 550
>>X:\a1706-cmd-out.txt echo Status: Started
I:\MacbookISOBuildingSpace\work\staging\a1706iris.exe
echo HIT=%ERRORLEVEL%
>X:\a1706-cmd-out.txt echo Status: Problem
I:\MacbookISOBuildingSpace\work\staging\a1706iris.exe
echo MISS=%ERRORLEVEL%
python I:\MacbookISOBuildingSpace\work\staging\write_utf16_dump.py
I:\MacbookISOBuildingSpace\work\staging\a1706iris.exe
echo UTF=%ERRORLEVEL%
subst X: /d
echo DONE
