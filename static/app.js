// Aplikacja obszaru: ujęcia, podgląd, pasek generacji (szukaj / ★ / porównaj), panel generowania, kolejka.
const APP = document.getElementById("app");
const OBSZAR = APP.dataset.obszar;
const RODZAJ = { obraz: "obraz", wideo: "wideo", muzyka: "dzwiek", sfx: "dzwiek", mowa: "dzwiek", tekst: "tekst" }[OBSZAR];
const MODELS = window.MODELS || [];
const $ = (id) => document.getElementById(id);
const state = {
  model: null, values: {}, inputs: {}, inputAssets: {}, adv: false, ile: 1,
  shots: [], shot: null, scope: "ujecie", q: "", onlyStar: false,
  thumbs: [], selected: null, cmp: new Set(), history: [], seenDone: new Set(), primed: false,
};
const CHIP_LABELS = { szybki: "opt_szybki", jakosc: "opt_jakosc", domyslny: "opt_domyslny", z_dzwiekiem: "opt_z_dzwiekiem", bez_dzwieku: "opt_bez_dzwieku" };
const label = (p) => L(p.etykieta) || T[p.id] || p.id;

// ---------- ujęcia ----------
async function loadShots(keepSel = true) {
  state.shots = await api("/api/ujecia");
  const saved = parseInt(localStorage.getItem("ujecie") || "0");
  if (!keepSel || !state.shots.some((s) => s.id === state.shot)) {
    state.shot = state.shots.some((s) => s.id === saved) ? saved : state.shots[0]?.id;
  }
  renderShots();
}

function renderShots() {
  const box = $("shots");
  box.replaceChildren(...state.shots.map((s) => {
    const b = h("button", { class: "shot" + (s.id === state.shot ? " on" : ""), title: T.dwuklik_nazwa },
      h("span", { class: "nr" }, String(s.nr).padStart(2, "0")), h("span", { class: "nm" }, s.nazwa), h("span", { class: "ct" }, s.ile || ""));
    b.onclick = () => selectShot(s.id);
    b.ondblclick = () => renameShot(b, s);
    b.addEventListener("dragover", (e) => { e.preventDefault(); b.classList.add("drop"); });
    b.addEventListener("dragleave", () => b.classList.remove("drop"));
    b.addEventListener("drop", async (e) => {
      e.preventDefault(); b.classList.remove("drop");
      const id = e.dataTransfer.getData("text/asset");
      if (!id) return;
      try {
        await api(`/api/zasoby/${id}/przenies`, { method: "POST", body: JSON.stringify({ ujecie: s.id }) });
        toast(tf("przeniesiono_do", { n: s.nazwa }));
      } catch (err) { toast(err.message); }
      await loadShots(); loadThumbs();
    });
    return b;
  }));
  const cur = state.shots.find((s) => s.id === state.shot);
  $("cur-shot").replaceChildren(T.ujecie + ": ", h("b", {}, cur ? cur.nazwa : "—"));
}

function selectShot(id) {
  state.shot = id; localStorage.setItem("ujecie", id);
  state.selected = null; state.cmp.clear();
  renderShots();
  if (state.scope !== "ujecie") setScope("ujecie"); else loadThumbs();
}

function renameShot(btn, s) {
  const inp = h("input", { type: "text" }); inp.value = s.nazwa;
  btn.replaceChildren(inp); inp.focus(); inp.select();
  let finished = false;
  const done = async (save) => {
    if (finished) return; finished = true;
    if (save && inp.value.trim() && inp.value.trim() !== s.nazwa) await api(`/api/ujecia/${s.id}`, { method: "POST", body: JSON.stringify({ nazwa: inp.value.trim() }) });
    await loadShots();
  };
  inp.onkeydown = (e) => { if (e.key === "Enter") done(true); if (e.key === "Escape") done(false); };
  inp.onblur = () => done(true);
  inp.onclick = (e) => e.stopPropagation();
}

function newShotUI() {
  const btn = $("shot-new");
  const inp = h("input", { type: "text", placeholder: T.nazwa_ujecia, style: "margin-top:8px" });
  btn.style.display = "none";
  btn.after(inp); inp.focus();
  let finished = false;
  const close = () => { if (finished) return; finished = true; inp.remove(); btn.style.display = ""; };
  inp.onkeydown = async (e) => {
    if (e.key === "Escape") close();
    if (e.key === "Enter") {
      const s = await api("/api/ujecia", { method: "POST", body: JSON.stringify({ nazwa: inp.value.trim() }) });
      close(); await loadShots(); selectShot(s.id);
    }
  };
  inp.onblur = close;
}
$("shot-new").onclick = newShotUI;

// ---------- model i formularz ----------
function selectModel(id, keep = false) {
  state.model = MODELS.find((m) => m.id === id) || MODELS[0];
  if (!keep) {
    const prompt = state.values.prompt;
    state.values = {};
    for (const p of state.model.parametry) if (p.domyslnie !== undefined) state.values[p.id] = p.domyslnie;
    if (prompt) state.values.prompt = prompt;
    state.inputs = {}; state.inputAssets = {};
  } else {
    for (const p of state.model.parametry) if (state.values[p.id] === undefined && p.domyslnie !== undefined) state.values[p.id] = p.domyslnie;
  }
  localStorage.setItem("model:" + OBSZAR, state.model.id);
  renderForm();
}

