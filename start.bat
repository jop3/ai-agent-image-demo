@echo off
echo ========================================
echo   Elevate Avega
echo ========================================
echo.

REM Check if virtual environment is activated
if not defined VIRTUAL_ENV (
    echo [INFO] Virtual environment inte aktiverat, aktiverar nu...
    if exist .venv\Scripts\activate.bat (
        call .venv\Scripts\activate.bat
        echo [OK] Virtual environment aktiverat!
        echo.
    ) else (
        echo [ERROR] Virtual environment .venv hittades inte!
        echo Kor python -m venv .venv for att skapa det.
        echo.
        pause
        exit /b 1
    )
) else (
    echo [OK] Virtual environment redan aktiverat
    echo.
)

REM Check if .env exists
if not exist .env (
    echo [ERROR] .env filen saknas!
    echo.
    echo Kopiera .env.example till .env och lagg till din GEMINI_API_KEY
    echo.
    pause
    exit /b 1
)

echo [1/4] Startar n8n med owner account...
start "n8n Workflow Automation" cmd /k "set N8N_USER_MANAGEMENT_DISABLED=true && set N8N_OWNER_EMAIL=tenkan@gmail.com && n8n"

REM Wait for n8n to start
timeout /t 5 /nobreak > nul

echo [2/4] Startar backend (main.py)...
start "AI Agent Backend" cmd /k python main.py

REM Wait a bit for backend to start
timeout /t 3 /nobreak > nul

echo [3/4] Startar webserver (server.py)...
start "AI Agent Webserver" cmd /k python server.py

REM Wait a bit for webserver to start
timeout /t 2 /nobreak > nul

echo [4/4] Oppnar webblasaren...
start http://localhost:8000

echo.
echo ========================================
echo   Allt igång!
echo ========================================
echo.
echo n8n Workflow Editor: http://localhost:5678
echo Webgranssnitt: http://localhost:8000
echo.
echo Tryck pa en tangent for att avsluta...
pause > nul
