#Requires -Version 5.1
# Build ClaudeUsage.exe for this Windows machine.
# Single executable: opens widget by default, runs checker with --check flag.
# Chromium is still installed separately by Playwright.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$DIST_DIR = Join-Path $PSScriptRoot "dist"
$BUILD_DIR = Join-Path $PSScriptRoot "build"
$APP_EXE = Join-Path $DIST_DIR "ClaudeUsage.exe"
$CERT_SUBJECT = "CN=Claude Usage Tools, O=Personal Tool"

function Step($n, $msg) { Write-Host "[${n}/6] $msg" -ForegroundColor Cyan }
function OK($msg) { Write-Host "  OK   $msg" -ForegroundColor Green }
function WARN($msg) { Write-Host "  WARN $msg" -ForegroundColor Yellow }

Step 1 "Installing build dependencies"
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt pyinstaller --quiet
OK "Dependencies ready"

Step 2 "Ensuring Playwright Chromium is installed"
python -m playwright install chromium
OK "Playwright Chromium ready"

Step 3 "Building executable with PyInstaller"
Push-Location $PSScriptRoot
python -m PyInstaller claude_usage.spec --distpath $DIST_DIR --workpath $BUILD_DIR --clean --noconfirm
Pop-Location

if (-not (Test-Path $APP_EXE)) {
    throw "Build failed - $APP_EXE not found."
}
$sizeMB = [Math]::Round((Get-Item $APP_EXE).Length / 1MB, 1)
OK "Built: $APP_EXE (${sizeMB} MB)"

Step 4 "Creating or reusing self-signed certificate"
$cert = Get-ChildItem Cert:\CurrentUser\My |
        Where-Object { $_.Subject -eq $CERT_SUBJECT -and $_.HasPrivateKey } |
        Sort-Object NotAfter -Descending |
        Select-Object -First 1

if ($cert) {
    $expiry = $cert.NotAfter.ToString("yyyy-MM-dd")
    OK "Reusing existing cert $($cert.Thumbprint), expires $expiry"
} else {
    $cert = New-SelfSignedCertificate `
        -Type CodeSigning `
        -Subject $CERT_SUBJECT `
        -KeyAlgorithm RSA -KeyLength 2048 `
        -HashAlgorithm SHA256 `
        -CertStoreLocation "Cert:\CurrentUser\My" `
        -NotAfter (Get-Date).AddYears(10) `
        -KeyExportPolicy Exportable
    OK "Created cert $($cert.Thumbprint)"
}

Step 5 "Trusting local certificate"
function Add-CertToStore($storeName, $storeScope) {
    $store = [System.Security.Cryptography.X509Certificates.X509Store]::new($storeName, $storeScope)
    $store.Open([System.Security.Cryptography.X509Certificates.OpenFlags]::ReadWrite)
    $store.Add($cert)
    $store.Close()
}

Add-CertToStore "TrustedPublisher" "CurrentUser"
Add-CertToStore "Root" "CurrentUser"
OK "Added certificate to CurrentUser trusted stores"

Step 6 "Signing executable and adding Defender exclusion"
$sig = Set-AuthenticodeSignature `
    -FilePath $APP_EXE `
    -Certificate $cert `
    -TimestampServer "http://timestamp.digicert.com" `
    -HashAlgorithm SHA256

if ($sig.Status -eq "Valid") {
    OK "Signed $([System.IO.Path]::GetFileName($APP_EXE))"
} else {
    WARN "Signing status for $APP_EXE`: $($sig.Status) - $($sig.StatusMessage)"
}

try {
    Add-MpPreference -ExclusionPath $APP_EXE -ErrorAction Stop
    OK "Defender exclusion added for $APP_EXE"
} catch {
    WARN "Could not add Defender exclusion for $APP_EXE (may need admin): $_"
}

Write-Host ""
Write-Host "Build complete:" -ForegroundColor Green
Write-Host "  $APP_EXE" -ForegroundColor Green
Write-Host ""
Write-Host "Run 'ClaudeUsage.exe --check' once first to log in, then launch ClaudeUsage.exe for the widget." -ForegroundColor Green
