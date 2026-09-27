p = r"I:\MacbookISOBuildingSpace\work\staging\a1706.cmd"
t = open(p, "rb").read().decode("ascii")
i = t.find("v14 delete oem0")
print(t[i:i+1600])
print("uninstall", "uninstall" in t.lower())
print("v13", "v13" in t)
