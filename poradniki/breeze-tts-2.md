# Breeze TTS 2 — jak promptować

## Jak model słucha
Model mowy BreezeBlue — **tylko angielski i chiński** (polskiego nie obsługuje; do polskiego: OmniVoice). Mocna strona to sterowanie głosem opisem: **projektowanie głosu** prozą (bez nagrania) i **reżyseria** — klonowanie głosu z nagrania z poleceniem, jak ma zagrać (ton, emocja, tempo, sposób podania).

## Struktura
- **Projektowanie głosu:** opis prozą w języku tekstu, np. „A warm, thoughtful young woman with a clear voice and a calm, reflective delivery.”
- **Reżyseria (z nagraniem):** polecenie aktorskie, np. „Speak slowly with a restrained, serious tone.” Można w nim prosić o akcent, śmiech, westchnienia, zmęczenie, zdenerwowanie.
- **Zdarzenia w tekście (angielski):** w nawiasach okrągłych — `(laugh)`, `(cough)`, `(clears throat)`, `(sigh)`; po chińsku w kwadratowych — `[笑]`, `[叹气]`.

## Na co jest wrażliwy / pułapki
- Język opisu powinien zgadzać się z językiem tekstu.
- Nagranie do klonu: czysta mowa, mało tła, z **dokładną transkrypcją** w polu „transkrypcja próbki”.
- **Czysty klon:** próbka + transkrypcja, pole „głos i sposób mówienia” **puste** (domyślnie), CFG 1. Każde wpisane polecenie zamienia klon w reżyserię.
- W Studiu usługa obsługuje **jedno zapytanie naraz** — przy kolejce trzeba chwilę poczekać.

## Przykład (struktura)
- Opis głosu: „An elderly man with a low, gravelly voice, speaking slowly, as if remembering something painful.”
- Tekst: „I kept the key for years. (sigh) I never found the door.”

## Parametry, które realnie zmieniają wynik
- **Siła instrukcji (CFG)** — zaawansowane, 0,5–4. Przy opisie głosu i reżyserii autorzy zalecają 4. Bez instrukcji zostaw 1 (inna wartość kończy się błędem).

## Licencja
Wagi tylko do badań i użytku niekomercyjnego.

## Źródła (dostęp 2026-10-05)
- Hugging Face — BreezeBlue/Breeze-TTS-2: https://huggingface.co/BreezeBlue/Breeze-TTS-2
- BreezeBlue — Introducing Breeze TTS 2: https://breezeblue.ai/breeze-tts-2
