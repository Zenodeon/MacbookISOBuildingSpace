from pathlib import Path
p = Path(r"I:\MacbookISOBuildingSpace\WorkingReport.md")
text = """# Working report

MacBook Pro 2016 A1706, Iris Graphics 550 (`PCI\\VEN_8086&DEV_1927`). The internal panel is unplugged. HDMI is the USB-C dongle. Boot the ISO with Ventoy `w`. Logs are `\\A1706Logs` on the Ventoy partition.

## What put a picture on HDMI

v13, `out\\Win10_Pro_A1706_SetupGUI_v13.iso`.

The driver that started is Intel 21.20.16.5174 (package 15.45.34.5174). It was staged offline in `boot.wim` as the slim unsigned `igdiris64.inf`, published as `oem0.inf`. After the log was written, `pnputil /restart-device` ran on:

`PCI\\VEN_8086&DEV_1927&SUBSYS_015D106B&REV_0A\\3&11583659&0&10`

Basic Display stayed running (`Start=1`). The later device list showed Intel(R) Iris(TM) Graphics 550, class Display, status Started. That is the boot that lit HDMI.

## Leave these alone

- Do not `drvload` the graphics package onto the Setup RAM disk. The full package filled that disk.
- Do not disable Basic Display. Setup then had no fallback and produced no log.
- Do not set `igfx` to boot-start.
- Do not put a live `SYSTEM` hive back into `boot.wim`. That image did not boot.

## Setup after the picture

The log ends when `X:\\sources\\setup.exe` starts. The dialog text was not saved. It was closer to "could not install one or more boot-critical drivers" than to the Browse screen that says a media driver is missing.

The running Iris package has no catalog. Setup tries to carry that package into the new Windows. `install.wim` is on the ISO (label `ESD-ISO`), not on the RAM disk `X:`.
"""
p.write_bytes(text.encode("utf-8"))
b = p.read_bytes()
assert b[:3] != b"\\xef\\xbb\\xbf" or True
assert b"\\x00" not in b
print("bytes", len(b), "nulls", b.count(b"\\x00"))
