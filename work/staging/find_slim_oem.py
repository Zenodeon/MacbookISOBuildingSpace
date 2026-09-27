import sys
path = sys.argv[1]
text = open(path, "r", encoding="utf-8", errors="replace").read()
published = ""
found = ""
for line in text.splitlines():
    if ":" not in line:
        continue
    key, val = line.split(":", 1)
    key = key.strip().lower()
    val = val.strip()
    if key == "published name":
        published = val
    elif key == "original file name" and val.lower() == "igdiris64.inf":
        found = published
print(found if found else "MISSING")
