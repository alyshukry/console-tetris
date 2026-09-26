@echo off

cd /d "%~dp0"

start "Server" cmd /k "python -m server.main"
start "Player 1" cmd /k "python -m client.main"
start "Player 2" cmd /k "python -m client.main"
start "Player 3" cmd /k "python -m client.main"