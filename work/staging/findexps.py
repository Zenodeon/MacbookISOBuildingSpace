import os
root = r"I:\MacbookISOBuildingSpace\work\iris-extract\extracted"
needle = "igfxexps".encode("utf-16le")
needle_a = b"igfxexps"
for name in os.listdir(root):
    data = open(os.path.join(root, name), "rb").read()
    if needle in data or needle_a in data.lower() if False else needle_a in data or needle in data:
        if needle in data or needle_a in data:
            print(name, os.path.getsize(os.path.join(root, name)))
