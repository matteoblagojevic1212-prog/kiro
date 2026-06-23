@echo off
REM Launch the World Cup 2026 Predictor on Windows.
cd /d "%~dp0"
echo Starting World Cup 2026 Predictor...
echo Open http://localhost:8000 in your browser.
where py >nul 2>nul
if %errorlevel%==0 (
  py server.py
) else (
  python server.py
)
pause
