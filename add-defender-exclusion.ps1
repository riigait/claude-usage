# Run this once as Administrator to add Defender exclusion for the widget exe.
# Right-click this file -> "Run with PowerShell" (then approve UAC prompt).

$EXE_PATH = Join-Path $PSScriptRoot "dist\ClaudeUsageWidget.exe"

if (-not (Test-Path $EXE_PATH)) {
    Write-Host "Exe not found at $EXE_PATH - run build.ps1 first." -ForegroundColor Red
    pause
    exit 1
}

Add-MpPreference -ExclusionPath $EXE_PATH
Write-Host "Defender exclusion added for: $EXE_PATH" -ForegroundColor Green
pause
