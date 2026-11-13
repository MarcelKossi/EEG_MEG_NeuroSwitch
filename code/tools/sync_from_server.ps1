# Copies results and preprocessing logs from the lab server to this PC.
# Run on a computer on the lab network, in PowerShell:
#   powershell -ExecutionPolicy Bypass -File E:\eeg_meg_switch_model_research\code\tools\sync_from_server.ps1
# The server password is asked for up to 3 times (one per copy).

# Server address and folder come from server_settings.ps1 (next to this script, not versioned).
# Create it once by copying server_settings.example.ps1 and filling in your values.
$Settings = Join-Path $PSScriptRoot "server_settings.ps1"
if (-not (Test-Path $Settings)) {
    Write-Host "Missing $Settings. Copy server_settings.example.ps1 to server_settings.ps1 and fill it in."
    exit 1
}
. $Settings
$Remote = $ServerWorkDir

$Root   = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$Stamp  = Get-Date -Format "yyyy-MM-dd_HHmm"
$Target = Join-Path $Root "results\server_sync\$Stamp"
$Logs   = Join-Path $Target "preprocessing_logs"
New-Item -ItemType Directory -Force -Path $Logs | Out-Null

Write-Host "1/3  Results (classical + deep)..."
scp -r "${Server}:${Remote}/results" "$Target"

Write-Host "2/3  Preprocessing logs per subject..."
scp "${Server}:${Remote}/derivatives/sub-*/sub-*_log.json" "$Logs"

Write-Host "3/3  Run logs (*.log)..."
scp "${Server}:${Remote}/eegmeg_pipeline/*.log" "$Logs"

Write-Host ""
Write-Host "Done. Files are in: $Target"
Write-Host "Summary tables: $Target\results\<classical|deep>\summary_*.md"
