@echo off
rem ===========================================================
rem starten.bat - startet den Wander Poster Generator
rem Danach im Browser oeffnen: http://localhost:5000
rem Beenden: dieses Fenster schliessen.
rem ===========================================================
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
    py start.py
) else (
    python start.py
)
pause
