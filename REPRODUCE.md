# Reproduce the A1706 Setup GUI fix

This is the build spec for the Windows 10 Pro installer that put a Setup window on HDMI and installed onto a MacBook Pro 2016 A1706. `WorkingReport.md` is the short history. This file is the contract for an automatic patcher.

The boot that worked is `out\Win10_Pro_A1706_SetupGUI_v17.iso`. The user confirmed the Setup window was visible on HDMI, then installed Windows and reached the desktop. Do not rebuild that history. Implement the end state below.

## Machine

- MacBook Pro 2016, 13-inch, Touch Bar, model A1706, board MacBookPro13,2
- Intel Iris Graphics 550, `PCI\VEN_8086&DEV_1927`
- Subsystem on this machine: `PCI\VEN_8086&DEV_1927&SUBSYS_015D106B`
- Device instance restarted by the script: `PCI\VEN_8086&DEV_1927&SUBSYS_015D106B&REV_0A\3&11583659&0&10`
- T1 security chip, not T2
- USB-C only. All four ports are Thunderbolt 3. HDMI is DisplayPort alt-mode from the Iris GPU through Alpine Ridge
- The internal eDP panel is unplugged. Apple EFI GOP mirrors to the USB-C dongle until Windows takes the iGPU. Windows then prefers the missing internal panel and the external picture dies. Basic Display does not light HDMI
- Official Boot Camp for this Mac is Windows 10, not Windows 11

A patcher aimed at this exact model can keep that instance id. A patcher that only knows the hardware id should restart the display device whose id contains `PCI\VEN_8086&DEV_1927&SUBSYS_015D106B`.

## What the patcher consumes

1. A Windows 10 64-bit installer, build 19041, en-US, one image, edition Professional. The image used here was 19041.3803. `sources\ei.cfg` is:

```
[EditionID]
Professional
[Channel]
Retail
[VL]
0
```

2. Intel Graphics Driver package 15.45.34.5174, Windows version 21.20.16.5174. File `win64_15.45.5174.exe`, 255,770,016 bytes, SHA256 `AAB51027DAC8210BCA98B6679472B2A00AB15A5D4F8A6B777259200DE52E48E2`. Direct URL: `https://downloadmirror.intel.com/30195/a08/win64_15.45.5174.exe`. This is the last official package that still lists Iris Graphics 550 / `DEV_1927`. Current 31.0.101 packages do not.

3. Apple Boot Camp 6.1 package 041-88734, product version 6.1.6660. URL: `https://swcdn.apple.com/content/downloads/28/47/041-88734-A_Q0SKN07BL0/7knxzec1xmojr5x5t7xnu5a4u6lslmlf9v/BootCampESD.pkg`. Unpack xar, then bzip2 Payload, then cpio (magic `070707`), then `Library/Application Support/BootCamp/WindowsSupport.dmg`. The Windows support tree has `BootCamp\Setup.exe` and a `Drivers` folder.

## What the patcher writes

One ISO, label `ESD-ISO`, El Torito BIOS plus EFI boot, no optimization flag. Volume label matters only as a human check. The running script finds the installer by the file `\sources\install.wim`, not by the label.

`oscdimg` line, with no `-o`:

```
oscdimg -m -u2 -udfver102 -lESD-ISO -bootdata:2#p0,e,b<iso-root>\boot\etfsboot.com#pEF,e,b<iso-root>\efi\microsoft\boot\efisys.bin <iso-root> <out>.iso
```

The ADK copy used here is `C:\Program Files (x86)\Windows Kits\10\Assessment and Deployment Kit\Deployment Tools\amd64\Oscdimg\oscdimg.exe`.

## Image map

`boot.wim` index 2 is Setup. `install.wim` index 1 is Windows 10 Pro.

| Piece | Where it has to be |
| --- | --- |
| Signed `igdlh64.inf` + `igdlh.cat` | Driver store of `boot.wim` index 2 and of `install.wim` index 1 |
| `a1706.cmd`, `a1706iris.exe`, `a1706dlg.exe`, `a1706cue.exe`, `winpeshl.ini` | `\Windows\System32` inside `boot.wim` index 2 |
| Allowed Boot Camp INF folders | ISO root `\$WinPEDriver$` |
| Full Boot Camp driver tree, including folders banned from the boot path | `\Drivers` inside `install.wim` |
| `BootCamp\Setup.exe` and its `Drivers` EXEs | `\BootCamp` inside `install.wim`, and on the ISO root |
| `SetupComplete.cmd` | `\Windows\Setup\Scripts\SetupComplete.cmd` inside `install.wim` |
| `autounattend.xml` | ISO root. Accept EULA and point at driver paths. No disk layout |

