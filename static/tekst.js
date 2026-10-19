// Obszar Tekst: prywatne rozmowy z LLM (odpowiedź płynie na bieżąco), zapis fragmentów jako artefakty .md.
const MODELS = window.MODELS || [];
const $ = (id) => document.getElementById(id);
const st = { rid: null, rozmowa: null, pisze: false, tryb: "rozmowa", lista: [], biblia: "", zal: [] };
function ustawTryb(k) {
  st.tryb = k;
  document.querySelectorAll("#tryb .chip").forEach((c) => c.classList.toggle("on", c.dataset.k === k));
  $("tryb-opis").textContent = { lustro: T.tryb_lustro_opis, prompt: T.tryb_prompt_opis }[k] || T.tryb_rozmowa_opis;
  panelLustra(); panelPromptow();
}

// --- lustro: biblia i tematy (każdy temat = osobna rozmowa przypięta do tej samej biblii) ---
async function panelLustra() {
  const pole = $("biblia-pole");
  pole.hidden = st.tryb === "rozmowa";
  if (pole.hidden) return;
  const bs = await api("/api/biblie");
  if (st.rozmowa?.biblia) st.biblia = st.rozmowa.biblia;
  if (st.biblia && !bs.some((b) => b.sciezka === st.biblia)) st.biblia = "";
  $("biblia").replaceChildren(h("option", { value: "" }, "—"), ...bs.map((b) => h("option", { value: b.sciezka }, b.nazwa)));
  $("biblia").value = st.biblia;
  const chips = $("tematy");
  if (!st.biblia) { chips.replaceChildren(); $("tematy-opis").textContent = st.tryb === "prompt" ? T.prompt_nieaktywny : T.tematy_nieaktywne; return; }
  if (st.tryb === "prompt") return panelModeli(chips);
  const b = await api("/api/biblia?sciezka=" + encodeURIComponent(st.biblia));
  const teraz = st.rozmowa?.biblia === st.biblia ? (st.rozmowa.temat || "") + "|" + (st.rozmowa.temat_nazwa || "") : null;
  const chip = (etyk, temat, nazwa, tytul) => {
    const c = h("button", { class: "chip" + (teraz === (temat || "") + "|" + (nazwa || "") ? " on" : ""), type: "button", title: tytul || "" }, etyk);
    c.onclick = () => otworzTemat(temat, nazwa);
    return c;
  };
  chips.replaceChildren(chip("◇ " + T.poczatek, "", ""),
    ...b.tematy.map((t) => chip((t.wypelniony ? "● " : "○ ") + t.nazwa, t.klucz, t.nazwa, t.wypelniony ? T.temat_zapisany : T.temat_pusty)),
    ...b.wlasne.map((n) => chip("◆ " + n, "_inny", n, T.temat_wlasny)));
  $("tematy-opis").textContent = T.tematy_opis;
}

async function panelModeli(chips) {
  const gr = await api("/api/promptmaker/modele");
  const teraz = st.rozmowa?.tryb === "prompt" && st.rozmowa?.biblia === st.biblia ? st.rozmowa.model_docelowy : null;
  chips.replaceChildren(...gr.map((g) => h("div", { class: "pm-grupa" }, h("div", { class: "pr-nazwa" }, g.nazwa),
    h("div", { class: "chips" }, ...g.modele.map((m) => {
      const c = h("button", { class: "chip" + (m.id === teraz ? " on" : ""), type: "button", title: m.karta ? "" : T.brak_karty }, m.nazwa + (m.karta ? "" : " ·"));
      c.onclick = () => otworzPrompt(m.id);
      return c;
    })))));
  $("tematy-opis").textContent = T.prompt_opis;
}

async function otworzPrompt(mid) {
  const jest = st.lista.find((r) => r.tryb === "prompt" && r.biblia === st.biblia && r.model_docelowy === mid);
  if (jest) return otworz(jest.id);
  const r = await api("/api/rozmowy", { method: "POST", body: JSON.stringify({ model: $("model").value, tryb: "prompt", biblia: st.biblia, model_docelowy: mid }) });
  await otworz(r.id); $("tresc").focus();
}

