import sys
path = sys.argv[1]
text = open(path, "r", encoding="utf-8", errors="replace").read().lower()
slim = "igdiris64.inf" in text
signed = "igdlh64.inf" in text
print("slim_present", slim)
print("signed_present", signed)
if slim or not signed:
    sys.exit(1)
sys.exit(0)
