# Working report

MacBook Pro 2016 A1706, Iris Graphics 550 (`PCI\VEN_8086&DEV_1927`). The internal panel is unplugged. HDMI is the USB-C dongle. Boot the ISO with Ventoy `w`. Logs are `\A1706Logs` on the Ventoy partition.

## What put a picture on HDMI

The file is named v13, `out\Win10_Pro_A1706_SetupGUI_v13.iso`. That number is just where the filenames started keeping score. Another six or seven ISOs came before the count, and they never got a number. HDMI stayed dark through all of those.

The driver that started is Intel 21.20.16.5174 (package 15.45.34.5174). It was staged offline in `boot.wim` as the slim unsigned `igdiris64.inf`, published as `oem0.inf`. After the log was written, `pnputil /restart-device` ran on:

`PCI\VEN_8086&DEV_1927&SUBSYS_015D106B&REV_0A\3&11583659&0&10`

Basic Display stayed running (`Start=1`). The later device list showed Intel(R) Iris(TM) Graphics 550, class Display, status Started. That is the boot that lit HDMI.

## Leave these alone

- Do not `drvload` the graphics package onto the Setup RAM disk. The full package filled that disk.
- Do not disable Basic Display. Setup then had no fallback and produced no log.
- Do not set `igfx` to boot-start.
- Do not put a live `SYSTEM` hive back into `boot.wim`. That image did not boot.

## Setup after the picture

The log ends when `X:\sources\setup.exe` starts. The dialog text was not saved. It was closer to "could not install one or more boot-critical drivers" than to the Browse screen that says a media driver is missing.

The running Iris package has no catalog. Setup tries to carry that package into the new Windows. `install.wim` is on the ISO (label `ESD-ISO`), not on the RAM disk `X:`.

## What got Setup on HDMI

The file that showed Setup is `out\Win10_Pro_A1706_SetupGUI_v17.iso`. Three changes, in order.

The unsigned `igdiris64.inf` (`oem0.inf`) was removed from `boot.wim`. Intel's original `igdlh64.inf` plus `igdlh.cat`, version 21.20.16.5174, is in the driver store. Basic Display stays `Start=1`. `igfx` stays demand-start. The same signed package is already in `install.wim`. Turning off driver signature checks only lets an unsigned driver load. It does not let Setup copy that driver into the new Windows.

Thunderbolt (`tbt81x.inf`, missing `setup.msi`) and the older Cirrus CS4206 (missing catalogs) are no longer under `$WinPEDriver$`. CS4208 stays. The 2016 Intel graphics tree stays off the ISO. After that removal, Setup reached the language page, but the picture was already gone.

`work\staging\a1706.cmd` restarts the Iris device once, then polls until the display list contains both `Iris` and `Started`. Only then it runs `DisplaySwitch.exe /external` once and `setup.exe /InstallFrom` the drive that has `\sources\install.wim` (the ISO, label `ESD-ISO`). v16 opened Setup about one second after the script started, before that restart finished, so HDMI went black the old way.

## The Mac disk

Windows Setup cannot shrink the APFS Mac volume. Make the `BOOTCAMP` partition with Boot Camp Assistant in macOS, then boot this v17 ISO with Ventoy `w` and install only onto that partition. Do not point Boot Camp Assistant at this ISO. It adds Apple's 2016 driver pack back.
