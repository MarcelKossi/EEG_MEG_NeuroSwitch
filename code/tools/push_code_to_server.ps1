# Copies the pipeline code (code\pipeline) from this PC to the lab server.
# Run on a computer on the lab network, in PowerShell:
#   powershell -ExecutionPolicy Bypass -File E:\eeg_meg_switch_model_research\code\tools\push_code_to_server.ps1
# It overwrites the scripts in <ServerWorkDir>/eegmeg_pipeline/ on the server.
# Data, results and the Python environment are not touched.

# Server address and folder come from server_settings.ps1 (next to this script, not versioned).
# Create it once by copying server_settings.example.ps1 and filling in your values.
$Settings = Join-Path $PSScriptRoot "server_settings.ps1"
if (-not (Test-Path $Settings)) {
    Write-Host "Missing $Settings. Copy server_settings.example.ps1 to server_settings.ps1 and fill it in."
    exit 1
}
. $Settings
$Remote = "$ServerWorkDir/eegmeg_pipeline"

$Root  = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$Code  = Join-Path $Root "code\pipeline"
$Files = Get-ChildItem -Path $Code -File | Where-Object { $_.Extension -in ".py", ".md" } | ForEach-Object { $_.FullName }

Write-Host "Sending $($Files.Count) files to ${Server}:${Remote}/"
scp $Files "${Server}:${Remote}/"

Write-Host ""
Write-Host "Done. On the server, check the version with:"
Write-Host '  grep -c "feats\[m\]\[tr\]" classical_models.py   # 1 (v1.2)'
Write-Host '  ls cross_subject.py                             # present (v1.2)'
