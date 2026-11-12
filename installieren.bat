@echo off
rem ===========================================================
rem installieren.bat - installiert die benoetigten Bibliotheken
rem (flask, staticmap, Pillow). Nur einmal noetig.
rem Doppelklick genuegt. Python muss installiert sein.
rem ===========================================================
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
    py -m pip install -r requirements.txt
) else (
    python -m pip install -r requirements.txt
)
echo.
echo Fertig. Jetzt starten.bat doppelklicken.
pause