// Lista zapisanych promptów tego obszaru (dla wybranego modelu na górze) — wstawienie z „Cofnij”.
async function listaPromptow(btn, ta, wpisz) {
  document.querySelector(".pr-pop")?.remove();
  const szukaj = h("input", { type: "text", placeholder: T.szukaj, spellcheck: "false" });
  const lista = h("div", { class: "pr-lista" }, h("div", { class: "pr-puste" }, "…"));
  const pop = h("div", { class: "pr-pop" }, h("div", { class: "pr-gora" }, szukaj,
    h("button", { class: "btn quiet", onclick: () => pop.remove() }, "✕")), lista);
  btn.closest(".field").append(pop);
  const zamknij = (e) => { if (!pop.contains(e.target) && e.target !== btn) { pop.remove(); document.removeEventListener("mousedown", zamknij); } };
  setTimeout(() => document.addEventListener("mousedown", zamknij), 0);
  pop.addEventListener("keydown", (e) => { if (e.key === "Escape") pop.remove(); });
  let ps = [];
  try { ps = await api(`/api/prompty-obszaru?obszar=${OBSZAR}&model=${encodeURIComponent(state.model.id)}`); }
  catch (e) { lista.replaceChildren(h("div", { class: "pr-puste" }, e.message)); return; }
  const wstaw = async (p) => {
    const a = await api("/api/artefakty/" + p.id);
    let t = (a.tresc || "").trim();
    t = jsonZTekstu(t) ?? czystyPrompt(t.replace(/^```\w*\n|\n```$/g, ""));
    const poprzedni = ta.value;
    wpisz(t); pop.remove(); ta.focus(); blysk(ta);
    toastAkcja(tf("wstawiono", { n: p.nazwa }), T.cofnij, () => { wpisz(poprzedni); blysk(ta); });
  };
  const rysuj = () => {
    const q = szukaj.value.trim().toLowerCase();
    const w = ps.filter((p) => !q || [p.nazwa, p.podglad, p.jednostka, p.biblia].join(" ").toLowerCase().includes(q));
    lista.replaceChildren(...(w.length ? w.map((p) => h("button", { class: "pr-item" + (p.ten_model ? "" : " inny"), type: "button", onclick: () => wstaw(p) },
      h("div", { class: "pr-nazwa" }, p.nazwa, p.jednostka ? h("span", { class: "pr-meta" }, " · " + p.jednostka) : null),
      h("div", { class: "pr-meta" }, [p.biblia, p.model_nazwa || (p.model ? p.model : T.prompty_bez_modelu), new Date(p.utworzone * 1000).toLocaleDateString(LOCALE)]
        .filter(Boolean).join(" · ") + (p.ten_model ? "" : " · " + T.prompty_inny_model)),
      h("div", { class: "pr-podglad" }, p.podglad)))
      : [h("div", { class: "pr-puste" }, ps.length ? T.pusto : T.prompty_brak)]));
  };
  szukaj.oninput = rysuj; rysuj(); szukaj.focus();
}

