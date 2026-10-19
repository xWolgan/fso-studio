// Notatki .md — wysuwany z boku edytor (w stylu Typory: pisze się na czysto), dostępny w każdym obszarze.
// Pliki to artefakty uczestnika (zasoby/<login>/artefakty/*.md): widoczne w innych obszarach i w galerii.
const notatki = (() => {
  let panel, ed, biezacy = null, zapisany = "", ladowanie = null;
  // zmiany = treść różni się od zapisanej (edytor zgłasza „zmianę” już przy wczytaniu — tamtym sygnałom nie ufamy)
  const zmienione = () => Boolean(biezacy && ed && ed.getMarkdown() !== zapisany);
  let wczytuje = false;   // edytor normalizuje treść chwilę po wczytaniu — to nie jest zmiana użytkownika
  const ustawZapisany = () => {
    wczytuje = true; zapisany = ed.getMarkdown();
    setTimeout(() => { zapisany = ed.getMarkdown(); wczytuje = false; panel._stan.textContent = ""; }, 120);
  };

  const ciemny = () => matchMedia("(prefers-color-scheme: dark)").matches;
  function zaladujEdytor() {
    if (ladowanie) return ladowanie;
    ladowanie = new Promise((ok) => {
      for (const href of ["/static/vendor/toastui-editor.min.css", ...(ciemny() ? ["/static/vendor/toastui-editor-dark.css"] : [])]) {
        document.head.append(h("link", { rel: "stylesheet", href }));
      }
      const s = h("script", { src: "/static/vendor/toastui-editor-all.min.js" });
      s.onload = ok; document.head.append(s);
    });
    return ladowanie;
  }

  function zbuduj() {
    if (panel) return;
    const lista = h("ul", { class: "nl-lista" });
    const nazwa = h("span", { class: "nl-nazwa" }, "—");
    const zmien = h("button", { class: "btn quiet", title: T.zmien_nazwe, onclick: zmienNazwe, hidden: true }, "✎");
    const stan = h("span", { class: "nl-stan" });
    const pole = h("div", { class: "nl-ed" });
    const decyzja = h("div", { class: "nl-decyzja", hidden: true });
    panel = h("aside", { class: "notatki" },
      h("div", { class: "nl-head" }, h("b", {}, T.notatki), h("span", { class: "sp" }),
        h("button", { class: "btn quiet", onclick: nowa }, "+ " + T.nowa_notatka),
        h("button", { class: "btn quiet", title: T.zamknij_panel, onclick: zamknij }, "✕")),
      decyzja,
      h("div", { class: "nl-body" }, lista,
        h("div", { class: "nl-prawa" },
          h("div", { class: "nl-pasek" }, nazwa, zmien, stan, h("span", { class: "sp" }),
            h("button", { class: "btn quiet", title: T.wstaw_do_promptu, onclick: wstaw }, "↙ " + T.wstaw_do_promptu),
            h("button", { class: "btn", onclick: zapisz }, T.zapisz)),
          pole)));
    panel._lista = lista; panel._nazwa = nazwa; panel._stan = stan; panel._pole = pole; panel._zmien = zmien; panel._decyzja = decyzja;
    document.body.append(panel);
    document.addEventListener("keydown", (e) => {
      if (panel.classList.contains("on") && (e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") { e.preventDefault(); zapisz(); }
      if (panel.classList.contains("on") && e.key === "Escape" && panel._decyzja.hidden && !document.querySelector(".modal-back")) zamknij();
    });
  }

  async function odswiezListe() {
    const obszar = document.body.dataset.obszar || "";
    const as = (await api("/api/artefakty")).map((a, i) => ({ ...a, i, tu: a.folder === "prompty/" + obszar }));
    as.sort((a, b) => (b.tu - a.tu) || (a.i - b.i));     // prompty dla bieżącego obszaru na górze
    panel._lista.replaceChildren(...as.map((a) => {
      const li = h("li", { class: (a.id === biezacy?.id ? "on" : "") + (a.tu ? " tu" : ""), title: a.folder ? a.folder + "/" + a.nazwa : a.nazwa },
        a.folder ? h("span", { class: "nl-folder" }, a.folder + "/") : null, a.nazwa.replace(/\.md$/, ""));
      li.onclick = () => otworz(a.id);
      return li;
    }));
  }

  async function pokaz() {
    zbuduj();
    panel.classList.add("on");
    await zaladujEdytor();
    if (!ed) {
      ed = new toastui.Editor({ el: panel._pole, height: "100%", initialEditType: "wysiwyg", hideModeSwitch: false,
        previewStyle: "tab", usageStatistics: false, theme: ciemny() ? "dark" : "light",
        toolbarItems: [["heading", "bold", "italic", "strike"], ["ul", "ol", "quote"], ["link"]] });
      ed.on("change", () => { if (!wczytuje) panel._stan.textContent = zmienione() ? "•" : ""; });
    }
    odswiezListe();
  }

  // Pytanie w samym panelu (okienka przeglądarki bywają zablokowane — wtedy panel nie dawał się zamknąć).
  function pytaj(tekst, opcje) {
    return new Promise((ok) => {
      const d = panel._decyzja;
      d.replaceChildren(h("span", {}, tekst), h("span", { class: "sp" }),
        ...opcje.map(([k, etykieta, glowny]) => h("button", { class: "btn" + (glowny ? " primary" : " quiet"),
          onclick: () => { d.hidden = true; ok(k); } }, etykieta)));
      d.hidden = false;
    });
  }

  // Niezapisane zmiany przed przejściem dalej: true = można iść dalej.
  async function rozstrzygnij(tekst) {
    if (!zmienione()) return true;
    const k = await pytaj(tekst, [["zapisz", T.zapisz, true], ["porzuc", T.porzuc], ["anuluj", T.anuluj]]);
    if (k === "zapisz") { await zapisz(); return true; }
    return k === "porzuc";
  }

  async function otworz(id) {
    await pokaz();
    if (!(await rozstrzygnij(T.porzucic_zmiany))) return;
    const a = await api("/api/artefakty/" + id);
    ed.changeMode("wysiwyg", true);
    biezacy = a; ed.setMarkdown(a.tresc || ""); ustawZapisany();
    panel._nazwa.textContent = a.nazwa.replace(/\.md$/, ""); panel._stan.textContent = "";
    panel._zmien.hidden = a.login !== window.LOGIN;
    odswiezListe();
  }

  async function zmienNazwe() {
    if (!biezacy?.id) return;
    const stara = biezacy.nazwa.replace(/\.md$/, "");
    const n = prompt(T.nowa_nazwa, stara);
    if (n === null || !n.trim() || n.trim() === stara) return;
    try {
      const a = await api(`/api/artefakty/${biezacy.id}/nazwa`, { method: "POST", body: JSON.stringify({ nazwa: n.trim() }) });
      biezacy.nazwa = a.nazwa; panel._nazwa.textContent = a.nazwa.replace(/\.md$/, "");
      toast(T.zmieniono_nazwe); odswiezListe();
      document.dispatchEvent(new Event("notatki:zapisane"));
    } catch (e) { toast(e.message); }
  }

  async function nowa() {
    await pokaz();
    const nazwa = prompt(T.nazwa_pliku, "notatka");
    if (nazwa === null) return;
    const a = await api("/api/artefakty", { method: "POST", body: JSON.stringify({ nazwa, tresc: "",
      ujecie: parseInt(localStorage.getItem("ujecie") || "0") || null }) });
    await otworz(a.id);
    document.dispatchEvent(new Event("notatki:zapisane"));
  }

  // Tekst spoza artefaktów (np. kopia promptu systemowego): surowy markdown, zapis przez podaną funkcję.
  async function edytujTekst({ tytul, tresc, zapisz: fn }) {
    await pokaz();
    if (!(await rozstrzygnij(T.porzucic_zmiany))) return;
    ed.changeMode("markdown", true);
    biezacy = { zewn: fn }; ed.setMarkdown(tresc || ""); ustawZapisany();
    panel._nazwa.textContent = tytul; panel._stan.textContent = ""; panel._zmien.hidden = true;
    odswiezListe();
  }

  async function zapisz() {
    if (!biezacy || !ed) return;
    const tresc = ed.getMarkdown();
    if (biezacy.zewn) { await biezacy.zewn(tresc); zapisany = tresc; panel._stan.textContent = ""; toast(T.zapisano); return; }
    await api("/api/artefakty/" + biezacy.id, { method: "POST", body: JSON.stringify({ tresc }) });
    zapisany = tresc; panel._stan.textContent = ""; toast(T.zapisano);
    document.dispatchEvent(new Event("notatki:zapisane"));
  }

  function wstaw() {
    const cel = document.getElementById("prompt") || document.getElementById("tresc");
    if (!cel || !ed) return;
    let t = (ed.getSelectedText() || "").trim() || ed.getMarkdown();
    if (cel.id === "prompt") t = jsonZTekstu(t) ?? czystyPrompt(t);     // edytor notatek psuje JSON znakami „\”
    const a = cel.selectionStart ?? cel.value.length, b = cel.selectionEnd ?? a;
    cel.value = cel.value.slice(0, a) + t + cel.value.slice(b);
    cel.dispatchEvent(new Event("input")); cel.focus();
    toast(T.wstaw_do_promptu);
  }

  // Agent mógł właśnie zmienić otwarty plik (np. biblię) — wczytaj świeżą wersję, jeśli nie ma niezapisanych zmian.
  async function odswiezBiezacy() {
    if (!panel || !biezacy?.id || biezacy.zewn) return;
    if (zmienione()) { panel._stan.textContent = T.plik_zmieniony; return; }
    const a = await api("/api/artefakty/" + biezacy.id);
    if ((a.tresc || "") !== ed.getMarkdown()) { biezacy = a; ed.setMarkdown(a.tresc || ""); ustawZapisany(); panel._stan.textContent = ""; }
  }

  async function zamknij() {
    if (!panel) return;
    if (zmienione()) {
      const k = await pytaj(T.zamknac_bez_zapisu, [["zapisz", T.zapisz_i_zamknij, true], ["porzuc", T.zamknij_bez_zapisu], ["anuluj", T.anuluj]]);
      if (k === "anuluj") return;
      if (k === "zapisz") await zapisz();
      else { ed.setMarkdown(zapisany); }            // porzucone zmiany nie wracają przy następnym otwarciu
    }
    panel._decyzja.hidden = true;
    panel.classList.remove("on");
  }

  const otwarty = () => Boolean(panel && panel.classList.contains("on"));
  return { pokaz, otworz, nowa, zamknij, edytujTekst, odswiezBiezacy, otwarty };
})();

// link „notatki” w nagłówku: otwiera i zamyka
document.querySelectorAll("[data-notatki]").forEach((a) => a.addEventListener("click", (e) => {
  e.preventDefault(); notatki.otwarty() ? notatki.zamknij() : notatki.pokaz();
}));
