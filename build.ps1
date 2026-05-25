#Requires -Version 5.1
# Build ClaudeUsageWidget.exe and make it trusted on this Windows 11 machine.
# Run once. Subsequent runs reuse the same cert. No admin rights needed.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$EXE_NAME     = "ClaudeUsageWidget"
$DIST_DIR     = Join-Path $PSScriptRoot "dist"
$EXE_PATH     = Join-Path $DIST_DIR "$EXE_NAME.exe"
$CERT_SUBJECT = "CN=Claude Usage Widget, O=Personal Tool"

function Step($n, $msg) { Write-Host "[${n}/6] $msg" -ForegroundColor Cyan }
function OK($msg)        { Write-Host "  OK   $msg" -ForegroundColor Green }
function WARN($msg)      { Write-Host "  WARN $msg" -ForegroundColor Yellow }

# 1 - Install PyInstaller
Step 1 "Installing PyInstaller"
pip install pyinstaller --quiet
OK "PyInstaller ready"

# 2 - Build EXE
Step 2 "Building exe with PyInstaller"
Push-Location $PSScriptRoot
pyinstaller widget.spec --distpath dist --workpath build --clean --noconfirm
Pop-Location

if (-not (Test-Path $EXE_PATH)) {
    throw "Build failed - $EXE_PATH not found."
}
$sizeMB = [Math]::Round((Get-Item $EXE_PATH).Length / 1MB, 1)
OK "Built: $EXE_PATH (${sizeMB} MB)"

# 3 - Self-signed code-signing certificate
Step 3 "Creating or reusing self-signed certificate"
$cert = Get-ChildItem Cert:\CurrentUser\My |
        Where-Object { $_.Subject -eq $CERT_SUBJECT -and $_.HasPrivateKey } |
        Sort-Object NotAfter -Descending |
        Select-Object -First 1

if ($cert) {
    $expiry = $cert.NotAfter.ToString("yyyy-MM-dd")
    OK "Reusing existing cert $($cert.Thumbprint) expires $expiry"
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

# 4 - Sign the EXE
Step 4 "Signing the exe"

$sig = Set-AuthenticodeSignature `
    -FilePath $EXE_PATH `
    -Certificate $cert `
    -TimestampServer "http://timestamp.digicert.com" `
    -HashAlgorithm SHA256

if ($sig.Status -eq "Valid") {
    OK "Signed with SHA-256 + RFC3161 timestamp (Set-AuthenticodeSignature)"
} else {
    WARN "Signing status: $($sig.Status) - $($sig.StatusMessage)"
}

# 5 - Trust the certificate on this machine
Step 5 "Adding cert to Trusted Publishers + Root (CurrentUser)"

function Add-CertToStore($storeName, $storeScope) {
    $store = [System.Security.Cryptography.X509Certificates.X509Store]::new($storeName, $storeScope)
    $store.Open([System.Security.Cryptography.X509Certificates.OpenFlags]::ReadWrite)
    $store.Add($cert)
    $store.Close()
}

Add-CertToStore "TrustedPublisher" "CurrentUser"
OK "Added to CurrentUser\TrustedPublisher"

Add-CertToStore "Root" "CurrentUser"
OK "Added to CurrentUser\Root (validates certificate chain)"

# 6 - Windows Defender exclusion
Step 6 "Adding Windows Defender path exclusion"
try {
    Add-MpPreference -ExclusionPath $EXE_PATH -ErrorAction Stop
    OK "Defender exclusion added for $EXE_PATH"
} catch {
    WARN "Could not add Defender exclusion (may need admin): $_"
    WARN "If blocked: right-click the exe, Properties, Unblock."
}

Write-Host ""
Write-Host "Build complete: $EXE_PATH" -ForegroundColor Green
Write-Host "Windows will trust this exe on this machine." -ForegroundColor Green
Write-Host "Run with: .\dist\ClaudeUsageWidget.exe" -ForegroundColor Green