async function otworzTemat(temat, nazwa) {
  const jest = st.lista.find((r) => r.tryb === "lustro" && r.biblia === st.biblia && (r.temat || "") === (temat || "")
    && (temat !== "_inny" || r.temat_nazwa === nazwa));
  if (jest) return otworz(jest.id);
  const r = await api("/api/rozmowy", { method: "POST", body: JSON.stringify({ model: $("model").value, tryb: "lustro",
    biblia: st.biblia, temat: temat || null, temat_nazwa: nazwa || null }) });
  await otworz(r.id); $("tresc").focus();
}

// --- prompty systemowe: podgląd, kopie, wybór obowiązującej wersji w każdej sekcji ---
async function panelPromptow() {
  const ps = await api(`/api/prompty?tryb=${st.tryb}&temat=${encodeURIComponent(st.tryb === "lustro" ? st.rozmowa?.temat || "" : "")}&model=${encodeURIComponent(st.tryb === "prompt" ? st.rozmowa?.model_docelowy || "" : "")}`);
  $("prompty").replaceChildren(...ps.map((p) => {
    const sel = h("select", {}, h("option", { value: "" }, T.oryginal),
      ...p.kopie.map((k) => h("option", { value: "k:" + k.id }, k.nazwa + (k.udostepniona ? " ⇄" : ""))),
      p.udostepnione.length ? h("optgroup", { label: T.udostepnione }, ...p.udostepnione.map((k) => h("option", { value: `u:${k.login}:${k.id}` }, `${k.login}: ${k.nazwa}`))) : null);
    sel.value = p.wybrana ? "k:" + p.wybrana : "";
    const moja = p.kopie.find((k) => k.id === p.wybrana);
    sel.onchange = async () => {
      if (sel.value.startsWith("u:")) { const [, login, id] = sel.value.split(":"); sel.value = p.wybrana ? "k:" + p.wybrana : ""; return podglad(p, id, login); }
      await api("/api/prompty/wybierz", { method: "POST", body: JSON.stringify({ sekcja: p.sekcja, id: sel.value.slice(2) || null }) });
      panelPromptow();
    };
    const akcje = [h("button", { class: "btn quiet", onclick: () => podglad(p, p.wybrana) }, T.podglad),
      h("button", { class: "btn quiet", onclick: () => duplikuj(p, p.wybrana) }, T.duplikuj)];
    if (moja) akcje.push(
      h("button", { class: "btn quiet", onclick: () => edytuj(p, moja) }, T.edytuj),
      h("button", { class: "btn quiet", title: T.udostepnij_opis, onclick: async () => {
        await api("/api/prompty/kopia/" + moja.id, { method: "POST", body: JSON.stringify({ udostepniona: !moja.udostepniona }) });
        toast(moja.udostepniona ? T.nie_udostepniona : T.udostepniona); panelPromptow(); } }, moja.udostepniona ? T.nie_udostepniaj : T.udostepnij),
      h("button", { class: "btn quiet", onclick: async () => {
        if (!confirm(T.usun_kopie + " „" + moja.nazwa + "”?")) return;
        await api("/api/prompty/kopia/" + moja.id + "/usun", { method: "POST" }); panelPromptow(); } }, T.usun));
    return h("div", { class: "pr-wiersz" }, h("div", { class: "pr-nazwa" }, p.nazwa), sel, h("div", { class: "pr-akcje" }, ...akcje));
  }));
}

async function podglad(p, kopia, login) {
  const d = await api(`/api/prompty/tekst?sekcja=${encodeURIComponent(p.sekcja)}&kopia=${kopia || ""}&login=${login || ""}`);
  let okno;
  const body = h("div", {}, h("pre", { class: "pr-pre" }, d.tresc),
    h("button", { class: "btn", onclick: () => { okno.close(); duplikuj(p, kopia, login); } }, T.duplikuj_edytuj));
  okno = modal(p.nazwa + " — " + (kopia ? d.nazwa : T.oryginal), body, { wide: true });
}

