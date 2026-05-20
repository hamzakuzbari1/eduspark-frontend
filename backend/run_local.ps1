# Start EduSpark API locally (PostgreSQL on localhost — no Docker)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (Test-Path "venv\Scripts\Activate.ps1") {
    .\venv\Scripts\Activate.ps1
} elseif (Test-Path ".venv\Scripts\Activate.ps1") {
    .\.venv\Scripts\Activate.ps1
}

$env:PYTHONPATH = (Get-Location).Path
Write-Host "EduSpark API -> http://127.0.0.1:8000/docs"
Write-Host "PostgreSQL should be running on localhost (see scripts/setup_local_db.sql)"
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
