// Tablica na duży ekran: maszyny, kolejka lokalna (z przewidywaniem), API, ostatnio gotowe. Odświeżanie co 3 s.
const $ = (id) => document.getElementById(id);
const NAZWY = {};                                // id maszyny → nazwa (z config.yaml: maszyny[].nazwa)
let D = null, roznica = 0;

const nazwa = (id) => NAZWY[id] || id || "—";
const minut = (s) => s < 60 ? "<1 min" : Math.round(s / 60) + " min";
const godz = (t) => new Date(t * 1000).toLocaleTimeString(LOCALE, { hour: "2-digit", minute: "2-digit" });
const teraz = () => Date.now() / 1000 - roznica;
const co = (j) => [j.model, T["obszar." + j.obszar], j.opis].filter(Boolean).join(" · ");

function maszyna(m) {
  const z = m.zadanie;
  const klasa = "tb-m" + (!m.ok ? " off" : z ? "" : " wolna");
  NAZWY[m.id] = m.nazwa || m.id;
  const nag = h("div", { class: "nag" }, h("span", { class: "dot" }), h("b", {}, nazwa(m.id)), h("span", {}, m.opis || ""),
    h("span", { class: "sp" }), h("span", {}, !m.ok ? T.tb_niedostepna : z ? T.tb_pracuje : T.tb_wolna));
  if (!z) return h("div", { class: klasa }, nag, h("div", { class: "pusto" }, m.ok ? T.tb_czeka : "—"));
  const t = teraz(), od = t - (z.start || t);
  let pasek = 0, ile = tf("tb_trwa", { t: minut(od) });
  if (z.koniec) {
    pasek = Math.min(0.99, od / Math.max(1, z.koniec - z.start));
    const zostalo = z.koniec - t;
    ile += " · " + (zostalo > 0 ? tf("tb_zostalo", { t: minut(zostalo) }) : T.tb_dluzej);
  }
  return h("div", { class: klasa }, nag, h("div", { class: "kto" }, z.login), h("div", { class: "co" }, co(z)),
    h("div", { class: "bar" }, h("i", { style: `width:${Math.round(pasek * 100)}%` })), h("div", { class: "ile" }, ile));
}

function kartaApi(lista) {
  const nag = h("div", { class: "nag" }, h("span", { class: "dot" }), h("b", {}, "API"), h("span", {}, T.tb_api_opis),
    h("span", { class: "sp" }), h("span", {}, lista.length ? tf("tb_w_toku", { n: lista.length }) : T.tb_nic));
  const t = teraz();
  return h("div", { class: "tb-m" + (lista.length ? "" : " wolna") }, nag,
    ...(lista.length ? lista.slice(0, 4).map((j) => h("div", { class: "api-l" }, h("b", {}, j.login), h("span", {}, co(j) + (j.start ? " · " + minut(t - j.start) : ""))))
                     : [h("div", { class: "pusto" }, T.tb_api_pusto)]));
}

function rysuj() {
  if (!D) return;
  const t = teraz();
  $("tb-zegar").textContent = godz(t);
  $("tb-sub").textContent = T.tb_podtytul;
  $("tb-maszyny").replaceChildren(...D.maszyny.map(maszyna), kartaApi(D.api));
  $("tb-h-kolejka").textContent = T.tb_kolejka + (D.kolejka.length ? " · " + D.kolejka.length : "");
  $("tb-kolejka").replaceChildren(...(D.kolejka.length ? D.kolejka.map((j, i) => h("li", {},
      h("span", { class: "nr" }, String(i + 1)), h("span", { class: "kto" }, j.login),
      h("span", { class: "kiedy" }, j.koniec ? tf("tb_gotowe_o", { t: godz(j.koniec) }) : "—",
        h("small", {}, j.maszyna ? nazwa(j.maszyna) + " · " + (j.start && j.start > t + 30 ? tf("tb_start_za", { t: minut(j.start - t) }) : T.tb_zaraz) : T.tb_brak_maszyny)),
      h("span", { class: "co" }, co(j))))
    : [h("li", { class: "pusto" }, T.tb_kolejka_pusta)]));
  $("tb-h-ostatnie").textContent = T.tb_ostatnie;
  $("tb-ostatnie").replaceChildren(...D.ostatnie.map((j) => h("li", {},
    h("span", { class: "nr" }, ""), h("span", { class: "kto" }, j.login),
    h("span", { class: "kiedy" }, godz(j.koniec), h("small", {}, (j.maszyna === "api" ? "API" : nazwa(j.maszyna)) + (j.czas != null ? " · " + minut(j.czas) : ""))),
    h("span", { class: "co" }, co(j)))));
}

async function pobierz() {
  try {
    D = await api("/api/tablica");
    roznica = Date.now() / 1000 - D.teraz;
    rysuj();
  } catch (e) {}
}
pobierz();
setInterval(pobierz, 3000);
setInterval(rysuj, 1000);
