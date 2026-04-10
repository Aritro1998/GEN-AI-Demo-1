# ============================================================================
# Policy Lens — Setup & Run Script (PowerShell)
# Creates venv, installs dependencies, seeds DB, starts backend & frontend
# ============================================================================

param(
    [switch]$SkipVenv,      # Skip venv creation if it already exists
    [switch]$SkipSeed       # Skip DB migration and seeding
)

$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
$VENV = Join-Path $ROOT ".venv"
$BACKEND = Join-Path $ROOT "Backend"
$FRONTEND = Join-Path $ROOT "Frontend"
$REQUIREMENTS = Join-Path $ROOT "requirements.txt"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Policy Lens - Setup & Run" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# -- Step 1: Create virtual environment ------------------------------------
if (-not $SkipVenv -and -not (Test-Path (Join-Path $VENV "Scripts\python.exe"))) {
    Write-Host "[1/5] Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv $VENV
    Write-Host "       Created at $VENV" -ForegroundColor Green
} else {
    Write-Host "[1/5] Virtual environment already exists - skipping" -ForegroundColor DarkGray
}

# -- Step 2: Install requirements ------------------------------------------
$PIP = Join-Path $VENV "Scripts\pip.exe"
$PYTHON = Join-Path $VENV "Scripts\python.exe"

Write-Host "[2/5] Installing requirements..." -ForegroundColor Yellow
& $PIP install -q -r $REQUIREMENTS
Write-Host "       Requirements installed" -ForegroundColor Green

# -- Step 3: Check .env file ----------------------------------------------
$ENV_FILE = Join-Path $BACKEND ".env"
$ENV_EXAMPLE = Join-Path $BACKEND ".env.example"

if (-not (Test-Path $ENV_FILE)) {
    Write-Host "[3/5] .env not found - copying from .env.example" -ForegroundColor Yellow
    Copy-Item $ENV_EXAMPLE $ENV_FILE
    Write-Host "       IMPORTANT: Edit $ENV_FILE and set your OPENAI_API_KEY" -ForegroundColor Red
    Write-Host "       Press Enter after updating .env to continue..." -ForegroundColor Red
    Read-Host
} else {
    Write-Host "[3/5] .env file found" -ForegroundColor Green
}

# -- Step 4: Migrate DB & seed demo data ----------------------------------
if (-not $SkipSeed) {
    Write-Host "[4/5] Running migrations and seeding demo data..." -ForegroundColor Yellow
    Push-Location $BACKEND
    & $PYTHON manage.py migrate --run-syncdb 2>&1 | Out-Null
    & $PYTHON manage.py seed_demo 2>&1
    Pop-Location
    Write-Host "       Database ready" -ForegroundColor Green
} else {
    Write-Host "[4/5] Skipping DB setup" -ForegroundColor DarkGray
}

# -- Step 5: Launch backend & frontend in separate terminals -------------
Write-Host "[5/5] Starting servers..." -ForegroundColor Yellow
Write-Host ""

# Backend — Django dev server on port 8000
$backendCmd = "cd '$BACKEND'; & '$PYTHON' manage.py runserver 0.0.0.0:8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

# Give backend a moment to start
Start-Sleep -Seconds 3

# Frontend — Streamlit on port 8501
$STREAMLIT = Join-Path $VENV "Scripts\streamlit.exe"
$APP_PY = Join-Path $FRONTEND "app.py"
$frontendCmd = "cd '$FRONTEND'; & '$STREAMLIT' run '$APP_PY' --server.port 8501 --server.headless true"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd -WindowStyle Normal

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Servers are starting!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Backend  : http://localhost:8000" -ForegroundColor White
Write-Host "  Frontend : http://localhost:8501" -ForegroundColor White
Write-Host ""
Write-Host "  Demo accounts:" -ForegroundColor DarkGray
Write-Host "    swarnali / swarnali123" -ForegroundColor DarkGray
Write-Host "    aritro   / aritro123" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  Close the terminal windows to stop the servers." -ForegroundColor DarkGray
Write-Host ""
