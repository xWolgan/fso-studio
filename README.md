# Studio — improwizacja z AI w tekście, obrazie, wideo i dźwięku

*English: [README.en.md](README.en.md)*

Przeglądarkowe Studio, które powstało na warsztaty „Grupa poszukiwawcza formy AI” (Kraków, 2026). Jedno miejsce do pracy
z modelami generatywnymi w sześciu obszarach — **Tekst, Obraz, Wideo, Muzyka, SFX, Mowa** — z kolejką zadań, galerią,
notatkami i rozmówcą (LLM), który pomaga szukać formy, prowadzi „biblię” utworu i pisze prompty dla konkretnych modeli.

To repozytorium **nie zawiera żadnych kluczy, modeli ani dostępu do naszych maszyn**. Podłączasz własne:
- **własny komputer z kartą NVIDIA i ComfyUI** — generowanie lokalne, bez opłat;
- **własne klucze API** — OpenRouter (rozmowa) i HiggsField (wideo: Kling, WAN, MiniMax H3);
- albo jedno i drugie. Studio pokazuje tylko te modele, które Twoja instalacja umie uruchomić.

Interfejs: polski, angielski, francuski (przełącznik w nagłówku).

## Co jest w środku

| Obszar | Lokalnie (ComfyUI) | Przez API |
|---|---|---|
| Tekst | — (opcjonalnie lokalny LLM jako zapas) | OpenRouter (domyślnie Qwen 3.8 Flash) |
| Obraz | Z-Image Turbo, Qwen-Image 2.1 (+ Edit), Qwen-Image-Edit 2511, Ideogram 4 | — |
| Wideo | MiniMax H3 (+ klatki kluczowe, referencje), FastH3 V2, LTX-2.3, LTX-2.5, WAN 2.2 | Kling 3.0, Kling 3.0 Omni, WAN 3.0 (HiggsField); MiniMax H3 jako zapas dla lokalnego |
| Muzyka | ACE-Step 1.5 XL, MiniMax Music 3, YuE 2 (+ cover z nagrania) | — |
| SFX | Stable Audio 3 small-SFX (Woosh — osobna usługa, nie ma jej w repo) | — |
| Mowa | OmniVoice: tekst → mowa, projektowanie i klonowanie głosu (Breeze TTS — osobna usługa) | — |

Pełna lista z plikami do pobrania i licencjami: **[MODELE.md](MODELE.md)**. Licencje modeli są ich własne — część jest niekomercyjna.

## Wymagania

