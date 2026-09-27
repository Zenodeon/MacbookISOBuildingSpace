import ctypes, hashlib, os
from ctypes import wintypes
from pathlib import Path

cat = Path(r"I:\MacbookISOBuildingSpace\work\staging\iris1545\igdlh.cat").read_bytes()
marker = bytes.fromhex("2b0e03021a05000414")
file_tag = bytes.fromhex("1e0800460069006c0065")
# collect (offset of sha1, digest)
digests = []
idx = 0
while True:
    i = cat.find(marker, idx)
    if i < 0:
        break
    digests.append((i, cat[i+len(marker):i+len(marker)+20]))
    idx = i + len(marker)
print("sha1 markers", len(digests), "file tags", cat.count(file_tag))

names_at = []
idx = 0
while True:
    i = cat.find(file_tag, idx)
    if i < 0:
        break
    # expect 02 04 10 01 00 01 04 len
    p = i + len(file_tag)
    rest = cat[p:p+16]
    names_at.append((i, rest[:8].hex()))
    idx = i + 1
print("first file-tag tails", names_at[:3])
