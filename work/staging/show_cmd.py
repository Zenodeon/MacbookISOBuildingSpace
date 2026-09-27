p = r"I:\MacbookISOBuildingSpace\work\staging\a1706.cmd"
t = open(p, "rb").read().decode("ascii")
i = t.find("v13 display cycle")
print(t[i:i+1100])
print("---SETUP---")
j = t.find("setup.exe")
print(t[j-200:j+350])
