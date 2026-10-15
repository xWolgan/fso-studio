// Galeria ogólna: wszystkie rodzaje mediów i ujęcia; moje / wszystkich / osoba; szukaj, ★, porównaj.
const g = { kind: "", kto: "ja", q: "", star: false, cmp: new Set(), items: [] };
const grid = document.getElementById("grid");

async function load() {
  const kto = document.getElementById("f-person").value || g.kto;
  const p = new URLSearchParams({ kto, q: g.q });
  if (g.kind) p.set("rodzaj", g.kind);
  if (g.star) p.set("wybrane", 1);
  const items = await api("/api/zasoby?" + p);
  g.items = items;
  grid.replaceChildren(...(items.length ? items.map((a) => {
    const c = h("div", { class: "cell" + (g.cmp.has(a.id) ? " cmp" : ""), title: T.galeria_klik },
      mediaEl(a, { thumb: true }), starBtn(a, () => g.star && load()),
      h("span", { class: "lbl" }, [a.login !== window.LOGIN ? a.login : "", a.ujecie_nazwa, a.meta?.nazwa_modelu || a.nazwa].filter(Boolean).join(" · ")));
    c.onclick = (e) => {
      if (e.shiftKey || e.ctrlKey || e.metaKey) { g.cmp.has(a.id) ? g.cmp.delete(a.id) : g.cmp.size < 4 && g.cmp.add(a.id); c.style.outline = g.cmp.has(a.id) ? "2px solid var(--accent)" : ""; renderCmp(); return; }
      open(a);
    };
    if (g.cmp.has(a.id)) c.style.outline = "2px solid var(--accent)";
    return c;
  }) : [h("div", { class: "kind" }, T.pusto)]));
  renderCmp();
}

function renderCmp() {
  const b = document.getElementById("f-cmp");
  b.style.display = g.cmp.size >= 2 ? "" : "none";
  b.textContent = `${T.porownaj} (${g.cmp.size})`;
  b.onclick = () => compareView(g.items.filter((a) => g.cmp.has(a.id)));
  let d = document.getElementById("f-del");
  if (!d) { d = h("button", { class: "btn quiet danger", id: "f-del" }); b.after(d); }
  const own = g.items.filter((a) => g.cmp.has(a.id) && a.login === window.LOGIN).map((a) => a.id);
  d.style.display = own.length ? "" : "none";
  d.textContent = `${T.usun_zazn} (${own.length})`;
  d.onclick = () => deleteAssets(own, (ids) => { ids.forEach((id) => g.cmp.delete(id)); load(); });
}

function open(a) {
  if (a.rodzaj === "tekst" && typeof notatki !== "undefined") { notatki.otworz(a.id); return; }
  let m;
  const body = h("div", { class: "viewer" }, h("div", { class: "v-stage" }, mediaEl(a)), h("div", { class: "v-side meta" }, metaView(a, {
    q: g.q,
    onDelete: (ids) => { m.close(); ids.forEach((id) => g.cmp.delete(id)); load(); },
    onReuse: a.obszar ? (x) => { localStorage.setItem("reuse", JSON.stringify(x)); location.href = "/" + x.obszar; } : null,
  })));
  m = modal(a.ujecie_nazwa ? a.ujecie_nazwa + " — " + a.nazwa : a.nazwa, body, { wide: true });
  m.el.querySelector(".modal-body").style.padding = "0";
}

function bind(id, key) {
  document.getElementById(id).querySelectorAll("a").forEach((x) => x.onclick = () => {
    g[key] = x.dataset.k;
    document.getElementById(id).querySelectorAll("a").forEach((y) => y.classList.toggle("on", y === x));
    if (key === "kto") document.getElementById("f-person").value = "";
    load();
  });
}
bind("f-kind", "kind");
bind("f-who", "kto");
document.getElementById("f-person").onchange = load;
let tm;
document.getElementById("f-q").oninput = (e) => { clearTimeout(tm); tm = setTimeout(() => { g.q = e.target.value; load(); }, 180); };
document.getElementById("f-star").onclick = (e) => { g.star = !g.star; e.target.style.color = g.star ? "var(--accent)" : "var(--muted)"; load(); };
api("/api/osoby").then((people) => {
  const sel = document.getElementById("f-person");
  for (const p of people) sel.append(h("option", { value: p }, p));
});
load();
