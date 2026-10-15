# ACE-Step 1.5 XL — jak promptować

## Jak model słucha
Model muzyczny z dwoma polami tekstu: **opis (caption / tagi)** — gatunek, nastrój, instrumenty, brzmienie, produkcja — i **tekst utworu (lyrics)** ze znacznikami sekcji. Tempo (BPM), tonacja, metrum i długość mają **osobne ustawienia** — nie wpisuj ich do opisu. W Studiu działa wariant **sft** (50 kroków, z CFG): wolniejszy od turbo, ale bogatszy w detal i wyraźnie lepszy przy śpiewie.

## Struktura opisu (kolejność zalecana przez autorów)
`gatunek/styl → emocja/atmosfera → instrumenty → faktura brzmienia → charakter wokalu (jeśli jest) → epoka/produkcja`

Konkret wygrywa: „sad piano ballad with female breathy vocal” działa lepiej niż „a sad song”.

## Tekst utworu i muzyka instrumentalna
- Znaczniki sekcji: `[Intro]`, `[Verse]`, `[Chorus]`, `[Bridge]`, `[Outro]`; z krótkim dookreśleniem: `[Chorus - anthemic]`, `[Bridge - whispered]`.
- **Instrumentalnie:** pusty tekst albo `[Instrumental]`; rozwój utworu opisz znacznikami, np.:
```
[Intro - ambient]
[Main Theme - piano]
[Climax - powerful]
[Outro - fade out]
```
- Partie solowe: `[Guitar Solo]`, `[Piano Interlude]`, `[drum break]`.

## Na co jest wrażliwy / pułapki
- **Sprzeczność opisu i tekstu** (np. „violin solo” w opisie, `[Guitar Solo]` w tekście) psuje wynik.
- Nie piętrz dookreśleń w znaczniku (`[Chorus - anthemic - stacked harmonies - high energy]` — za dużo); złożony opis idzie do pola opisu.
- BPM i tonacja w opisie zamiast w ustawieniach — gorzej działa.
- Krótsze utwory (30–60 s) są najbardziej przewidywalne; metrum 4/4 najstabilniejsze.

## Przykłady (struktura)
- Opis: „minimal ambient, melancholic and spacious, felt piano and soft string pads, warm tape saturation, slow evolving textures, lo-fi home recording.” Tekst: `[Instrumental]`
- Opis: „dark post-rock, tense then cathartic, tremolo electric guitars, deep bass, live drums with heavy room reverb, 2000s production.” Tekst: `[Intro - quiet guitar]` `[Build - drums enter]` `[Climax - full band]` `[Outro - feedback fade]`

## Parametry, które realnie zmieniają wynik
- **BPM** (30–300), **tonacja**, **metrum**, **długość** (osobne pola). **Seed.**

## Źródła (dostęp 2026-10-05)
- ACE-Step 1.5 — Ultimate Guide (oficjalny): https://github.com/ace-step/ACE-Step-1.5/blob/main/docs/en/Tutorial.md
- ACE-Step 1.5 — A Musician's Guide: https://github.com/ace-step/ACE-Step-1.5/blob/main/docs/en/ace_step_musicians_guide.md
