# Studio — improwizacja z AI w tekście, obrazie, wideo i dźwięku

*English: [README.en.md](README.en.md)*

Przeglądarkowe Studio do pracy z modelami generatywnymi w sześciu obszarach — **Tekst, Obraz, Wideo, Muzyka, SFX, Mowa** —
z kolejką zadań, galerią, notatkami i rozmówcą (LLM), który pomaga szukać formy, prowadzi „biblię” utworu i pisze prompty
dla konkretnych modeli. Powstało na warsztaty „Grupa poszukiwawcza formy AI” (Kraków, 2026).

To wersja **dla jednej osoby, na własnym komputerze**. Modele działają **w chmurze, na Twoich kluczach API** — nie
potrzebujesz karty graficznej. Repozytorium nie zawiera żadnych kluczy ani dostępu do cudzych maszyn.

Interfejs: polski, angielski, francuski (przełącznik w nagłówku).

## Dostawcy

Klucze wpisujesz w Studiu (**Ustawienia**), pobierasz listę modeli dostawcy i zaznaczasz te, które mają się pojawić
w obszarach. Wybór możesz zmieniać w każdej chwili.

| Dostawca | Co daje w Studiu | Klucz |
|---|---|---|
| **OpenRouter** | tekst (setki modeli), obraz, wideo, mowa | https://openrouter.ai/keys |
| **fal.ai** | obraz, wideo, muzyka, efekty dźwiękowe, mowa (ponad tysiąc modeli; formularze budują się same) | https://fal.ai/dashboard/keys |
| **HiggsField** | wideo: Kling 3.0, Kling 3.0 Omni, WAN 3.0 | https://cloud.higgsfield.ai/api-keys |
| **Kling AI** | wideo (Kling 3.0, 3.0 Omni, 2.6), obraz, efekty dźwiękowe — bezpośrednio u Klinga | https://kling.ai/dev/api-key |
| **Kie.ai** | obraz, wideo, mowa (Kling, Wan, Veo, Seedream, Hailuo, ElevenLabs…) | https://kie.ai/api-key |
| **Claude** (Anthropic) | tekst | https://console.anthropic.com/settings/keys |
| **ChatGPT** (OpenAI) | tekst, obraz, mowa | https://platform.openai.com/api-keys |
| **Gemini** (Google) | tekst, obraz | https://aistudio.google.com/apikey |
| **Lokalnie** (Ollama, LM Studio, llama.cpp) | tekst na Twoim komputerze — bez kosztów, treść nie wychodzi na zewnątrz; zamiast klucza adres serwera | https://ollama.com/download |

Na start wystarczy jeden klucz — np. **OpenRouter** daje tekst, obraz, wideo i mowę. Modele oznaczone w Ustawieniach
„obsługa wkrótce” są widoczne, ale jeszcze niedostępne (m.in. muzyka Lyria, wideo i mowa Gemini).

## Instalacja jednym poleceniem

