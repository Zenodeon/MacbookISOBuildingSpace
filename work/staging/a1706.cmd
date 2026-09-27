@echo off
setlocal EnableDelayedExpansion
if exist X:\a1706.ran goto :eof
echo ran>X:\a1706.ran
set LOGX=X:\a1706-setup-log.txt
set LOGS=
for %%L in (C D E F G H I J K L M N O P Q R S T U V W Y Z) do if exist %%L:\ call :try %%L
set "MSG=A1706 setup log v10 %DATE% %TIME%"
call :note
set "MSG=writable drives:!LOGS!"
call :note
set "MSG=logs appended to \A1706Logs on each writable drive"
call :note
wpeinit
set RC=!ERRORLEVEL!
set "MSG=wpeinit finished errorlevel=!RC!"
call :note
call :copysapi
set "MSG=step after-wpeinit"
call :note
set "MSG=v10 BasicDisplay stays on, start igfx after log"
call :note
call :dump sc query igfx
call :dump sc query BasicDisplay
set "MSG=step start igfx"
call :note
call :dump sc start igfx
call :dump sc query igfx
set DRV=
for %%L in (C D E F G H I J K L M N O P Q R S T U V W Y Z) do if exist %%L:\ call :finddrv %%L
set "MSG=disc=!DRV!"
call :note
if not defined DRV (
  set "MSG=ERROR missing WinPEDriver"
  call :note
  goto :afterdrv
)
set "TAG=thunderbolt"
set "ONE=!DRV!\Thunderbolt\tbt81x.inf"
call :loadone
set "TAG=cirrus4208"
set "ONE=!DRV!\CirrusAudioCS4208x64\cs4208_36.inf"
call :loadone
set "TAG=cirrus4206"
set "ONE=!DRV!\CirrusAudioCS4206x64\cs420x_46.inf"
call :loadone
call :cue speakers
set "TAG=keyboard"
set "ONE=!DRV!\AppleSPIKeyboard\AppleSPIKeyboard.inf"
call :loadone
call :cue keyboard
set "TAG=touchbar"
set "ONE=!DRV!\AppleDFR64\AppleDFR.inf"
call :loadone
:afterdrv
call :dump pnputil /enum-devices /connected
call :dump pnputil /enum-devices /problem
call :dump pnputil /enum-devices /class Display
call :dump pnputil /enum-devices /class Monitor
call :dump pnputil /enum-drivers
call :dump reg query HKLM\SYSTEM\CurrentControlSet\Enum\DISPLAY /s
call :dump reg query HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers /s
call :dump sc query igfx
call :dump sc query BasicDisplay
set "MSG=----- volumes -----"
call :note
for %%L in (C D E F G H I J K L M N O P Q R S T U V W X Y Z) do if exist %%L:\ (
  vol %%L: >X:\a1706-cmd-out.txt 2>&1
  call :addfile X:\a1706-cmd-out.txt
)
dir %SystemRoot%\System32\DisplaySwitch.exe >X:\a1706-cmd-out.txt 2>&1
call :addfile X:\a1706-cmd-out.txt
if exist %SystemRoot%\System32\DisplaySwitch.exe (
  set "MSG=DisplaySwitch.exe present"
  call :note
) else (
  set "MSG=ERROR missing DisplaySwitch.exe"
  call :note
)
call :copysapi
if exist %SystemRoot%\System32\Narrator.exe start "" %SystemRoot%\System32\Narrator.exe
set "MSG=v10 igfx demand-start, BasicDisplay left enabled"
call :note
set "MSG=display cycle start %TIME%"
call :note
call :cue display
call :copysapi
if exist %SystemRoot%\System32\DisplaySwitch.exe (
  for /L %%N in (1,1,8) do (
    %SystemRoot%\System32\DisplaySwitch.exe /clone
    ping -n 3 127.0.0.1 >nul
    %SystemRoot%\System32\DisplaySwitch.exe /extend
    ping -n 3 127.0.0.1 >nul
    %SystemRoot%\System32\DisplaySwitch.exe /external
    ping -n 3 127.0.0.1 >nul
  )
)
set "MSG=display cycle finished %TIME%"
call :note
call :cue done
call :copysapi
if exist X:\sources\setup.exe (
  X:\sources\setup.exe
) else (
  %SYSTEMDRIVE%\sources\setup.exe
)
goto :eof
:try
echo probe>"%~1:\a1706-write.test"
if not exist "%~1:\a1706-write.test" goto :tryfolder
del "%~1:\a1706-write.test"
if exist "%~1:\a1706-write.test" goto :eof
set LOGS=!LOGS! %~1
if not exist "%~1:\A1706Logs\" mkdir "%~1:\A1706Logs"
goto :eof
:tryfolder
if not exist "%~1:\A1706Logs\" goto :eof
echo probe>"%~1:\A1706Logs\a1706-write.test"
if not exist "%~1:\A1706Logs\a1706-write.test" goto :eof
del "%~1:\A1706Logs\a1706-write.test"
if exist "%~1:\A1706Logs\a1706-write.test" goto :eof
set LOGS=!LOGS! %~1
goto :eof
:finddrv
set "MSG=check %~1"
call :note
if exist "%~1:\$WinPEDriver$\IntelIrisSetup\igdiris64.inf" (
  set "DRV=%~1:\$WinPEDriver$"
  set "MSG=iris-inf-on %~1"
  call :note
)
goto :eof
:loadone
set "MSG=step load !TAG!"
call :note
if not exist "!ONE!" (
  set "MSG=ERROR missing !ONE!"
  call :note
  goto :eof
)
set "MSG=LOAD !ONE!"
call :note
drvload "!ONE!" >X:\a1706-cmd-out.txt 2>&1
set RC=!ERRORLEVEL!
call :addfile X:\a1706-cmd-out.txt
if !RC! equ 0 (
  set "MSG=errorlevel=!RC! loaded !TAG!"
) else (
  set "MSG=ERROR errorlevel=!RC! !TAG!"
)
call :note
call :copysapi
goto :eof
:dump
set "MSG=----- %* -----"
call :note
%* >X:\a1706-cmd-out.txt 2>&1
set RC=!ERRORLEVEL!
call :addfile X:\a1706-cmd-out.txt
if !RC! equ 0 (
  set "MSG=dump errorlevel=!RC!"
) else (
  set "MSG=ERROR dump errorlevel=!RC!"
)
call :note
goto :eof
:copysapi
if not exist "%SystemRoot%\inf\setupapi.dev.log" (
  set "MSG=ERROR missing setupapi.dev.log"
  call :note
  goto :eof
)
for %%D in (!LOGS!) do copy /y "%SystemRoot%\inf\setupapi.dev.log" "%%D:\A1706Logs\a1706-setupapi.dev.log" >nul
set "MSG=copied setupapi.dev.log !TAG!"
call :note
goto :eof
:addfile
if not exist "%~1" goto :eof
type "%~1" >>"%LOGX%"
for %%D in (!LOGS!) do type "%~1" >>"%%D:\A1706Logs\a1706-setup-log.txt"
goto :eof
:cue
if not exist %SystemRoot%\System32\a1706cue.exe (
  set "MSG=ERROR missing a1706cue.exe"
  call :note
  goto :eof
)
%SystemRoot%\System32\a1706cue.exe %~1
set RC=!ERRORLEVEL!
set "MSG=cue %~1 errorlevel=!RC!"
call :note
goto :eof
:note
>>"%LOGX%" echo(!MSG!
for %%D in (!LOGS!) do >>"%%D:\A1706Logs\a1706-setup-log.txt" echo(!MSG!
goto :eof