`winpeshl.ini` in the Setup image must be only:

```
[LaunchApps]
%SYSTEMROOT%\System32\a1706.cmd
```

Stock Setup starts `setup.exe` from `winpeshl.ini`. That races the GPU restart and the HDMI picture dies before the window is drawn. `a1706.cmd` calls `wpeinit`, waits for Iris, then starts `setup.exe` itself.

## Signed Iris package

Unpack `win64_15.45.5174.exe` with 7-Zip. The folder passed to DISM must contain Intel's original `igdlh64.inf` and `igdlh.cat`. Do not edit the INF. Intel's catalog hashes those INF bytes. A rewritten INF with the same `DriverVer` and a copied `.cat` is still unsigned.

Facts the patcher should check after unpack, and refuse to continue if any fail:

- `DriverVer=11/08/2020,21.20.16.5174`
- `CatalogFile=igdlh.cat`
- The Windows 10 section for `DEV_1927` on build 14393 and newer is `iSKLD_w10_DS`
- Service `igfx` is `StartType=3` (demand). Leave it there
- `igfxCUIService` depends on `SENS`. WinPE has no `SENS`, so that service fails with error 1075. Ignore it. The display device still reaches Started

Add it with elevated DISM. Do not pass `/ForceUnsigned`.

```
dism /Mount-Image /ImageFile:<boot.wim> /Index:2 /MountDir:<mount>
dism /Image:<mount> /Add-Driver /Driver:<signed-folder>
dism /Unmount-Image /MountDir:<mount> /Commit
```

Repeat `/Add-Driver` for `install.wim` index 1. If the package is already in that image, do not add it a second time.

After the boot-image add, the offline `SYSTEM` hive must still show:

- `ControlSet001\Services\BasicDisplay` Start = `0x1`
- `ControlSet001\Services\igfx` Start = `0x3`

Clear the read-only bit on `boot.wim` before an update. DISM mount and commit need an elevated process. `wimlib-imagex` can add the loose files without elevation. SACL warnings from wimlib without admin are harmless.

`wimlib-imagex update <boot.wim> 2` reads its command file on stdin, not as an argument:

```
add "<staging>\a1706.cmd" \Windows\System32\a1706.cmd
add "<staging>\a1706iris.exe" \Windows\System32\a1706iris.exe
add "<staging>\a1706dlg.exe" \Windows\System32\a1706dlg.exe
add "<staging>\a1706cue.exe" \Windows\System32\a1706cue.exe
add "<staging>\winpeshl.ini" \Windows\System32\winpeshl.ini
```

