@echo off

cd /d "%~dp0"

start "Server" cmd /k "python -m server.main"
start "Client 1" cmd /k "python -m client.main"
start "Client 2" cmd /k "python -m client.main"
start "Client 3" cmd /k "python -m client.main"