async function duplikuj(p, kopia, login) {
  const nazwa = prompt(T.nazwa_kopii, (login ? login + " — " : "") + (kopia ? "" : T.moja_wersja));
  if (nazwa === null) return;
  const k = await api("/api/prompty/duplikuj", { method: "POST", body: JSON.stringify({ sekcja: p.sekcja, kopia: kopia || null, login: login || null, nazwa }) });
  await panelPromptow();
  edytuj(p, { id: k.id, nazwa: nazwa || T.moja_wersja });
}

async function edytuj(p, k) {
  const d = await api(`/api/prompty/tekst?sekcja=${encodeURIComponent(p.sekcja)}&kopia=${k.id}`);
  notatki.edytujTekst({ tytul: "⚙ " + p.nazwa + " — " + k.nazwa, tresc: d.tresc,
    zapisz: (md) => api("/api/prompty/kopia/" + k.id, { method: "POST", body: JSON.stringify({ tresc: md }) }) });
}

async function pelnyPrompt() {
  if (!st.rid) return toast(T.najpierw_rozmowa);
  const d = await api(`/api/rozmowy/${st.rid}/prompt`);
  modal(T.pelny_prompt, h("div", {}, h("p", { class: "hint" }, T.pelny_prompt_opis), h("pre", { class: "pr-pre" }, d.prompt)), { wide: true });
}

const md = (t) => DOMPurify.sanitize(marked.parse(t || "", { breaks: true }));

async function lista() {
  const rs = await api("/api/rozmowy");
  st.lista = rs;
  $("rozmowy").replaceChildren(...rs.filter((r) => !r.pusta || r.id === st.rid).map((r) => {
    const b = h("div", { class: "shot rozm" + (r.id === st.rid ? " on" : ""), title: fmtDate(r.zmienione) }, h("span", { class: "nm" }, r.tytul),
      h("span", { class: "akc" },
        h("button", { class: "btn quiet", title: T.zmien_nazwe, onclick: (e) => { e.stopPropagation(); zmienTytul(r); } }, "✎"),
        h("button", { class: "btn quiet", title: T.usun_rozmowe, onclick: (e) => { e.stopPropagation(); usunRozmowe(r); } }, "✕")));
    b.onclick = () => otworz(r.id);
    return b;
  }));
}

async function zmienTytul(r) {
  const t = prompt(T.nazwa_rozmowy, r.tytul === "—" ? "" : r.tytul);
  if (t === null || !t.trim()) return;
  await api(`/api/rozmowy/${r.id}/tytul`, { method: "POST", body: JSON.stringify({ tytul: t.trim() }) });
  if (st.rozmowa?.id === r.id) st.rozmowa.tytul = t.trim();
  lista();
}

async function usunRozmowe(r) {
  if (!r.pusta && !confirm(tf("usunac_rozmowe", { t: r.tytul }))) return;
  await api(`/api/rozmowy/${r.id}/usun`, { method: "POST" });
  if (st.rid === r.id) { st.rid = null; st.rozmowa = null; localStorage.removeItem("rozmowa"); rysuj(); }
  lista();
}

// --- szkic: niewysłany tekst pola przechowywany per rozmowa (przeżywa przełączenie, odświeżenie, błąd) ---
const szkicKlucz = (rid) => "szkic:" + rid;
function szkicZapisz() {
  if (!st.rid) return;
  try { const t = $("tresc").value; t.trim() ? localStorage.setItem(szkicKlucz(st.rid), t) : localStorage.removeItem(szkicKlucz(st.rid)); } catch (e) {}
}
function szkicWczytaj(rid) { try { return localStorage.getItem(szkicKlucz(rid)) || ""; } catch (e) { return ""; } }