Use the files already in `work\staging\`. Do not regenerate `a1706.cmd` from a description. It has to stay ASCII, CRLF, no `FF FE` BOM, no NUL bytes. A UTF-16 script breaks under `cmd`.

## Boot-path driver allow list

ISO root `\$WinPEDriver$` on the working image contains only these folders:

- AppleBluetoothBroadcom64
- AppleCamera64
- AppleDFR64
- AppleDisplayInstaller64
- AppleKeyboardInstaller64
- AppleMultiTouchTrackPadInstaller64
- AppleMultiTouchTrackPadProInstaller64
- AppleNullDriver64
- AppleODDInstaller64
- AppleSOC64
- AppleSPIDevice
- AppleSPIKeyboard
- AppleSPITrackpad
- AppleSSD64
- AppleUSBCompositeDevice64
- AppleWirelessMouse64
- AppleWirelessTrackpad64
- AsixSetup64
- BroadcomBluetooth64
- BroadcomBluetoothHID64
- BroadcomCardReader64
- BroadcomComController64
- BroadcomEthernet64
- BroadcomWirelessWin8x64
- CirrusAudioCS4208x64
- IntelEthernetInstaller64
- SerialIO

`wpeinit` and `autounattend.xml` both import this directory. Anything placed here is in the Setup boot path.

Banned from `\$WinPEDriver$` and from any other Setup boot path:

- `IntelHDGraphics64` and `IntelIrisSetup`. That is the 2016 Boot Camp graphics package, `igdlh64.inf` version `07/01/2016,20.19.15.4483`. On this WinPE it fails the device with `CM_PROB_FAILED_ADD` / `0xC00000BB`
- Any hand-written slim INF such as `igdiris64.inf`. It has no `CatalogFile`. Setup stops with "Windows Setup could not install one or more boot-critical drivers"
- `Thunderbolt` (`tbt81x.inf`). The catalog is present. The INF also copies `setup.msi`, and that file is not in the Boot Camp tree, so import fails `0x80070002` and aborts the package. HDMI does not need it
- `CirrusAudioCS4206x64` (`cs420x_46.inf`). This Mac's codec is CS4208. CS4206 is missing `CS420x.cat` and `CS420x86.cat`

`autounattend.xml` on the working ISO only accepts the EULA and sets two driver paths: `\$WinPEDriver$` for Windows PE, and `C:\Drivers` for specialize. It must not contain `DiskConfiguration`, `ImageInstall`, or any wipe of the Apple disk.

## Inside the installed Windows

Copy the full unpacked Boot Camp driver tree to `\Drivers` in `install.wim`, including the folders banned from the boot path. Copy `BootCamp\Setup.exe` and its driver EXEs to `\BootCamp`. Copy `work\staging\SetupComplete.cmd` to `\Windows\Setup\Scripts\SetupComplete.cmd`. Its whole body is:

```
@echo off
pnputil /add-driver %SystemDrive%\Drivers\*.inf /subdirs /install
```

The signed 2021 package is already in the install image's driver store, and its `DriverVer` is newer than 20.19.15.4483, so the first boot keeps Iris 21.20.16.5174 even though `\Drivers\IntelHDGraphics64` is also present. After Windows is running, do not run that 2016 graphics installer.

`C:\BootCamp\Setup.exe` is required after the first desktop boot. The INF pass gives a moving cursor. Right-click, two-finger scroll, the Touch Bar, and the T1 chip come from the EXEs and `BootCamp.msi` next to `Setup.exe`. That Setup.exe's Intel folder is chipset, Management Engine, and ethernet only. It does not contain the Iris package.

Thunderbolt stays uninstalled. The missing `setup.msi` is the Intel Thunderbolt application, not the HDMI path.

## Runtime order

`a1706.cmd` is the Setup session. Ventoy WIMBOOT copies it into the RAM disk `X:`. `install.wim` and `\$WinPEDriver$` stay on the ISO. The USB has to stay plugged in. A reboot reloads the WIM and drops the RAM session, so the GPU switch cannot live only in the running hive. It has to be baked into `boot.wim`, then applied again by this script on each Setup boot.

Order in the script:

1. Probe drives C through Z, skipping the loop's own X. A drive is writable if creating and deleting `a1706-write.test` works. Append logs to `X:\a1706-setup-log.txt` and to `<drive>\A1706Logs\a1706-setup-log.txt`. Append. Do not copy over the script log.
2. `wpeinit`.
3. One `pnputil /restart-device` on the Iris instance above. Do not restart it twice. Do not delete the published OEM package.
4. `drvload` only these three, and only if `\$WinPEDriver$\AppleSPIKeyboard\AppleSPIKeyboard.inf` is found: `CirrusAudioCS4208x64\cs4208_36.inf`, `AppleSPIKeyboard\AppleSPIKeyboard.inf`, `AppleDFR64\AppleDFR.inf`.
5. Poll up to 30 times. Each pass writes `pnputil /enum-devices /class Display` to `X:\a1706-cmd-out.txt` and runs `a1706iris.exe`. Exit 0 means the file contains both `Iris` and `Started` after NUL bytes are stripped. `pnputil` output is often UTF-16, so `findstr` misses it. Wait `ping -n 3` between misses.
6. If Iris never starts, log `ERROR iris not started` and do not start `setup.exe`.
7. On success, run `DisplaySwitch.exe /external` once. No `/clone`, no `/extend`, no repeat loop.
8. Set the install source to the first drive that has `\sources\install.wim`. Do not detect it with `vol` plus `findstr`. That output is UTF-16 and the label check falsely fails while the drive is `ESD-ISO`.
9. Start `a1706dlg.exe`, log `launching setup`, then `X:\sources\setup.exe /InstallFrom:<that drive>\sources\install.wim`.

`a1706iris.exe` is a console program, `cl /nologo /O1 /MT /W3`, kernel32 only. Do not define `UNICODE`. It returns 0 only when both substrings are present, else 1.

`a1706dlg.exe` is a Windows subsystem program (`/SUBSYSTEM:WINDOWS`, `user32.lib`). Every 500 ms it copies `X:\Windows\Panther\setuperr.log` and `setupact.log` into `X:\` and each `\A1706Logs\`, and it appends visible `#32770` and "Windows Setup" window text to `a1706-after-setup.txt`. DirectUI body text on the boot-critical dialog is not visible to `GetWindowText`. The language page body is.

