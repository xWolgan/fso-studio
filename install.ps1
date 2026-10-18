# Instalator Studia (Windows). Uruchom w PowerShellu:
#   irm https://raw.githubusercontent.com/xWolgan/fso-studio/main/install.ps1 | iex
# Pobiera Studio do %USERPROFILE%\Studio (ponowne uruchomienie = aktualizacja; klucze, ustawienia i Twoje pliki zostają),
# w razie potrzeby instaluje Pythona (winget), tworzy skrót „Studio” na pulpicie i uruchamia Studio.
$ErrorActionPreference = "Stop"
$Repo = "xWolgan/fso-studio"
$Cel = if ($env:STUDIO_DIR) { $env:STUDIO_DIR } else { Join-Path $HOME "Studio" }
$Zostaw = @("config.yaml", "sekrety.env", "zasoby", ".venv")

function Python-OK {
    $test = "import sys; print(sys.version_info >= (3, 11))"
    try { if ((& py -3 -c $test 2>$null) -eq "True") { return $true } } catch {}
    try { if ((& python -c $test 2>$null) -eq "True") { return $true } } catch {}
    return $false
}

Write-Host "`n== Studio: instalacja do $Cel ==`n"
if (-not (Python-OK)) {
    Write-Host "Brak Pythona 3.11+ — instaluję Python 3.12 (winget, tylko dla tego użytkownika)…"
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        Write-Host "Nie ma winget. Zainstaluj Pythona ręcznie: https://www.python.org/downloads/ (zaznacz 'Add python.exe to PATH') i uruchom instalator ponownie." -ForegroundColor Yellow
        return
    }
    winget install -e --id Python.Python.3.12 --scope user --accept-package-agreements --accept-source-agreements
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "User") + ";" + [Environment]::GetEnvironmentVariable("Path", "Machine")
    if (-not (Python-OK)) { Write-Host "Python zainstalowany — zamknij to okno, otwórz nowy PowerShell i uruchom instalator jeszcze raz." -ForegroundColor Yellow; return }
}

$tmp = Join-Path $env:TEMP ("studio-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force $tmp | Out-Null
Write-Host "Pobieram Studio z GitHuba…"
Invoke-WebRequest "https://github.com/$Repo/archive/refs/heads/main.zip" -OutFile "$tmp\studio.zip" -UseBasicParsing
Expand-Archive "$tmp\studio.zip" -DestinationPath $tmp -Force
$zrodlo = Get-ChildItem $tmp -Directory | Where-Object { $_.Name -like "fso-studio-*" } | Select-Object -First 1
New-Item -ItemType Directory -Force $Cel | Out-Null
# aktualizacja: kod podmieniany, Twoje pliki (klucze, ustawienia, wyniki, środowisko) zostają
Get-ChildItem $Cel -Force | Where-Object { $Zostaw -notcontains $_.Name } | Remove-Item -Recurse -Force
Get-ChildItem $zrodlo.FullName -Force | Copy-Item -Destination $Cel -Recurse -Force
Remove-Item $tmp -Recurse -Force

if (-not $env:STUDIO_BEZ_SKROTU) {
    $skrot = Join-Path ([Environment]::GetFolderPath("Desktop")) "Studio.lnk"
    $sh = New-Object -ComObject WScript.Shell
    $l = $sh.CreateShortcut($skrot)
    $l.TargetPath = Join-Path $Cel "start.cmd"
    $l.WorkingDirectory = $Cel
    $l.Description = "Studio — improwizacja z AI"
    $l.Save()
    Write-Host "Skrót 'Studio' jest na pulpicie. Następnym razem wystarczy dwuklik.`n"
}

Start-Process (Join-Path $Cel "start.cmd") -WorkingDirectory $Cel
Write-Host "Studio startuje w osobnym oknie (pierwszy raz instaluje zależności — chwilę to trwa)."
Write-Host "Przeglądarka otworzy się sama na http://127.0.0.1:8100/ustawienia — wpisz tam klucze API."
