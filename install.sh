#!/usr/bin/env bash
# Instalator Studia (macOS / Linux). Uruchom w terminalu:
#   curl -fsSL https://raw.githubusercontent.com/xWolgan/fso-studio/main/install.sh | bash
# Pobiera Studio do ~/Studio (ponowne uruchomienie = aktualizacja; klucze, ustawienia i Twoje pliki zostają)
# i uruchamia je. Potrzebny Python 3.11+.
set -euo pipefail
REPO="xWolgan/fso-studio"
CEL="${STUDIO_DIR:-$HOME/Studio}"

echo; echo "== Studio: instalacja do $CEL =="; echo
# folder istnieje, nie jest pusty i nie ma w nim Studia → nie ruszamy cudzych plików
if [ -d "$CEL" ] && [ -n "$(ls -A "$CEL" 2>/dev/null)" ] && [ ! -f "$CEL/studio/main.py" ]; then
  echo "Folder $CEL już istnieje i zawiera inne pliki — nie nadpisuję go."
  echo "Wybierz inny folder, np.:  curl -fsSL https://raw.githubusercontent.com/xWolgan/fso-studio/main/install.sh | STUDIO_DIR=\"\$HOME/Studio-AI\" bash"
  exit 1
fi
if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
  echo "Potrzebny Python 3.11 lub nowszy."
  if [ "$(uname)" = "Darwin" ]; then
    echo "macOS: zainstaluj z https://www.python.org/downloads/ (albo: brew install python@3.12) i uruchom instalator ponownie."
  else
    echo "Linux: np. sudo apt install python3 python3-venv  (Ubuntu/Debian) i uruchom instalator ponownie."
  fi
  exit 1
fi
python3 -c "import venv, ensurepip" 2>/dev/null || { echo "Brak modułu venv — Ubuntu/Debian: sudo apt install python3-venv"; exit 1; }

TMP="$(mktemp -d)"
echo "Pobieram Studio z GitHuba…"
curl -fsSL "https://github.com/$REPO/archive/refs/heads/main.tar.gz" | tar -xz -C "$TMP"
ZRODLO="$(find "$TMP" -maxdepth 1 -type d -name 'fso-studio-*' | head -1)"
mkdir -p "$CEL"
# aktualizacja: kod podmieniany, Twoje pliki (klucze, ustawienia, wyniki, środowisko) zostają
find "$CEL" -mindepth 1 -maxdepth 1 ! -name config.yaml ! -name sekrety.env ! -name zasoby ! -name .venv -exec rm -rf {} +
cp -R "$ZRODLO"/. "$CEL"/
rm -rf "$TMP"
chmod +x "$CEL/start.sh"

if [ "$(uname)" = "Darwin" ] && [ -d "$HOME/Desktop" ] && [ -z "${STUDIO_BEZ_SKROTU:-}" ]; then   # macOS: dwuklik na pulpicie (otwiera Terminal ze Studiem)
  printf '#!/bin/bash\nexec "%s/start.sh"\n' "$CEL" > "$HOME/Desktop/Studio.command"
  chmod +x "$HOME/Desktop/Studio.command"
  echo "Na pulpicie jest 'Studio.command' — następnym razem wystarczy dwuklik."
fi
echo "Gotowe. Następnym razem uruchomisz Studio poleceniem:  $CEL/start.sh"
echo "Przeglądarka otworzy się sama na http://127.0.0.1:8100/ustawienia — wpisz tam klucze API."; echo
[ -n "${STUDIO_BEZ_STARTU:-}" ] && { echo "Zainstalowano (bez uruchamiania)."; exit 0; }
exec "$CEL/start.sh"
