#!/usr/bin/env bash
# Uruchamia Studio (Linux / macOS): http://127.0.0.1:8100
# Pierwsze uruchomienie tworzy config.yaml i sekrety.env z przykładów oraz środowisko .venv z zależnościami.
# Dostęp z innych komputerów w sieci: HOST=0.0.0.0 ./start.sh  (Studio nie ma haseł — tylko w zaufanej sieci!)
set -euo pipefail
cd "$(dirname "$0")"
[ -f config.yaml ] || cp config.example.yaml config.yaml
[ -f sekrety.env ] || cp sekrety.env.example sekrety.env
[ -x .venv/bin/python ] || python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt
echo "Studio: http://${HOST:-127.0.0.1}:${PORT:-8100}   (Ctrl+C, żeby zatrzymać)"
if [ -z "${STUDIO_BEZ_PRZEGLADARKI:-}" ]; then
  # bez kluczy — od razu Ustawienia; przeglądarka otwiera się, gdy serwer już ruszy
  URL="http://127.0.0.1:${PORT:-8100}/"; grep -Eq '^[A-Z_]+_(KEY|API_KEY)=[^[:space:]]' sekrety.env || URL="${URL}ustawienia"
  OTWORZ="$(command -v open || command -v xdg-open || true)"
  [ -n "$OTWORZ" ] && ( sleep 5; "$OTWORZ" "$URL" ) >/dev/null 2>&1 &
fi
exec .venv/bin/uvicorn studio.main:app --host "${HOST:-127.0.0.1}" --port "${PORT:-8100}"