async function otworz(rid) {
  if (rid !== st.rid) {
    st.zal = []; rysujZal();
    if (st.rid) { szkicZapisz(); $("tresc").value = szkicWczytaj(rid); }
    else $("tresc").value = szkicWczytaj(rid) || $("tresc").value;   // nowa rozmowa: tekst wpisany przed jej utworzeniem zostaje
  }
  st.rid = rid; localStorage.setItem("rozmowa", rid);
  try { st.rozmowa = await api("/api/rozmowy/" + rid); } catch (e) { st.rid = null; st.rozmowa = null; }
  if (st.rozmowa?.model && MODELS.some((m) => m.id === st.rozmowa.model)) $("model").value = st.rozmowa.model;
  ustawTryb(st.rozmowa?.tryb || "rozmowa");
  rysuj(); lista();
}

function wiadomosc(w) {
  const tresc = h("div", { class: "tresc", html: w.rola === "user" ? escapeHtml(w.tresc).replace(/\n/g, "<br>") : md(w.tresc) });
  const el = h("div", { class: "w " + w.rola });
  if (w.mysl) el.append(h("details", { class: "mysli" }, h("summary", {}, T.mysli), h("div", { html: md(w.mysl) })));
  if (w.narzedzia) el.append(h("div", { class: "narz" }, w.narzedzia.map((n) => h("div", {}, "· " + n))));
  el.append(tresc);
  if (w.rola === "assistant") tresc.querySelectorAll("pre").forEach((pre) => {
    const kod = pre.querySelector("code") || pre;
    pre.classList.add("z-kopiuj");
    pre.append(h("button", { class: "btn quiet kopiuj-kod", type: "button", title: T.kopiuj_kod_pomoc,
      onclick: () => kopiujZToastem(kod.textContent.replace(/\n$/, "")) }, T.kopiuj));
  });
  if (w.zalaczniki?.length) el.append(zalWiadomosci(w.zalaczniki));
  if (w.rola === "assistant") {
    el.append(h("div", { class: "w-akcje" },
      h("button", { class: "btn quiet", title: T.zaznacz_aby, onclick: () => doArtefaktu(zaznaczenie(el) || w.tresc) }, "↓ " + T.do_artefaktu),
      h("button", { class: "btn quiet", onclick: () => kopiujZToastem(zaznaczenie(el) || w.tresc) }, T.kopiuj),
      w.czas_s ? h("span", { class: "czas" }, w.czas_s + " s") : null));
  }
  return el;
}

function zaznaczenie(el) {
  const s = window.getSelection();
  return s && !s.isCollapsed && el.contains(s.anchorNode) ? s.toString().trim() : "";
}

function rysuj() {
  const w = $("watek");
  if (!st.rozmowa || !st.rozmowa.wiadomosci.length) { w.replaceChildren(h("div", { class: "pusto" }, T.rozmowy_prywatne)); return; }
  w.replaceChildren(...st.rozmowa.wiadomosci.map(wiadomosc));
  w.scrollTop = w.scrollHeight;
}

