# OmniCare AI - PowerShell Launcher
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "  OMNICARE AI - SNAPDRAGON HP PC CLINICAL EDGE STATION" -ForegroundColor White
Write-Host "  Target: HP OmniBook X / EliteBook Ultra (Snapdragon X Elite, 45 TOPS NPU)" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$scriptDir\backend"

Write-Host "[*] Freeing port 8000 if occupied..." -ForegroundColor Yellow
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { 
    Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue 
}

Write-Host "[*] Launching OmniCare AI FastAPI Backend on Hexagon NPU..." -ForegroundColor Yellow
$backendJob = Start-Process python -ArgumentList "main.py" -PassThru

Start-Sleep -Seconds 4

Write-Host "[*] Launching Clinical Cockpit in default browser..." -ForegroundColor Green
Start-Process "http://localhost:8000"

Write-Host "`n==============================================================================" -ForegroundColor Cyan
Write-Host "[✓] OmniCare AI Clinical Workstation is Active!" -ForegroundColor Green
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "    • Live Clinical Cockpit:  http://localhost:8000" -ForegroundColor White
Write-Host "    • Evaluator Showcase:     http://localhost:8000/showcase/" -ForegroundColor White
Write-Host "    • 10-Slide Pitch Deck:    http://localhost:8000/pitch-deck" -ForegroundColor White
Write-Host "    • Direct Offline File:    $scriptDir\frontend\index.html" -ForegroundColor Gray
Write-Host "`nPress Ctrl+C in the backend window to stop." -ForegroundColor Gray
