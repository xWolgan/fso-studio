"""Baza Studia (SQLite): zadania, zasoby, ujęcia. Pliki leżą w zasoby/<login>/..., baza je indeksuje."""
import json
import re
import shlex
import shutil
import sqlite3
import time
import unicodedata
from datetime import datetime
from pathlib import Path

from .config import BAZA, ZASOBY

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  login TEXT NOT NULL, obszar TEXT NOT NULL, model TEXT NOT NULL,
  wartosci TEXT NOT NULL, wejscia TEXT NOT NULL DEFAULT '{}',
  status TEXT NOT NULL DEFAULT 'czeka',          -- czeka | w_toku | gotowe | blad | anulowane
  maszyna TEXT, prompt_id TEXT, postep REAL DEFAULT 0,
  utworzone REAL NOT NULL, start REAL, koniec REAL, blad TEXT,
  wyniki TEXT NOT NULL DEFAULT '[]'              -- id zasobów
);
CREATE TABLE IF NOT EXISTS assets (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  login TEXT NOT NULL,
  rodzaj TEXT NOT NULL,                          -- obraz | wideo | dzwiek | tekst
  zrodlo TEXT NOT NULL,                          -- wynik | wgrane | artefakt
  sciezka TEXT NOT NULL UNIQUE,                  -- względem ZASOBY
  nazwa TEXT NOT NULL,
  obszar TEXT, model TEXT, job_id INTEGER,
  meta TEXT NOT NULL DEFAULT '{}',
  ukryte INTEGER NOT NULL DEFAULT 0,
  utworzone REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS ujecia (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  login TEXT NOT NULL, nr INTEGER NOT NULL, nazwa TEXT NOT NULL, katalog TEXT NOT NULL,
  utworzone REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS assets_login ON assets(login, utworzone);
CREATE TABLE IF NOT EXISTS llm_uzycie (           -- tokeny i koszt LLM przez API (podgląd wydatków)
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  login TEXT NOT NULL, tryb TEXT, wejscie INTEGER, wyjscie INTEGER, usd REAL, czas REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS nowe_konta (            -- wolne miejsca zajęte przez nowe loginy (config: budzet.nowe_konta)
  login TEXT PRIMARY KEY, sekund REAL NOT NULL, czas REAL NOT NULL
);
"""
MIGRATIONS = [  # (tabela, kolumna, definicja)
    ("assets", "ujecie_id", "INTEGER"),
    ("assets", "wybrane", "INTEGER NOT NULL DEFAULT 0"),
    ("jobs", "ujecie_id", "INTEGER"),
    ("jobs", "zamkniete", "INTEGER NOT NULL DEFAULT 0"),
    ("jobs", "grupa", "INTEGER"),
    ("jobs", "koszt", "REAL NOT NULL DEFAULT 0"),     # sekundy budżetu (tylko zadania przez API)
    ("jobs", "koszt_usd", "REAL"),
    ("jobs", "api", "TEXT"),                          # zadanie API: {request_id, status_url, cancel_url} (JSON)
]

LOGIN_RE = re.compile(r"^[a-z0-9][a-z0-9_.-]{1,23}$")
EXT_RODZAJ = {
    ".png": "obraz", ".jpg": "obraz", ".jpeg": "obraz", ".webp": "obraz", ".heic": "obraz", ".gif": "obraz",
    ".mp4": "wideo", ".mov": "wideo", ".webm": "wideo", ".mkv": "wideo",
    ".wav": "dzwiek", ".mp3": "dzwiek", ".flac": "dzwiek", ".m4a": "dzwiek", ".ogg": "dzwiek",
    ".md": "tekst", ".txt": "tekst",
}
LIMIT_CZEKAJACYCH = 8   # oczekujących zadań na osobę


def db() -> sqlite3.Connection:
    BAZA.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(BAZA, timeout=30)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    return c


def init():
    with db() as c:
        c.executescript(SCHEMA)
        for table, col, defn in MIGRATIONS:
            cols = {r[1] for r in c.execute(f"PRAGMA table_info({table})")}
            if col not in cols:
                c.execute(f"ALTER TABLE {table} ADD COLUMN {col} {defn}")
        # zadania API trwają u dostawcy także podczas restartu — dyspozytor wznowi ich śledzenie
        c.execute("""UPDATE jobs SET status='blad', blad='@e_restart'
                     WHERE status='w_toku' AND (maszyna IS NULL OR maszyna!='api')""")


def norm_login(s: str) -> str | None:
    s = (s or "").strip().lower()
    s = re.sub(r"\s+", "-", s)
    return s if LOGIN_RE.match(s) else None


def slug(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.translate(str.maketrans("łŁ", "lL"))).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:40] or "ujecie"


def user_dir(login: str, *parts) -> Path:
    p = ZASOBY / login
    for x in parts:
        p = p / x
    p.mkdir(parents=True, exist_ok=True)
    return p


def konto_istnieje(login: str) -> bool:
    return (ZASOBY / login).is_dir()


def nowe_konta() -> dict[str, float]:
    with db() as c:
        return {r[0]: r[1] for r in c.execute("SELECT login, sekund FROM nowe_konta ORDER BY czas").fetchall()}


def zajmij_miejsce(login: str, sekund: float, miejsc: int) -> bool:
    """Nowy login zajmuje wolne miejsce, jeśli jeszcze jest (atomowo)."""
    with db() as c:
        if c.execute("SELECT COUNT(*) FROM nowe_konta").fetchone()[0] >= miejsc:
            return False
        c.execute("INSERT OR IGNORE INTO nowe_konta (login, sekund, czas) VALUES (?,?,?)", (login, sekund, time.time()))
        return True


def rel(p: Path) -> str:
    return str(p.relative_to(ZASOBY)).replace("\\", "/")


# --- ujęcia ---

def ujecia(login) -> list[dict]:
    with db() as c:
        rows = c.execute("""SELECT u.*, (SELECT COUNT(*) FROM assets a WHERE a.ujecie_id=u.id) AS ile
                            FROM ujecia u WHERE login=? ORDER BY nr""", (login,)).fetchall()
    out = [dict(r) for r in rows]
    if not out:
        out = [create_ujecie(login, "ogólne", nr=0)]
    return out


def ujecie(uid) -> dict | None:
    with db() as c:
        r = c.execute("SELECT * FROM ujecia WHERE id=?", (uid,)).fetchone()
    return dict(r) if r else None


def default_ujecie(login) -> dict:
    return ujecia(login)[0]


def create_ujecie(login, nazwa, nr=None) -> dict:
    nazwa = (nazwa or "").strip()[:60]
    with db() as c:
        if nr is None:
            nr = (c.execute("SELECT COALESCE(MAX(nr),0) FROM ujecia WHERE login=?", (login,)).fetchone()[0]) + 1
        nazwa = nazwa or f"ujęcie {nr}"
        katalog = f"{nr:02d}-{slug(nazwa)}"
        user_dir(login, "ujecia", katalog)
        cur = c.execute("INSERT INTO ujecia(login,nr,nazwa,katalog,utworzone) VALUES(?,?,?,?,?)",
                        (login, nr, nazwa, katalog, time.time()))
        uid = cur.lastrowid
    return {**ujecie(uid), "ile": 0}


def rename_ujecie(uid, login, nazwa):
    u = ujecie(uid)
    if not u or u["login"] != login:
        return None
    nazwa = (nazwa or "").strip()[:60] or u["nazwa"]
    katalog = f"{u['nr']:02d}-{slug(nazwa)}"
    old, new = ZASOBY / login / "ujecia" / u["katalog"], ZASOBY / login / "ujecia" / katalog
    with db() as c:
        if katalog != u["katalog"] and old.exists() and not new.exists():
            old.rename(new)
            prefix_old, prefix_new = rel(old) + "/", rel(new) + "/"
            for r in c.execute("SELECT id, sciezka FROM assets WHERE ujecie_id=?", (uid,)).fetchall():
                if r["sciezka"].startswith(prefix_old):
                    c.execute("UPDATE assets SET sciezka=? WHERE id=?", (prefix_new + r["sciezka"][len(prefix_old):], r["id"]))
        else:
            katalog = u["katalog"]
        c.execute("UPDATE ujecia SET nazwa=?, katalog=? WHERE id=?", (nazwa, katalog, uid))
    return ujecie(uid)


def ujecie_dir(login, uid) -> tuple[Path, int]:
    u = ujecie(uid) if uid else None
    if not u or u["login"] != login:
        u = default_ujecie(login)
    return user_dir(login, "ujecia", u["katalog"]), u["id"]


def move_asset(asset_id, login, uid) -> bool:
    a, u = asset(asset_id), ujecie(uid)
    if not a or not u or a["login"] != login or u["login"] != login:
        return False
    src = ZASOBY / a["sciezka"]
    dst_dir = user_dir(login, "ujecia", u["katalog"])
    dst = dst_dir / src.name
    i = 1
    while dst.exists() and dst != src:
        dst, i = dst_dir / f"{src.stem}-{i}{src.suffix}", i + 1
    if src.exists() and dst != src:
        shutil.move(str(src), str(dst))
        side = src.with_suffix(src.suffix + ".json")
        if side.exists():
            shutil.move(str(side), str(dst.with_suffix(dst.suffix + ".json")))
    with db() as c:
        c.execute("UPDATE assets SET ujecie_id=?, sciezka=? WHERE id=?", (uid, rel(dst), asset_id))
    return True


# --- zadania ---

def add_job(login, obszar, model, wartosci, wejscia, ujecie_id=None, grupa=None, koszt=0.0, koszt_usd=None) -> int:
    with db() as c:
        cur = c.execute("""INSERT INTO jobs(login,obszar,model,wartosci,wejscia,utworzone,ujecie_id,grupa,koszt,koszt_usd)
                           VALUES(?,?,?,?,?,?,?,?,?,?)""",
                        (login, obszar, model, json.dumps(wartosci, ensure_ascii=False),
                         json.dumps(wejscia, ensure_ascii=False), time.time(), ujecie_id, grupa, koszt, koszt_usd))
        return cur.lastrowid


def spent(login) -> float:
    """Sekundy budżetu zużyte przez API (czekające i trwające są zarezerwowane; błąd/anulowanie = zwrot)."""
    with db() as c:
        return c.execute("""SELECT COALESCE(SUM(koszt),0) FROM jobs WHERE login=?
                            AND status IN ('czeka','w_toku','gotowe')""", (login,)).fetchone()[0]


def spent_all() -> list[dict]:
    with db() as c:
        rows = c.execute("""SELECT login, SUM(koszt) AS sekundy, SUM(COALESCE(koszt_usd,0)) AS usd, COUNT(*) AS zadan
                            FROM jobs WHERE koszt>0 AND status IN ('czeka','w_toku','gotowe') GROUP BY login""").fetchall()
    return [dict(r) for r in rows]


def add_llm_usage(login, tryb, wejscie, wyjscie, usd):
    with db() as c:
        c.execute("INSERT INTO llm_uzycie(login,tryb,wejscie,wyjscie,usd,czas) VALUES(?,?,?,?,?,?)",
                  (login, tryb, wejscie, wyjscie, usd, time.time()))


def llm_usage_all() -> list[dict]:
    with db() as c:
        rows = c.execute("""SELECT login, COUNT(*) AS odpowiedzi, SUM(wejscie) AS wejscie, SUM(wyjscie) AS wyjscie,
                            SUM(usd) AS usd FROM llm_uzycie GROUP BY login""").fetchall()
    return [dict(r) for r in rows]


def api_jobs_running() -> list[dict]:
    with db() as c:
        rows = c.execute("SELECT * FROM jobs WHERE status='w_toku' AND maszyna='api'").fetchall()
    return [dict(r) for r in rows]


def waiting_count(login) -> int:
    with db() as c:
        return c.execute("SELECT COUNT(*) FROM jobs WHERE login=? AND status='czeka'", (login,)).fetchone()[0]


def update_job(job_id, **kw):
    if not kw:
        return
    cols = ", ".join(f"{k}=?" for k in kw)
    with db() as c:
        c.execute(f"UPDATE jobs SET {cols} WHERE id=?", (*kw.values(), job_id))


def job(job_id):
    with db() as c:
        r = c.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    return dict(r) if r else None


def jobs_visible(login) -> list[dict]:
    """Do panelu kolejki: czekające, trwające, niezamknięte błędy i ostatnie gotowe."""
    with db() as c:
        active = c.execute("""SELECT * FROM jobs WHERE login=? AND (status IN ('czeka','w_toku')
                              OR (status='blad' AND zamkniete=0)) ORDER BY id DESC""", (login,)).fetchall()
        last = c.execute("SELECT * FROM jobs WHERE login=? AND status='gotowe' ORDER BY koniec DESC LIMIT 4",
                         (login,)).fetchall()
    return [dict(r) for r in active] + [dict(r) for r in last]


def pending_jobs():
    with db() as c:
        rows = c.execute("SELECT * FROM jobs WHERE status='czeka' ORDER BY id").fetchall()
    return [dict(r) for r in rows]


def queue_position(job_id, order: list[int]) -> int:
    return order.index(job_id) if job_id in order else 0


# --- zasoby ---

def add_asset(login, rodzaj, zrodlo, sciezka: Path, nazwa, obszar=None, model=None, job_id=None, meta=None,
              ujecie_id=None) -> int:
    with db() as c:
        cur = c.execute("""INSERT OR REPLACE INTO assets(login,rodzaj,zrodlo,sciezka,nazwa,obszar,model,job_id,meta,
                           utworzone,ujecie_id) VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                        (login, rodzaj, zrodlo, rel(sciezka), nazwa, obszar, model, job_id,
                         json.dumps(meta or {}, ensure_ascii=False), time.time(), ujecie_id))
        return cur.lastrowid


def asset(asset_id):
    with db() as c:
        r = c.execute("SELECT * FROM assets WHERE id=?", (asset_id,)).fetchone()
    return dict(r) if r else None


def parse_query(q: str) -> tuple[list[str], list[str]]:
    """'mgła "stary port" -noc' → (['mgła', 'stary port'], ['noc'])"""
    try:
        parts = shlex.split(q or "")
    except ValueError:
        parts = (q or "").split()
    inc, exc = [], []
    for p in parts:
        (exc if p.startswith("-") and len(p) > 1 else inc).append(p.lstrip("-").lower() if p.startswith("-") else p.lower())
    return inc, exc


def haystack(a: dict, uj_names: dict) -> str:
    m = json.loads(a["meta"] or "{}")
    s = m.get("ustawienia", {})
    parts = [str(s.get("prompt", "")), a.get("model") or "", m.get("nazwa_modelu", ""), a["login"], a["nazwa"],
             uj_names.get(a.get("ujecie_id"), "")]
    return " ".join(parts).lower()


def list_assets(viewer, kto="ja", rodzaj=None, obszar=None, ujecie_id=None, wybrane=False, q="", limit=300):
    sql, args = "SELECT * FROM assets WHERE 1=1", []
    if kto == "ja":
        sql += " AND login=?"; args.append(viewer)
    elif kto == "wszyscy":
        sql += " AND (login=? OR ukryte=0)"; args.append(viewer)
    else:
        sql += " AND login=? AND (ukryte=0 OR login=?)"; args += [kto, viewer]
    if rodzaj:
        sql += " AND rodzaj=?"; args.append(rodzaj)
    if obszar:
        sql += " AND obszar=?"; args.append(obszar)
    if ujecie_id:
        u = ujecie(ujecie_id)
        if u and u["nr"] == 0:   # ujęcie domyślne obejmuje też zasoby bez ujęcia
            sql += " AND (ujecie_id=? OR ujecie_id IS NULL)"
        else:
            sql += " AND ujecie_id=?"
        args.append(ujecie_id)
    if wybrane:
        sql += " AND wybrane=1"
    sql += " ORDER BY utworzone DESC"
    with db() as c:
        rows = [dict(r) for r in c.execute(sql + " LIMIT 5000", args).fetchall()]
        uj_names = {r[0]: r[1] for r in c.execute("SELECT id, nazwa FROM ujecia").fetchall()}
        domyslne = {r[0]: r[1] for r in c.execute("SELECT login, id FROM ujecia WHERE nr=0").fetchall()}
    for r in rows:   # zasoby sprzed ujęć należą do ujęcia domyślnego autora
        if r.get("ujecie_id") is None and r["login"] in domyslne:
            r["ujecie_id"] = domyslne[r["login"]]
    inc, exc = parse_query(q)
    if inc or exc:
        rows = [r for r in rows if (h := haystack(r, uj_names)) and all(t in h for t in inc) and not any(t in h for t in exc)]
    for r in rows:
        r["ujecie_nazwa"] = uj_names.get(r.get("ujecie_id"), "")
    return rows[:limit]


def logins():
    with db() as c:
        return [r[0] for r in c.execute("SELECT DISTINCT login FROM assets ORDER BY login").fetchall()]


def set_flag(asset_id, login, col, value: bool):
    assert col in ("ukryte", "wybrane")
    with db() as c:
        c.execute(f"UPDATE assets SET {col}=? WHERE id=? AND login=?", (1 if value else 0, asset_id, login))


def delete_assets(ids: list[int], login: str) -> tuple[list[int], list[str]]:
    """Trwale usuwa zasoby autora: plik, plik opisu .json i wpis w bazie.
    Pomija zasoby cudze i użyte jako wejście w czekającej / trwającej generacji. Zwraca (usunięte, powody pominięć)."""
    done, skipped = [], []
    with db() as c:
        busy = set()
        for (w,) in c.execute("SELECT wejscia FROM jobs WHERE status IN ('czeka','w_toku')").fetchall():
            busy |= {int(v) for v in json.loads(w or "{}").values() if str(v).isdigit()}
        for aid in ids:
            r = c.execute("SELECT * FROM assets WHERE id=?", (aid,)).fetchone()
            if not r or r["login"] != login:
                skipped.append(f"{aid}: nie Twój albo nie istnieje")
                continue
            if aid in busy:
                skipped.append(f"{r['nazwa']}: używany w trwającej generacji")
                continue
            p = ZASOBY / r["sciezka"]
            for f in (p, p.with_suffix(p.suffix + ".json")):
                try:
                    f.unlink()
                except FileNotFoundError:
                    pass
            c.execute("DELETE FROM assets WHERE id=?", (aid,))
            done.append(aid)
    return done, skipped


def result_path(login, ujecie_id, obszar, model, seed, ext, dopisek="") -> tuple[Path, int]:
    d, uid = ujecie_dir(login, ujecie_id)
    base = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}_{obszar}_{model}_{seed}" + (f"_{dopisek}" if dopisek else "")
    p, i = d / f"{base}{ext}", 1
    while p.exists():
        p, i = d / f"{base}-{i}{ext}", i + 1
    return p, uid
