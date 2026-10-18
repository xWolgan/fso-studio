// Ustawienia: klucze dostawców, katalogi modeli, wybór modeli do obszarów.
const OBSZARY = ["tekst", "obraz", "wideo", "muzyka", "sfx", "mowa"];
const NA_GRUPE = 40;
const BEZ_KLUCZA = ["openrouter", "fal", "higgsfield", "kie"];   // katalog widać i bez klucza                                   // tyle pozycji w obszarze, reszta pod „pokaż więcej”

function sekcja(d) {
  const stanKlucza = h("span", { class: "u-stan " + (d.ma_klucz ? "ok" : "") }, d.ma_klucz ? T.u_jest_klucz : T.u_brak_klucza);
  const info = h("span", { class: "u-info" });
  const pole = h("input", { type: "password", autocomplete: "off", spellcheck: "false",
    placeholder: T.u_klucz + (d.format ? " · " + tf("u_format", { f: d.format }) : "") });
  const lista = h("div", { class: "u-modele" });
  const pobierz = h("button", { class: "btn", disabled: !d.ma_klucz && !BEZ_KLUCZA.includes(d.id) },
    d.katalog_czas ? T.u_odswiez : T.u_pobierz);

  const ustawStan = (ma) => { d.ma_klucz = ma; stanKlucza.textContent = ma ? T.u_jest_klucz : T.u_brak_klucza;
    stanKlucza.classList.toggle("ok", ma); pobierz.disabled = !ma && !BEZ_KLUCZA.includes(d.id); };
  const pokazWynik = (r) => { info.textContent = r.info || ""; info.className = "u-info " + (r.ok ? "ok" : "err"); };

  const zapisz = async (wartosc) => {
    info.textContent = "…"; info.className = "u-info";
    try {
      const r = await api("/api/ustawienia/klucz", { method: "POST", body: JSON.stringify({ dostawca: d.id, klucz: wartosc }) });
      pole.value = ""; ustawStan(r.ma_klucz); pokazWynik(r);
      if (r.ok && !d.katalog_czas) wczytaj(true);
    } catch (e) { info.textContent = e.message; info.className = "u-info err"; }
  };

  const wczytaj = async (odswiez) => {
    lista.replaceChildren(h("div", { class: "u-puste" }, T.u_pobieram));
    try {
      const r = await api(`/api/ustawienia/katalog?dostawca=${d.id}&odswiez=${odswiez ? 1 : 0}`);
      d.katalog_czas = Date.now() / 1000; pobierz.textContent = T.u_odswiez;
      rysujModele(d, r.modele, new Set(r.wybrane), lista);
    } catch (e) { lista.replaceChildren(h("div", { class: "u-puste err" }, e.message)); }
  };
  pobierz.onclick = () => wczytaj(true);

  const el = h("section", { class: "u-dostawca" },
    h("div", { class: "u-nag" }, h("h2", {}, d.nazwa), stanKlucza, h("span", { style: "flex:1" }),
      h("a", { class: "link", href: d.klucz_url, target: "_blank", rel: "noopener" }, T.u_gdzie_klucz + " ↗")),
    h("div", { class: "u-klucz" }, pole,
      h("button", { class: "btn primary", onclick: () => pole.value.trim() && zapisz(pole.value.trim()) }, T.u_zapisz),
      h("button", { class: "btn", onclick: async () => { info.textContent = "…"; pokazWynik(await api("/api/ustawienia/sprawdz", { method: "POST", body: JSON.stringify({ dostawca: d.id }) })); } }, T.u_sprawdz),
      h("button", { class: "btn quiet", onclick: () => d.ma_klucz && zapisz("") }, T.u_usun), info),
    h("div", { class: "u-akcje" }, pobierz), lista);
  pole.addEventListener("keydown", (e) => { if (e.key === "Enter" && pole.value.trim()) zapisz(pole.value.trim()); });
  if (d.katalog_czas) wczytaj(false);
  return el;
}

function rysujModele(d, modele, wybrane, lista) {
  const szukaj = h("input", { type: "text", placeholder: T.u_szukaj, spellcheck: "false" });
  const tylko = h("input", { type: "checkbox" });
  const licznik = h("span", { class: "u-licznik" });
  const grupy = h("div");
  const odswiezLicznik = () => { licznik.textContent = tf("u_modeli", { n: modele.length }) + " · " + tf("u_wybrane", { n: wybrane.size }); };

  const wiersz = (m) => {
    const cb = h("input", { type: "checkbox", disabled: !m.obslugiwany });
    cb.checked = wybrane.has(m.id);
    cb.onchange = async () => {
      try {
        const r = await api("/api/ustawienia/wybor", { method: "POST", body: JSON.stringify({ dostawca: d.id, id: m.id, tak: cb.checked }) });
        wybrane.clear(); r.wybrane.forEach((x) => wybrane.add(x)); odswiezLicznik(); toast(T.u_zapisano);
      } catch (e) { cb.checked = !cb.checked; toast(e.message); }
    };
    return h("label", { class: "u-model" + (m.obslugiwany ? "" : " off"), title: m.opis || "" }, cb,
      h("span", { class: "u-mnazwa" }, m.nazwa),
      m.nazwa !== m.id ? h("span", { class: "u-mid" }, m.id) : null,
      m.obraz_we && m.obszar === "tekst" ? h("span", { class: "u-znak" }, T.u_obrazy) : null,
      m.cena ? h("span", { class: "u-cena" }, m.cena) : null,
      m.obslugiwany ? null : h("span", { class: "u-znak" }, T.u_wkrotce));
  };

  const rysuj = () => {
    const q = szukaj.value.trim().toLowerCase();
    const pasuje = (m) => (!tylko.checked || wybrane.has(m.id)) && (!q || (m.nazwa + " " + m.id).toLowerCase().includes(q));
    grupy.replaceChildren(...OBSZARY.map((o) => {
      const ms = modele.filter((m) => m.obszar === o && pasuje(m));
      if (!ms.length) return null;
      const box = h("div", { class: "u-grupa" }, h("h3", {}, T["obszar." + o] || o, h("span", { class: "u-ile" }, " · " + ms.length)));
      ms.slice(0, NA_GRUPE).forEach((m) => box.append(wiersz(m)));
      if (ms.length > NA_GRUPE) {
        const wiecej = h("button", { class: "btn quiet" }, tf("u_pokaz_wiecej", { n: ms.length - NA_GRUPE }));
        wiecej.onclick = () => { wiecej.replaceWith(...ms.slice(NA_GRUPE).map(wiersz)); };
        box.append(wiecej);
      }
      return box;
    }).filter(Boolean));
  };
  szukaj.oninput = rysuj; tylko.onchange = rysuj;
  odswiezLicznik(); rysuj();
  lista.replaceChildren(h("div", { class: "u-filtry" }, szukaj, h("label", { class: "inline" }, tylko, " " + T.u_tylko_wybrane), licznik), grupy);
}

(async () => {
  const box = document.getElementById("dostawcy");
  try {
    const ds = await api("/api/ustawienia");
    box.replaceChildren(...ds.map(sekcja));
  } catch (e) { box.replaceChildren(h("p", { class: "u-puste err" }, e.message)); }
})();
