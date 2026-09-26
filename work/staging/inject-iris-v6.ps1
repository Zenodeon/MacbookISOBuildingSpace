
$ErrorActionPreference = "Stop"
$Log = "I:\MacbookISOBuildingSpace\work\staging\inject-iris-v6.log"
$Wim = "I:\MacbookISOBuildingSpace\work\iso-root\sources\boot.wim"
$Mnt = "I:\MacbookISOBuildingSpace\work\mount-boot"
$Inf = 'I:\MacbookISOBuildingSpace\work\iso-root\$WinPEDriver$\IntelIrisSetup\igdiris64.inf'
$Cmd = "I:\MacbookISOBuildingSpace\work\staging\a1706.cmd"
$Sys = 'I:\MacbookISOBuildingSpace\work\iso-root\$WinPEDriver$\IntelIrisSetup\igdkmd64.sys'
function Log([string]$m) {
  $line = "{0} {1}" -f (Get-Date -Format "HH:mm:ss"), $m
  Add-Content -LiteralPath $Log -Value $line -Encoding Ascii
  Write-Host $line
}
function Run-Reg([string[]]$argList) {
  Log ("reg " + ($argList -join " "))
  $p = Start-Process -FilePath "reg.exe" -ArgumentList $argList -Wait -PassThru -NoNewWindow -RedirectStandardOutput "$env:TEMP\a1706-reg-out.txt" -RedirectStandardError "$env:TEMP\a1706-reg-err.txt"
  $out = ""
  if (Test-Path "$env:TEMP\a1706-reg-out.txt") { $out += (Get-Content "$env:TEMP\a1706-reg-out.txt" -Raw) }
  if (Test-Path "$env:TEMP\a1706-reg-err.txt") { $out += (Get-Content "$env:TEMP\a1706-reg-err.txt" -Raw) }
  if ($out) { Add-Content -LiteralPath $Log -Value $out.TrimEnd() -Encoding Ascii }
  if ($p.ExitCode -ne 0) { throw "reg failed $($p.ExitCode): $($argList -join ' ')" }
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
  $existing = @(Get-WindowsDriver -Path $Mnt | Where-Object { $_.OriginalFileName -match "igdiris64" })
  foreach ($d in $existing) {
    Log ("remove " + $d.Driver + " " + $d.OriginalFileName)
    Remove-WindowsDriver -Path $Mnt -Driver $d.Driver | Out-Null
  }
  if ($existing.Count -eq 0) { Log "no staged igdiris64 to remove" }
  Log "add-driver"
  Add-WindowsDriver -Path $Mnt -Driver $Inf -ForceUnsigned | Out-Null
  $added = @(Get-WindowsDriver -Path $Mnt | Where-Object { $_.OriginalFileName -match "igdiris64" })
  foreach ($d in $added) { Log ("staged " + $d.Driver + " " + $d.OriginalFileName + " " + $d.Version) }
  if ($added.Count -lt 1) { throw "igdiris64 was not staged" }
  $destSys = Join-Path $Mnt "Windows\System32\drivers\igdkmd64.sys"
  Copy-Item -LiteralPath $Sys -Destination $destSys -Force
  Log ("copied sys " + (Get-Item -LiteralPath $destSys).Length)
  $hive = Join-Path $Mnt "Windows\System32\config\SYSTEM"
  Run-Reg @("load","HKLM\A1706SYS",$hive)
  $loaded = $true
  $q = reg.exe query "HKLM\A1706SYS\Select" /v Current
  Add-Content -LiteralPath $Log -Value ($q -join "`n") -Encoding Ascii
  $curLine = $q | Where-Object { $_ -match "Current" } | Select-Object -First 1
  if ($curLine -notmatch "0x([0-9A-Fa-f]+)") { throw "could not read Select\Current" }
  $n = [Convert]::ToInt32($Matches[1], 16)
  $cs = "ControlSet{0:D3}" -f $n
  Log "control set $cs"
  $svc = "HKLM\A1706SYS\$cs\Services\igfx"
  Run-Reg @("add",$svc,"/v","Type","/t","REG_DWORD","/d","1","/f")
  Run-Reg @("add",$svc,"/v","Start","/t","REG_DWORD","/d","0","/f")
  Run-Reg @("add",$svc,"/v","ErrorControl","/t","REG_DWORD","/d","0","/f")
  Run-Reg @("add",$svc,"/v","Group","/t","REG_SZ","/d","Video","/f")
  Run-Reg @("add",$svc,"/v","ImagePath","/t","REG_EXPAND_SZ","/d","\SystemRoot\System32\drivers\igdkmd64.sys","/f")
  $guid = "{4d36e968-e325-11ce-bfc1-08002be10318}"
  $keys = @(
    "pci#ven_8086&dev_1927",
    "pci#ven_8086&dev_1927&subsys_015d106b&rev_0a"
  )
  foreach ($k in $keys) {
    $path = "HKLM\A1706SYS\$cs\Control\CriticalDeviceDatabase\$k"
    Run-Reg @("add",$path,"/v","Service","/t","REG_SZ","/d","igfx","/f")
    Run-Reg @("add",$path,"/v","ClassGUID","/t","REG_SZ","/d",$guid,"/f")
  }
  Run-Reg @("query",$svc)
  Copy-Item -LiteralPath $Cmd -Destination (Join-Path $Mnt "Windows\System32\a1706.cmd") -Force
  Log "copied a1706.cmd"
  Run-Reg @("unload","HKLM\A1706SYS")
  $loaded = $false
  Log "commit"
  Dismount-WindowsImage -Path $Mnt -Save | Out-Null
  Log "SUCCESS"
  exit 0
} catch {
  Log ("FAIL " + $_.Exception.Message)
  if ($loaded) {
    Start-Sleep -Seconds 1
    reg.exe unload HKLM\A1706SYS | Out-Null
  }
  if (Test-Path -LiteralPath $Mnt) {
    Dismount-WindowsImage -Path $Mnt -Discard -ErrorAction SilentlyContinue | Out-Null
  }
  exit 1
}
