@echo off
REM Double-click this on Windows to start the World Cup 2026 Predictor.
cd /d "%~dp0"
where py >nul 2>nul && (py wc2026.py) || (python wc2026.py)
echo.
echo If a browser did not open, go to:  http://localhost:8000
pause
