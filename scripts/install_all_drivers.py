#!/usr/bin/env python3
"""Put the full A1706 Boot Camp driver set on a Pro ISO.

boot.wim stays the stock Microsoft file.
Every INF package is copied to $WinPEDriver$ for Setup.
The same packages are stored in the Pro image under \\Drivers,
and SetupComplete.cmd installs them with pnputil on first boot.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"I:\MacbookISOBuildingSpace")
LOG = ROOT / "work" / "install-all-drivers.log"
WIMLIB = ROOT / "work" / "wimlib" / "wimlib-imagex.exe"
SRC = ROOT / "WindowsISO" / "Extracted"
ISO_ROOT = ROOT / "work" / "iso-root"
DMG = ROOT / "work" / "tb-extract" / "apple-pkg" / "dmg"
UNPACKED = ROOT / "work" / "tb-extract" / "apple-pkg" / "unpacked"
TB = ROOT / "BootcampDrivers" / "Thunderbolt"
STAGED = ROOT / "work" / "all-drivers"
OUT_ISO = ROOT / "out" / "Win10_Pro_A1706_SetupGUI.iso"
OSCDIMG = Path(
    r"C:\Program Files (x86)\Windows Kits\10\Assessment and Deployment Kit\Deployment Tools\amd64\Oscdimg\oscdimg.exe"
)
ESD = SRC / "sources" / "install.esd"
PRO_INDEX = "6"

SETUP_COMPLETE = r"""@echo off
pnputil /add-driver %SystemDrive%\Drivers\*.inf /subdirs /install
"""

EI_CFG = "[EditionID]\nProfessional\n[Channel]\nRetail\n[VL]\n0\n"

AUTONATTEND = """<?xml version="1.0" encoding="utf-8"?>
<unattend xmlns="urn:schemas-microsoft-com:unattend">
  <settings pass="windowsPE">
    <component name="Microsoft-Windows-PnpCustomizationsWinPE" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State">
      <DriverPaths>
        <PathAndCredentials wcm:action="add" wcm:keyValue="1">
          <Path>\\$WinPEDriver$</Path>
        </PathAndCredentials>
      </DriverPaths>
    </component>
    <component name="Microsoft-Windows-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
      <UserData>
        <AcceptEula>true</AcceptEula>
      </UserData>
    </component>
  </settings>
  <settings pass="specialize">
    <component name="Microsoft-Windows-PnpCustomizationsNonWinPE" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State">
      <DriverPaths>
        <PathAndCredentials wcm:action="add" wcm:keyValue="1">
          <Path>C:\\Drivers</Path>
        </PathAndCredentials>
      </DriverPaths>
    </component>
  </settings>
</unattend>
"""

README = """Windows 10 Pro for MacBook Pro 2016 A1706
==========================================

Output ISO
----------
I:\\MacbookISOBuildingSpace\\out\\Win10_Pro_A1706_SetupGUI.iso

What is on this disc
--------------------
Windows 10 Pro only (sources\\ei.cfg and sources\\install.wim).
sources\\boot.wim is the original Microsoft Setup image.

$WinPEDriver$ contains every driver unpacked from Apple Boot Camp
041-88734 for this Mac, plus the Intel Thunderbolt driver:
Iris 550 graphics, Cirrus speakers (CS4206 and CS4208), Touch Bar
(AppleDFR), T1 (AppleSOC), keyboard, trackpad, Broadcom Wi-Fi,
Bluetooth, SSD, USB, and the rest of the Boot Camp INF set.

