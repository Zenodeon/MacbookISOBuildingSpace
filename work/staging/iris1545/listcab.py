import struct
p = r"I:\MacbookISOBuildingSpace\work\staging\iris1545\payload.cab"
f = open(p, "rb")
hdr = f.read(80)
sig, res1, cb, res2, coff, res3, vmin, vmaj, cFolders, cFiles, flags, setID, iCab = struct.unpack_from("<4sIIIII BBHHHHH".replace(" ", ""), hdr, 0)
print("files", cFiles, "coff", coff, "flags", hex(flags))
f.seek(coff)
out = []
for i in range(cFiles):
    chunk = f.read(16)
    cbFile, uoff, iFolder, date, time, attr = struct.unpack("<IIHHHH", chunk)
    name = bytearray()
    while True:
        c = f.read(1)
        if c == b"\x00" or c == b"":
            break
        name += c
    out.append((name.decode("mbcs", "replace"), cbFile))
print("parsed", len(out))
for n, s in out:
    low = n.lower()
    if low.endswith(".inf") or "igdlh" in low or "graphics" in low or low.endswith(".sys") or "drv64" in low:
        print(s, n)
