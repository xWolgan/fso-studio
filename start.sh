#!/usr/bin/env bash
# Uruchamia Studio (Linux / macOS): http://127.0.0.1:8100
# Pierwsze uruchomienie tworzy config.yaml i sekrety.env z przykładów oraz środowisko .venv z zależnościami.
# Dostęp z innych komputerów w sieci: HOST=0.0.0.0 ./start.sh  (Studio nie ma haseł — tylko w zaufanej sieci!)
set -euo pipefail
cd "$(dirname "$0")"
[ -f config.yaml ] || { cp config.example.yaml config.yaml; echo "Utworzono config.yaml — dopasuj go (maszyny, modele)."; }
[ -f sekrety.env ] || { cp sekrety.env.example sekrety.env; echo "Utworzono sekrety.env — wpisz swoje klucze API."; }
[ -x .venv/bin/python ] || python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt
echo "Studio: http://${HOST:-127.0.0.1}:${PORT:-8100}"
exec .venv/bin/uvicorn studio.main:app --host "${HOST:-127.0.0.1}" --port "${PORT:-8100}"
