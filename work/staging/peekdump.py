from pathlib import Path
p = Path(r"I:\MacbookISOBuildingSpace\work\iris-extract\catdump.txt")
b = p.read_bytes()
print("dump bytes", len(b), "head", b[:40])
text = b.decode("utf-16") if b[:2] in (b"\xff\xfe", b"\xfe\xff") or (len(b)>3 and b[1]==0) else b.decode("utf-8", "replace")
print("chars", len(text), "entries", text.count("Subject Identifier:"))
print(text[text.find("CTL Entries"):text.find("CTL Entries")+40])