// --- załączniki: 📎, przeciągnij na pole, wklej obraz ---
const zalUrl = (n) => `/api/rozmowy/${st.rid}/zalaczniki/${encodeURIComponent(n)}`;
function zalChip(z, usun) {
  const info = z.rodzaj === "obraz" ? "" : z.strony_obrazy?.length ? tf("zal_strony", { n: z.strony_obrazy.length }) : z.znaki != null ? tf("zal_znaki", { n: z.znaki.toLocaleString(LOCALE) }) : "";
  return h("span", { class: "zal" + (z.wysylanie ? " wysylanie" : "") },
    z.rodzaj === "obraz" && !z.wysylanie ? h("img", { src: zalUrl(z.nazwa), alt: "" }) : h("span", { class: "ik" }, z.rodzaj === "pdf" ? "PDF" : "📄"),
    h("a", { href: z.wysylanie ? null : zalUrl(z.nazwa), target: "_blank" }, z.nazwa), info ? h("small", {}, info) : null,
    usun ? h("button", { class: "btn quiet", type: "button", title: T.zal_usun, onclick: usun }, "✕") : null);
}
function zalWiadomosci(lista) { return h("div", { class: "zal-lista w-zal" }, lista.map((z) => zalChip(z))); }
function rysujZal() {
  $("zal-lista").replaceChildren(...st.zal.map((z) => zalChip(z, z.wysylanie ? null : async () => {
    st.zal = st.zal.filter((x) => x !== z); rysujZal();
    try { await api(zalUrl(z.nazwa) + "/usun", { method: "POST" }); } catch (e) {}
  })));
}
async function dolacz(pliki) {
  pliki = [...pliki].filter((p) => p && p.size);
  if (!pliki.length) return;
  if (!st.rid) { const r = await api("/api/rozmowy", { method: "POST", body: JSON.stringify({ model: $("model").value, tryb: st.tryb, biblia: st.biblia || null }) }); await otworz(r.id); }
  const tymczasowe = pliki.map((p) => ({ nazwa: p.name, rodzaj: p.type.startsWith("image/") ? "obraz" : "tekst", wysylanie: true }));
  st.zal.push(...tymczasowe); rysujZal();
  const fd = new FormData();
  pliki.forEach((p, i) => fd.append("pliki", p, p.name || `obraz-${Date.now()}-${i}.png`));
  try {
    const gotowe = await api(`/api/rozmowy/${st.rid}/zalaczniki`, { method: "POST", body: fd });
    st.zal = st.zal.filter((z) => !tymczasowe.includes(z)).concat(gotowe);
  } catch (e) { st.zal = st.zal.filter((z) => !tymczasowe.includes(z)); $("msg").textContent = e.message; }
  rysujZal();
}

async function wyslij(wymuszona) {
  if (typeof wymuszona !== "string") wymuszona = undefined;          // wywołanie z kliknięcia przekazuje zdarzenie
  const tresc = (wymuszona ?? $("tresc").value).trim();
  if ((!tresc && !st.zal.length) || st.pisze || st.zal.some((z) => z.wysylanie)) return;
  if (st.tryb === "prompt" && !st.rozmowa?.model_docelowy) { toast(T.wybierz_model); return; }
  $("msg").textContent = "";
  if (!st.rid) { const r = await api("/api/rozmowy", { method: "POST", body: JSON.stringify({ model: $("model").value, tryb: st.tryb, biblia: st.biblia || null }) }); await otworz(r.id); }
  st.pisze = true; $("wyslij").disabled = true;
  if (wymuszona == null) { $("tresc").value = ""; szkicZapisz(); }   // przycisk „Tak, zapisz” nie rusza tego, co jest w polu
  const zal = st.zal; st.zal = []; rysujZal();
  st.rozmowa.wiadomosci.push({ rola: "user", tresc, zalaczniki: zal });
  const odp = { rola: "assistant", tresc: "", mysl: "", narz: [] };
  let dotarlo = false;
  rysuj();
  const el = h("div", { class: "w assistant pisze" }, h("div", { class: "tresc" }, "…"));
  $("watek").append(el); $("watek").scrollTop = $("watek").scrollHeight;
  try {
    const r = await fetch(`/api/rozmowy/${st.rid}/wyslij`, { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tresc, model: $("model").value, mysl: $("mysl").checked, tryb: st.tryb, zalaczniki: zal.map((z) => z.nazwa) }) });
    if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || r.status);
    dotarlo = true;
    const rd = r.body.getReader(), dec = new TextDecoder();
    let buf = "", t0 = performance.now(), raf = null;
    const odswiez = () => { raf = null; el.replaceChildren(...[odp.mysl ? h("details", { class: "mysli", open: !odp.tresc }, h("summary", {}, T.mysli), h("div", { html: md(odp.mysl) })) : null, odp.narz.length ? h("div", { class: "narz" }, odp.narz.map((n) => h("div", {}, "· " + n))) : null, h("div", { class: "tresc", html: md(odp.tresc) || "…" })].filter(Boolean)); const wt = $("watek"); if (wt.scrollHeight - wt.scrollTop - wt.clientHeight < 160) wt.scrollTop = wt.scrollHeight; };
    for (;;) {
      const { value, done } = await rd.read();
      if (done) break;
      buf += dec.decode(value, { stream: true });
      let i;
      while ((i = buf.indexOf("\n\n")) >= 0) {
        const linia = buf.slice(0, i).trim(); buf = buf.slice(i + 2);
        if (!linia.startsWith("data: ")) continue;
        const d = JSON.parse(linia.slice(6));
        if (d.t) odp.tresc += d.t;
        if (d.r) odp.mysl += d.r;
        if (d.n) odp.narz.push(d.n);
        if (d.zgoda) odp.zgoda = true;
        if (d.blad) $("msg").textContent = d.blad;
        if (!raf) raf = requestAnimationFrame(odswiez);
      }
    }
  } catch (e) {
    $("msg").textContent = e.message;
    if (!dotarlo && wymuszona == null && !$("tresc").value.trim()) { $("tresc").value = tresc; szkicZapisz(); }   // nie dotarło — tekst wraca do pola
  }
  st.pisze = false; $("wyslij").disabled = false;
  await otworz(st.rid);
  if (odp.zgoda) $("msg").replaceChildren(h("button", { class: "btn primary", onclick: () => wyslij(T.zgoda_tekst) },
    "✓ " + T.zgoda_przycisk));
  artefakty();                                   // agent mógł zapisać notatkę (np. biblię)
  notatki.odswiezBiezacy();
}