function fieldFor(p) {
  const v = state.values[p.id];
  const set = (x) => { state.values[p.id] = x; pokazKoszt(); };
  const help = p.pomoc ? h("div", { class: "help" }, L(p.pomoc)) : null;
  if (p.typ === "prompt") {
    const ta = h("textarea", { rows: p.json ? 14 : 6, spellcheck: p.json ? "false" : "true", id: "prompt", class: p.json ? "prompt-json" : null });
    ta.value = v || "";
    ta.oninput = () => set(ta.value);
    ta.onfocus = enterFocus;
    // prompt w JSON pisze się w wielu liniach: Enter = nowa linia, Ctrl+Enter = generuj
    ta.onkeydown = (e) => { if (e.key === "Enter" && !e.isComposing && (p.json ? (e.ctrlKey || e.metaKey) : !e.shiftKey)) { e.preventDefault(); submit(); } };
    const wpisz = (t) => { pushHistory(); ta.value = t; set(t); };
    if (p.json) ta.addEventListener("paste", (e) => {     // wklejony JSON (z czatu, z ``` albo ze znakami „\”) → czysty i czytelny
      const t = e.clipboardData?.getData("text/plain"), j = t && jsonZTekstu(t);
      if (!j || j === t) return;
      e.preventDefault();
      const a = ta.selectionStart, b = ta.selectionEnd;
      wpisz(ta.value.trim() ? ta.value.slice(0, a) + j + ta.value.slice(b) : j);
    });
    const tplBtn = p.szablon ? h("button", { class: "btn quiet", type: "button", onclick: () => {
      if (ta.value.trim() && !confirm(T.zastapic_szablonem)) return;
      wpisz(p.szablon); ta.focus(); } }, T.szablon) : null;
    const jsonBtn = p.json ? h("button", { class: "btn quiet", type: "button", title: T.opis_na_json_pomoc, onclick: async (e) => {
      const b = e.currentTarget, msg = $("go-msg");
      if (!ta.value.trim()) { msg.textContent = T.opis_na_json_pusty; ta.focus(); return; }
      const napis = b.textContent; b.disabled = true; b.textContent = T.json_trwa; msg.textContent = "";
      try {
        const r = await api("/api/prompt-json", { method: "POST", body: JSON.stringify({ model: state.model.id, opis: ta.value, proporcje: state.values.proporcje }) });
        wpisz(jsonZTekstu(r.json) ?? r.json);
      } catch (err) { msg.textContent = err.message; }
      finally { b.disabled = false; b.textContent = napis; }
    } }, "✦ " + T.opis_na_json) : null;
    const promptyBtn = h("button", { class: "btn quiet", type: "button", title: T.prompty_pomoc,
      onclick: (e) => listaPromptow(e.currentTarget, ta, wpisz) }, "▤ " + T.prompty_btn);
    api(`/api/prompty-obszaru?obszar=${OBSZAR}&model=${encodeURIComponent(state.model.id)}`).then((ps) => {
      promptyBtn.textContent = "▤ " + T.prompty_btn + (ps.length ? ` (${ps.length})` : ""); }).catch(() => {});
    const przyciski = h("span", { style: "float:right;margin-top:-4px;display:flex;gap:4px" }, promptyBtn, jsonBtn, tplBtn);
    return h("div", { class: "field" }, przyciski, h("label", {}, L(p.etykieta) || T.prompt), ta,
      p.json ? h("div", { class: "help" }, T.json_pomoc) : null, help);
  }
  if (p.typ === "proporcje" || p.typ === "tryb" || p.typ === "wybor") {
    const chips = h("div", { class: "chips" });
    for (const o of p.opcje) {
      const c = h("button", { class: "chip" + (String(v) === String(o) ? " on" : ""), type: "button" }, (p.etykiety_opcji && p.etykiety_opcji[o]) || (CHIP_LABELS[o] ? T[CHIP_LABELS[o]] : "") || o);
      c.onclick = () => { set(o); chips.querySelectorAll(".chip").forEach((x) => x.classList.toggle("on", x === c)); };
      chips.append(c);
    }
    return h("div", { class: "field" }, h("label", {}, p.typ === "proporcje" ? T.w_proporcje : label(p)), chips, help);
  }
  if (p.typ === "cechy") {
    const wybrane = new Set(String(v || "").split(",").map((x) => x.trim().toLowerCase()).filter(Boolean));
    const zapisz = () => set(p.grupy.flatMap((g) => g.opcje.map((o) => o.v)).filter((x) => wybrane.has(x)).join(", "));
    const rows = p.grupy.map((g) => {
      const chips = h("div", { class: "chips" });
      for (const o of g.opcje) {
        const c = h("button", { class: "chip" + (wybrane.has(o.v) ? " on" : ""), type: "button", title: o.v }, L(o) || o.v);
        c.onclick = () => {
          const byl = wybrane.has(o.v);
          g.opcje.forEach((x) => wybrane.delete(x.v));
          if (!byl) wybrane.add(o.v);
          chips.querySelectorAll(".chip").forEach((x, k) => x.classList.toggle("on", wybrane.has(g.opcje[k].v)));
          zapisz(); podglad.textContent = state.values[p.id] || "—";
        };
        chips.append(c);
      }
      return h("div", { class: "cechy-grupa" }, h("span", { class: "g" }, L(g.etykieta)), chips);
    });
    const podglad = h("code", { class: "cechy-podglad" }, v || "—");
    return h("div", { class: "field" }, h("label", {}, label(p)), rows, podglad, help);
  }
  if (p.typ === "seed") {
    const inp = h("input", { type: "text", placeholder: T.losowe, inputmode: "numeric" });
    inp.value = v ?? "";
    inp.oninput = () => set(inp.value.trim());
    return h("div", { class: "field" }, h("label", {}, "seed"), inp, h("div", { class: "help" }, T.seed_pomoc));
  }
  if (p.typ === "liczba" || p.typ === "ulamek" || p.typ === "dlugosc") {
    const unit = p.typ === "dlugosc" ? " s" : "";
    const out = h("span", { style: "min-width:44px;text-align:right;color:var(--ink-2)" }, String(v) + unit);
    const r = h("input", { type: "range", min: p.min, max: p.max, step: p.krok || (p.typ === "ulamek" ? 0.05 : p.typ === "dlugosc" && !p.int ? 0.5 : 1), value: v });
    r.oninput = () => { set(p.typ === "liczba" ? parseInt(r.value) : parseFloat(r.value)); out.textContent = r.value + unit; };
    const lbl = p.typ === "dlugosc" ? (L(p.etykieta) || T.dlugosc) : label(p);
    return h("div", { class: "field" }, h("label", {}, lbl), h("div", { class: "inline" }, r, out), help);
  }
  if (p.typ === "przelacznik") {
    const cb = h("input", { type: "checkbox", checked: !!v });
    cb.onchange = () => set(cb.checked);
    return h("div", { class: "field" }, h("label", { class: "inline", style: "cursor:pointer" }, cb, label(p)), help);
  }
  if (p.typ === "tekst") {
    const ta = h("textarea", { rows: 3, style: "min-height:70px" });
    ta.value = v || "";
    ta.oninput = () => set(ta.value);
    return h("div", { class: "field" }, h("label", {}, label(p)), ta, help);
  }
  return null;
}

