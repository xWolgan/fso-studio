# Uruchamia Studio (Windows): http://127.0.0.1:8100   — albo dwuklik na start.cmd
# Pierwsze uruchomienie tworzy config.yaml i sekrety.env z przykładów oraz środowisko .venv z zależnościami.
# Dostęp z innych komputerów w sieci: $env:HOST = "0.0.0.0"; .\start.ps1  (Studio nie ma haseł — tylko w zaufanej sieci!)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path config.yaml)) { Copy-Item config.example.yaml config.yaml }
if (-not (Test-Path sekrety.env)) { Copy-Item sekrety.env.example sekrety.env }
if (-not (Test-Path .venv\Scripts\python.exe)) { py -3 -m venv .venv; if (-not $?) { python -m venv .venv } }
.\.venv\Scripts\python.exe -m pip install -q -r requirements.txt
$h = if ($env:HOST) { $env:HOST } else { "127.0.0.1" }
$p = if ($env:PORT) { $env:PORT } else { "8100" }
Write-Host "Studio: http://${h}:${p}   (zamknij to okno, żeby zatrzymać)"
if (-not $env:STUDIO_BEZ_PRZEGLADARKI) {
    # bez kluczy — od razu Ustawienia; przeglądarka otwiera się, gdy serwer już ruszy
    $klucze = @(Get-Content sekrety.env | Where-Object { $_ -match '^\s*[A-Z_]+_(KEY|API_KEY)\s*=\s*\S' }).Count
    $url = "http://127.0.0.1:${p}/" + $(if ($klucze -eq 0) { "ustawienia" } else { "" })
    Start-Process powershell -WindowStyle Hidden -ArgumentList "-NoProfile", "-Command", "Start-Sleep 5; Start-Process '$url'"
}
.\.venv\Scripts\python.exe -m uvicorn studio.main:app --host $h --port $p
