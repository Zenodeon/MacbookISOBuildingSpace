#!/usr/bin/env python3
"""Rebuild a Ventoy/Mac-friendlier Pro-only ISO.

Do not patch boot.wim (drvload in startnet can hang Setup).
Keep a stock Microsoft boot path. Put drivers in $WinPEDriver$.
Use Pro-only install.esd so every file stays under 4 GiB.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"I:\MacbookISOBuildingSpace")
LOG = ROOT / "work" / "rebuild-bootable.log"
WIMLIB = ROOT / "work" / "wimlib" / "wimlib-imagex.exe"
SRC = ROOT / "WindowsISO" / "Extracted"
ISO_ROOT = ROOT / "work" / "iso-root"
PE = ROOT / "BootcampDrivers" / "WindowsSupport" / "$WinPEDriver$"
TB = ROOT / "BootcampDrivers" / "Thunderbolt"
OUT_ISO = ROOT / "out" / "Win10_Pro_A1706_SetupGUI.iso"
OSCDIMG = Path(
    r"C:\Program Files (x86)\Windows Kits\10\Assessment and Deployment Kit\Deployment Tools\amd64\Oscdimg\oscdimg.exe"
)
ESD = SRC / "sources" / "install.esd"
PRO_INDEX = "6"
FAT32_LIMIT = 4 * 1024 * 1024 * 1024


def log(msg: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    print(msg, flush=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(msg + "\n")


def run(args: list[str]) -> None:
    log("RUN " + " ".join(args))
    subprocess.run(args, check=True)


def assert_fat32_safe(root: Path) -> None:
    bad = []
    for p in root.rglob("*"):
        if p.is_file() and p.stat().st_size >= FAT32_LIMIT:
            bad.append((p.stat().st_size, p))
    if bad:
        for size, p in bad:
            log("TOO LARGE: %s %s" % (size, p))
        raise SystemExit(2)


def main() -> int:
    if LOG.exists():
        LOG.unlink()
    log("=== rebuild bootable Pro ISO (stock boot.wim) ===")
    for p in (WIMLIB, ESD, OSCDIMG, TB / "tbt81x.inf"):
        if not p.exists():
            log("MISSING %s" % p)
            return 1

    if ISO_ROOT.exists():
        subprocess.run(
            ["attrib", "-R", "-S", "-H", str(ISO_ROOT / "*"), "/S", "/D"],
            check=False,
        )
        shutil.rmtree(ISO_ROOT, ignore_errors=True)
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
    install_esd = ISO_ROOT / "sources" / "install.esd"
    install_wim = ISO_ROOT / "sources" / "install.wim"
    if not boot_wim.exists():
        log("MISSING boot.wim")
        return 1
    if install_wim.exists():
        install_wim.unlink()

    # Stock boot.wim from the original extract (already copied). Do not patch it.
    log("Keeping stock boot.wim (no startnet/drvload patch)")

    log("Exporting Windows 10 Pro as solid ESD")
    run(
        [
            str(WIMLIB),
            "export",
            str(ESD),
            PRO_INDEX,
            str(install_esd),
            "--compress=LZMS",
            "--solid",
        ]
    )
    log("install.esd size=%s" % install_esd.stat().st_size)

    (ISO_ROOT / "sources" / "ei.cfg").write_text(
        "[EditionID]\nProfessional\n[Channel]\nRetail\n[VL]\n0\n",
        encoding="ascii",
    )

    # Microsoft Setup auto-loads $WinPEDriver$ from media root.
    dest_pe = ISO_ROOT / "$WinPEDriver$"
    if dest_pe.exists():
        shutil.rmtree(dest_pe)
    shutil.copytree(PE, dest_pe)
    tb_dest = dest_pe / "Thunderbolt"
    if tb_dest.exists():
        shutil.rmtree(tb_dest)
    shutil.copytree(TB, tb_dest)
    audio = dest_pe / "IntelHDGraphics64" / "DisplayAudio"
    if audio.exists():
        shutil.rmtree(audio)
    log("Copied $WinPEDriver$ + Thunderbolt onto ISO root")

    assert_fat32_safe(ISO_ROOT)

    etfs = ISO_ROOT / "boot" / "etfsboot.com"
    efi = ISO_ROOT / "efi" / "microsoft" / "boot" / "efisys.bin"
    if not etfs.exists() or not efi.exists():
        log("MISSING boot files")
        return 1

    if OUT_ISO.exists():
        OUT_ISO.unlink()
    OUT_ISO.parent.mkdir(parents=True, exist_ok=True)
    bootdata = "2#p0,e,b%s#pEF,e,b%s" % (etfs, efi)
    # No -o optimize. Label ESD-ISO to match official Windows 10 media.
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