// Wejście z wieloma plikami (np. inspiracje H3): lista z przyciskiem „+”, przy każdym pliku jego znacznik do promptu.
function multiSlotFor(inp) {
  const rodzaj = inp.typ, max = inp.wiele;
  const box = h("div", { class: "slot multi" });
  const list = () => (state.inputAssets[inp.id] ||= []);
  const sync = () => { state.inputs[inp.id] = list().map((a) => a.id); if (!list().length) { delete state.inputs[inp.id]; delete state.inputAssets[inp.id]; } };
  const add = (a) => { if (a.rodzaj !== rodzaj || list().length >= max) return; list().push(a); sync(); draw(); };
  const tag = (i) => (inp.znacznik || "").replace("{n}", i + 1);
  const draw = () => {
    const file = h("input", { type: "file", multiple: true, style: "display:none", accept: { obraz: "image/*", wideo: "video/*", dzwiek: "audio/*" }[rodzaj] || "" });
    file.onchange = async () => {
      for (const f of [...file.files].slice(0, max - list().length)) {
        try { add(await uploadFile(f, state.shot)); } catch (e) { toast(e.message); }
      }
      loadThumbs(); loadShots();
    };
    const items = list().map((a, i) => h("div", { class: "mitem" },
      a.rodzaj === "obraz" ? h("img", { src: a.url }) : a.rodzaj === "wideo" ? h("video", { src: a.url, muted: true }) : h("span", { class: "kind" }, "♪"),
      h("code", { class: "tag", title: T.klik_wstaw, onclick: () => insertTag(tag(i)) }, tag(i)),
      h("span", { class: "name" }, a.nazwa),
      h("button", { class: "btn quiet", type: "button", title: T.usun, onclick: () => { list().splice(i, 1); sync(); draw(); } }, "✕")));
    const full = list().length >= max;
    box.replaceChildren(...items, h("div", { class: "acts" },
      h("span", { class: "count" }, `${list().length} / ${max}`),
      full ? null : h("button", { class: "btn quiet", type: "button", onclick: () => pickAsset(rodzaj, add) }, "+ " + T.z_zasobow),
      full ? null : h("button", { class: "btn quiet", type: "button", onclick: () => file.click() }, "+ " + T.z_dysku)), file);
  };
  draw();
  box.addEventListener("dragover", (e) => { e.preventDefault(); box.style.borderColor = "var(--accent)"; });
  box.addEventListener("dragleave", () => { box.style.borderColor = ""; });
  box.addEventListener("drop", async (e) => {
    e.preventDefault(); box.style.borderColor = "";
    const aid = e.dataTransfer.getData("text/asset");
    if (aid) { const a = state.thumbs.find((x) => String(x.id) === aid); if (a) add(a); return; }
    for (const f of [...e.dataTransfer.files]) { try { add(await uploadFile(f, state.shot)); } catch (err) { toast(err.message); } }
    loadThumbs(); loadShots();
  });
  return h("div", { class: "field" }, h("label", {}, L(inp.etykieta) || inp.id), box);
}

function insertTag(t) {
  const ta = $("prompt"); if (!ta) return;
  const a = ta.selectionStart ?? ta.value.length, b = ta.selectionEnd ?? a;
  ta.value = ta.value.slice(0, a) + t + ta.value.slice(b);
  state.values.prompt = ta.value; ta.focus(); ta.selectionStart = ta.selectionEnd = a + t.length;
}

function slotFor(inp) {
  if (inp.wiele) return multiSlotFor(inp);
  const rodzaj = inp.typ;
  const slot = h("div", { class: "slot" });
  const setAsset = (a) => { state.inputs[inp.id] = a.id; state.inputAssets[inp.id] = a; draw(); };
  const draw = () => {
    const a = state.inputAssets[inp.id];
    const file = h("input", { type: "file", style: "display:none", accept: { obraz: "image/*", wideo: "video/*", dzwiek: "audio/*" }[rodzaj] || "" });
    file.onchange = async () => {
      if (!file.files[0]) return;
      slot.querySelector(".name").textContent = T.wgrywanie;
      try { setAsset(await uploadFile(file.files[0], state.shot)); loadThumbs(); loadShots(); } catch (e) { toast(e.message); draw(); }
    };
    const preview = a ? (a.rodzaj === "obraz" ? h("img", { src: a.url }) : a.rodzaj === "wideo" ? h("video", { src: a.url, muted: true, style: "height:64px" }) : null) : null;
    slot.replaceChildren(...[preview,
      h("span", { class: "name" }, a ? a.nazwa : "—"),
      h("span", { class: "acts" },
        h("button", { class: "btn quiet", type: "button", onclick: () => pickAsset(rodzaj, setAsset) }, T.z_zasobow),
        h("button", { class: "btn quiet", type: "button", onclick: () => file.click() }, T.z_dysku),
        a ? h("button", { class: "btn quiet", type: "button", onclick: () => { delete state.inputs[inp.id]; delete state.inputAssets[inp.id]; draw(); } }, T.usun) : null),
      file].filter(Boolean));
  };
  draw();
  slot.addEventListener("dragover", (e) => { e.preventDefault(); slot.style.borderColor = "var(--accent)"; });
  slot.addEventListener("dragleave", () => { slot.style.borderColor = ""; });
  slot.addEventListener("drop", async (e) => {
    e.preventDefault(); slot.style.borderColor = "";
    const aid = e.dataTransfer.getData("text/asset");
    if (aid) { const a = state.thumbs.find((x) => String(x.id) === aid); if (a && a.rodzaj === rodzaj) setAsset(a); return; }
    const f = e.dataTransfer.files[0]; if (!f) return;
    try { setAsset(await uploadFile(f, state.shot)); loadThumbs(); loadShots(); } catch (err) { toast(err.message); }
  });
  return h("div", { class: "field" }, h("label", {}, L(inp.etykieta) || inp.id), slot);
}

