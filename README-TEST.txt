Windows 10 Pro for MacBook Pro 2016 A1706
==========================================

Output ISO
----------
I:\MacbookISOBuildingSpace\out\Win10_Pro_A1706_SetupGUI.iso

What is on this disc
--------------------
Windows 10 Pro only (sources\ei.cfg and sources\install.wim).
sources\boot.wim is the original Microsoft Setup image.

$WinPEDriver$ contains every driver unpacked from Apple Boot Camp
041-88734 for this Mac, plus the Intel Thunderbolt driver:
Iris 550 graphics, Cirrus speakers (CS4206 and CS4208), Touch Bar
(AppleDFR), T1 (AppleSOC), keyboard, trackpad, Broadcom Wi-Fi,
Bluetooth, SSD, USB, and the rest of the Boot Camp INF set.

The same driver folders are inside the installed Windows at C:\Drivers.
At the end of Setup, Windows\Setup\Scripts\SetupComplete.cmd runs
pnputil so those drivers install on the first real boot.
The Boot Camp folder with Setup.exe is both on the ISO and in
C:\BootCamp if you need to run Apple's installer again.

Hotplug test on the Mac
-----------------------
Other systems already light this USB-C port. Windows drops the picture
at the logo, before Setup finishes loading drivers.

1. Wait about 45 seconds after the picture goes dark.
2. Unplug the dongle and plug it into a USB-C port on the other side.
3. Press Windows+Ctrl+Shift+B.
4. Press Windows+P, Down, Enter.

The Touch Bar strip and the Mac speakers start on the real Windows
desktop. They stay off during the Setup window even with the drivers
present. HDMI can still drop at the logo.

Boot
----
Ventoy's normal mode often goes black on this Mac after you pick an ISO.
Boot Camp Assistant copies onto FAT32, so an install.wim over 4 GB can
fail that copy. A USB made as GPT/UEFI (Rufus) can hold this image.
