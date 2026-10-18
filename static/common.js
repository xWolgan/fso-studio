// Wspólne: API, budowanie elementów, podgląd i opis zasobu, okna.
const T = window.T || {};
const L = (o) => (o && typeof o === "object") ? (o[LANG] || (LANG !== "pl" && o.en) || o.pl || o.en || "") : (o || "");
const LANG = ["pl", "en", "fr"].includes(window.LANG) ? window.LANG : "pl";
const LOCALE = { pl: "pl-PL", en: "en-GB", fr: "fr-FR" }[LANG];
// tekst z {zmiennymi}: tf("klucz", {n: 3})
const tf = (k, v = {}) => String(T[k] ?? k).replace(/\{(\w+)\}/g, (_, x) => v[x] ?? "");

async function api(path, opts = {}) {
  const r = await fetch(path, { headers: opts.body && !(opts.body instanceof FormData) ? { "Content-Type": "application/json" } : {}, ...opts });
  if (!r.ok) {
    let msg = r.status + "";
    try { const j = await r.json(); msg = j.detail || msg; } catch (e) {}
    throw new Error(msg);
  }
  return r.json();
}

function h(tag, attrs = {}, ...kids) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "class") e.className = v;
    else if (k.startsWith("on")) e.addEventListener(k.slice(2), v);
    else if (k === "html") e.innerHTML = v;
    else e.setAttribute(k, v === true ? "" : v);
  }
  for (const k of kids.flat(Infinity)) {
    if (k === null || k === undefined || k === false) continue;
    e.append(k instanceof Node ? k : document.createTextNode(k));
  }
  return e;
}

function toast(msg) {
  const t = h("div", { class: "toast" }, msg);
  document.body.append(t);
  setTimeout(() => t.remove(), 1600);
}

function mediaEl(a, { controls = true, thumb = false } = {}) {
  if (a.rodzaj === "obraz") return h("img", { src: a.url, loading: "lazy", alt: a.nazwa, draggable: "false" });
  if (a.rodzaj === "wideo") {
    const v = h("video", { src: a.url, preload: "metadata", controls: controls && !thumb, loop: true, playsinline: true });
    if (thumb) { v.muted = true; v.addEventListener("mouseenter", () => v.play()); v.addEventListener("mouseleave", () => v.pause()); }
    return v;
  }
  if (a.rodzaj === "dzwiek") return thumb ? h("div", { class: "kind" }, (a.meta?.nazwa_modelu ? a.meta.nazwa_modelu + " — " : "") + (a.meta?.ustawienia?.prompt || a.nazwa).slice(0, 160)) : h("audio", { src: a.url, controls: true, preload: "metadata" });
  return h("div", { class: "kind" }, a.nazwa);
}