function renderForm() {
  const m = state.model;
  const sel = h("select", { title: L(m.opis) }, MODELS.map((x) => h("option", { value: x.id, selected: x.id === m.id, title: L(x.opis) }, x.nazwa)));
  sel.onchange = () => { pushHistory(); selectModel(sel.value); };
  const guide = m.poradnik ? h("button", { class: "btn", type: "button", title: T.poradnik, onclick: () => showGuide(m.id, m.nazwa) }, "?") : null;
  const basic = [], adv = [];
  for (const p of m.parametry) { const f = fieldFor(p); if (f) (p.zaawansowane ? adv : basic).push(f); }
  const moreBody = h("div", { class: "more-body", style: state.adv ? "" : "display:none" }, adv);
  const moreBtn = h("button", { class: "btn quiet", type: "button" }, state.adv ? T.mniej : T.wiecej);
  moreBtn.onclick = () => { state.adv = !state.adv; moreBody.style.display = state.adv ? "" : "none"; moreBtn.textContent = state.adv ? T.mniej : T.wiecej; };
  const ile = h("span", { class: "ile" }, T.warianty + ":", [1, 2, 3, 4].map((n) => {
    const c = h("button", { class: "chip" + (state.ile === n ? " on" : ""), type: "button" }, String(n));
    c.onclick = () => { state.ile = n; ile.querySelectorAll(".chip").forEach((x) => x.classList.toggle("on", x === c)); pokazKoszt(); };
    return c;
  }));
  $("form").replaceChildren(...[
    h("div", { class: "model-row" }, sel, guide),
    h("p", { class: "desc" }, L(m.opis)),
    m.uwagi && L(m.uwagi) ? h("p", { class: "note" }, L(m.uwagi)) : null,
    m.licencja ? h("div", { class: "lic" }, T.licencja + ": " + m.licencja) : null,
    h("div", { class: "gen-grid" },
      h("div", {}, basic, adv.length ? h("div", { class: "more" }, moreBtn, moreBody) : null),
      h("div", {}, m.wejscia.map(slotFor))),
    h("div", { class: "go" }, h("button", { class: "btn primary", id: "go", onclick: submit }, T.generuj), h("span", { class: "msg", id: "go-msg" }), ile),
    m.api ? h("div", { class: "koszt", id: "koszt" }) : null,
  ].flat(Infinity).filter(Boolean));
  pokazKoszt();
}

// Koszt zadania API (sekundy budżetu) — pod przyciskiem; liczy serwer, odświeżane po zmianie ustawień i wejść.
let kosztT = null;
function pokazKoszt() {
  if (!state.model?.api) return;
  clearTimeout(kosztT);
  kosztT = setTimeout(async () => {
    const el = $("koszt"); if (!el) return;
    try {
      const w = await api("/api/wycena", { method: "POST", body: JSON.stringify({ model: state.model.id, wartosci: state.values, wejscia: state.inputs, ile: state.ile }) });
      if (w.budzet.tryb === "usd") {                   // jeden użytkownik: tylko szacunek ceny, jeśli jest
        el.className = "koszt";
        el.textContent = (w.koszt_usd ? tf("koszt_usd_linia", { k: (Math.round(w.koszt_usd * 100) / 100).toLocaleString(LOCALE) }) : "")
          + (w.dostepne ? "" : (w.koszt_usd ? " · " : "") + T.api_niedostepne);
        return;
      }
      const brak = w.koszt_s > w.budzet.zostalo;
      el.className = "koszt" + (brak ? " brak" : "");
      el.textContent = tf("koszt_linia", { k: fmtS(w.koszt_s), z: fmtS(w.budzet.zostalo) })
        + (brak ? " — " + T.za_malo : "") + (w.dostepne ? "" : " · " + T.api_niedostepne);
    } catch (e) { el.textContent = ""; }
  }, 250);
}

// ---------- tryb „prompt w centrum” ----------
function enterFocus() {
  if (APP.classList.contains("focus")) return;
  APP.classList.add("focus");
  const a = state.selected;
  $("focus-mini").replaceChildren(...[a && (a.rodzaj === "obraz" || a.rodzaj === "wideo") ? mediaEl(a, { thumb: true }) : null, h("span", {}, T.esc)].filter(Boolean));
}
function exitFocus() { APP.classList.remove("focus"); }
document.addEventListener("mousedown", (e) => {
  if (APP.classList.contains("focus") && !$("panel").contains(e.target) && !e.target.closest(".modal-back")) exitFocus();
});

