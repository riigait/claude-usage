#Requires -Version 5.1
# Build ClaudeUsageChecker.exe and ClaudeUsageWidget.exe for this Windows machine.
# The checker exe contains the Python app code; Chromium is still installed by Playwright.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$DIST_DIR = Join-Path $PSScriptRoot "dist"
$BUILD_DIR = Join-Path $PSScriptRoot "build"
$CHECKER_EXE = Join-Path $DIST_DIR "ClaudeUsageChecker.exe"
$WIDGET_EXE = Join-Path $DIST_DIR "ClaudeUsageWidget.exe"
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

Step 3 "Building executables with PyInstaller"
Push-Location $PSScriptRoot
python -m PyInstaller check_usage.spec --distpath $DIST_DIR --workpath $BUILD_DIR --clean --noconfirm
python -m PyInstaller widget.spec --distpath $DIST_DIR --workpath $BUILD_DIR --clean --noconfirm
Pop-Location

foreach ($path in @($CHECKER_EXE, $WIDGET_EXE)) {
    if (-not (Test-Path $path)) {
        throw "Build failed - $path not found."
    }
    $sizeMB = [Math]::Round((Get-Item $path).Length / 1MB, 1)
    OK "Built: $path (${sizeMB} MB)"
}

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

Step 6 "Signing executables and adding Defender exclusions"
foreach ($path in @($CHECKER_EXE, $WIDGET_EXE)) {
    $sig = Set-AuthenticodeSignature `
        -FilePath $path `
        -Certificate $cert `
        -TimestampServer "http://timestamp.digicert.com" `
        -HashAlgorithm SHA256

    if ($sig.Status -eq "Valid") {
        OK "Signed $([System.IO.Path]::GetFileName($path))"
    } else {
        WARN "Signing status for $path`: $($sig.Status) - $($sig.StatusMessage)"
    }
}

foreach ($path in @($CHECKER_EXE, $WIDGET_EXE)) {
    try {
        Add-MpPreference -ExclusionPath $path -ErrorAction Stop
        OK "Defender exclusion added for $path"
    } catch {
        WARN "Could not add Defender exclusion for $path (may need admin): $_"
    }
}

Write-Host ""
Write-Host "Build complete:" -ForegroundColor Green
Write-Host "  $CHECKER_EXE" -ForegroundColor Green
Write-Host "  $WIDGET_EXE" -ForegroundColor Green
Write-Host ""
Write-Host "Run the checker once first, then launch the widget." -ForegroundColor Green
