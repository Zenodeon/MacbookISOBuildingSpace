import os
root = r"I:\MacbookISOBuildingSpace\work\iris-extract\extracted"
for name in ["a6","a10","a29","a72","a73","a358"]:
    path = os.path.join(root, name)
    data = open(path, "rb").read(16)
    size = os.path.getsize(path)
    whole = open(path, "rb").read()
    print(name, size, data[:8].hex(), "sys", b"igdkmd64.sys" in whole or "igdkmd64.sys".encode("utf-16le") in whole)