// ---------- historia (Ctrl+Z) ----------
function pushHistory() {
  if (!state.model) return;
  state.history.push(JSON.stringify({ model: state.model.id, values: state.values, inputs: state.inputs, inputAssets: state.inputAssets }));
  if (state.history.length > 40) state.history.shift();
}
function undo() {
  const s = state.history.pop();
  if (!s) return;
  const d = JSON.parse(s);
  state.model = MODELS.find((m) => m.id === d.model) || state.model;
  state.values = d.values; state.inputs = d.inputs; state.inputAssets = d.inputAssets;
  renderForm(); toast(T.cofnieto);
}
document.addEventListener("keydown", (e) => {
  const tag = (document.activeElement?.tagName || "").toLowerCase();
  if (e.key === "Escape" && APP.classList.contains("focus") && !document.querySelector(".modal-back")) { exitFocus(); document.activeElement?.blur(); return; }
  if (e.key === "Delete" && tag !== "textarea" && tag !== "input" && !document.querySelector(".modal-back")) {
    const ids = state.cmp.size ? state.thumbs.filter((a) => state.cmp.has(a.id) && a.login === window.LOGIN).map((a) => a.id)
      : (state.selected && state.selected.login === window.LOGIN ? [state.selected.id] : []);
    if (ids.length) { e.preventDefault(); deleteAssets(ids, afterDelete); }
    return;
  }
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "z" && !e.shiftKey && tag !== "textarea" && tag !== "input") { e.preventDefault(); undo(); }
});

// ---------- przenoszenie wartości z wyniku ----------
function takeable(key) { return key === "prompt" || (state.model && state.model.parametry.some((p) => p.id === key)); }
function take(key, val) {
  pushHistory();
  if (key === "__model") { if (MODELS.some((m) => m.id === val)) selectModel(val, true); toast(T.przenies); return; }
  state.values[key] = val;
  renderForm(); toast(T.przenies);
}
function reuse(a) {
  const m = a.meta || {};
  const alias = (window.ALIASY || {})[m.model];
  const mid = alias ? alias.model : m.model;
  if (!MODELS.find((x) => x.id === mid)) return;
  pushHistory();
  selectModel(mid);
  for (const [k, v] of Object.entries(m.ustawienia || {})) if (state.model.parametry.some((p) => p.id === k)) state.values[k] = v;
  for (let [k, v] of Object.entries(m.wejscia || {})) {
    const lista = k.match(/^(.+) (\d+)$/);                 // „obrazy 2” — kolejny plik wejścia z wieloma plikami
    if (lista) k = lista[1];
    if (alias && alias.mapa[k]) k = alias.mapa[k];
    const inp = state.model.wejscia.find((x) => x.id === k);
    if (!inp) continue;
    const asset = { id: v.id, nazwa: v.nazwa, rodzaj: inp.typ, url: `/pliki/${v.id}` };
    if (inp.wiele) { (state.inputAssets[k] ||= []).push(asset); state.inputs[k] = state.inputAssets[k].map((x) => x.id); }
    else { state.inputs[k] = v.id; state.inputAssets[k] = asset; }
  }
  renderForm();
}

// ---------- generowanie i kolejka ----------
async function submit() {
  const btn = $("go"), msg = $("go-msg");
  msg.textContent = "";
  for (const inp of state.model.wejscia) if (inp.wymagane && !state.inputs[inp.id]) { msg.textContent = tf("brakuje", { n: L(inp.etykieta) || inp.id }); return; }
  if (state.model.parametry.some((p) => p.typ === "prompt" && !p.opcjonalny) && !(state.values.prompt || "").trim()) { msg.textContent = T.prompt_pusty; return; }
  for (const p of state.model.parametry) if (p.wymagane && p.typ !== "prompt" && !String(state.values[p.id] ?? "").trim()) { msg.textContent = tf("brakuje", { n: label(p) }); return; }
  for (const p of state.model.parametry) if (p.typ === "prompt" && p.json) { const b = bladJson(state.values[p.id]); if (b) { msg.textContent = b; return; } }
  btn.disabled = true;
  const wyslij = async (przezApi) => {
    await api("/api/zadania", { method: "POST", body: JSON.stringify({ model: state.model.id, wartosci: state.values, wejscia: state.inputs, ujecie: state.shot, ile: state.ile, przez_api: przezApi }) });
    exitFocus(); pollJobs(); odswiezBudzet();
  };
  try {
    // model lokalny z wersją w API: gdy samo zadanie potrwa długo, uczestnik wybiera — lokalnie (za darmo) czy API (z budżetu)
    const w = state.model.zapas_api ? await api("/api/wycena", { method: "POST", body: JSON.stringify({ model: state.model.id, wartosci: state.values, wejscia: state.inputs, ile: state.ile }) }) : null;
    if (w && w.zapasy?.length && w.czas_s != null && w.czas_s > w.prog_s) wyborApi(w, wyslij);
    else await wyslij(false);
  } catch (e) { msg.textContent = e.message; }
  finally { setTimeout(() => (btn.disabled = false), 400); }
}

