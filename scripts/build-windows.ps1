$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

Write-Host ""
Write-Host "DFG-Kursverwaltung - Windows-Build"
Write-Host "=================================="
Write-Host ""

$python = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    throw "Virtuelle Python-Umgebung wurde nicht gefunden: $python"
}

Write-Host "Entferne alte Build-Verzeichnisse ..."

Remove-Item `
    (Join-Path $projectRoot "build") `
    -Recurse `
    -Force `
    -ErrorAction SilentlyContinue

Remove-Item `
    (Join-Path $projectRoot "dist") `
    -Recurse `
    -Force `
    -ErrorAction SilentlyContinue

Write-Host "Prüfe Python-Quellcode ..."

& $python -m compileall -q `
    (Join-Path $projectRoot "src\dfg_kursverwaltung")

if ($LASTEXITCODE -ne 0) {
    throw "Python-Kompilierungsprüfung fehlgeschlagen."
}

Write-Host "Erstelle Windows-Anwendung ..."

& $python -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --onedir `
    --name "DFG-Kursverwaltung" `
    --icon (Join-Path $projectRoot "src\dfg_kursverwaltung\resources\icons\DFG-Kursverwaltung.ico") `
    --paths (Join-Path $projectRoot "src") `
    --add-data "$projectRoot\src\dfg_kursverwaltung\resources;dfg_kursverwaltung\resources" `
    --add-data "$projectRoot\src\dfg_kursverwaltung\database\schema.sql;dfg_kursverwaltung\database" `
    (Join-Path $projectRoot "src\dfg_kursverwaltung\main.py")

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller-Build fehlgeschlagen."
}

$exe = Join-Path `
    $projectRoot `
    "dist\DFG-Kursverwaltung\DFG-Kursverwaltung.exe"

if (-not (Test-Path $exe)) {
    throw "EXE wurde nicht erzeugt: $exe"
}

Write-Host ""
Write-Host "Build erfolgreich:"
Write-Host $exe
