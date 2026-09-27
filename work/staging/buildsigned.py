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
    if cat[p:p+7] != bytes.fromhex("02041001000104"):
        raise SystemExit("bad tail")
    n = cat[p+7]
    name = cat[p+8:p+8+n].decode("utf-16le").rstrip("\x00")
    prev = [d for off, d in hashes if off < i][-1]
    entries.append((name, prev))
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
        if not wintrust.CryptCATAdminCalcHashFromFileHandle(h, ctypes.byref(cb), None, 0):
            raise OSError("size", ctypes.get_last_error())
        buf = (ctypes.c_ubyte * cb.value)()
        if not wintrust.CryptCATAdminCalcHashFromFileHandle(h, ctypes.byref(cb), buf, 0):
            raise OSError("hash", ctypes.get_last_error())
        return bytes(buf[:cb.value])
    finally:
        kernel.CloseHandle(h)

root = Path(r"I:\MacbookISOBuildingSpace\work\iris-extract\extracted")
by_hash = {}
for member in os.listdir(root):
    path = root / member
    if path.is_file():
        by_hash.setdefault(cat_hash(path), member)

groups = defaultdict(list)
for name, digest in entries:
    groups[name.lower()].append((name, digest, by_hash.get(digest)))
dups = {k: v for k, v in groups.items() if len(v) > 1}
print("dup groups", len(dups))
for k, v in dups.items():
    print(k, [(n, m, d.hex()[:8]) for n, d, m in v])
missing = [n for n, d in entries if by_hash.get(d) is None]
print("missing", missing)