function wyborApi(w, wyslij) {
  const min = (s) => Math.max(1, Math.round(s / 60)) + " min";
  const etykieta = (id) => { const inp = state.model.wejscia.find((x) => x.id === id); return inp ? (L(inp.etykieta) || id) : id; };
  let okno;
  const wybierz = async (przezApi) => {
    okno.close();
    try { await wyslij(przezApi); } catch (e) { $("go-msg").textContent = e.message; }
  };
  const opcja = (z) => {
    const starczy = z.koszt_s <= w.budzet.zostalo;
    return h("button", { class: "btn primary", disabled: !starczy, onclick: () => wybierz(z.model) },
      h("b", {}, z.nazwa),
      h("span", {}, tf("api_opcja", { t: min(z.czas_s), k: fmtS(z.koszt_s) })
        + " · " + (starczy ? tf("api_zostanie", { z: fmtS(Math.max(0, w.budzet.zostalo - z.koszt_s)) }) : T.za_malo_budzetu)),
      h("span", {}, tf("api_dlugosc", { s: z.dlugosc_s })
        + (z.pominiete.length ? " · " + tf("api_pominie", { n: z.pominiete.map(etykieta).join(", ") }) : "")));
  };
  okno = modal(T.api_tytul, h("div", { class: "wybor-api" },
    h("p", {}, tf("api_lokalnie_opis", { t: min(w.czas_s), e: min(w.eta_s) })),
    h("div", { class: "opcje" },
      h("button", { class: "btn", onclick: () => wybierz(false) }, h("b", {}, T.api_poczekam),
        h("span", {}, tf("api_lokalnie", { e: min(w.eta_s) }))),
      ...w.zapasy.map(opcja)),
    h("p", { class: "hint" }, T.api_uwaga)));
}

async function pollJobs() {
  let jobs = [];
  try { jobs = await api("/api/zadania"); } catch (e) { return; }
  const mine = jobs.filter((j) => j.obszar === OBSZAR);
  const active = mine.filter((j) => j.status !== "gotowe");
  const done = mine.filter((j) => j.status === "gotowe").slice(0, 2);
  $("jobs").replaceChildren(...[...active, ...done].map((j) => {
    const eta = j.eta != null ? " · " + T.gotowe_za + (j.eta < 90 ? Math.max(5, Math.round(j.eta / 5) * 5) + " s" : Math.round(j.eta / 60) + " min") : "";
    const st = (j.status === "czeka" ? `${T.czeka}${j.przed ? " · " + j.przed + " " + T.przed_toba : ""}${eta}` : (T[j.status] || j.status) + (j.czas ? ` · ${j.czas} s` : ""))
      + (j.maszyna === "api" && j.status === "w_toku" ? " · API" : "");
    return h("li", { class: "job" },
      h("div", { class: "l1" }, h("span", {}, j.nazwa), h("span", { class: "sp" }), h("span", { class: "st " + j.status }, st),
        (j.status === "czeka" || j.status === "w_toku") ? h("button", { class: "btn quiet", onclick: async () => { await api(`/api/zadania/${j.id}/anuluj`, { method: "POST" }); pollJobs(); } }, T.anuluj) : null,
        j.status === "blad" ? h("button", { class: "btn quiet x", title: T.zamknij_blad, onclick: async () => { await api(`/api/zadania/${j.id}/zamknij`, { method: "POST" }); pollJobs(); } }, "✕") : null),
      j.status === "w_toku" ? h("div", { class: "bar" }, h("i", { style: `width:${Math.round((j.postep || 0) * 100)}%` })) : null,
      j.status === "blad" && j.blad ? h("div", { class: "err" }, j.blad) : null);
  }));
  const fresh = mine.filter((j) => j.status === "gotowe" && !state.seenDone.has(j.id));
  mine.forEach((j) => j.status === "gotowe" && state.seenDone.add(j.id));
  if (fresh.length || mine.some((j) => j.status === "blad")) odswiezBudzet();     // błąd/anulowanie API = zwrot
  if (fresh.length && state.primed) {
    await loadThumbs(); loadShots();
    const a = state.thumbs.find((x) => x.id === fresh[0].wyniki[0]);
    if (a) show(a);
  }
  state.primed = true;
}

// ---------- pasek generacji ----------
function setScope(k) {
  state.scope = k;
  $("scope").querySelectorAll("a").forEach((y) => y.classList.toggle("on", y.dataset.k === k));
  state.selected = null;
  loadThumbs();
}

