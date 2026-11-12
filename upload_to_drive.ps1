param(
    [string]$FilePath = "",
    [switch]$All
)

$DRIVE_CINEMA_FOLDER = "1bHMIsbn6FORPU-FG-gNmdgtGdkfXWCam"
$LOCAL_OUTPUTS = "D:\Cinematic_AI_Studio\outputs\final"

if ($FilePath -and (Test-Path $FilePath)) {
    $item = Get-Item $FilePath
    $szMb = [math]::Round($item.Length / 1MB, 2)
    Write-Host "`n[Drive Sync] Uploading single master: $($item.Name) ($szMb MB)..." -ForegroundColor Cyan
    $res = gdrive mutate upload $item.FullName --parent $DRIVE_CINEMA_FOLDER
    Write-Host "✓ $res" -ForegroundColor Green
    exit 0
}

Write-Host "`n=== Syncing Cinematic AI Studio Videos to Google Drive ===" -ForegroundColor Cyan
$existingRaw = gdrive readonly ls $DRIVE_CINEMA_FOLDER --json | ConvertFrom-Json
$existingNames = @{}
if ($existingRaw) {
    foreach ($entry in $existingRaw) {
        $existingNames[$entry.name] = $entry.id
    }
}

$files = Get-ChildItem -Path $LOCAL_OUTPUTS -Filter "*.mp4"
Write-Host "Found $($files.Count) local videos. Already on Drive: $($existingNames.Count)" -ForegroundColor Yellow

$uploaded = 0
foreach ($file in $files) {
    if ($existingNames.ContainsKey($file.Name)) {
        Write-Host "  [-] Skipped (already on Drive): $($file.Name)" -ForegroundColor DarkGray
        continue
    }

    $szMb = [math]::Round($file.Length / 1MB, 2)
    Write-Host "  [+] Uploading: $($file.Name) ($szMb MB)..." -ForegroundColor Green
    $out = gdrive mutate upload $file.FullName --parent $DRIVE_CINEMA_FOLDER
    Write-Host "      $out" -ForegroundColor Gray
    $uploaded++
}

Write-Host "`nFinished! Uploaded $uploaded new cinematic videos to Google Drive." -ForegroundColor Green
