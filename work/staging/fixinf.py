import ctypes, os
from ctypes import wintypes
from pathlib import Path

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
print("markers", len(hashes))

kernel = ctypes.WinDLL("kernel32", use_last_error=True)
wintrust = ctypes.WinDLL("wintrust", use_last_error=True)
kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
kernel.CreateFileW.restype = wintypes.HANDLE
kernel.CloseHandle.argtypes = [wintypes.HANDLE]
wintrust.CryptCATAdminCalcHashFromFileHandle.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD), ctypes.POINTER(ctypes.c_ubyte), wintypes.DWORD]
wintrust.CryptCATAdminCalcHashFromFileHandle.restype = wintypes.BOOL

def cat_hash(path):
    h = kernel.CreateFileW(str(path), 0x80000000, 1, None, 3, 0, None)
    cb = wintypes.DWORD(0)
    wintrust.CryptCATAdminCalcHashFromFileHandle(h, ctypes.byref(cb), None, 0)
    buf = (ctypes.c_ubyte * cb.value)()
    wintrust.CryptCATAdminCalcHashFromFileHandle(h, ctypes.byref(cb), buf, 0)
    kernel.CloseHandle(h)
    return bytes(buf[:cb.value])

root = Path(r"I:\MacbookISOBuildingSpace\work\iris-extract\extracted")
by_hash = {}
for member in os.listdir(root):
    path = root / member
    if path.is_file():
        by_hash.setdefault(cat_hash(path), member)

# find file tags whose decoded name contains inf
idx = 0
n = 0
while True:
    i = cat.find(file_tag, idx)
    if i < 0:
        break
    p = i + len(file_tag)
    ln = cat[p+7]
    name = cat[p+8:p+8+ln].decode("utf-16le", "replace").rstrip("\x00")
    digest = [d for off, d in hashes if off < i][-1]
    member = by_hash.get(digest)
    if "inf" in name.lower() or (member and member in ("a73","a72")):
        mag = b""
        if member:
            mag = (root/member).read_bytes()[:2]
        print(repr(name), "lenbyte", ln, "member", member, "magic", mag)
    n += 1
    idx = i + 1
print("tags", n)
# what name is paired with a73 hash
h73 = cat_hash(root/"a73")
print("a73 hash in map", h73 in by_hash)
# which file tag has this digest
idx=0
while True:
    i = cat.find(file_tag, idx)
    if i < 0:
        break
    p = i + len(file_tag)
    ln = cat[p+7]
    name = cat[p+8:p+8+ln].decode("utf-16le","replace").rstrip("\x00")
    digest = [d for off,d in hashes if off < i][-1]
    if digest == h73:
        print("a73 paired name", repr(name))
    idx = i+1