// --- artefakty ---
async function artefakty() {
  const as = await api("/api/artefakty");
  $("artefakty").replaceChildren(...as.map((a) => h("li", {}, h("a", { onclick: () => notatki.otworz(a.id) }, (a.folder ? a.folder + "/" : "") + a.nazwa))));
}

async function doArtefaktu(tresc) {
  const nazwa = prompt(T.nazwa_pliku, (st.rozmowa?.tytul || "notatka").slice(0, 40));
  if (nazwa === null) return;
  const a = await api("/api/artefakty", { method: "POST", body: JSON.stringify({ nazwa, tresc, ujecie: parseInt(localStorage.getItem("ujecie") || "0") || null, zrodlo: "rozmowa" }) });
  toast(T.zapisano + ": " + a.nazwa); artefakty();
  notatki.otworz(a.id);
}

// --- start ---
$("model").replaceChildren(...MODELS.map((m) => h("option", { value: m.id }, m.nazwa)));
const opisModelu = () => { const m = MODELS.find((x) => x.id === $("model").value); $("model-opis").textContent = m ? L(m.opis) : ""; };
$("model").onchange = opisModelu; opisModelu();
// ---------- karty postaci i lokacji (sztywne, z biblii; jedna karta = jeden obraz) ----------
const POLA_KART = { postac: ["tozsamosc", "stroj", "wyraz", "czynnosc"], lokacja: ["uklad", "materialy", "swiatlo"] };
async function otworzKarty() {
  const bs = await api("/api/biblie");
  const modele = await api("/api/modele?obszar=obraz");
  const k = { typ: "postac", biblia: st.biblia || bs[0]?.sciezka || "", dane: { postacie: [], lokacje: [], styl: "" } };
  const selBiblia = h("select", {}, h("option", { value: "" }, T.karty_bez_biblii), ...bs.map((b) => h("option", { value: b.sciezka }, b.nazwa)));
  selBiblia.value = k.biblia;
  const typy = h("div", { class: "chips" });
  const selWpis = h("select");
  const nazwa = h("input", { type: "text", placeholder: T.karty_nazwa });
  const pola = h("div");
  const styl = h("textarea", { rows: 2, placeholder: T.karty_styl_pomoc });
  const selModel = h("select", {}, ...modele.map((m) => h("option", { value: m.id }, m.nazwa)));
  const wynik = h("textarea", { rows: 9, class: "karty-wynik", spellcheck: "false", placeholder: T.karty_wynik_pomoc });
  const msg = h("span", { class: "msg" });
  const ostatni = localStorage.getItem("karty:model");
  if (ostatni && modele.some((m) => m.id === ostatni)) selModel.value = ostatni;

  const rysujPola = (wartosci = {}) => {
    pola.replaceChildren(...POLA_KART[k.typ].map((p) => h("div", { class: "field" }, h("label", {}, T["karty_" + p]),
      h("textarea", { rows: 2, "data-pole": p }, wartosci[p] || ""))));
  };
  const rysujWpisy = () => {
    const lista = k.typ === "postac" ? k.dane.postacie : k.dane.lokacje;
    selWpis.replaceChildren(h("option", { value: "" }, T.karty_nowa), ...lista.map((x, i) => h("option", { value: i }, x.nazwa)));
    selWpis.value = lista.length ? "0" : "";
    wybierzWpis();
  };
  const wybierzWpis = () => {
    const lista = k.typ === "postac" ? k.dane.postacie : k.dane.lokacje;
    const x = lista[parseInt(selWpis.value)];
    nazwa.value = x ? x.nazwa : ""; rysujPola(x ? x.pola : {});
  };
  const wczytajBiblie = async () => {
    k.biblia = selBiblia.value;
    k.dane = k.biblia ? await api("/api/karty?biblia=" + encodeURIComponent(k.biblia)) : { postacie: [], lokacje: [], styl: "" };
    styl.value = k.dane.styl || ""; rysujWpisy();
  };
  for (const [t, et] of [["postac", T.karty_postac], ["lokacja", T.karty_lokacja]]) {
    const c = h("button", { class: "chip" + (t === k.typ ? " on" : ""), type: "button" }, et);
    c.onclick = () => { k.typ = t; typy.querySelectorAll(".chip").forEach((x) => x.classList.toggle("on", x === c)); wynik.value = ""; rysujWpisy(); };
    typy.append(c);
  }
  selBiblia.onchange = wczytajBiblie; selWpis.onchange = wybierzWpis;
  selModel.onchange = () => localStorage.setItem("karty:model", selModel.value);
  const zbierz = () => Object.fromEntries([...pola.querySelectorAll("[data-pole]")].map((t) => [t.dataset.pole, t.value]));

  const przygotuj = h("button", { class: "btn primary", type: "button" }, T.karty_przygotuj);
  przygotuj.onclick = async () => {
    msg.textContent = T.karty_tlumacze; przygotuj.disabled = true;
    try { wynik.value = (await api("/api/karty/prompt", { method: "POST", body: JSON.stringify({ typ: k.typ, pola: zbierz(), styl: styl.value }) })).prompt; msg.textContent = ""; }
    catch (e) { msg.textContent = e.message; }
    finally { przygotuj.disabled = false; }
  };
  const zapisz = h("button", { class: "btn", type: "button", onclick: async () => {
    if (!wynik.value.trim()) { msg.textContent = T.karty_najpierw; return; }
    const r = await api("/api/karty/zapisz", { method: "POST", body: JSON.stringify({ typ: k.typ, nazwa: nazwa.value, prompt: wynik.value, model: selModel.value, biblia: k.biblia }) });
    msg.textContent = r.ok ? T.karty_zapisano : r.info;
    if (r.ok) document.dispatchEvent(new Event("notatki:zapisane"));
  } }, T.karty_zapisz);
  const doObrazu = h("button", { class: "btn", type: "button", onclick: () => {
    if (!wynik.value.trim()) { msg.textContent = T.karty_najpierw; return; }
    const m = modele.find((x) => x.id === selModel.value);
    const ust = { prompt: wynik.value };
    if (m?.parametry.some((p) => p.id === "proporcje" && (p.opcje || []).includes("3:2"))) ust.proporcje = "3:2";
    localStorage.setItem("reuse", JSON.stringify({ obszar: "obraz", meta: { model: selModel.value, ustawienia: ust },
                                                    komunikat: tf("karty_wstawiono", { n: nazwa.value || "—" }) }));
    location.href = "/obraz";
  } }, T.karty_do_obrazu + " →");

  modal(T.karty, h("div", { class: "karty-okno" },
    h("div", { class: "field" }, h("label", {}, T.biblia), selBiblia),
    h("div", { class: "field" }, typy),
    h("div", { class: "karty-dwie" },
      h("div", {}, h("div", { class: "field" }, h("label", {}, T.karty_wpis), selWpis), h("div", { class: "field" }, h("label", {}, T.karty_nazwa_et), nazwa), pola,
        h("div", { class: "field" }, h("label", {}, T.karty_styl), styl)),
      h("div", {}, h("div", { class: "field" }, h("label", {}, T.karty_model), selModel),
        h("p", { class: "hint" }, T.karty_jeden_obraz), przygotuj,
        h("div", { class: "field", style: "margin-top:10px" }, h("label", {}, T.karty_prompt), wynik),
        h("div", { style: "display:flex;gap:8px;flex-wrap:wrap;align-items:center" }, zapisz, doObrazu, msg)))), { wide: true });
  await wczytajBiblie();
}
$("karty-btn").onclick = otworzKarty;

