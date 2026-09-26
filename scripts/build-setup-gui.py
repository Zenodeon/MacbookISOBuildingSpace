#!/usr/bin/env python3
"""Build Windows 10 Pro Setup-GUI ISO for MacBookPro A1706."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"I:\MacbookISOBuildingSpace")
LOG = ROOT / "work" / "build-setup-gui.log"
WIMLIB = ROOT / "work" / "wimlib" / "wimlib-imagex.exe"
SRC = ROOT / "WindowsISO" / "Extracted"
ISO_ROOT = ROOT / "work" / "iso-root"
STAGING = ROOT / "work" / "staging"
PE = ROOT / "BootcampDrivers" / "WindowsSupport" / "$WinPEDriver$"
TB = ROOT / "BootcampDrivers" / "Thunderbolt"
OUT_ISO = ROOT / "out" / "Win10_Pro_A1706_SetupGUI.iso"
OSCDIMG = Path(
    r"C:\Program Files (x86)\Windows Kits\10\Assessment and Deployment Kit\Deployment Tools\amd64\Oscdimg\oscdimg.exe"
)
ESD = SRC / "sources" / "install.esd"
PRO_INDEX = "6"


def log(msg: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = msg
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def run(args: list[str], **kwargs) -> None:
    log("RUN " + " ".join(str(a) for a in args))
    subprocess.run(args, check=True, **kwargs)


def main() -> int:
    if LOG.exists():
        LOG.unlink()
    log("=== A1706 Setup-GUI ISO build start (python/wimlib) ===")
    for p in (WIMLIB, ESD, OSCDIMG, TB / "tbt81x.inf"):
        if not p.exists():
            log(f"MISSING {p}")
            return 1

    log("Copying ISO tree excluding install.esd")
    if ISO_ROOT.exists():
        shutil.rmtree(ISO_ROOT)
    ISO_ROOT.mkdir(parents=True)
    rc = subprocess.run(
        [
            "robocopy",
            str(SRC),
            str(ISO_ROOT),
            "/E",
            "/XF",
            "install.esd",
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
        log(f"robocopy failed {rc.returncode}")
        return 1

    boot_wim = ISO_ROOT / "sources" / "boot.wim"
    install_wim = ISO_ROOT / "sources" / "install.wim"
    if not boot_wim.exists():
        log("MISSING boot.wim after copy")
        return 1
    subprocess.run(["attrib", "-R", str(boot_wim)], check=False)
    subprocess.run(["attrib", "-R", str(ISO_ROOT / "sources" / "*.*"), "/S"], check=False)

    log(f"Exporting Windows 10 Pro ESD index {PRO_INDEX}")
    if install_wim.exists():
        install_wim.unlink()
    run([str(WIMLIB), "export", str(ESD), PRO_INDEX, str(install_wim), "--compress=LZX"])
    log(f"install.wim size={install_wim.stat().st_size}")

    ei = ISO_ROOT / "sources" / "ei.cfg"
    ei.write_text("[EditionID]\nProfessional\n[Channel]\nRetail\n[VL]\n0\n", encoding="ascii")
    log("Wrote ei.cfg Professional only")

    log("Staging drivers")
    if STAGING.exists():
        shutil.rmtree(STAGING)
    copies = {
        "IntelHD": PE / "IntelHDGraphics64" / "Graphics",
        "AppleSSD": PE / "AppleSSD64",
        "AppleUSB": PE / "AppleUSBCompositeDevice64",
        "AppleSPIKbd": PE / "AppleSPIKeyboard",
        "AppleSPIPad": PE / "AppleSPITrackpad",
        "AppleSPIDev": PE / "AppleSPIDevice",
        "SerialIO": PE / "SerialIO",
        "Thunderbolt": TB,
    }
    drv_root = STAGING / "A1706Drivers"
    for name, src in copies.items():
        if not src.exists():
            log(f"MISSING driver source {src}")
            return 1
        dst = drv_root / name
        shutil.copytree(src, dst)
        log(f"Staged {name}")

    startnet = """@echo off
wpeinit
set DRV=%SYSTEMDRIVE%\\A1706Drivers
if not exist \"%DRV%\" set DRV=X:\\A1706Drivers
if exist \"%DRV%\" (
    for /r \"%DRV%\" %%I in (*.inf) do (
        echo %%~nxI | findstr /i /x \"autorun.inf\" >nul
        if errorlevel 1 drvload \"%%I\"
    )
)
if exist %SystemRoot%\\System32\\DisplaySwitch.exe (
    %SystemRoot%\\System32\\DisplaySwitch.exe /external
)
"""
    startnet_path = STAGING / "startnet.cmd"
    startnet_path.write_text(startnet, encoding="ascii")

    ds_host = Path(r"C:\Windows\System32\DisplaySwitch.exe")
    ds_stage = STAGING / "DisplaySwitch.exe"
    if ds_host.exists():
        shutil.copy2(ds_host, ds_stage)
    mui_host = Path(r"C:\Windows\System32\en-US\DisplaySwitch.exe.mui")
    mui_stage = STAGING / "DisplaySwitch.exe.mui"
    if mui_host.exists():
        shutil.copy2(mui_host, mui_stage)

    cmds = [
        f'add "{startnet_path}" \\Windows\\System32\\startnet.cmd',
        f'add "{drv_root}" \\A1706Drivers',
    ]
    if ds_stage.exists():
        cmds.append(f'add "{ds_stage}" \\Windows\\System32\\DisplaySwitch.exe')
    if mui_stage.exists():
        cmds.append(f'add "{mui_stage}" \\Windows\\System32\\en-US\\DisplaySwitch.exe.mui')
    cmd_file = STAGING / "wimlib-update.txt"
    cmd_file.write_text("\n".join(cmds) + "\n", encoding="ascii")
    log("wimlib update commands:")
    for c in cmds:
        log("  " + c)

    log("Updating boot.wim index 2")
    with cmd_file.open("r", encoding="ascii") as stdin:
        run([str(WIMLIB), "update", str(boot_wim), "2"], stdin=stdin)

    log("Verifying patched files")
    listed = subprocess.check_output([str(WIMLIB), "dir", str(boot_wim), "2"], text=True, errors="replace")
    for needle in ("startnet.cmd", "A1706Drivers", "DisplaySwitch", "tbt81x", "igdlh64"):
        hits = [ln for ln in listed.splitlines() if needle.lower() in ln.lower()]
        log(f"  {needle}: {len(hits)} hit(s)")
        for ln in hits[:8]:
            log("    " + ln)

    etfs = ISO_ROOT / "boot" / "etfsboot.com"
    efi = ISO_ROOT / "efi" / "microsoft" / "boot" / "efisys.bin"
    if not etfs.exists() or not efi.exists():
        log("MISSING boot files")
        return 1

    log("Building ISO with oscdimg")
    if OUT_ISO.exists():
        OUT_ISO.unlink()
    OUT_ISO.parent.mkdir(parents=True, exist_ok=True)
    bootdata = f"2#p0,e,b{etfs}#pEF,e,b{efi}"
    run([str(OSCDIMG), "-m", "-o", "-u2", "-udfver102", f"-bootdata:{bootdata}", str(ISO_ROOT), str(OUT_ISO)])
    log(f"ISO ready: {OUT_ISO} ({OUT_ISO.stat().st_size} bytes)")
    log("=== build complete ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
