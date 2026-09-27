import os
root = r"I:\MacbookISOBuildingSpace\work\iris-extract\extracted"
needles = ["igdlh.cat", "igdlh64.inf", "CatalogFile"]
enc = [(n, n.encode("utf-16le"), n.encode("ascii")) for n in needles]
for name in sorted(os.listdir(root), key=lambda s: (len(s), s)):
    path = os.path.join(root, name)
    if not os.path.isfile(path):
        continue
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        data = f.read()
    hits = []
    for label, u, a in enc:
        if a in data or u in data:
            hits.append(label)
    if hits:
        print(f"{name}\t{size}\t{hits}")
