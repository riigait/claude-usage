#Requires -Version 5.1
# Run as Administrator to add Defender exclusions for the built executables.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$exePaths = @(
    (Join-Path $PSScriptRoot "dist\ClaudeUsageChecker.exe"),
    (Join-Path $PSScriptRoot "dist\ClaudeUsageWidget.exe")
)

$missing = $exePaths | Where-Object { -not (Test-Path $_) }
if ($missing) {
    Write-Host "Missing executable(s). Run build.ps1 first:" -ForegroundColor Red
    $missing | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
    pause
    exit 1
}

foreach ($path in $exePaths) {
    Add-MpPreference -ExclusionPath $path
    Write-Host "Defender exclusion added for: $path" -ForegroundColor Green
}

pause
