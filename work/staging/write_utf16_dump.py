from pathlib import Path
text = "Device Description: Intel(R) Iris(TM) Graphics 550\r\nStatus: Started\r\n"
Path(r"X:\a1706-cmd-out.txt").write_bytes(text.encode("utf-16le"))
print("wrote utf16")
