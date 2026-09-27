from pathlib import Path
b = Path(r"I:\MacbookISOBuildingSpace\work\iris-extract\extracted\a91").read_bytes()
j = b.find("igfxexps".encode("utf-16le"))
chunk = b[j-64:j+80]
chars = []
s = []
for i in range(0, len(chunk)-1, 2):
    c = chunk[i] + (chunk[i+1]<<8)
    if c == 0:
        if s:
            chars.append("".join(s))
            s = []
    elif 32 <= c < 127:
        s.append(chr(c))
    else:
        if s:
            chars.append("".join(s))
            s = []
print(chars)
