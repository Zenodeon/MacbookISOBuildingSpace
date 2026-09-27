$ErrorActionPreference = "Stop"
$Log = "I:\MacbookISOBuildingSpace\work\staging\inject-iris-v12.log"
$Wim = "I:\MacbookISOBuildingSpace\work\iso-root\sources\boot.wim"
$Mnt = "I:\MacbookISOBuildingSpace\work\mount-boot"
$Inf = "I:\MacbookISOBuildingSpace\work\staging\iris1545\slim\igdiris64.inf"
$Cmd = "I:\MacbookISOBuildingSpace\work\staging\a1706.cmd"
$Bcd1 = "I:\MacbookISOBuildingSpace\work\iso-root\efi\microsoft\boot\bcd"
$Bcd2 = "I:\MacbookISOBuildingSpace\work\iso-root\boot\bcd"
function Log([string]$m) {
  $line = "{0} {1}" -f (Get-Date -Format "HH:mm:ss"), $m
  Add-Content -LiteralPath $Log -Value $line -Encoding Ascii
  Write-Host $line
}
Set-Content -LiteralPath $Log -Value "start" -Encoding Ascii
$loaded = $false
try {
  attrib -R $Wim
  if (Test-Path -LiteralPath $Mnt) {
    cmd /c "dism /Unmount-Image /MountDir:$Mnt /Discard" | Out-Null
    if (Test-Path -LiteralPath $Mnt) { Remove-Item -LiteralPath $Mnt -Recurse -Force -ErrorAction SilentlyContinue }
  }
  New-Item -ItemType Directory -Path $Mnt | Out-Null
  Log "mount"
  Mount-WindowsImage -ImagePath $Wim -Index 2 -Path $Mnt | Out-Null
  Log "mounted"
  $existing = @(Get-WindowsDriver -Path $Mnt | Where-Object { $_.OriginalFileName -match "igdiris64" -or ($_.ClassName -eq "Display" -and $_.ProviderName -match "Intel") })
  foreach ($d in $existing) {
    Log ("remove " + $d.Driver + " " + $d.OriginalFileName + " " + $d.Version)
    Remove-WindowsDriver -Path $Mnt -Driver $d.Driver | Out-Null
  }
  if ($existing.Count -eq 0) { Log "no staged igdiris64 to remove" }
  $oldSys = Join-Path $Mnt "Windows\System32\drivers\igdkmd64.sys"
  if (Test-Path -LiteralPath $oldSys) {
    Remove-Item -LiteralPath $oldSys -Force
    Log "deleted old igdkmd64.sys"
  } else {
    Log "no old igdkmd64.sys in drivers"
  }
  Log "add-driver"
  Add-WindowsDriver -Path $Mnt -Driver $Inf -ForceUnsigned | Out-Null
  $added = @(Get-WindowsDriver -Path $Mnt | Where-Object { $_.OriginalFileName -match "igdiris64" })
  foreach ($d in $added) { Log ("staged " + $d.Driver + " " + $d.OriginalFileName + " " + $d.Version + " " + $d.ClassName) }
  if ($added.Count -lt 1) { throw "igdiris64 was not staged" }
  Copy-Item -LiteralPath $Cmd -Destination (Join-Path $Mnt "Windows\System32\a1706.cmd") -Force
  Log "copied a1706.cmd"
  Dismount-WindowsImage -Path $Mnt -Save | Out-Null
  Log "committed"
  attrib -R -S -H $Bcd1
  attrib -R -S -H $Bcd2
  & bcdedit.exe /store $Bcd1 /set "{default}" nointegritychecks on | Out-String | ForEach-Object { Log $_ }
  & bcdedit.exe /store $Bcd2 /set "{default}" nointegritychecks on | Out-String | ForEach-Object { Log $_ }
  Log "SUCCESS"
  exit 0
} catch {
  Log ("FAIL " + $_.Exception.Message)
  if (Test-Path -LiteralPath $Mnt) {
    Dismount-WindowsImage -Path $Mnt -Discard -ErrorAction SilentlyContinue | Out-Null
  }
  exit 1
}
