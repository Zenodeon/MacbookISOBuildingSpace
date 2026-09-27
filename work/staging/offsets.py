from pathlib import Path
cat = Path(r"I:\MacbookISOBuildingSpace\work\staging\iris1545\igdlh.cat").read_bytes()
marker = bytes.fromhex("2b0e03021a05000414")
file_tag = bytes.fromhex("1e0800460069006c0065")
hs=[]
idx=0
while True:
    i=cat.find(marker, idx)
    if i<0: break
    hs.append(i)
    idx=i+1
fs=[]
idx=0
while True:
    i=cat.find(file_tag, idx)
    if i<0: break
    fs.append(i)
    idx=i+1
print("first hash", hs[:8])
print("first file", fs[:8])
print("delta file-hash", [fs[i]-hs[i] for i in range(8)])
print("delta file-prevhash", [fs[0]-hs[0]] + [fs[i]-hs[i-1] for i in range(1,8)])
