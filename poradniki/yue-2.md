# YuE 2 — jak promptować

## Jak model słucha
YuE 2 (3B) to z natury **model piosenek**: z opisu stylu i tekstu robi cały utwór z wokalem i akompaniamentem, z budową intro–zwrotka–refren–bridge–outro. Dwa pola: **styl** i **tekst**. Ma też tryb **cover**: z nagrania odczytuje melodię (zapis nutowy), a potem generuje utwór z nowym stylem i tekstem.

## Struktura
- **Styl:** po angielsku, w jednej linii, po przecinkach, krótko (ok. 15–35 słów). Kolejność: język, gatunek, charakter wokalu, tempo, instrumenty, cechy muzyczne. Przykład z dokumentacji: „English, warm piano pop, expressive female voice, acoustic piano, rounded bass and light drums, lyrical memorable melody, unhurried phrasing, 88 BPM”. Tempo (BPM) i tonację wpisz w styl — nie ma na nie osobnych pól.
- **Tekst:** tylko słowa do zaśpiewania, ze znacznikami sekcji `[Verse]`, `[Chorus]`, `[Bridge]`, `[Outro]` — każdy znacznik w osobnej linii, pusta linia między sekcjami. Polecenia muzyczne tylko w stylu.
- **Bez nawiasów z didaskaliami w tekście** (np. „(instrumental theme)”, „(guitar solo)”) — tekst w nawiasie może zostać zaśpiewany.
- **Instrumentalnie** (wg oficjalnego przepisu YuE2): styl zaczyna się od „Instrumental,” i kończy „no vocals, no singing, no choir, no spoken words.”; w polu tekstu **same znaczniki sekcji, bez żadnych słów ani nawiasów** (np. domyślne Studia). Oficjalny przepis dodatkowo przenosi melodię z partii wokalu do instrumentu — Studio tego nie robi, a nawet oficjalnie brak głosu nie jest gwarantowany. **Odsłuchaj wynik** — przy głosie zmień seed.

## Na co jest wrażliwy / pułapki
- Nie wkładaj do tekstu tagów stylu, BPM, akordów, emoji ani formatowania.
- **Budżet tokenów:** długi prompt skraca utwór; gdy budżet się kończy, nagranie może urwać się w pół frazy.
- Cover działa najlepiej, gdy nowy tekst ma podobną frazę i liczbę sylab jak oryginał, a sekcje idą w tej samej kolejności co w nagraniu. Styl opisuje brzmienie docelowe, nie oryginał; nagranie przenosi tylko melodię (nie głos ani brzmienie).
- Polski nie jest oficjalnie wspierany (udokumentowane: angielski, chiński) — zrób krótką próbę przed długim utworem.

## Przykład (struktura)
Instrumental:
- Styl: „Instrumental, slow cinematic folk, nylon guitar leading the melody, cello and soft hand percussion accompaniment, D minor, 70 BPM, a quiet opening that grows and fades out, intimate room sound, no vocals, no singing, no choir, no spoken words.”
- Tekst (same znaczniki, bez słów):
```
[Intro]

[Verse]

[Chorus]

[Outro]
```

## Parametry, które realnie zmieniają wynik
- **Maks. długość** — górna granica, utwór może skończyć się wcześniej (domyślnie 60 s, w coverze 120 s; ustaw nie mniej niż długość nagrania). Za niska urwie utwór w pół frazy.
- **Seed** — wspólny dla partytury i dźwięku; przy porównywaniu stylów trzymaj stały.
- Tryb planowania jest ustawiony przez Studio: „YuE 2” = full (melodia i akordy), „YuE 2 · cover” = melody (melodia z nagrania, swobodniejszy akompaniament).

## Źródła (dostęp 2026-10-05)
- ComfyUI — YuE2 Music Generation Guide: https://docs.comfy.org/tutorials/audio/yue2/yue2
- YuE — generation docs: https://github.com/multimodal-art-projection/YuE/blob/main/docs/generation.md
- YuE2 — skill instrumentalny (oficjalny przepis): https://github.com/multimodal-art-projection/YuE/tree/main/skills/yue2-music/instrumental
- ComfyUI — szablon coveru YuE2: https://github.com/Comfy-Org/workflow_templates/blob/main/templates/audio_yue2_music_cover.json