$("nowa").onclick = async () => { if (st.rozmowa && !st.rozmowa.wiadomosci.length && (st.rozmowa.tryb || "rozmowa") === st.tryb) { $("tresc").focus(); return; } const r = await api("/api/rozmowy", { method: "POST", body: JSON.stringify({ model: $("model").value, tryb: st.tryb }) }); await otworz(r.id); $("tresc").focus(); };
$("biblia").onchange = async () => {
  st.biblia = $("biblia").value;
  if (st.rozmowa && (st.rozmowa.tryb || st.tryb) === "lustro" && !st.rozmowa.temat && st.tryb === "lustro") {
    await api(`/api/rozmowy/${st.rid}/biblia`, { method: "POST", body: JSON.stringify({ biblia: st.biblia || null }) });
    st.rozmowa.biblia = st.biblia || null;
  }
  panelLustra();
};
$("pelny").onclick = pelnyPrompt;
$("wyslij").onclick = () => wyslij();
document.querySelectorAll("#tryb .chip").forEach((c) => c.onclick = () => ustawTryb(c.dataset.k));
ustawTryb("rozmowa");
$("zal-dodaj").onclick = () => $("zal-plik").click();
$("zal-plik").onchange = () => { dolacz($("zal-plik").files); $("zal-plik").value = ""; };
$("tresc").addEventListener("dragover", (e) => { e.preventDefault(); $("tresc").classList.add("drop"); });
$("tresc").addEventListener("dragleave", () => $("tresc").classList.remove("drop"));
$("tresc").addEventListener("drop", (e) => { e.preventDefault(); $("tresc").classList.remove("drop"); dolacz(e.dataTransfer.files); });
$("tresc").addEventListener("paste", (e) => {
  const pliki = [...(e.clipboardData?.files || [])];
  if (pliki.length) { e.preventDefault(); dolacz(pliki); }
});
$("tresc").addEventListener("input", () => { clearTimeout(st.szkicT); st.szkicT = setTimeout(szkicZapisz, 400); });
window.addEventListener("pagehide", szkicZapisz);
$("tresc").onkeydown = (e) => { if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); wyslij(); } };
$("art-nowy").onclick = () => notatki.nowa();
document.addEventListener("notatki:zapisane", artefakty);
(async () => {
  await lista();
  const ost = localStorage.getItem("rozmowa");
  if (ost) await otworz(ost);
  artefakty();
})();