The same driver folders are inside the installed Windows at C:\\Drivers.
At the end of Setup, Windows\\Setup\\Scripts\\SetupComplete.cmd runs
pnputil so those drivers install on the first real boot.
The Boot Camp folder with Setup.exe is both on the ISO and in
C:\\BootCamp if you need to run Apple's installer again.

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
"""


def log(msg: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    print(msg, flush=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(msg + "\n")


def run(args: list[str], **kwargs) -> None:
    log("RUN " + " ".join(args))
    subprocess.run(args, check=True, **kwargs)


def stage_drivers() -> None:
    if STAGED.exists():
        shutil.rmtree(STAGED)
    STAGED.mkdir(parents=True)
    pe = DMG / "$WinPEDriver$"
    for child in pe.iterdir():
        dest = STAGED / child.name
        if child.is_dir():
            shutil.copytree(child, dest)
        else:
            shutil.copy2(child, dest)
        log("staged WinPE %s" % child.name)
    for folder in sorted(UNPACKED.iterdir()):
        if not folder.is_dir():
            continue
        if not any(folder.rglob("*.inf")):
            continue
        dest = STAGED / folder.name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(folder, dest)
        log("staged unpacked %s" % folder.name)
    tb_dest = STAGED / "Thunderbolt"
    if tb_dest.exists():
        shutil.rmtree(tb_dest)
    shutil.copytree(TB, tb_dest)
    log("staged Thunderbolt")
    infs = list(STAGED.rglob("*.inf"))
    log("staged inf count=%s" % len(infs))
    for inf in infs:
        log("  %s" % inf.relative_to(STAGED))


def reset_iso_root() -> None:
    if ISO_ROOT.exists():
        subprocess.run(
            ["attrib", "-R", "-S", "-H", str(ISO_ROOT) + "\\*", "/S", "/D"],
            check=False,
        )
        shutil.rmtree(ISO_ROOT, ignore_errors=True)
        if ISO_ROOT.exists():
            shutil.rmtree(ISO_ROOT)
    ISO_ROOT.mkdir(parents=True)


def main() -> int:
    if LOG.exists():
        LOG.unlink()
    log("=== install all A1706 drivers ===")
    for p in (WIMLIB, ESD, OSCDIMG, DMG / "BootCamp" / "Setup.exe", TB / "tbt81x.inf"):
        if not p.exists():
            log("MISSING %s" % p)
            return 1

    stage_drivers()
    reset_iso_root()
    rc = subprocess.run(
        [
            "robocopy",
            str(SRC),
            str(ISO_ROOT),
            "/E",
            "/XF",
            "install.esd",
            "install.wim",
            "/NFL",
            "/NDL",
            "/NJH",
            "/NJS",
            "/nc",
            "/ns",
            "/np",
        ]
    )
    if rc.returncode >= 8:
        log("robocopy failed %s" % rc.returncode)
        return 1

    boot_wim = ISO_ROOT / "sources" / "boot.wim"
    install_wim = ISO_ROOT / "sources" / "install.wim"
    if not boot_wim.exists():
        log("MISSING stock boot.wim")
        return 1
    log("stock boot.wim size=%s (not patched)" % boot_wim.stat().st_size)

    log("Exporting Windows 10 Pro")
    run(
        [
            str(WIMLIB),
            "export",
            str(ESD),
            PRO_INDEX,
            str(install_wim),
            "--compress=LZX",
        ]
    )
    log("install.wim size=%s" % install_wim.stat().st_size)

    scripts = ROOT / "work" / "staging"
    scripts.mkdir(parents=True, exist_ok=True)
    setup_cmd = scripts / "SetupComplete.cmd"
    setup_cmd.write_text(SETUP_COMPLETE, encoding="ascii")
    cmd_file = scripts / "wim-add-drivers.txt"
    bootcamp = DMG / "BootCamp"
    lines = [
        'add "%s" \\Drivers' % STAGED,
        'add "%s" \\BootCamp' % bootcamp,
        'add "%s" \\Windows\\Setup\\Scripts\\SetupComplete.cmd' % setup_cmd,
    ]
    cmd_file.write_text("\n".join(lines) + "\n", encoding="ascii")
    log("Updating install.wim with drivers")
    with cmd_file.open("r", encoding="ascii") as fh:
        run([str(WIMLIB), "update", str(install_wim), "1"], stdin=fh)
    log("install.wim size after drivers=%s" % install_wim.stat().st_size)

    dest_pe = ISO_ROOT / "$WinPEDriver$"
    if dest_pe.exists():
        shutil.rmtree(dest_pe)
    shutil.copytree(STAGED, dest_pe)
    dest_bc = ISO_ROOT / "BootCamp"
    if dest_bc.exists():
        shutil.rmtree(dest_bc)
    shutil.copytree(bootcamp, dest_bc)
    (ISO_ROOT / "sources" / "ei.cfg").write_text(EI_CFG, encoding="ascii")
    (ISO_ROOT / "autounattend.xml").write_text(AUTONATTEND, encoding="utf-8")
    (ISO_ROOT / "README-A1706.txt").write_text(README, encoding="utf-8")
    (ROOT / "README-TEST.txt").write_text(README, encoding="utf-8")
    log("ISO root drivers and BootCamp copied")

    etfs = ISO_ROOT / "boot" / "etfsboot.com"
    efi = ISO_ROOT / "efi" / "microsoft" / "boot" / "efisys.bin"
    if not etfs.exists() or not efi.exists():
        log("MISSING boot files")
        return 1
    if OUT_ISO.exists():
        OUT_ISO.unlink()
    OUT_ISO.parent.mkdir(parents=True, exist_ok=True)
    bootdata = "2#p0,e,b%s#pEF,e,b%s" % (etfs, efi)
    run(
        [
            str(OSCDIMG),
            "-m",
            "-u2",
            "-udfver102",
            "-lESD-ISO",
            "-bootdata:%s" % bootdata,
            str(ISO_ROOT),
            str(OUT_ISO),
        ]
    )
    log("ISO ready: %s (%s bytes)" % (OUT_ISO, OUT_ISO.stat().st_size))
    log("=== done ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
