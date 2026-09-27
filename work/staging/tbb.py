from pathlib import Path
cat = Path(r"I:\MacbookISOBuildingSpace\work\staging\iris1545\igdlh.cat").read_bytes()
file_tag = bytes.fromhex("1e0800460069006c0065")
needle = "tbbmalloc.dll".encode("utf-16le")
idx = 0
while True:
    i = cat.find(needle, idx)
    if i < 0:
        break
    window = cat[max(0,i-200):i+len(needle)+80]
    chars=[]
    s=[]
    for k in range(0, len(window)-1, 1):
        pass
    strings=[]
    j=0
    while j < len(window)-1:
        if window[j+1]==0 and 32<=window[j]<127:
            ch=[]
            k=j
            while k < len(window)-1 and window[k+1]==0 and 32<=window[k]<127:
                ch.append(chr(window[k])); k+=2
            if len(ch)>3:
                strings.append("".join(ch))
            j=k
        else:
            j+=1
    print("---", i, strings)
    idx=i+2