async function loadThumbs() {
  const p = new URLSearchParams({ rodzaj: RODZAJ, q: state.q });
  if (state.scope === "ujecie") { p.set("kto", "ja"); if (state.shot) p.set("ujecie", state.shot); }
  else p.set("kto", state.scope);
  if (state.onlyStar) p.set("wybrane", 1);
  // dźwięk jest wspólnym rodzajem Mowy, Muzyki i SFX — w galerii obszaru tylko jego wyniki (+ pliki wgrane, bez obszaru)
  const items = (await api("/api/zasoby?" + p)).filter((a) => !a.obszar || a.obszar === OBSZAR);
  state.thumbs = items;
  const groups = {};
  for (const a of items) if (a.meta?.grupa) (groups[a.meta.grupa] ||= []).push(a.id);
  $("thumbs").replaceChildren(...items.map((a) => {
    const t = h("div", { class: "thumb" + (state.selected?.id === a.id ? " on" : "") + (state.cmp.has(a.id) ? " cmp" : "") + (a.ukryte ? " hidden-mark" : ""),
      draggable: "true", title: T.miniatura_klik },
      mediaEl(a, { thumb: true }), starBtn(a, () => state.onlyStar && loadThumbs()));
    const g = groups[a.meta?.grupa];
    if (g && g.length > 1) t.append(h("span", { class: "vr" }, `${g.length - g.indexOf(a.id)}/${g.length}`));
    if (a.login !== window.LOGIN) t.append(h("span", { class: "by" }, a.login));
    t.onclick = (e) => {
      if (e.shiftKey || e.ctrlKey || e.metaKey) { state.cmp.has(a.id) ? state.cmp.delete(a.id) : state.cmp.size < 4 && state.cmp.add(a.id); t.classList.toggle("cmp", state.cmp.has(a.id)); renderCmp(); return; }
      show(a);
    };
    t.addEventListener("dragstart", (e) => e.dataTransfer.setData("text/asset", String(a.id)));
    return t;
  }));
  renderCmp();
  if (!items.length) { $("stage").replaceChildren(h("span", { class: "empty" }, T.pusto)); $("sel-meta").replaceChildren(); return; }
  if (!state.selected || !items.some((x) => x.id === state.selected.id)) show(items[0]);
}

function renderCmp() {
  const b = $("cmp-btn");
  const n = state.cmp.size;
  b.style.display = n >= 2 ? "" : "none";
  b.textContent = `${T.porownaj} (${n})`;
  b.onclick = () => compareView(state.thumbs.filter((a) => state.cmp.has(a.id)));
  let d = $("del-btn");
  if (!d) { d = h("button", { class: "btn quiet danger", id: "del-btn" }); b.after(d); }
  const own = state.thumbs.filter((a) => state.cmp.has(a.id) && a.login === window.LOGIN).map((a) => a.id);
  d.style.display = own.length ? "" : "none";
  d.textContent = `${T.usun_zazn} (${own.length})`;
  d.onclick = () => deleteAssets(own, afterDelete);
}

function afterDelete(ids) {
  ids.forEach((id) => state.cmp.delete(id));
  if (state.selected && ids.includes(state.selected.id)) state.selected = null;
  loadThumbs(); loadShots();
}

function show(a) {
  state.selected = a;
  document.querySelectorAll(".thumb").forEach((t, i) => t.classList.toggle("on", state.thumbs[i]?.id === a.id));
  const m = a.meta || {};
  const stage = $("stage");
  stage.classList.remove("natural");
  const tools = h("div", { class: "stage-tools" });
  if (a.rodzaj === "obraz") {
    const z = h("button", { class: "btn" }, T.rozmiar_1_1);
    z.onclick = () => { const on = stage.classList.toggle("natural"); z.textContent = on ? T.dopasuj : T.rozmiar_1_1; };
    tools.append(z);
  }
  if (a.rodzaj === "obraz" || a.rodzaj === "wideo") tools.append(h("button", { class: "btn", onclick: () => stage.requestFullscreen?.() }, T.pelny_ekran));
  const info = h("div", { class: "info" }, h("span", {}, m.nazwa_modelu || a.nazwa), m.ustawienia?.rozdzielczosc ? h("span", {}, m.ustawienia.rozdzielczosc) : null,
    m.czas_s ? h("span", {}, m.czas_s + " s") : null, h("span", { class: "sp" }), h("span", {}, a.login));
  const media = a.rodzaj === "dzwiek"
    ? h("div", { class: "audio-wrap" }, mediaEl(a), m.ustawienia?.prompt ? h("div", { class: "said" }, m.ustawienia.prompt) : null)
    : mediaEl(a);
  stage.replaceChildren(media, tools, info);
  $("sel-meta").replaceChildren(metaView(a, { onReuse: reuse, onTake: take, onDelete: afterDelete, q: state.q, takeable }));
}

$("scope").querySelectorAll("a").forEach((x) => x.onclick = () => setScope(x.dataset.k));
$("star-f").onclick = () => { state.onlyStar = !state.onlyStar; $("star-f").classList.toggle("on", state.onlyStar); loadThumbs(); };
let qTimer;
$("q").oninput = () => { clearTimeout(qTimer); qTimer = setTimeout(() => { state.q = $("q").value; loadThumbs(); }, 180); };

// ---------- start ----------
(async () => {
  await loadShots(false);
  if (MODELS.length) {
    const last = localStorage.getItem("model:" + OBSZAR);
    selectModel(MODELS.some((m) => m.id === last) ? last : MODELS[0].id);
  } else {
    $("form").replaceChildren(h("p", { class: "desc" }, T.wkrotce));
  }
  try {
    const r = JSON.parse(localStorage.getItem("reuse") || "null");
    if (r && r.obszar === OBSZAR) {
      localStorage.removeItem("reuse"); reuse(r);
      if (r.komunikat) { renderForm(); setTimeout(() => { blysk($("prompt")); toast(r.komunikat); }, 100); }   // np. karta z Tekstu
    }
  } catch (e) {}
  await loadThumbs();
  pollJobs();
  setInterval(pollJobs, 1500);
})();
