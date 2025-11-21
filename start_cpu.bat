@echo off
echo ========================================
echo   AI Agent Voice-to-Image Demo (CPU)
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo [ERROR] .env filen saknas!
    echo.
    echo Kopiera .env.example till .env och lagg till dina GEMINI_API_KEYs
    echo.
    pause
    exit /b 1
)

echo [1/3] Startar backend (main_cpu.py)...
start "AI Agent Backend (CPU)" cmd /k python main_cpu.py

REM Wait a bit for backend to start
timeout /t 3 /nobreak > nul

echo [2/3] Startar webserver pa port 8080...
start "AI Agent Webserver" cmd /k "set HTTP_PORT=8080 && python server.py"

REM Wait a bit for webserver to start
timeout /t 2 /nobreak > nul

echo [3/3] Oppnar webblasaren...
start http://localhost:8080

echo.
echo ========================================
echo   Allt igång!
echo ========================================
echo.
echo Webgranssnitt: http://localhost:8080
echo OBS: Kor i CPU-mode (lite langsammare)
echo.
echo Tryck pa en tangent for att avsluta...
pause > nul
