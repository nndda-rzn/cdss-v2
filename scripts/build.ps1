# Build frontend into backend/app/static for single-process production serving.
$ErrorActionPreference = "Stop"
Push-Location frontend
npm install
npm run build
Pop-Location
Write-Host "Frontend built into backend/app/static"
