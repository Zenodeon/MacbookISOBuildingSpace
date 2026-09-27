import ctypes, os, shutil
from ctypes import wintypes
from pathlib import Path
from collections import defaultdict

cat = Path(r"I:\MacbookISOBuildingSpace\work\staging\iris1545\igdlh.cat").read_bytes()
marker = bytes.fromhex("2b0e03021a05000414")
file_tag = bytes.fromhex("1e0800460069006c0065")
hashes = []
idx = 0
while True:
    i = cat.find(marker, idx)
    if i < 0:
        break
    hashes.append((i, cat[i+len(marker):i+len(marker)+20]))
    idx = i + len(marker)
entries = []
idx = 0
while True:
    i = cat.find(file_tag, idx)
    if i < 0:
        break
    p = i + len(file_tag)
    n = cat[p+7]
    name = cat[p+8:p+8+n].decode("utf-16le").rstrip("\x00")
    digest = [d for off, d in hashes if off < i][-1]
    entries.append((name, digest))
    idx = i + 1

kernel = ctypes.WinDLL("kernel32", use_last_error=True)
wintrust = ctypes.WinDLL("wintrust", use_last_error=True)
kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
kernel.CreateFileW.restype = wintypes.HANDLE
kernel.CloseHandle.argtypes = [wintypes.HANDLE]
wintrust.CryptCATAdminCalcHashFromFileHandle.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD), ctypes.POINTER(ctypes.c_ubyte), wintypes.DWORD]
wintrust.CryptCATAdminCalcHashFromFileHandle.restype = wintypes.BOOL

def cat_hash(path):
    h = kernel.CreateFileW(str(path), 0x80000000, 1, None, 3, 0, None)
    if h == wintypes.HANDLE(-1).value:
        raise OSError(ctypes.get_last_error(), str(path))
    try:
        cb = wintypes.DWORD(0)
        wintrust.CryptCATAdminCalcHashFromFileHandle(h, ctypes.byref(cb), None, 0)
        buf = (ctypes.c_ubyte * cb.value)()
        if not wintrust.CryptCATAdminCalcHashFromFileHandle(h, ctypes.byref(cb), buf, 0):
            raise OSError("hash", ctypes.get_last_error())
        return bytes(buf[:cb.value])
    finally:
        kernel.CloseHandle(h)

root = Path(r"I:\MacbookISOBuildingSpace\work\iris-extract\extracted")
by_hash = {}
sizes = {}
for member in os.listdir(root):
    path = root / member
    if path.is_file():
        by_hash.setdefault(cat_hash(path), member)
        sizes[member] = path.stat().st_size

chosen = {}
for name, digest in entries:
    member = by_hash[digest]
    key = name.lower()
    if key not in chosen or sizes[member] > sizes[chosen[key][1]]:
        chosen[key] = (name, member)

dest = Path(r"I:\MacbookISOBuildingSpace\work\iris-extract\signed")
if dest.exists():
    shutil.rmtree(dest)
dest.mkdir()
for name, member in chosen.values():
    shutil.copyfile(root / member, dest / name)
print("copied", len(list(dest.iterdir())))
print("inf", (dest/"igdlh64.inf").is_file(), "cat", (dest/"igdlh.cat").is_file())
for key, (name, member) in sorted(chosen.items()):
    if name.lower() in ("tbbmalloc.dll","tbb.dll","tbb_preview.dll","intelopencl32.dll","intelopencl64.dll"):
        print("kept", name, member, sizes[member])
