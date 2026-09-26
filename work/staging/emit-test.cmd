@echo off
setlocal EnableDelayedExpansion
set "DRV=E:\$WinPEDriver$"
echo BEFORE
call :emit DRV=!DRV!
echo AFTER_CALL
set "MSG=disc=!DRV!"
call :note
echo AFTER_NOTE
goto :eof
:emit
set "LINE=%*"
echo EMIT=[!LINE!]
goto :eof
:note
echo NOTE=[!MSG!]
goto :eof
