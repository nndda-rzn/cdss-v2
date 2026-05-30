# Run backend (Flask :5000) and frontend (Vite :5173) in parallel.
$ErrorActionPreference = "Stop"
$backend = Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd backend; flask --app wsgi run --port 5000" -PassThru
$frontend = Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev" -PassThru
Write-Host "Backend PID $($backend.Id), Frontend PID $($frontend.Id)"
Write-Host "Press Ctrl+C in each window to stop."