- **Python 3.11+**
- przeglądarka
- do generowania lokalnego: **ComfyUI ≥ 0.39** (https://github.com/comfyanonymous/ComfyUI) na komputerze z kartą NVIDIA
  (wideo: realnie 24–48 GB VRAM; obraz i dźwięk mniej); dla Mowy (OmniVoice) — węzły **TTS-Audio-Suite**
- opcjonalnie: `pdftotext` / `pdftoppm` (Poppler) — czytanie PDF-ów dołączonych w czacie

## Szybki start

```bash
git clone https://github.com/xWolgan/fso-studio.git
cd fso-studio
./start.sh            # Linux / macOS
```
Windows: dwuklik na **`start.cmd`** (albo `.\start.ps1` w PowerShellu).

Pierwsze uruchomienie tworzy `config.yaml` i `sekrety.env` z przykładów i instaluje zależności. Potem:

1. **Klucze** — wpisz do `sekrety.env` (nie trafia do gita):
   - `OPENROUTER_API_KEY` — https://openrouter.ai/keys (rozmowa, lustro, promptmaker, „opis → JSON”),
   - `HF_KEY` — https://console.higgsfield.ai, format `id_klucza:sekret` (wideo przez API; płatne).
2. **Maszyny** — w `config.yaml` → `maszyny:` dopisz swój ComfyUI (adres i obszary, które obsługuje). Bez karty graficznej zostaw `maszyny: []`.
3. **Pliki modeli** — pobierz do `ComfyUI/models/...` te, których chcesz używać (lista: `MODELE.md`). Modele, których nie masz, ukryj w `modele_wylaczone:`.
4. Uruchom ponownie i otwórz **http://127.0.0.1:8100**. Login to dowolna nazwa (bez hasła) — oddziela pliki i budżety osób.

### Tryb „tylko API” (bez karty graficznej)
Wystarczy `OPENROUTER_API_KEY` (Tekst) i/lub `HF_KEY` (Wideo przez API) oraz `maszyny: []`. Obszary bez modeli będą oznaczone jako „nieskonfigurowane”.

### Z własnym ComfyUI
```yaml
maszyny:
  - id: moj-pc
    nazwa: Mój komputer
    comfyui: http://127.0.0.1:8188
    role: [obraz, muzyka, sfx, mowa]     # dopisz „wideo”, jeśli karta to udźwignie
modele_wylaczone: [ideogram-4]           # modele, których wag nie pobrałeś
```
Kilka maszyn = kilka wpisów; Studio rozdziela zadania między nie (planowanie wg historii czasów, `mnoznik_czasu`, `priorytet`).

## Bezpieczeństwo — przeczytaj

- **Studio nie ma haseł.** Login to tylko nazwa. Domyślnie słucha wyłącznie na `127.0.0.1` (ten komputer).
  Udostępniaj je tylko w zaufanej sieci (`HOST=0.0.0.0 ./start.sh`) albo przez VPN typu Tailscale — **nigdy wprost w internecie**,
  bo każdy mógłby generować na Twój koszt i czytać pliki innych osób.
- Klucze trzymaj tylko w `sekrety.env`. Rozmowy i pliki użytkowników są w `zasoby/` (też poza gitem).
- Rozmowy w obszarze Tekst idą do dostawcy LLM (OpenRouter i dalej), a zadania API — do HiggsField.

## Budżet (tylko API)
Generacje przez API zużywają budżet liczony w „sekundach” (`budzet` w `config.yaml`): domyślnie 1000 s na osobę,
1 s = 0,042 USD. Lokalne generacje są bez limitu. Gdy zadanie lokalne potrwa dłużej niż `prog_zadania_s`, Studio zaproponuje model płatny.
Ceny w `modele/wideo/*.yaml` (`cena`) są z października 2026 (z rabatem promocyjnym) — sprawdź aktualne w HiggsField.

## Własne modele
Model = plik YAML w `modele/<obszar>/` + workflow ComfyUI w formacie API w `workflows/` (w ComfyUI: *Workflow → Export (API)*).
```yaml
id: moj-model
nazwa: Mój model
obszar: obraz                 # tekst | obraz | wideo | muzyka | sfx | mowa
kolejnosc: 50                 # miejsce na liście
licencja: Apache 2.0
opis: {pl: "Krótki opis", en: "Short description"}
backend: comfyui
workflow: obraz/moj-workflow.api.json
wyjscie: obraz
parametry:
  - id: prompt
    typ: prompt
    cel: ["@6.text"]          # „@<id węzła>.<wejście>” w workflow albo „<Klasa>.<wejście>” (wszystkie węzły tej klasy)
  - id: seed
    typ: seed
    cel: ["@3.seed"]
```
Więcej przykładów: istniejące pliki w `modele/` (proporcje, długość, wejścia obrazów/dźwięku, tryby, warianty, modele przez API).
Poradnik „jak promptować” dla modelu: `poradniki/<id>.md`; karta dla promptmakera: `prompty/modele/<id>.md`.

## Uwagi
- Czasy w opisach i poradnikach mierzyliśmy na **NVIDIA DGX Spark** (w tekstach: „Spark”) i RTX PRO 5000 48 GB.
- Rozmówca (prompty w `prompty/`) jest ustawiony pedagogicznie: zadaje pytania zamiast podawać gotowe rozwiązania. Możesz to zmienić
  w Studio (Tekst → podgląd i własne kopie promptów systemowych) albo w plikach.
- Tablica na duży ekran: **/tablica** (maszyny, kolejka, ostatnie wyniki — bez treści promptów).

Licencja: MIT (kod i teksty). Modele AI — ich własne licencje.
