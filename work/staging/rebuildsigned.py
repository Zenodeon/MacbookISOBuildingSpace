import ctypes, os, shutil
from ctypes import wintypes
from pathlib import Path
from collections import defaultdict

class GUID(ctypes.Structure):
    _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD), ("Data3", wintypes.WORD), ("Data4", ctypes.c_ubyte * 8)]

class CRYPT_ATTR_BLOB(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]

class CRYPT_ATTRIBUTE_TYPE_VALUE(ctypes.Structure):
    _fields_ = [("pszObjId", ctypes.c_char_p), ("Value", CRYPT_ATTR_BLOB)]

class CRYPT_ALGORITHM_IDENTIFIER(ctypes.Structure):
    _fields_ = [("pszObjId", ctypes.c_char_p), ("Parameters", CRYPT_ATTR_BLOB)]

class SIP_INDIRECT_DATA(ctypes.Structure):
    _fields_ = [
        ("Data", CRYPT_ATTRIBUTE_TYPE_VALUE),
        ("DigestAlgorithm", CRYPT_ALGORITHM_IDENTIFIER),
        ("Digest", CRYPT_ATTR_BLOB),
    ]

class CRYPTCATMEMBER(ctypes.Structure):
    _fields_ = [
        ("cbStruct", wintypes.DWORD),
        ("pwszReferenceTag", wintypes.LPWSTR),
        ("pwszFileName", wintypes.LPWSTR),
        ("gSubjectType", GUID),
        ("fdwMemberFlags", wintypes.DWORD),
        ("pIndirectData", ctypes.POINTER(SIP_INDIRECT_DATA)),
        ("dwCertVersion", wintypes.DWORD),
        ("dwReserved", wintypes.DWORD),
        ("hReserved", wintypes.HANDLE),
    ]

class CRYPTCATATTRIBUTE(ctypes.Structure):
    _fields_ = [
        ("cbStruct", wintypes.DWORD),
        ("pwszReferenceTag", wintypes.LPWSTR),
        ("dwAttrTypeAndAction", wintypes.DWORD),
        ("cbValue", wintypes.DWORD),
        ("pbValue", ctypes.POINTER(ctypes.c_ubyte)),
        ("dwReserved", wintypes.DWORD),
    ]

wintrust = ctypes.WinDLL("wintrust", use_last_error=True)
kernel = ctypes.WinDLL("kernel32", use_last_error=True)
wintrust.CryptCATOpen.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD]
wintrust.CryptCATOpen.restype = wintypes.HANDLE
wintrust.CryptCATEnumerateMember.argtypes = [wintypes.HANDLE, ctypes.POINTER(CRYPTCATMEMBER)]
wintrust.CryptCATEnumerateMember.restype = ctypes.POINTER(CRYPTCATMEMBER)
wintrust.CryptCATEnumerateAttr.argtypes = [wintypes.HANDLE, ctypes.POINTER(CRYPTCATMEMBER), ctypes.POINTER(CRYPTCATATTRIBUTE)]
wintrust.CryptCATEnumerateAttr.restype = ctypes.POINTER(CRYPTCATATTRIBUTE)
wintrust.CryptCATClose.argtypes = [wintypes.HANDLE]
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

catpath = r"I:\MacbookISOBuildingSpace\work\staging\iris1545\igdlh.cat"
hcat = wintrust.CryptCATOpen(catpath, 0, None, 0, 0)
entries = []
member = None
while True:
    member = wintrust.CryptCATEnumerateMember(hcat, member)
    if not member:
        break
    m = member.contents
    digest = bytes.fromhex(m.pwszReferenceTag)
    name = None
    attr = None
    while True:
        attr = wintrust.CryptCATEnumerateAttr(hcat, member, attr)
        if not attr:
            break
        a = attr.contents
        if a.pwszReferenceTag == "File" and a.pbValue and a.cbValue:
            name = bytes(a.pbValue[:a.cbValue]).decode("utf-16le").rstrip("\x00")
    entries.append((name, digest))
wintrust.CryptCATClose(hcat)
print("entries", len(entries), "named", sum(1 for n,_ in entries if n))

root = Path(r"I:\MacbookISOBuildingSpace\work\iris-extract\extracted")
by_hash = {}
sizes = {}
for member_name in os.listdir(root):
    path = root / member_name
    if path.is_file():
        by_hash.setdefault(cat_hash(path), member_name)
        sizes[member_name] = path.stat().st_size

groups = defaultdict(list)
missing = []
for name, digest in entries:
    mem = by_hash.get(digest)
    if mem is None:
        missing.append(name)
    groups[name.lower() if name else ""].append((name, mem, sizes.get(mem, 0)))
print("missing", missing)
dups = {k:v for k,v in groups.items() if len(v)>1}
print("dups", len(dups))
for k,v in dups.items():
    print(" ", k, [(n,m,s) for n,m,s in v])

chosen = {}
for name, digest in entries:
    mem = by_hash.get(digest)
    if not name or not mem:
        continue
    key = name.lower()
    if key not in chosen or sizes[mem] > sizes[chosen[key][1]]:
        chosen[key] = (name, mem)

dest = Path(r"I:\MacbookISOBuildingSpace\work\iris-extract\signed")
if dest.exists():
    shutil.rmtree(dest)
dest.mkdir()
for name, mem in chosen.values():
    shutil.copyfile(root/mem, dest/name)
shutil.copyfile(catpath, dest/"igdlh.cat")
inf = (dest/"igdlh64.inf").read_bytes()[:4]
print("copied", len(list(dest.iterdir())), "infmagic", inf.hex(), "infsize", (dest/"igdlh64.inf").stat().st_size)
