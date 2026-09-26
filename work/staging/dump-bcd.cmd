@echo off
bcdedit /store "I:\MacbookISOBuildingSpace\work\iso-root\efi\microsoft\boot\bcd" /enum {default} > "I:\MacbookISOBuildingSpace\work\staging\bcd-efi.txt" 2>&1
bcdedit /store "I:\MacbookISOBuildingSpace\work\iso-root\boot\bcd" /enum {default} > "I:\MacbookISOBuildingSpace\work\staging\bcd-bios.txt" 2>&1