`a1706cue.exe` only beeps or taps Caps Lock. Exit 3 means `PlaySound` had no audio device. It is not part of the display fix. Narrator is started by the script and is not part of the display fix.

`sc.exe` is not in this WinPE. `pnputil` can return errorlevel 0 when its text says the operation failed. Trust the Iris-and-Started check, not the restart errorlevel.

## Boot and install

1. On the Mac, in macOS, use Boot Camp Assistant only to shrink the APFS volume and create the `BOOTCAMP` partition. Windows Setup cannot resize APFS. Do not give Boot Camp Assistant this custom ISO. Assistant downloads Apple's 2016 driver pack and will put the old graphics package back into the install.
2. When the Mac restarts into Apple's installer, hold Option and boot the Ventoy USB instead.
3. Copy the ISO onto the Ventoy data partition, not into `\A1706Logs`.
4. In Ventoy, press `w` for WIMBOOT. Normal mode emulates a CD and goes black on this Apple EFI after the ISO is chosen.
5. Leave the USB plugged in. `X:` is the RAM disk. The Ventoy partition is the writable log drive. The ISO volume is the drive whose root contains `\sources\install.wim`.
6. On the disk screen, select only the `BOOTCAMP` partition and format it. Leave EFI, Macintosh HD, and Recovery in place.
7. After the first desktop boot, confirm Display adapters is Intel(R) Iris(TM) Graphics 550, version 21.20.16.5174. Then run `C:\BootCamp\Setup.exe` as administrator and reboot. Do not run `C:\Drivers\IntelHDGraphics64`.
8. Trackpad: two-finger click, or a click in the bottom-right corner, is right-click. Two-finger drag is scroll. The Touch Bar lights as the function-key strip after that Setup.exe reboot.

## Checks a patcher must fail closed on

- `boot.wim` index 2 still contains `igdiris64.inf` or any other unsigned Iris INF
- `igdlh64.inf` in the driver store is not byte-identical to Intel's file, or `igdlh.cat` is absent
- Basic Display Start is not 1, or `igfx` Start is not 3
- `\$WinPEDriver$` contains Thunderbolt, CS4206, IntelHDGraphics64, IntelIrisSetup, or a slim Iris INF
- `winpeshl.ini` launches anything except `a1706.cmd`
- `a1706.cmd` is UTF-16 or contains a NUL
- `autounattend.xml` partitions or formats a disk
- The ISO label was set with `oscdimg -o`

## Do not repeat these

These were built and booted, or deliberately not booted, and they are not the fix:

- `drvload` of the full graphics package onto `X:`. The second copy of `igd11dxva64.dll` fills the RAM disk, error 112 / `0x80070070`
- Disabling Basic Display, or setting its Start to 4. Setup then has no fallback and writes no log
- Setting `igfx` to boot-start
- Transplanting a live `SYSTEM` hive into `boot.wim`. That image did not boot
- Loading every INF under `\$WinPEDriver$` at `drvload` time. That bugchecked WinPE. `wpeinit` may import the allow list; the script itself drvloads only the three INFs above
- Turning on test signing, `bcdedit /set nointegritychecks on`, or DISM `/ForceUnsigned`, and expecting Setup to accept an unsigned boot-critical driver. Those switches only let WinPE load the driver. They do not let Setup copy it into the new Windows. There is no `setup.exe` switch, unattend value, or LabConfig value that skips "could not install one or more boot-critical drivers"
- Pointing a rewritten INF at `igdlh.cat`
- Starting `setup.exe` before the display list says Iris is Started. The v16 boot reached the language page in the log and still showed a black HDMI, because Setup opened about one second after the script banner
- Detecting the ISO with `findstr` on `vol` output
- Deleting older ISOs as part of the build

`testsigning` is already `Yes` in the BCD stores of the image that was iterated on. Leave an existing BCD alone. A fresh stock ISO plus the signed catalog does not need signature checks disabled.

## How to tell the rebuild worked

During Setup, `\A1706Logs\a1706-setup-log.txt` on the Ventoy partition contains `iris started` and then `launching setup`, and the HDMI dongle shows the Windows Setup language page. It must not show the boot-critical driver dialog.

After the first real boot, Device Manager's display adapter is Iris Graphics 550 version 21.20.16.5174, and the picture is still on HDMI. Right-click, scroll, and the Touch Bar come from `C:\BootCamp\Setup.exe`, not from another ISO.
