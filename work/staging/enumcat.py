import ctypes
from ctypes import wintypes
from pathlib import Path

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
wintrust.CryptCATOpen.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD]
wintrust.CryptCATOpen.restype = wintypes.HANDLE
wintrust.CryptCATEnumerateMember.argtypes = [wintypes.HANDLE, ctypes.POINTER(CRYPTCATMEMBER)]
wintrust.CryptCATEnumerateMember.restype = ctypes.POINTER(CRYPTCATMEMBER)
wintrust.CryptCATEnumerateAttr.argtypes = [wintypes.HANDLE, ctypes.POINTER(CRYPTCATMEMBER), ctypes.POINTER(CRYPTCATATTRIBUTE)]
wintrust.CryptCATEnumerateAttr.restype = ctypes.POINTER(CRYPTCATATTRIBUTE)
wintrust.CryptCATClose.argtypes = [wintypes.HANDLE]
wintrust.CryptCATClose.restype = wintypes.BOOL

path = r"I:\MacbookISOBuildingSpace\work\staging\iris1545\igdlh.cat"
h = wintrust.CryptCATOpen(path, 0, None, 0, 0)
print("handle", h, "err", ctypes.get_last_error())
member = None
count = 0
samples = []
while True:
    member = wintrust.CryptCATEnumerateMember(h, member)
    if not member:
        break
    m = member.contents
    digest = b""
    if m.pIndirectData:
        d = m.pIndirectData.contents.Digest
        if d.pbData and d.cbData:
            digest = bytes(d.pbData[:d.cbData])
    attrs = []
    attr = None
    while True:
        attr = wintrust.CryptCATEnumerateAttr(h, member, attr)
        if not attr:
            break
        a = attr.contents
        tag = a.pwszReferenceTag
        val = b""
        if a.pbValue and a.cbValue:
            val = bytes(a.pbValue[:a.cbValue])
        attrs.append((tag, val[:80]))
    count += 1
    if count <= 2 or any((t or "").lower()=="file" and b"igdlh" in v.lower() for t,v in attrs):
        samples.append((m.pwszFileName, m.pwszReferenceTag, digest.hex()[:16], [(t, v) for t,v in attrs]))
print("count", count)
for s in samples:
    print("---")
    print("file", s[0], "tag", s[1], "digest", s[2])
    for t,v in s[3]:
        try:
            shown = v.decode("utf-16le")
        except Exception:
            shown = v[:40]
        print(" ", t, shown)
wintrust.CryptCATClose(h)