function fmtDate(ts) {
  const d = new Date(ts * 1000);
  return d.toLocaleString(LOCALE, { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
}

// Prompt skopiowany z czatu albo notatki: bez ``` i bez znaków ucieczki markdownu (edytor notatek dopisuje „\” przed _ [ ] * …).
function czystyPrompt(t) {
  let s = String(t || "").trim();
  const m = s.match(/^```[\w-]*\n([\s\S]*?)\n?```$/);
  if (m) s = m[1].trim();
  return s.replace(/\\([!#$%&'()*+,\-.:;<=>?@[\]^_`{|}~])/g, "$1");
}
// JSON ukryty w tekście (cały tekst, blok ``` albo od pierwszej „{” do ostatniej „}”) → czytelnie sformatowany; brak → null.
function jsonZTekstu(t) {
  const s = czystyPrompt(t);
  const blok = s.match(/```[\w-]*\n([\s\S]*?)```/);
  for (const x of [s, blok && blok[1], s.includes("{") ? s.slice(s.indexOf("{"), s.lastIndexOf("}") + 1) : null]) {
    if (!x) continue;
    try { const o = JSON.parse(x); if (o && typeof o === "object" && !Array.isArray(o)) return jsonCzytelny(o); } catch (e) {}
  }
  return null;
}
// Wcięcia 2 spacje, ale krótkie listy (bbox, palety) w jednej linii: [80, 100, 300, 900]
function jsonCzytelny(o) {
  return JSON.stringify(o, null, 2).replace(/\[\n\s*([^\[\]{}]*?)\n\s*\]/g, (_, x) => "[" + x.split(/,\n\s*/).join(", ") + "]");
}
// Co jest nie tak z promptem w JSON (tekst do pokazania) albo "" gdy jest dobrze.
function bladJson(t) {
  const s = String(t || "").trim();
  if (!s.startsWith("{")) return T.json_proza;
  try { JSON.parse(s); return ""; } catch (e) {
    let poz = +((e.message.match(/position (\d+)/) || [])[1] ?? NaN);
    const lc = e.message.match(/line (\d+) column (\d+)/);
    if (lc) return tf("json_blad", { l: lc[1], k: lc[2] });
    if (isNaN(poz)) return T.json_blad_ogolny;
    const przed = s.slice(0, poz).split("\n");
    return tf("json_blad", { l: przed.length, k: przed[przed.length - 1].length + 1 });
  }
}

function escapeHtml(s) { return String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])); }

// Podświetlenie trafień wyszukiwania (słowa z zapytania, bez wykluczeń).
function highlight(text, q) {
  let html = escapeHtml(text || "");
  const terms = [];
  (q || "").replace(/"([^"]+)"|(\S+)/g, (_, a, b) => { const t = a || b; if (t && !t.startsWith("-")) terms.push(t); });
  for (const t of terms.sort((a, b) => b.length - a.length)) {
    const re = new RegExp("(" + t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "gi");
    html = html.replace(re, "<mark>$1</mark>");
  }
  return html;
}

const ROW_LABELS = { proporcje: "w_proporcje", tryb: "w_tryb", rozdzielczosc: "w_rozdzielczosc", dlugosc_s: "w_dlugosc_s", klatki: "w_klatki", kroki: "w_kroki",
  dostawca: "w_dostawca", endpoint: "w_endpoint", wariant: "w_wariant", fps: "w_fps" };

// Opis zasobu: prompt, ustawienia (ze strzałkami „przenieś”), autor, czas, ścieżka, akcje.
// Trwałe usuwanie (tylko własne pliki), zawsze z potwierdzeniem.
async function deleteAssets(ids, onDone) {
  if (!ids.length) return;
  if (!confirm(T.usun_pyt.replace("{n}", ids.length))) return;
  try {
    const r = await api("/api/zasoby/usun", { method: "POST", body: JSON.stringify({ ids }) });
    toast(`${T.usunieto}: ${r.usuniete.length}` + (r.pominiete.length ? " · " + r.pominiete.join("; ") : ""));
    onDone && onDone(r.usuniete);
  } catch (e) { toast(e.message); }
}

function metaView(a, { onReuse, onTake, onDelete, q = "", takeable = () => false } = {}) {
  const m = a.meta || {};
  const s = m.ustawienia || {};
  const arrow = (key, val) => onTake && takeable(key) ? h("button", { class: "arrow", title: T.przenies, onclick: () => onTake(key, val) }, "↑") : null;
  const rows = [];
  rows.push([T.model_l, m.nazwa_modelu || a.model || "—", m.model ? h("button", { class: "arrow", title: T.przenies, onclick: () => onTake && onTake("__model", m.model) }, onTake ? "↑" : "") : null]);
  if (m.czas_s) rows.push([T.czas_gen, m.czas_s + " s", null]);
  for (const [k, v] of Object.entries(s)) {
    if (k === "prompt" || (typeof v === "string" && v.length > 120)) continue;
    rows.push([(ROW_LABELS[k] ? T[ROW_LABELS[k]] : "") || k, String(v), arrow(k, v)]);
  }
  const wejscie = (k) => { const [id, nr] = k.split(" "); return (T["we." + id] || id) + (nr ? " " + nr : ""); };
  if (m.wejscia) for (const [k, v] of Object.entries(m.wejscia)) rows.push([wejscie(k), v.nazwa + (v.autor !== a.login ? " · " + v.autor : ""), null]);
  rows.push([T.autor, a.login, null]);
  if (a.ujecie_nazwa) rows.push([T.ujecie, a.ujecie_nazwa, null]);
  rows.push(["", fmtDate(a.utworzone), null]);
  const acts = h("div", { class: "acts" });
  if (onReuse && m.model) acts.append(h("button", { class: "btn", onclick: () => onReuse(a) }, T.powtorz));
  acts.append(h("a", { class: "btn", href: a.url + "?pobierz=1" }, T.pobierz));
  if (a.login === window.LOGIN) {
    const b = h("button", { class: "btn quiet" }, a.ukryte ? T.odkryj : T.ukryj);
    b.onclick = async () => { await api(`/api/zasoby/${a.id}/ukryj?ukryj=${!a.ukryte}`, { method: "POST" }); a.ukryte = !a.ukryte; b.textContent = a.ukryte ? T.odkryj : T.ukryj; };
    acts.append(b);
    if (onDelete) acts.append(h("button", { class: "btn quiet danger", onclick: () => deleteAssets([a.id], onDelete) }, T.usun_trwale));
  }
  return h("div", {},
    s.prompt ? h("div", { class: "ph" }, h("span", {}, T.prompt), arrow("prompt", s.prompt)) : null,
    s.prompt ? h("div", { class: "prompt", html: highlight(s.prompt, q) }) : null,
    h("dl", {}, rows.map(([k, v, ar]) => [h("dt", {}, k), h("dd", {}, v, ar ? " " : "", ar)])),
    h("div", { class: "path", title: T.sciezka }, a.sciezka || ""),
    h("div", { style: "height:10px" }),
    acts);
}

function starBtn(a, onChange) {
  if (a.login !== window.LOGIN) return a.wybrane ? h("span", { class: "star on" }, "★") : null;
  const b = h("button", { class: "star" + (a.wybrane ? " on" : ""), title: a.wybrane ? T.odznacz : T.wybierz }, a.wybrane ? "★" : "☆");
  b.onclick = async (e) => {
    e.stopPropagation();
    a.wybrane = !a.wybrane;
    await api(`/api/zasoby/${a.id}/wybrane?tak=${a.wybrane}`, { method: "POST" });
    b.classList.toggle("on", a.wybrane); b.textContent = a.wybrane ? "★" : "☆";
    onChange && onChange(a);
  };
  return b;
}

// Budżet generacji przez API (sekundy) — w górnym pasku; generacje lokalne nie schodzą z budżetu.
const fmtS = (x) => (Math.round(x * 10) / 10).toLocaleString(LOCALE) + " s";
async function odswiezBudzet() {
  const el = document.getElementById("budzet");
  if (!el) return null;
  try {
    const b = await api("/api/budzet");
    if (b.tryb === "usd") {                             // jeden użytkownik: wydatki w USD (bez budżetu w sekundach)
      const usd = (x) => (Math.round((x || 0) * 100) / 100).toLocaleString(LOCALE, { minimumFractionDigits: 2 }) + " USD";
      el.textContent = tf("wydatki_pasek", { u: usd(b.miesiac.usd) });
      el.classList.toggle("malo", Boolean(b.limit && b.miesiac.usd >= b.limit * 0.85));
      el.onclick = (e) => {
        e.preventDefault();
        modal(T.wydatki_tytul, h("div", { class: "budzet-info" },
          h("p", {}, T.wydatki_dzis + " ", h("b", {}, usd(b.dzis)), " · " + T.wydatki_miesiac + " ", h("b", {}, usd(b.miesiac.usd)),
            " · " + T.wydatki_razem + " ", usd(b.razem)),
          b.limit ? h("p", {}, tf("wydatki_limit", { l: usd(b.limit) })) : null,
          b.miesiac.modele.length ? h("ul", {}, b.miesiac.modele.map((x) => h("li", {}, `${x.nazwa}: ${usd(x.usd)} (${x.zadan})`))) : null,
          b.miesiac.tekst_usd ? h("p", {}, tf("wydatki_tekst", { u: usd(b.miesiac.tekst_usd) })) : null,
          b.miesiac.bez_ceny ? h("p", { class: "hint" }, tf("wydatki_bez_ceny", { n: b.miesiac.bez_ceny })) : null,
          h("p", { class: "hint" }, T.wydatki_opis)));
      };
      return b;
    }
    el.textContent = tf("budzet_pasek", { s: fmtS(b.zostalo) });
    el.classList.toggle("malo", b.zostalo < b.przydzial * 0.15);
    el.onclick = (e) => {
      e.preventDefault();
      modal(T.budzet_tytul, h("div", { class: "budzet-info" },
        h("p", {}, h("b", {}, fmtS(b.zostalo)), " " + T.budzet_zostalo_z + " ", fmtS(b.przydzial), " · " + T.budzet_wydane + " ", fmtS(b.wydane)),
        h("p", {}, T.budzet_opis1),
        h("p", {}, T.budzet_opis2)));
    };
    return b;
  } catch (e) { return null; }
}
odswiezBudzet();

function modal(title, body, { wide = false } = {}) {
  const back = h("div", { class: "modal-back" });
  const esc = (e) => { if (e.key === "Escape") close(); };
  const close = () => { back.remove(); document.removeEventListener("keydown", esc, true); };
  back.addEventListener("click", (e) => { if (e.target === back) close(); });
  document.addEventListener("keydown", esc, true);
  const m = h("div", { class: "modal" },
    h("div", { class: "modal-head" }, h("span", {}, title), h("span", { class: "sp" }), h("button", { class: "btn quiet", onclick: close }, T.zamknij)),
    h("div", { class: "modal-body" }, body));
  if (wide) m.style.width = "min(1400px, 100%)";
  back.append(m);
  document.body.append(back);
  return { close, el: m };
}

function compareView(items) {
  const g = h("div", { class: "cmp-grid n" + items.length }, items.map((a) =>
    h("div", { class: "cmp-cell" }, mediaEl(a), h("span", { class: "lbl" }, [a.meta?.nazwa_modelu || a.nazwa, a.meta?.ustawienia?.seed ? "seed " + a.meta.ustawienia.seed : "", a.meta?.czas_s ? a.meta.czas_s + " s" : ""].filter(Boolean).join(" · ")))));
  modal(T.porownaj + " (" + items.length + ")", g, { wide: true });
}

async function showGuide(modelId, name) {
  try {
    const d = await api("/api/poradnik/" + modelId);
    modal(T.poradnik + " — " + name, h("div", { class: "guide", html: d.html }), { wide: false });
  } catch (e) { toast(e.message); }
}

// Okno wyboru zasobu danego rodzaju (moje / wszystkich), z wyszukiwaniem.
function pickAsset(rodzaj, onPick) {
  const grid = h("div", { class: "grid" });
  const tog = h("span", { class: "toggle" });
  const q = h("input", { type: "text", placeholder: T.szukaj, style: "width:240px;margin-left:12px" });
  let kto = "ja";
  const load = async () => {
    const items = await api(`/api/zasoby?kto=${kto}&rodzaj=${rodzaj}&q=${encodeURIComponent(q.value)}`);
    grid.replaceChildren(...(items.length ? items.map((a) => h("div", { class: "cell", onclick: () => { onPick(a); m.close(); } }, mediaEl(a, { thumb: true }), h("span", { class: "lbl" }, a.login === window.LOGIN ? (a.ujecie_nazwa || a.nazwa) : a.login))) : [h("div", { class: "kind" }, T.pusto)]));
  };
  for (const [k, lbl] of [["ja", T.moje], ["wszyscy", T.wszystkich]]) {
    const x = h("a", { class: k === kto ? "on" : "" }, lbl);
    x.onclick = () => { kto = k; tog.querySelectorAll("a").forEach((y) => y.classList.toggle("on", y === x)); load(); };
    tog.append(x);
  }
  let tm; q.oninput = () => { clearTimeout(tm); tm = setTimeout(load, 200); };
  const m = modal(T.z_zasobow, h("div", {}, h("div", { style: "margin-bottom:12px;display:flex;align-items:center" }, tog, q), grid));
  load();
}

async function uploadFile(file, ujecie) {
  const fd = new FormData();
  fd.append("plik", file);
  if (ujecie) fd.append("ujecie", ujecie);
  return api("/api/zasoby", { method: "POST", body: fd });
}