**Windows** — otwórz PowerShell (menu Start → wpisz „PowerShell”) i wklej:
```powershell
irm https://raw.githubusercontent.com/xWolgan/fso-studio/main/install.ps1 | iex
```
**macOS / Linux** — otwórz Terminal i wklej:
```bash
curl -fsSL https://raw.githubusercontent.com/xWolgan/fso-studio/main/install.sh | bash
```
Instalator pobiera Studio do folderu `Studio` w Twoim katalogu domowym, na Windowsie w razie potrzeby instaluje
Pythona, tworzy na pulpicie skrót **Studio** (macOS: `Studio.command`), uruchamia Studio i otwiera przeglądarkę na
Ustawieniach. Następnym razem wystarczy dwuklik na skrót. Ponowne uruchomienie instalatora = aktualizacja
(klucze, ustawienia i Twoje pliki zostają). Na macOS potrzebny jest Python 3.11+ (https://www.python.org/downloads/).

## Szybki start (ręcznie)

Potrzebujesz **Pythona 3.11+** i przeglądarki.

```bash
git clone https://github.com/xWolgan/fso-studio.git
cd fso-studio
./start.sh            # Linux / macOS
```
Windows: dwuklik na **`start.cmd`** (albo `.\start.ps1` w PowerShellu).

Pierwsze uruchomienie instaluje zależności i tworzy `config.yaml` oraz `sekrety.env`. Potem:

1. Otwórz **http://127.0.0.1:8100/ustawienia**.
2. Wpisz klucz dostawcy → **Zapisz** (Studio od razu sprawdza, czy działa).
3. **Pobierz listę modeli**, rozwiń ją i zaznacz modele — pojawią się w odpowiednich obszarach.
4. Opcjonalnie ustaw **limit wydatków** na miesiąc.

Logowania nie ma — Studio otwiera się od razu.

## Wydatki

Każda generacja w chmurze kosztuje według cennika dostawcy i jest **pobierana z Twojego konta u dostawcy**.
Pasek u góry pokazuje wydatki w tym miesiącu; po kliknięciu — dziś / miesiąc / łącznie i najdroższe modele.
Kwoty pochodzą od dostawców (OpenRouter podaje koszt każdego zapytania) albo z cennika modelu w Studiu; zadania,
dla których dostawca nie podaje ceny, są wyliczone osobno — sprawdź je w jego panelu. Gdy wydatki dojdą do limitu
z Ustawień, Studio wstrzyma płatne generacje (rozmowy działają dalej).

## Bezpieczeństwo — przeczytaj

- **Studio nie ma haseł.** Domyślnie słucha wyłącznie na `127.0.0.1` — tylko ten komputer. Nie wystawiaj go do sieci
  (`HOST=0.0.0.0`) ani do internetu: każdy, kto by się dostał, generowałby na Twój koszt i czytał Twoje pliki.
- **Ustawienia** (klucze, limit) działają tylko z tego komputera, nawet gdy Studio jest udostępnione w sieci.
  Klucze nigdy nie wracają do przeglądarki.
- Klucze są w `sekrety.env`, Twoje pliki, rozmowy i wybór modeli — w `zasoby/`. Oba są poza gitem.
- Treść rozmów i promptów trafia do dostawcy, którego model wybierzesz. W rozmowach przez OpenRouter Studio wybiera tylko
  dostawców, którzy nie zbierają danych z zapytań (przy obrazie, wideo i mowie obowiązują warunki dostawcy modelu).

## Opcjonalnie: modele lokalne

Bez kosztów, na Twoim komputerze. Wszystko ustawiasz w **Ustawieniach** — bez edycji plików.

- **Tekst:** zainstaluj [LM Studio](https://lmstudio.ai) (włącz serwer: Developer → Start Server) albo
  [Ollamę](https://ollama.com/download). W Ustawieniach → **Lokalnie** wpisz adres (LM Studio: `http://127.0.0.1:1234/v1`,
  Ollama: `http://127.0.0.1:11434/v1`), pobierz listę i zaznacz modele.
- **Obraz, wideo, muzyka, mowa:** zainstaluj [ComfyUI](https://www.comfy.org/download) (karta NVIDIA; wideo realnie
  24–48 GB VRAM) i pobierz pliki modeli według **[MODELE.md](MODELE.md)** (część modeli ma licencje niekomercyjne).
  W Ustawieniach → **ComfyUI na tym komputerze** wpisz adres (`http://127.0.0.1:8188`) — Studio sprawdzi, które modele
  masz zainstalowane (✓ gotowy / ✗ czego brakuje), i włączy tylko te.

Zaawansowane: kilka maszyn z ComfyUI albo własne modele — `config.yaml` → `maszyny` oraz pliki YAML w `modele/<obszar>/`
+ workflow ComfyUI w formacie API w `workflows/` (przykłady w istniejących plikach).

## Uwagi

- Rozmówca (prompty w `prompty/`) jest ustawiony pedagogicznie: zadaje pytania zamiast podawać gotowe rozwiązania.
  Zmienisz to w Studiu (Tekst → podgląd i własne kopie promptów systemowych) albo w plikach.
- Katalog Kie.ai jest zbierany z dokumentacji (Kie.ai nie ma katalogu w API). Gdy dojdą nowe modele:
  `python narzedzia/kie_katalog.py`.
- Opcjonalnie: `pdftotext` / `pdftoppm` (Poppler) — czytanie PDF-ów dołączonych w czacie.

Licencja: MIT (kod i teksty). Modele AI i usługi dostawców — ich własne licencje i warunki.
