@echo off
echo ========================================
echo   AI Agent Voice-to-Image Demo
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo [ERROR] .env filen saknas!
    echo.
    echo Kopiera .env.example till .env och lagg till din GEMINI_API_KEY
    echo.
    pause
    exit /b 1
)

echo [1/3] Startar backend (main.py)...
start "AI Agent Backend" cmd /k python main.py

REM Wait a bit for backend to start
timeout /t 3 /nobreak > nul

echo [2/3] Startar webserver (server.py)...
start "AI Agent Webserver" cmd /k python server.py

REM Wait a bit for webserver to start
timeout /t 2 /nobreak > nul

echo [3/3] Oppnar webblasaren...
start http://localhost:8000

echo.
echo ========================================
echo   Allt igång!
echo ========================================
echo.
echo Webgranssnitt: http://localhost:8000
echo.
echo Tryck pa en tangent for att avsluta...
pause > nul
