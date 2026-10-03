@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

set CLIENTS=2

start "Server" cmd /k "python -m server.main"
timeout /t 1 >nul

set "WT=wt -M -d . cmd /k python -m client.main"

set /a SPLITS=CLIENTS-1
for /l %%k in (1,1,%SPLITS%) do (
    set /a "LEFT=CLIENTS-%%k"
    set /a "TOTAL=LEFT+1"
    set /a "PCT=LEFT*100/TOTAL"
    set "WT=!WT! ; split-pane -V -s 0.!PCT! -d . cmd /k python -m client.main"
)

echo %WT%
%WT%