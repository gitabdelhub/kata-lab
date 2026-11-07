/* Kata Lab : le site (parcours guidé, bibliothèque, espace d'examen, progression). */
(function () {
  "use strict";
  const $ = (s, el) => (el || document).querySelector(s);
  const $$ = (s, el) => Array.from((el || document).querySelectorAll(s));
  const E = window.KataEngines;
  const esc = (s) => String(s === undefined || s === null ? "" : s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const dec = (b) => JSON.parse(new TextDecoder().decode(Uint8Array.from(atob(b), (c) => c.charCodeAt(0))));
  const LANG = { pyspark: "PySpark", sql: "PostgreSQL", python: "Python 3" };
  const SHORT = { pyspark: "PySpark", sql: "SQL", python: "Python" };
  const FILE = { pyspark: "solution.py", sql: "query.sql", python: "solution.py" };
  const INTERVALS = [2, 5, 12, 30];

  /* ============================================================ stockage */
  const LS = "kata.v1", LSA = "kata.attempt";
  const load = (k, d) => { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (_) { return d; } };
  const save = (k, v) => { try { if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, JSON.stringify(v)); } catch (_) {} };
  const P0 = () => ({ v: 1, done: {}, sessCount: 0, cur: null, cards: {}, tasks: {}, exams: {}, review: [], errors: {}, notes: {}, days: [], ump: false, dur: 70, live: [], v2: 1, solSeen: {}, day: null, dayN: 1, tnotes: {} });
  let P = Object.assign(P0(), load(LS, {}));
  // v2 (6 nov 2026) : séance du jour simple, plus de parcours guidé ni d'UMPIRE imposé
  if (!P.v2) { P.v2 = 1; P.ump = false; P.cur = null; P.solSeen = P.solSeen || {}; }
  if (!P.solSeen) P.solSeen = {};
  const persist = () => save(LS, P);

  const pad = (n) => String(n).padStart(2, "0");
  const today = () => { const d = new Date(); return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()); };
  const frDate = (d) => (d || new Date()).toLocaleDateString("fr-FR", { weekday: "long", day: "numeric", month: "long", year: "numeric" });
  function markDay() { const t = today(); if (!P.days.includes(t)) { P.days.push(t); P.days = P.days.slice(-400); persist(); } }
  function streak() {
    const set = new Set(P.days); let n = 0; const d = new Date();
    if (!set.has(today())) d.setDate(d.getDate() - 1);
    for (;;) { const k = d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()); if (!set.has(k)) break; n++; d.setDate(d.getDate() - 1); }
    return n;
  }

  let CAT = null;
  const TASKS = {};
  async function getTask(id) {
    if (!TASKS[id]) {
      const r = await fetch("content/tasks/" + id + ".json", { cache: "no-cache" });
      if (!r.ok) throw new Error("task introuvable : " + id);
      TASKS[id] = await r.json();
    }
    return TASKS[id];
  }
  const hiddenOf = (t) => (t._hidden || (t._hidden = dec(t.hidden)));
  const solutionOf = (t) => dec(t.solution);
  // Corrigé : version simple (boucles, dict) d'abord quand elle existe, puis la version courte
  function corrigeHtml(t) {
    if (!t.simple) return codeBlock(solutionOf(t));
    return `<h4 class="solh">Version simple : celle à savoir écrire au test</h4>${codeBlock(dec(t.simple))}
      <details class="solalt"><summary>Version courte (bonus) : même résultat, avec des outils de Python à découvrir plus tard</summary>${codeBlock(solutionOf(t))}</details>`;
  }
  const reflex = (id) => CAT.reflexes.find((r) => r.id === id);
  const exam = (id) => CAT.exams.find((e) => e.id === id);

  /* ============================================================ parcours */
  function phaseDone(p) { return p.sessions.length > 0 && p.sessions.every((s) => P.done[s.id]); }
  // Tout est ouvert : le parcours conseille un ordre mais ne bloque rien (demande d'AB).
  function phaseOpen() { return true; }
  function findSession(id) {
    for (let i = 0; i < CAT.phases.length; i++) {
      const j = CAT.phases[i].sessions.findIndex((s) => s.id === id);
      if (j >= 0) return Object.assign({ pi: i, si: j, phase: CAT.phases[i] }, CAT.phases[i].sessions[j]);
    }
    return null;
  }
  function nextSession() {
    for (let i = 0; i < CAT.phases.length; i++) {
      if (!phaseOpen(i)) continue;
      for (const s of CAT.phases[i].sessions) if (!P.done[s.id]) return findSession(s.id);
    }
    return null;
  }
  function currentSession() { return P.cur ? findSession(P.cur.id) : nextSession(); }
  function stepHash(st) {
    return st.type === "review" ? "revision" : st.type === "learn" ? "reflexe-" + st.reflex : st.type === "dsa" ? "dsa-" + st.dsa : st.type === "read" ? "lire-" + st.read : st.type === "exo" ? "exo-" + st.task : st.type === "exam" ? "exam-" + st.exam : "analyse-" + st.exam;
  }
  function goHash(h) { if (location.hash === "#" + h) route(); else location.hash = h; }
  function startSession() {
    const s = currentSession();
    if (!s) { goHash("accueil"); return; }
    if (!P.cur) { P.cur = { id: s.id, step: 0 }; persist(); }
    goHash(stepHash(s.steps[P.cur.step]));
  }
  function introduceCards(rid) {
    const r = reflex(rid); if (!r) return;
    r.cards.forEach((_, j) => { const id = rid + "-" + j; if (!P.cards[id]) P.cards[id] = { due: P.sessCount + 1, lvl: 0 }; });
  }
  function sessNext() {
    if (!P.cur) return;
    const s = findSession(P.cur.id);
    const st = s.steps[P.cur.step];
    if (st.type === "learn") introduceCards(st.reflex);
    if (st.type === "dsa") { const d = dsaP(st.dsa); if (d) d.cards.forEach((_, j) => { const k = d.id + "-" + j; if (!P.cards[k]) P.cards[k] = { due: P.sessCount + 1, lvl: 0 }; }); }
    if (P.cur.step < s.steps.length - 1) {
      P.cur.step++; persist();
      goHash(stepHash(s.steps[P.cur.step]));
    } else {
      P.done[s.id] = { at: today() };
      P.sessCount++;
      P.cur = null; persist();
      flash = "Séance terminée. Bravo, c'est comme ça qu'on progresse : une séance après l'autre.";
      goHash("accueil");
    }
  }
  let flash = "";
  function inSessionStep(hash) {
    if (!P.cur) return false;
    const s = findSession(P.cur.id);
    return s && stepHash(s.steps[P.cur.step]) === hash;
  }
  function nextLabel() {
    const s = findSession(P.cur.id);
    if (P.cur.step >= s.steps.length - 1) return "Terminer la séance ✓";
    return "Étape suivante : " + s.steps[P.cur.step + 1].title;
  }

  /* ============================================================ cartes et révisions */
  function seedMethodCards() {
    CAT.method_cards.forEach((_, j) => { const id = "m-" + j; if (!P.cards[id]) P.cards[id] = { due: 0, lvl: 0 }; });
  }
  function cardText(id) {
    if (id.startsWith("m-")) return CAT.method_cards[+id.slice(2)];
    if (id.startsWith("dsa")) { const [pid, j] = id.split("-"); const d = dsaP(pid); return d ? d.cards[+j] : null; }
    const [rid, j] = id.split("-");
    const r = reflex(rid); return r ? r.cards[+j] : null;
  }
  function dueCards(n) {
    return Object.entries(P.cards).filter(([id, c]) => c.due <= P.sessCount && cardText(id)).sort((a, b) => a[1].due - b[1].due || a[1].lvl - b[1].lvl).slice(0, n).map(([id]) => id);
  }
  function gradeCard(id, knew) {
    const c = P.cards[id];
    if (knew) { c.lvl = Math.min(c.lvl + 1, INTERVALS.length - 1); c.due = P.sessCount + INTERVALS[c.lvl - 1 < 0 ? 0 : c.lvl - 1]; }
    else { c.lvl = 0; c.due = P.sessCount + 1; }
    persist();
  }
  function dueReviews() { return P.review.filter((r) => r.due <= P.sessCount); }
  // Exo fini hors du temps prévu (même réussi) : il revient en révision espacée
  function slowReview(tid) {
    const item = P.review.find((r) => r.task === tid);
    if (item) { item.stage = 0; item.due = P.sessCount + INTERVALS[0]; }
    else P.review.push({ task: tid, stage: 0, due: P.sessCount + INTERVALS[0] });
    persist();
  }
  // Fiche perso de 3 lignes par exo (déclencheur, outil, piège), écrite par AB
  const NOTE_F = [["trig", "Déclencheur", "Ex. « part du groupe » dans la consigne"], ["tool", "Outil", "Ex. SUM(SUM(x)) OVER (PARTITION BY groupe)"], ["trap", "Piège", "Ex. 100.0 et pas 100 (division entière)"]];
  const myNote = (tid) => ((P.tnotes || {})[tid]) || null;
  const hasNote = (tid) => { const n = myNote(tid); return !!(n && NOTE_F.some(([k]) => (n[k] || "").trim())); };
  function noteForm(tid) {
    const n = myNote(tid) || {};
    return NOTE_F.map(([k, lab, ph]) => `<label class="nf"><span>${lab}</span><textarea rows="2" data-note="${k}" data-tid="${tid}" placeholder="${esc(ph)}">${esc(n[k] || "")}</textarea></label>`).join("") + `<small class="nsaved">Enregistrée toute seule, dans ce navigateur.</small>`;
  }
  function bindNote(root) {
    $$("[data-note]", root).forEach((ta) => (ta.oninput = () => {
      P.tnotes = P.tnotes || {};
      const n = P.tnotes[ta.dataset.tid] || (P.tnotes[ta.dataset.tid] = {});
      n[ta.dataset.note] = ta.value; n.at = today(); persist();
    }));
  }
  function recordTask(tid, score, inReview) {
    const t = P.tasks[tid] || (P.tasks[tid] = { best: 0, last: 0, n: 0, hist: [] });
    t.best = Math.max(t.best, score); t.last = score; t.n++; t.hist.push({ at: today(), score }); t.hist = t.hist.slice(-20);
    const item = P.review.find((r) => r.task === tid);
    if (score < 80) {
      if (item) { item.stage = 0; item.due = P.sessCount + INTERVALS[0]; }
      else P.review.push({ task: tid, stage: 0, due: P.sessCount + INTERVALS[0] });
    } else if (item && item.due <= P.sessCount) {
      item.stage++;
      if (item.stage >= 3) P.review = P.review.filter((r) => r !== item);
      else item.due = P.sessCount + INTERVALS[item.stage];
    }
    persist();
  }
  function recordErrors(tags) { tags.forEach((g) => (P.errors[g] = (P.errors[g] || 0) + 1)); persist(); }

  /* ============================================================ rendu : outils */
  const view = () => $("#view");
  function band(title, tabsHtml, extra) {
    return `<div class="pband"><div class="wrap">${extra || ""}<h1 class="ptitle">${title}</h1>${tabsHtml || '<div style="height:18px"></div>'}</div></div>`;
  }
  const bib = (on) => on === "examens" || on === "exos" ? "" : `<div class="biblinks"><a href="#fiches">Fiches</a><a href="#apprendre" class="${on === "apprendre" ? "on" : ""}">Réflexes</a><a href="#dsa" class="${on === "dsa" ? "on" : ""}">DSA</a><a href="#lire" class="${on === "lire" ? "on" : ""}">Lire la consigne</a><a href="#live">Live coding</a><a href="#progression">Progression</a></div>`;
  function fmtVal(v, top) {
    if (v === null || v === undefined) return "null";
    if (typeof v === "string") return top === "cell" ? v : JSON.stringify(v);
    if (typeof v === "number" || typeof v === "boolean") return String(v);
    if (Array.isArray(v)) return "[" + v.map((x) => fmtVal(x)).join(", ") + "]";
    return "{" + Object.entries(v).map(([k, x]) => JSON.stringify(k) + ": " + fmtVal(x)).join(", ") + "}";
  }
  function codeBlock(code) { return `<pre class="code">${esc(code)}</pre>`; }
  function minitimer(id, sec) { return `<span class="minitimer"><span id="${id}T">${pad(Math.floor(sec / 60))}:${pad(sec % 60)}</span><button id="${id}B" data-s="${sec}">Démarrer</button></span>`; }
  function bindMinitimer(id, onEnd) {
    const b = $("#" + id + "B"); if (!b) return;
    let end = null, tk = null; const sec = +b.dataset.s;
    const show = (ms) => { const t = Math.max(0, Math.ceil(ms / 1000)); $("#" + id + "T").textContent = pad(Math.floor(t / 60)) + ":" + pad(t % 60); };
    b.onclick = () => {
      if (tk) { clearInterval(tk); tk = null; show(sec * 1000); b.textContent = "Démarrer"; return; }
      end = Date.now() + sec * 1000; b.textContent = "Arrêter";
      tk = setInterval(() => { const l = end - Date.now(); show(l); if (l <= 0) { clearInterval(tk); tk = null; b.textContent = "Recommencer"; if (onEnd) onEnd(); } }, 250);
      timers.push(() => clearInterval(tk));
    };
  }
  let timers = [];
  function clearTimers() { timers.forEach((f) => f()); timers = []; }

  /* ============================================================ alertes */
  function renderGuide() {
    if (!P.guideSeen) { P.guideSeen = true; persist(); renderAlerts(); }
    const sec = (n, t, body) => `<div class="card guide-sec"><span class="eyebrow">${n}</span><h3 style="margin:4px 0 10px">${t}</h3>${body}</div>`;
    view().innerHTML = `<section class="ws on">${band("Mode d'emploi", `<p class="lead" style="padding-bottom:28px">Kata Lab en 2 minutes : une séance par jour, et trois espaces libres à côté.</p>`)}
      <div class="wrap"><div class="sect guide">
        ${sec("1", "Chaque jour : la séance sur l'Accueil", `<p>L'Accueil te donne 4 exos : un SQL, un PySpark, un Python et une révision. Tu ne vois ni leur titre ni leur langage avant de les ouvrir, et leur ordre change à chaque séance : pas de choix à la carte. Un exo est coché quand tu as 80/100 ou plus, ou quand tu as regardé le corrigé (il revient alors plus tard en révision). Quand tout est coché, la séance suivante apparaît, peu importe le jour. Toutes les 7 séances, la séance est un examen complet.</p><div class="btnrow"><a class="pill" href="#accueil">Ma séance</a></div>`)}
        ${sec("2", "Pratiquer", `<p>Tous les exos dans une liste, dans l'ordre conseillé. Filtre par langage, thème ou statut (À faire, Réussi, À refaire), ou cherche un mot comme « Window ».</p>`)}
        ${sec("3", "Examens", `<p>${CAT.exams.filter((e) => !e.mini).length} examens au format du test : 4 tasks, 70 minutes, chaque task notée sur 100, avec PySpark, SQL et Python dans chacun. Le chrono est strict et aucun temps n'est conseillé par task : tu gères ton temps. Après l'examen, l'analyse guidée te montre le corrigé de chaque task.</p>`)}
        ${sec("4", "Fiches", `<p>Le résumé de SQL, PySpark et Python : syntaxe, exemple court, piège, et les exos liés. Dans chaque exo, un lien ouvre la bonne partie de la fiche dans un nouvel onglet.</p>`)}
        ${sec("5", "L'écran d'exo", `<ul><li>L'encadré bleu <b>Comment faire, exactement</b> dit en français où écrire, quoi renvoyer et ce que tu dois voir.</li><li><b>RUN TESTS</b> lance les tests visibles. <b>SUBMIT</b> note ta task sur 100 : soumets tôt, puis améliore.</li><li>Les indices sont sous l'énoncé. Le corrigé s'ouvre après 2 essais (MORE, Voir le corrigé).</li><li>Coller un texte venu d'ailleurs est bloqué, comme au vrai test. Copier-coller ton propre code marche.</li><li>Chaque zone s'agrandit en tirant sa barre ; un double-clic sur la barre remet la taille d'origine.</li><li>Un exo fini plus de 2 minutes après le temps prévu (10 % pour les longs) revient en révision, même réussi. Sur l'écran du résultat, écris ta fiche de 3 lignes : elle reste dans Fiches, Mes fiches d'exos.</li></ul>`)}
        ${sec("6", "PySpark : une clé, une seule fois", `<p>SQL et Python marchent tout de suite. Pour PySpark, colle ta clé GitHub une fois dans <a href="#connexion">Connexion</a>. Spark démarre en 1 à 2 minutes au premier exo, puis s'éteint seul après 30 minutes sans utilisation.</p>`)}
        ${sec("7", "Sauvegarder", `<p>Ta progression reste dans ce navigateur : utilise toujours le même, et exporte-la de temps en temps dans <a href="#progression">Progression et sauvegarde</a>.</p>`)}
      </div></div></section>`;
  }
  function renderAlerts() {
    const a = [];
    if (!P.guideSeen) a.push(`<div class="alert">Première visite ? Lis le <a href="#guide">Mode d'emploi</a> (3 minutes) : il explique comment utiliser le site.</div>`);
    const key = E.Key.get(), exp = E.Key.expiry();
    if (!key) a.push(`<div class="alert">Pour les exos PySpark, colle ta clé GitHub une seule fois dans <a href="#connexion">Connexion</a>. SQL et Python marchent déjà sans clé.</div>`);
    else if (exp) {
      const days = Math.round((new Date(exp + "T00:00:00") - new Date(today() + "T00:00:00")) / 86400000);
      if (days < 0) a.push(`<div class="alert ko">Ta clé GitHub a expiré le ${esc(exp)}. PySpark ne peut plus démarrer. <a href="#connexion">Créer une nouvelle clé</a> (5 minutes).</div>`);
      else if (days <= 21) a.push(`<div class="alert">Ta clé GitHub expire dans ${days} jour${days > 1 ? "s" : ""} (${esc(exp)}). <a href="#connexion">Crée la nouvelle clé maintenant</a> pour ne pas être bloqué.</div>`);
    }
    $("#alerts").innerHTML = a.join("");
  }

  /* ============================================================ accueil */
  function renderParcours() {
    const s = currentSession();
    const allDone = !s;
    const p1 = CAT.phases[0];
    let left = "", card = "";
    if (s) {
      const steps = s.steps.map((st, i) => {
        const cls = P.cur && P.cur.id === s.id ? (i < P.cur.step ? "done" : i === P.cur.step ? "cur" : "") : "";
        let sub = st.sub;
        if (st.type === "learn") sub = "Exemple guidé, puis mini-exo de mémoire";
        if (st.type === "exo") sub = esc(TITLE[st.task] || "") + " · note sur 100";
        return `<li class="${cls}"><span class="num">${i + 1}</span><div><b>${esc(st.title)}</b><span>${sub}</span></div><em>${st.min} min</em></li>`;
      }).join("");
      const total = s.steps.reduce((a, b) => a + b.min, 0);
      left = `<span class="eyebrow">${esc(s.phase.name)} · séance ${s.si + 1} sur ${s.phase.sessions.length}</span>
        <h1 class="ptitle" style="margin-bottom:14px">Bonjour AB, voici ta séance.</h1>
        <p class="lead">${esc(frDate())} · ${total} min. Fais les étapes dans l'ordre : le site te guide de l'une à l'autre.</p>
        ${flash ? `<p class="sc-done" style="margin-top:16px">✓ ${esc(flash)}</p>` : ""}`;
      card = `<div class="sesscard"><div class="sc-head"><b>Séance ${s.si + 1} · ${esc(s.title)}</b><span class="muted">${total} min</span></div>
        <ol class="steps3">${steps}</ol>
        <button class="pill big" id="startSess">${P.cur ? "Reprendre l'étape " + (P.cur.step + 1) : "Commencer la séance"}</button></div>`;
    } else {
      left = `<span class="eyebrow">Parcours terminé</span><h1 class="ptitle" style="margin-bottom:14px">Bravo AB, tout le parcours est fait.</h1>
        <p class="lead">${esc(frDate())}. Continue avec 1 examen complet par semaine en mode strict, et refais les exos que tu as ratés.</p>`;
      card = `<div class="sesscard"><div class="sc-head"><b>Pour rester prêt</b></div><p class="muted" style="margin:0">1 examen complet par semaine, en mode strict, puis l'analyse guidée.</p><a class="pill big" href="#examens">Choisir un examen</a></div>`;
    }
    flash = "";
    const phases = CAT.phases.map((p, i) => {
      const open = phaseOpen(i), done = p.sessions.filter((x) => P.done[x.id]).length, n = p.sessions.length;
      const cur = s && s.phase.id === p.id;
      let units = "";
      if (p.sessions.length) {
        units = `<div class="units">` + p.sessions.map((x, j) => {
          const isNow = s && s.id === x.id;
          const st = P.done[x.id] ? "done" : isNow ? "now" : "todo";
          return `<button class="unit ${st}" data-sess="${x.id}"><span class="u-st">${st === "done" ? "✓" : st === "now" ? "●" : "○"}</span><b>${esc(x.title)}</b><span>${isNow ? "Conseillée" : "Séance " + (j + 1)}</span></button>`;
        }).join("") + `</div>`;
      }
      const prog = n ? `<span class="ph-prog">${done} / ${n}</span>` : `<span class="ph-prog"></span>`;
      const note = !n && open ? p.note + " Elle arrive avec la prochaine mise à jour du site." : p.note;
      return `<div class="phase ${cur ? "cur" : open && n ? "" : "lock"}"><div class="ph-head"><span class="ph-dot"></span><div><b>${esc(p.name)}</b><span>${esc(p.dates)}</span></div>${prog}</div>
        ${n ? `<div class="ph-track"><i style="width:${Math.round((100 * done) / n)}%"></i></div>` : ""}${units || `<p class="ph-note">${esc(note)}</p>`}</div>`;
    }).join("");
    const nb = Object.values(P.exams).reduce((a, e) => a + (e.hist || []).filter((h) => !h.mini).length, 0);
    const rv = dueReviews().length;
    view().innerHTML = `<section class="ws on"><div class="pband"><div class="wrap"><div class="today"><div class="today-l">${left}</div>${card}</div></div></div>
      <div class="wrap"><div class="sect">
        ${rv ? `<div class="alert" style="margin:0 0 18px">${rv} exo${rv > 1 ? "s" : ""} raté${rv > 1 ? "s" : ""} à refaire : ils sont dans la révision éclair de ta prochaine séance.</div>` : ""}
        <h2>Ton parcours jusqu'au jour J</h2>
        <p class="sub"><a href="#guide">Mode d'emploi du site</a> · Tout est ouvert : clique sur n'importe quelle séance pour la faire maintenant. La séance conseillée est mise en avant, les dates ne sont que des repères. Les exos ratés reviennent seuls 2, 5 puis 12 séances plus tard.</p>
        <div class="phases">${phases}
          <div class="phase goal"><div class="ph-head"><span class="ph-dot"></span><div><b>Fin avril · Tu repostules</b><span>Avec des examens complets passés au chrono (${nb} pour l'instant)</span></div><span class="ph-prog">🎯</span></div></div>
        </div></div></div></section>`;
    const b = $("#startSess"); if (b) b.onclick = startSession;
    $$("[data-sess]").forEach((u) => (u.onclick = () => {
      const id = u.dataset.sess;
      if (P.cur && P.cur.id === id) return startSession();
      if (P.cur && P.cur.step > 0 && !confirm("Tu as une séance en cours. Passer à celle-ci ? Tu pourras reprendre l'autre plus tard.")) return;
      P.cur = { id, step: 0 }; persist(); startSession();
    }));
  }
  let TITLE = {};

  /* ============================================================ v2 : ordre des exos, statuts, thèmes */
  const FI = () => window.KATA_FICHES || {};
  let EXAM_OF = {}, RANK = {}, QUEUE = {};
  const LORD = { sql: 0, pyspark: 1, python: 2 };
  function buildOrder() {
    EXAM_OF = {};
    CAT.exams.forEach((e, i) => e.tasks.forEach((t) => { if (!EXAM_OF[t]) EXAM_OF[t] = { id: e.id, i, mini: !!e.mini }; }));
    const g = (id) => (/^p1m/.test(id) ? 0 : /^p1x/.test(id) ? 1 : /^p2x/.test(id) ? 2 : /^bs/.test(id) ? 3 : /^e\d/.test(id) ? 4 : /^(bp|d\d)/.test(id) ? 5 : 6);
    const num = (id) => parseInt(id.replace(/\D/g, ""), 10) || 0;
    ["sql", "pyspark", "python"].forEach((l) => {
      const s = Object.keys(CAT.tasks).filter((id) => !EXAM_OF[id] && CAT.tasks[id].lang === l).sort((a, b) => g(a) - g(b) || num(a) - num(b));
      const bp = s.filter((x) => /^bp/.test(x)), d = s.filter((x) => /^d\d/.test(x)), rest = s.filter((x) => !/^(bp|d\d)/.test(x));
      const mix = [];
      for (let i = 0; i < Math.max(bp.length, d.length); i++) { if (d[i]) mix.push(d[i]); if (bp[i]) mix.push(bp[i]); }
      QUEUE[l] = rest.concat(mix);
      const inExam = Object.keys(CAT.tasks).filter((id) => EXAM_OF[id] && CAT.tasks[id].lang === l).sort((a, b) => EXAM_OF[a].i - EXAM_OF[b].i || a.localeCompare(b));
      QUEUE[l].concat(inExam).forEach((id, i) => (RANK[id] = i));
    });
  }
  const THEMES = [
    ["Fenêtres", /window|lag|lead|row_number|rank|cumul|gaps|îlot|session|over|partition by|forward fill|ignorenulls/],
    ["Fichiers", /dossier|fichier|json|csv|partitions hive|parsing|parser|largeur fixe|regex|logs|edi|grille|posexplode|split/],
    ["Jointures", /join|jointure|as-of|anti/],
    ["Agrégation", /groupby|group by|agr|pivot|count|having|sum|percentile/],
    ["Nettoyage", /nettoy|null|try_cast|trim|doublon|dédoublon|normalis|format/],
    ["Dates", /date|jour|semaine|fuseau|heure|mois|cohorte/],
    ["Simulation", /simulation|deque|file|intervalle|tri|dict/],
  ];
  function themeOf(id) {
    if (/^d\d/.test(id)) return "Algorithmes";
    const s = (CAT.tasks[id].tags || []).join(" ").toLowerCase();
    for (const [n, rx] of THEMES) if (rx.test(s)) return n;
    return /^e1\d/.test(id) ? "Consigne longue" : "Bases";
  }
  function statusOf(id) {
    const t = P.tasks[id];
    if (t && t.best >= 80) return "ok";
    if ((t && t.n) || P.review.some((r) => r.task === id) || (P.solSeen || {})[id]) return "redo";
    return "todo";
  }
  const ST_LAB = { ok: "Réussi", redo: "À refaire", todo: "À faire" };
  function ficheSecFor(id) {
    const t = CAT.tasks[id]; if (!t) return null;
    const f = FI()[t.lang]; if (!f) return null;
    const s = (t.tags || []).join(" ").toLowerCase();
    const sec = f.secs.find((x) => x.match && new RegExp(x.match).test(s)) || f.secs[0];
    return { lang: t.lang, id: sec.id, t: sec.t };
  }
  function linkedTasks(lang, rx, n) {
    const re = new RegExp(rx);
    return Object.keys(CAT.tasks).filter((id) => CAT.tasks[id].lang === lang && !EXAM_OF[id] && re.test((CAT.tasks[id].tags || []).join(" ").toLowerCase())).sort((a, b) => RANK[a] - RANK[b]).slice(0, n || 4);
  }
  const solOK = (id) => ((P.tasks[id] || {}).n || 0) >= 2;

  /* ============================================================ v2 : séance du jour */
  const isDoneTask = (id) => (P.tasks[id] && P.tasks[id].best >= 80) || !!(P.solSeen || {})[id];
  // Pour la séance : un exo raté mais fini, avec au moins une ligne dans sa fiche, est terminé.
  // Il revient plus tard en révision. (La fiche n'apparaît qu'à la fin d'un exo.)
  const isClosedTask = (id) => isDoneTask(id) || hasNote(id);
  function nextOf(lang, taken) { return QUEUE[lang].find((id) => !isClosedTask(id) && !taken.includes(id)) || null; }
  function nextExam() { return CAT.exams.find((e) => !((P.exams[e.id] || {}).hist || []).length) || null; }
  function makeDay(n) {
    const at = Date.now();
    const e = nextExam();
    if (n % 7 === 0 && e) return { n, at, exam: e.id, h0: 0, items: [] };
    const items = [], taken = [];
    const FB = { sql: ["pyspark", "python"], pyspark: ["python", "sql"], python: ["pyspark", "sql"] };
    for (const want of ["sql", "pyspark", "python"]) {
      let id = nextOf(want, taken);
      for (const f of FB[want]) if (!id) id = nextOf(f, taken);
      if (id) { taken.push(id); items.push({ id, want }); }
    }
    for (let i = items.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [items[i], items[j]] = [items[j], items[i]]; }
    if (!items.length) return e ? { n, at, exam: e.id, h0: 0, items: [] } : { n, at, end: true, items: [] };
    const due = P.review.filter((r) => r.due <= P.sessCount && !taken.includes(r.task) && CAT.tasks[r.task]).sort((a, b) => a.due - b.due)[0];
    let rev;
    if (due) rev = { kind: "redo", id: due.task, n0: (P.tasks[due.task] || {}).n || 0 };
    else {
      const base = (items.find((i) => CAT.tasks[i.id].lang === "pyspark") || items[0]).id;
      const s = ficheSecFor(base);
      rev = s ? { kind: "fiche", lang: s.lang, sec: s.id, read: false } : null;
    }
    return { n, at, items, rev, shuf: 1 };
  }
  function dayStepDone(st) {
    if (st.kind === "exo") return isClosedTask(st.id);
    if (st.kind === "redo") { const t = P.tasks[st.id] || {}; return ((t.n || 0) > st.n0 && t.last >= 80) || ((P.solSeen || {})[st.id] || 0) > P.day.at || (((P.ended || {})[st.id] || 0) > P.day.at && hasNote(st.id)); }
    if (st.kind === "fiche") return !!P.day.rev.read;
    if (st.kind === "exam") return (((P.exams[st.id] || {}).hist || []).filter((h) => (h.ts || 0) >= P.day.at)).length > 0;
    return false;
  }
  function daySteps() {
    const d = P.day;
    if (d.exam) return [{ kind: "exam", id: d.exam }];
    const s = d.items.map((i) => ({ kind: "exo", id: i.id, want: i.want }));
    // Le rappel de cours passe en premier : on le lit avant d'attaquer les exos
    if (d.rev) { if (d.rev.kind === "redo") s.push({ kind: "redo", id: d.rev.id, n0: d.rev.n0 }); else s.unshift({ kind: "fiche", lang: d.rev.lang, sec: d.rev.sec }); }
    return s;
  }
  function ensureDay() {
    if (!P.dayN) P.dayN = 1;
    if (!P.day) { P.day = makeDay(P.dayN); persist(); }
    if (P.day.items && P.day.items.length > 1 && !P.day.shuf) {
      const it = P.day.items;
      for (let i = it.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [it[i], it[j]] = [it[j], it[i]]; }
      P.day.shuf = 1; persist();
    }
    return P.day;
  }
  function advanceDay() {
    P.sessCount++; P.dayN++;
    P.day = makeDay(P.dayN); persist();
  }
  function inDay(mode, id) {
    const d = P.day; if (!d) return false;
    if (mode === "exam") return d.exam === id;
    return d.items.some((i) => i.id === id) || !!(d.rev && d.rev.id === id);
  }
  const backHash = () => (inDay(W.mode, W.id) ? "accueil" : W.mode === "exo" ? "pratiquer" : "examens");

  function renderHome() {
    const d = ensureDay();
    let card;
    if (d.end) {
      card = `<div class="day"><div class="dayhead"><div><span class="eyebrow">Séance ${d.n}</span><h2>Tu as fini tous les exos et tous les examens.</h2></div></div><p class="muted" style="margin:0">Pour rester prêt : refais un examen par semaine et les exos marqués « À refaire » dans Pratiquer.</p><div class="btnrow"><a class="pill sm" href="#examens">Examens</a><a class="pill sm ghost" href="#pratiquer">Pratiquer</a></div></div>`;
    } else {
      const steps = daySteps();
      const done = steps.filter(dayStepDone).length;
      let exoN = 0;
      const row = (st) => {
        const ok = dayStepDone(st);
        if (st.kind !== "exam" && st.kind !== "fiche") exoN++;
        let lab, sub, href, btn;
        if (st.kind === "exam") {
          const e = exam(st.id);
          lab = "Examen"; sub = `${e.tasks.length} tasks · ${e.mini ? e.minutes : P.dur || 70} min · chrono strict`; href = "#exam-" + st.id; btn = attemptFor("exam", st.id) ? "Reprendre" : "Commencer l'examen";
        } else if (st.kind === "fiche") {
          const sec = ((FI()[st.lang] || {}).secs || []).find((x) => x.id === st.sec);
          lab = "Rappel de cours"; sub = ({ pyspark: "PySpark", sql: "SQL", python: "Python" }[st.lang] || st.lang) + (sec ? " · " + sec.t : ""); href = "#fiche-" + st.lang + "-" + st.sec; btn = "Lire";
        } else {
          const t = CAT.tasks[st.id];
          lab = "Exo " + exoN;
          sub = "";
          href = "#exo-" + st.id; btn = attemptFor("exo", st.id) ? "Reprendre" : st.kind === "redo" ? "Refaire" : "Ouvrir l'exo";
        }
        return `<div class="dstep ${ok ? "done" : ""}"><span class="ck">${ok ? "✓" : st.kind === "exam" ? "E" : st.kind === "fiche" ? "📖" : exoN}</span><div class="t"><b>${lab}</b>${sub ? `<small>${esc(sub)}</small>` : ""}</div><a class="pill sm ${ok ? "ghost" : ""}" href="${href}">${ok ? "Revoir" : btn}</a></div>`;
      };
      const all = done === steps.length;
      card = `<div class="day"><div class="dayhead"><div><span class="eyebrow">Séance du jour · séance ${d.n}</span><h2>${d.exam ? "Jour d'examen" : steps[0].kind === "fiche" ? "Lis le rappel, puis " + (steps.length - 1) + " exos dans l'ordre que tu veux" : steps.length + " exos, dans l'ordre que tu veux"}</h2></div><span class="muted">${done} / ${steps.length} fait${done > 1 ? "s" : ""}</span></div>
        <div class="ph-track" style="margin:0"><i style="width:${Math.round((100 * done) / steps.length)}%"></i></div>
        <div class="dsteps">${steps.map(row).join("")}</div>
        ${all ? `<div class="dunlock"><span>Séance ${d.n} terminée. Bravo, une de plus.</span><button class="pill sm" id="nextDay">Voir la séance suivante</button></div>`
          : `<p class="muted" style="margin:0;font-size:14px">${d.exam ? "L'étape est cochée quand tu termines l'examen (Finish test)." : "Un exo est coché quand tu as 80/100 ou plus. Raté ou hors du temps, il est coché aussi dès que tu écris au moins une ligne dans sa fiche (écran du résultat) ; idem si tu regardes le corrigé. Dans ces cas, il revient plus tard en révision."} La séance suivante apparaît quand tout est coché, peu importe le jour.</p>`}</div>`;
    }
    const nOk = Object.keys(CAT.tasks).filter((id) => statusOf(id) === "ok").length;
    view().innerHTML = `<section class="ws on"><div class="pband"><div class="wrap hero2"><h1 class="ptitle">Bonjour AB</h1><p class="lead">Ta séance du jour t'attend : 4 exos, tu découvres chacun en l'ouvrant. Le reste du site est libre, à côté.</p></div></div>
      <div class="wrap"><div class="sect">${card}
        <h2 class="h2s">Ou pratique librement</h2>
        <div class="doors">
          <a class="door" href="#pratiquer"><span class="ic">&lt;/&gt;</span><h3>Pratiquer</h3><p>${Object.keys(CAT.tasks).length} exos en Python, SQL et PySpark, du plus abordable au niveau du test. ${nOk} réussi${nOk > 1 ? "s" : ""}.</p><span class="go">Voir les exos →</span></a>
          <a class="door" href="#examens"><span class="ic">70′</span><h3>Examens</h3><p>${CAT.exams.length} examens au format du test : 4 tasks, 70 min, chaque task notée sur 100.</p><span class="go">Voir les examens →</span></a>
          <a class="door" href="#fiches"><span class="ic">Aa</span><h3>Fiches</h3><p>Le résumé de chaque langage : syntaxe, exemples courts, pièges, et les exos liés.</p><span class="go">Voir les fiches →</span></a>
        </div></div></div></section>`;
    const nb = $("#nextDay"); if (nb) nb.onclick = () => { advanceDay(); renderHome(); window.scrollTo(0, 0); };
  }

  /* ============================================================ v2 : Pratiquer */
  const PF = { lang: "all", theme: "", st: "", q: "", shown: 30 };
  function renderPratiquer() {
    const ids = Object.keys(CAT.tasks);
    const cnt = (l) => ids.filter((id) => l === "all" || CAT.tasks[id].lang === l).length;
    const tabs = `<div class="ptabs" role="group" aria-label="Langage">${[["all", "Tous"], ["sql", "SQL"], ["pyspark", "PySpark"], ["python", "Python"]].map(([k, n]) => `<button data-f="${k}" class="${PF.lang === k ? "on" : ""}">${n} <span class="cnt">${cnt(k)}</span></button>`).join("")}</div>`;
    const themes = [...new Set(ids.map(themeOf))].sort();
    const prog = ["sql", "pyspark", "python"].map((l) => {
      const all = ids.filter((id) => CAT.tasks[id].lang === l), ok = all.filter((id) => statusOf(id) === "ok").length;
      return `<div class="prl"><span><b>${SHORT[l]}</b><span>${ok} / ${all.length}</span></span><div class="ph-track"><i style="width:${Math.max(2, Math.round((100 * ok) / all.length))}%"></i></div></div>`;
    }).join("");
    const redo = P.review.filter((r) => CAT.tasks[r.task]).slice(0, 6).map((r) => `<li><a href="#exo-${r.task}">${esc(CAT.tasks[r.task].name)}</a> · ${SHORT[CAT.tasks[r.task].lang]}</li>`).join("");
    view().innerHTML = `<section class="ws on">${band("Pratiquer", `<p class="lead" style="margin:-4px 0 22px">Les exos sont rangés dans l'ordre conseillé : commence en haut de ton langage et descends. Clique sur une ligne pour ouvrir l'exo.</p>` + tabs)}
      <div class="wrap"><div class="sect prat">
        <div style="min-width:0">
          <div class="pfilters">
            <select id="fTheme" aria-label="Thème"><option value="">Tous les thèmes</option>${themes.map((t) => `<option ${PF.theme === t ? "selected" : ""}>${esc(t)}</option>`).join("")}</select>
            <select id="fStat" aria-label="Statut">${[["", "Tous les statuts"], ["todo", "À faire"], ["ok", "Réussi"], ["redo", "À refaire"]].map(([k, n]) => `<option value="${k}" ${PF.st === k ? "selected" : ""}>${n}</option>`).join("")}</select>
            <input id="fQ" type="search" placeholder="Chercher un exo (ex. Window, doublons)" aria-label="Chercher" value="${esc(PF.q)}">
          </div>
          <div class="ptable"><table><thead><tr><th>#</th><th>Exo</th><th>Langage</th><th>Thème</th><th>Durée</th><th>Statut</th></tr></thead><tbody id="prows"></tbody></table></div>
          <div class="pmore"><button class="pill sm ghost" id="pmore"></button></div>
        </div>
        <aside class="pside">
          <div class="card"><h3>Ta progression</h3><div class="prog3">${prog}</div><p class="muted" style="font-size:13px;margin:8px 0 0">Un exo est réussi à 80/100 ou plus.</p></div>
          <div class="card"><h3>À refaire</h3>${redo ? `<ul class="redo">${redo}</ul>` : `<p class="muted" style="margin:0;font-size:14px">Rien pour l'instant. Les exos ratés (moins de 80) arrivent ici.</p>`}</div>
          <div class="card"><h3>Bloqué sur une notion ?</h3><p class="muted" style="margin:0 0 6px;font-size:14px">Chaque exo a un lien vers la fiche qui l'explique.</p><a href="#fiches">Voir les fiches</a></div>
        </aside>
      </div></div></section>`;
    const draw = () => {
      const q = PF.q.trim().toLowerCase();
      let r = ids.filter((id) => {
        const t = CAT.tasks[id];
        return (PF.lang === "all" || t.lang === PF.lang) && (!PF.theme || themeOf(id) === PF.theme) && (!PF.st || statusOf(id) === PF.st) && (!q || (t.name + " " + (t.tags || []).join(" ")).toLowerCase().includes(q));
      }).sort((a, b) => RANK[a] - RANK[b] || LORD[CAT.tasks[a].lang] - LORD[CAT.tasks[b].lang]);
      const total = r.length; r = r.slice(0, PF.shown);
      $("#prows").innerHTML = r.map((id, i) => {
        const t = CAT.tasks[id], s = statusOf(id), ex = EXAM_OF[id], best = (P.tasks[id] || {}).best;
        return `<tr data-id="${id}" tabindex="0"><td class="num">${i + 1}</td><td class="ttl"><a href="#exo-${id}">${esc(t.name)}</a><small>${esc((t.tags || []).slice(0, 3).join(" · "))}${ex ? " · aussi dans l'examen " + (ex.mini ? "mini" : "#" + pad(CAT.exams.filter((x) => !x.mini).findIndex((x) => x.id === ex.id) + 1)) : ""}</small></td><td><span class="lg ${t.lang}">${SHORT[t.lang]}</span></td><td>${esc(themeOf(id))}</td><td class="num">${t.minutes} min</td><td><span class="st ${s}">${ST_LAB[s]}${best != null && s !== "todo" ? " · " + best : ""}</span></td></tr>`;
      }).join("") || `<tr><td colspan="6" class="muted">Aucun exo ne correspond à ces filtres.</td></tr>`;
      $$("#prows tr[data-id]").forEach((tr) => { tr.onclick = (e) => { if (e.target.tagName !== "A") goHash("exo-" + tr.dataset.id); }; tr.onkeydown = (e) => { if (e.key === "Enter") goHash("exo-" + tr.dataset.id); }; });
      const mb = $("#pmore"); mb.hidden = total <= PF.shown; mb.textContent = `Afficher plus (${total - PF.shown} restants)`;
    };
    $$(".ptabs button").forEach((b) => (b.onclick = () => { PF.lang = b.dataset.f; PF.shown = 30; renderPratiquer(); }));
    $("#fTheme").onchange = (e) => { PF.theme = e.target.value; PF.shown = 30; draw(); };
    $("#fStat").onchange = (e) => { PF.st = e.target.value; PF.shown = 30; draw(); };
    $("#fQ").oninput = (e) => { PF.q = e.target.value; PF.shown = 30; draw(); };
    $("#pmore").onclick = () => { PF.shown += 30; draw(); };
    draw();
  }

  /* ============================================================ v2 : Fiches */
  function myNotesHtml() {
    const ids = Object.keys(P.tnotes || {}).filter((id) => CAT.tasks[id] && hasNote(id)).sort((a, b) => ((P.tnotes[b].at || "") > (P.tnotes[a].at || "") ? 1 : -1));
    if (!ids.length) return `<h2 class="h2s">Mes fiches d'exos</h2><p class="muted">Après chaque exo, l'écran du résultat te propose d'écrire 3 lignes : déclencheur, outil, piège. Elles apparaîtront ici.</p>`;
    return `<h2 class="h2s">Mes fiches d'exos <span class="muted" style="font-size:15px;font-weight:500">· ${ids.length}, écrites par toi</span></h2><div class="mynotes">${ids.map((id) => {
      const n = P.tnotes[id];
      return `<div class="mn"><a href="#exo-${id}"><span class="lg ${CAT.tasks[id].lang}">${SHORT[CAT.tasks[id].lang]}</span> ${esc(CAT.tasks[id].name)}</a>${NOTE_F.map(([k, lab]) => (n[k] || "").trim() ? `<div><b>${lab} :</b> ${esc(n[k])}</div>` : "").join("")}</div>`;
    }).join("")}</div>`;
  }
  function renderFiches() {
    const f = FI();
    const card = (l) => `<a class="fcard" href="#fiche-${l}"><span class="lg ${l}">${SHORT[l]}</span><h3>${esc(f[l].title)}</h3><ul>${f[l].secs.slice(0, 6).map((s) => `<li>${esc(s.t)}</li>`).join("")}</ul><span class="go">Lire la fiche →</span></a>`;
    const tool = (h, t, d) => `<a class="fcard small" href="${h}"><h3>${t}</h3><p class="muted" style="margin:0;font-size:14px">${d}</p></a>`;
    view().innerHTML = `<section class="ws on">${band("Fiches", `<p class="lead" style="margin:-4px 0 28px">Quand tu as oublié une syntaxe : lis la partie qu'il te faut, puis fais un des exos liés.</p>`)}
      <div class="wrap"><div class="sect">
        <div class="fgrid">${["sql", "pyspark", "python"].map(card).join("")}</div>
        ${myNotesHtml()}
        <h2 class="h2s">Autres outils</h2>
        <div class="fgrid">
          ${tool("#apprendre", "Réflexes", "Les 8 gestes de base, avec un exemple guidé et un mini-exo chacun.")}
          ${tool("#dsa", "Algorithmes (DSA)", "13 patterns : fiche, exemple guidé, pièges et 2 exos par pattern.")}
          ${tool("#lire", "Lire la consigne", "13 exos de lecture d'énoncés longs, pour ne plus mal comprendre une consigne.")}
          ${tool("#live", "Live coding", "Une question d'entretien à voix haute, chronométrée, avec enregistrement.")}
          ${tool("#progression", "Progression et sauvegarde", "Tes notes, tes erreurs fréquentes, et l'export de ta progression.")}
          ${tool("#guide", "Mode d'emploi", "Comment utiliser le site en 3 minutes.")}
        </div></div></div></section>`;
  }
  function renderFiche(lang, sid) {
    const f = FI()[lang]; if (!f) return goHash("fiches");
    const isRev = P.day && P.day.rev && P.day.rev.kind === "fiche" && P.day.rev.lang === lang;
    const sec = (s) => {
      const links = s.match ? linkedTasks(lang, s.match, 4) : [];
      const revBtn = isRev && P.day.rev.sec === s.id ? `<div class="revbox">${P.day.rev.read ? "✓ Révision du jour faite." : `C'est ta révision du jour. Relis cette partie, puis : <button class="pill sm" id="revDone">J'ai relu</button>`}</div>` : "";
      return `<section class="fsec" id="sec-${s.id}"><h2>${esc(s.t)}</h2>${revBtn}<p>${s.p}</p>${codeBlock(s.code)}<div class="trap"><b>Piège :</b> ${s.trap}</div>
        ${links.length ? `<div class="flinks"><span class="muted">Pour pratiquer :</span>${links.map((id) => `<a href="#exo-${id}">${statusOf(id) === "ok" ? "✓ " : ""}${esc(CAT.tasks[id].name)}</a>`).join("")}</div>` : ""}
        ${s.more ? `<div class="flinks"><a class="pill sm ghost" href="${s.more.href}">${esc(s.more.label)}</a></div>` : ""}</section>`;
    };
    view().innerHTML = `<section class="ws on">${band(esc(f.title), `<p class="lead" style="margin:-4px 0 28px">${esc(f.lead)}</p>`, `<div class="crumbs"><a href="#fiches">Fiches</a> › ${SHORT[lang]}</div>`)}
      <div class="wrap"><div class="sect fiche">
        <nav class="ftoc" aria-label="Sommaire">${f.secs.map((s) => `<a href="#fiche-${lang}-${s.id}" data-sec="${s.id}">${esc(s.t)}</a>`).join("")}</nav>
        <div style="min-width:0">${f.start ? `<p class="muted" style="margin:0 0 6px">En haut de chaque solution :</p>${codeBlock(f.start)}` : ""}${f.secs.map(sec).join("")}</div>
      </div></div></section>`;
    const rb = $("#revDone"); if (rb) rb.onclick = () => { P.day.rev.read = true; persist(); renderFiche(lang, sid); };
    if (sid) { const el = document.getElementById("sec-" + sid); if (el) setTimeout(() => el.scrollIntoView({ block: "start" }), 0); }
  }

  /* ============================================================ révision éclair */
  function renderRevision() {
    seedMethodCards();
    const ids = dueCards(4);
    const reviews = dueReviews();
    let i = 0;
    const box = () => $("#flash");
    const insess = inSessionStep("revision");
    view().innerHTML = `<section class="ws on">${band("Révision éclair", `<p class="lead" style="padding-bottom:28px">Écris la réponse de mémoire avant de la regarder : c'est ce qui la fait rester. 5 minutes.</p>`)}
      <div class="wrap"><div class="sect"><div class="btnrow" style="margin-bottom:18px">${minitimer("rv", 300)}<span class="muted" id="rvCount"></span></div>
      <div class="card flash" id="flash"></div>
      ${reviews.length ? `<div class="card" style="margin-top:18px"><h3>Exos à refaire</h3><p class="muted">Tu les avais ratés. Refais-les sans regarder le corrigé.</p><div class="list">${reviews.map((r) => `<div class="row" style="grid-template-columns:1fr auto"><div class="t"><b>${esc(TITLE[r.task] || r.task)}</b><span>${esc(SHORT[(CAT.tasks[r.task] || {}).lang] || "")} · meilleure note ${(P.tasks[r.task] || {}).best || 0}/100</span></div><a class="pill sm" href="#exo-${r.task}">Refaire</a></div>`).join("")}</div></div>` : ""}
      </div></div></section>`;
    bindMinitimer("rv");
    const draw = () => {
      $("#rvCount").textContent = ids.length ? "Carte " + Math.min(i + 1, ids.length) + " sur " + ids.length : "";
      if (!ids.length) { box().innerHTML = `<p class="q">Aucune carte à revoir aujourd'hui.</p><p class="meta">Les cartes de chaque réflexe arrivent ici à partir de la séance suivante.</p>${insess ? "" : '<a class="pill sm" href="#accueil">Retour au parcours</a>'}`; return; }
      if (i >= ids.length) { box().innerHTML = `<p class="q">✓ Révision faite.</p><p class="meta">Les cartes « à revoir » reviendront à la prochaine séance, les autres plus tard.</p>`; return; }
      const [q, a] = cardText(ids[i]);
      box().innerHTML = `<span class="meta">${ids[i].startsWith("m-") ? "Méthode" : ids[i].startsWith("dsa") ? "DSA · " + esc((dsaP(ids[i].split("-")[0]) || {}).title || "") : esc((reflex(ids[i].split("-")[0]) || {}).title || "")}</span><p class="q">${esc(q)}</p>
        <div class="field"><label for="ans">Ta réponse, de mémoire</label><textarea id="ans" placeholder="Écris ce dont tu te souviens…"></textarea></div>
        <div class="btnrow" id="fb"><button class="pill sm" id="see">Voir la réponse</button></div>`;
      $("#see").onclick = () => {
        $("#fb").outerHTML = `<div class="a">${esc(a)}</div><div class="btnrow"><button class="pill sm mint" id="yes">Je savais ✓</button><button class="pill sm ghost" id="no">À revoir</button></div>`;
        $("#yes").onclick = () => { gradeCard(ids[i], true); i++; draw(); };
        $("#no").onclick = () => { gradeCard(ids[i], false); i++; draw(); };
      };
    };
    draw();
  }

  /* ============================================================ réflexes */
  function renderReflexes() {
    view().innerHTML = `<section class="ws on">${band("Réflexes", `<p class="lead" style="padding-bottom:28px">Les gestes à connaître par cœur. Chaque réflexe : un exemple guidé, les pièges, un mini-exo de mémoire.</p>`, bib("apprendre"))}
      <div class="wrap"><div class="sect"><div class="grid3">${CAT.reflexes.map((r, i) => {
        const m = P.tasks[r.mini];
        return `<div class="ex"><span class="src">Réflexe ${i + 1} · ${esc(r.lang)}</span><h3>${esc(r.title)}</h3><span class="muted">${esc(r.why)}</span>${m && m.best >= 80 ? '<span class="done-badge">✓ mini-exo réussi</span>' : ""}<a class="pill sm" href="#reflexe-${r.id}">Ouvrir</a></div>`;
      }).join("")}</div></div></div></section>`;
  }
  function renderLesson(rid) {
    const r = reflex(rid);
    if (!r) return goHash("apprendre");
    const insess = inSessionStep("reflexe-" + rid);
    const toc = CAT.reflexes.map((x, i) => `<a href="#reflexe-${x.id}" class="${x.id === rid ? "on" : ""}">${esc(x.title)} <span>${i + 1}</span></a>`).join("");
    const mini = CAT.tasks[r.mini];
    view().innerHTML = `<section class="ws on">${band(esc(r.title), `<p class="lead" style="padding-bottom:28px">${esc(r.why)}</p>`, insess ? "" : bib("apprendre"))}
      <div class="wrap"><div class="sect learn"><aside class="toc"><span class="lbl">Réflexes</span>${toc}</aside>
      <div class="panel lesson"><span class="chip">${esc(r.lang)}</span>
        <h2 style="font-size:28px;margin:12px 0 10px">Le geste</h2>
        <ul>${r.body.map((x) => `<li>${x}</li>`).join("")}</ul>
        <h3 style="margin-top:18px">Exemple guidé</h3>${codeBlock(r.code)}
        <h3>Les pièges</h3><ul class="traps">${r.traps.map((x) => `<li>${x}</li>`).join("")}</ul>
        <div class="card" style="margin-top:20px;background:var(--mint-soft);border-color:transparent">
          <h3>Mini-exo de mémoire · ${mini ? mini.minutes : 5} min</h3>
          <p class="muted" style="margin:0 0 12px">L'éditeur s'ouvre sans l'exemple : écris le geste de mémoire. Si tu bloques, les indices sont dans l'énoncé.</p>
          <div class="btnrow"><a class="pill sm" href="#exo-${r.mini}">Faire le mini-exo : ${esc(mini ? mini.name : "")}</a>${P.tasks[r.mini] ? `<span class="muted">Ta meilleure note : ${P.tasks[r.mini].best}/100</span>` : ""}</div>
        </div>
        <div class="btnrow" style="margin-top:20px">${(() => {
          const d = r.cards.map((c) => `<li><b>${esc(c[0])}</b><br><span class="muted">${esc(c[1])}</span></li>`).join("");
          return `<details><summary style="cursor:pointer;font-weight:500">Les 4 cartes de ce réflexe (elles reviendront en révision)</summary><ul style="margin-top:10px">${d}</ul></details>`;
        })()}</div>
      </div></div></div></section>`;
  }

  /* ============================================================ bibliothèque */
  let exoFilter = "all";
  function wipeTasks(tids) { tids.forEach((t) => delete P.tasks[t]); P.review = P.review.filter((r) => !tids.includes(r.task)); }
  function wipeAttempt(key) { const a = load(LSA, null); if (a && a.key === key) save(LSA, null); }
  function wipeExam(eid) {
    const e = exam(eid); if (!e) return;
    if (!confirm("Effacer « " + e.title.replace("Practice Assessment · ", "") + " » ? Ses notes, ta tentative en cours et ses tasks à refaire seront effacées. Tout le reste est gardé.")) return;
    delete P.exams[eid]; delete P.notes[eid]; wipeTasks(e.tasks); wipeAttempt("exam:" + eid); persist(); route();
  }
  function wipeExo(tid) {
    if (!confirm("Effacer « " + (TITLE[tid] || tid) + " » ? Ses notes, ta tentative en cours et sa place dans les exos à refaire seront effacées. Tout le reste est gardé.")) return;
    wipeTasks([tid]); wipeAttempt("exo:" + tid); persist(); route();
  }
  function renderExos() {
    const ids = CAT.library;
    const cnt = (l) => ids.filter((id) => l === "all" || CAT.tasks[id].lang === l).length;
    const tabs = `<div class="ptabs filters" role="group" aria-label="Langage">${[["all", "Tous"], ["pyspark", "PySpark"], ["sql", "SQL"], ["python", "Python"]].map(([k, n]) => `<button data-f="${k}" class="${exoFilter === k ? "on" : ""}">${n} <span class="cnt">${cnt(k)}</span></button>`).join("")}</div>`;
    const cards = ids.filter((id) => exoFilter === "all" || CAT.tasks[id].lang === exoFilter).map((id) => {
      const t = CAT.tasks[id], pr = P.tasks[id];
      return `<div class="ex"><span class="src">${esc(t.source)} · ${SHORT[t.lang]}</span><h3>${esc(t.name)}</h3><div class="tagrow">${t.tags.slice(0, 3).map((g) => `<span class="tag">${esc(g)}</span>`).join("")}</div>
        <span class="muted">Chrono ${t.minutes} min · ${t.tests} tests</span>${pr ? `<span class="${pr.best >= 80 ? "done-badge" : "muted"}">${pr.best >= 80 ? "✓ validé" : "Meilleure note"} · ${pr.best}/100</span>` : ""}<div class="btnrow"><a class="pill sm" href="#exo-${id}">Ouvrir</a>${pr || attemptFor("exo", id) ? `<button class="pill sm ghost" data-wipe-exo="${id}">Effacer</button>` : ""}</div></div>`;
    }).join("");
    view().innerHTML = `<section class="ws on">${band("Exos", tabs, bib("exos"))}<div class="wrap"><div class="sect">
      <p class="sub">Choix libre. Ton parcours, lui, te donne les exos dans le bon ordre. Les tasks des examens restent dans les examens, pour qu'elles soient neuves le jour où tu les passes.</p>
      <div class="grid3">${cards}</div>
      <h2 style="font-size:26px;margin-top:40px">Pour aller plus loin, ailleurs</h2><p class="sub">Sites gratuits, à faire en plus quand le parcours est à jour.</p>
      <div class="grid3">${CAT.links.map((l) => `<div class="ex"><span class="src">Lien externe</span><h3>${esc(l.name)}</h3><span class="muted">${esc(l.what)}</span><a class="pill sm ghost" href="${esc(l.url)}" target="_blank" rel="noopener">Ouvrir ↗</a></div>`).join("")}</div>
      </div></div></section>`;
    $$(".ptabs button").forEach((b) => (b.onclick = () => { exoFilter = b.dataset.f; renderExos(); }));
    $$("[data-wipe-exo]").forEach((b) => (b.onclick = () => wipeExo(b.dataset.wipeExo)));
  }
  let examTab = "todo";
  function renderExams() {
    const list = CAT.exams;
    const doneIds = list.filter((e) => (P.exams[e.id] || {}).hist && P.exams[e.id].hist.length);
    const tabs = `<div class="ptabs" role="tablist"><button data-t="todo" class="${examTab === "todo" ? "on" : ""}">À faire <span class="cnt">${list.length - doneIds.length}</span></button><button data-t="done" class="${examTab === "done" ? "on" : ""}">Terminés <span class="cnt">${doneIds.length}</span></button></div>`;
    const rows = list.filter((e) => (examTab === "done") === doneIds.includes(e)).map((e, i) => {
      const h = (P.exams[e.id] || {}).hist || [];
      const last = h[h.length - 1];
      const langs = e.tasks.map((t) => SHORT[CAT.tasks[t].lang]).join(" · ");
      const n = e.mini ? "mini" : "#" + pad(CAT.exams.filter((x) => !x.mini).indexOf(e) + 1);
      return `<div class="row"><span class="n">${n}</span><div class="t"><b>${esc(e.title.replace("Practice Assessment · ", ""))}</b><span>${langs} · ${e.minutes} min</span></div>
        ${last ? `<span class="chip">${last.scores.join(" · ")}</span>` : '<span class="score muted">Pas encore fait</span>'}
        <div class="btnrow">${last ? `<a class="pill sm ghost" href="#analyse-${e.id}">Analyse</a>` : ""}<a class="pill sm ${last ? "ghost" : ""}" href="#exam-${e.id}">${attemptFor("exam", e.id) ? "Reprendre" : last ? "Recommencer" : "Start"}</a>${last || attemptFor("exam", e.id) ? `<button class="pill sm ghost" data-wipe-exam="${e.id}">Effacer</button>` : ""}</div></div>`;
    }).join("") || `<p class="empty">${examTab === "done" ? "Aucun examen terminé pour l'instant." : "Tu as fait tous les examens disponibles. Refais-les dans l'onglet Terminés."}</p>`;
    view().innerHTML = `<section class="ws on">${band("Examens", tabs, bib("examens"))}<div class="wrap"><div class="sect">
      <p class="sub">Format du vrai test : 4 tasks, 70 minutes, chaque task notée sur 100. Les 4 premiers sont progressifs. Ensuite, comme le jour J, l'ordre des langages et la difficulté changent d'un examen à l'autre : SQL peut ouvrir l'examen, et les 4 tasks peuvent être coriaces. Prépare-toi à tout. « Effacer » remet un seul examen à zéro, sans toucher au reste.</p>
      <div class="list">${rows}</div></div></div></section>`;
    $$(".ptabs button").forEach((b) => (b.onclick = () => { examTab = b.dataset.t; renderExams(); }));
    $$("[data-wipe-exam]").forEach((b) => (b.onclick = () => wipeExam(b.dataset.wipeExam)));
  }

  /* ============================================================ analyse guidée */
  async function renderAnalysis(eid) {
    const e = exam(eid); if (!e) return goHash("examens");
    const h = ((P.exams[eid] || {}).hist || []).slice(-1)[0];
    const tasks = await Promise.all(e.tasks.map(getTask));
    const notes = P.notes[eid] || (P.notes[eid] = {});
    const Q = [["q1", "Quelle task t'a pris le plus de temps, et pourquoi ?"], ["q2", "Pour chaque test raté : quelle règle de la consigne as-tu mal lue ou oubliée ?"], ["q3", "Qu'est-ce que tu fais différemment au prochain examen ?"]];
    view().innerHTML = `<section class="ws on">${band("Analyse guidée", `<p class="lead" style="padding-bottom:28px">${esc(e.title)}. 15 minutes pour transformer tes erreurs en points au prochain examen.</p>`)}
      <div class="wrap"><div class="sect"><div class="btnrow" style="margin-bottom:18px">${minitimer("an", 900)}</div>
      ${h ? "" : '<div class="alert" style="margin:0 0 18px">Tu n\'as pas encore terminé cet examen. Fais-le d\'abord : le corrigé reste caché jusque-là.</div>'}
      <div class="card"><h3>1. Tes notes</h3><table class="tbl"><tr><th>Task</th><th>Note</th><th></th></tr>
        ${tasks.map((t, i) => `<tr><td>Task ${i + 1} · ${esc(t.name)} <span class="muted">(${SHORT[t.lang]})</span></td><td class="score-chip">${h ? h.scores[i] : "-"}/100</td><td><div class="btnrow">${h ? `<button class="pill sm ghost" data-sol="${i}">Corrigé</button>` : ""}<a class="pill sm ghost" href="#exo-${t.id}">Refaire</a></div></td></tr><tr hidden id="sol${i}"><td colspan="3"></td></tr>`).join("")}</table></div>
      <div class="card" style="margin-top:18px"><h3>2. Réponds par écrit</h3>${Q.map(([k, q]) => `<div class="field"><label for="${k}">${q}</label><textarea id="${k}" data-k="${k}">${esc(notes[k] || "")}</textarea></div>`).join("")}<span class="muted">Tes réponses sont gardées dans ce navigateur.</span></div>
      <div class="card" style="margin-top:18px"><h3>3. Refais ce que tu as raté</h3><p class="muted" style="margin:0">Les tasks sous 80/100 reviennent seules dans tes prochaines séances (2, 5 puis 12 séances plus tard). Tu peux aussi les refaire maintenant avec le bouton Refaire.</p></div>
      </div></div></section>`;
    bindMinitimer("an");
    $$("textarea[data-k]").forEach((ta) => (ta.oninput = () => { notes[ta.dataset.k] = ta.value; persist(); }));
    $$("[data-sol]").forEach((b) => (b.onclick = () => {
      const i = +b.dataset.sol, row = $("#sol" + i);
      row.hidden = !row.hidden;
      if (!row.hidden) row.firstElementChild.innerHTML = corrigeHtml(tasks[i]);
    }));
  }

  /* ============================================================ progression */
  let progTab = "exams";
  function renderProgress() {
    const ex = [];
    CAT.exams.forEach((e) => ((P.exams[e.id] || {}).hist || []).forEach((h) => ex.push({ e, h })));
    ex.sort((a, b) => (a.h.ts || 0) - (b.h.ts || 0));
    const taskIds = Object.keys(P.tasks);
    const errs = Object.entries(P.errors).sort((a, b) => b[1] - a[1]);
    const tabs = `<div class="ptabs" role="tablist">${[["exams", "Examens", ex.length], ["exos", "Exos", taskIds.length], ["errors", "Erreurs", errs.length], ["save", "Sauvegarde", ""]].map(([k, n, c]) => `<button data-t="${k}" class="${progTab === k ? "on" : ""}">${n} ${c !== "" ? `<span class="cnt">${c}</span>` : ""}</button>`).join("")}</div>`;
    let body = "";
    if (progTab === "exams") {
      if (!ex.length) body = `<p class="empty">Ta courbe apparaîtra après ton premier examen.</p>`;
      else {
        const pts = ex.slice(-10).map((x) => Math.round(x.h.scores.reduce((a, b) => a + b, 0) / x.h.scores.length));
        const W = 520, H = 200, x0 = 50, x1 = 500, y = (v) => 170 - v * 1.5;
        const xs = pts.map((_, i) => (pts.length === 1 ? (x0 + x1) / 2 : x0 + ((x1 - x0) * i) / (pts.length - 1)));
        const line = pts.map((v, i) => (i ? "L" : "M") + xs[i].toFixed(0) + " " + y(v).toFixed(0)).join(" ");
        body = `<div class="prog"><div class="panel"><h3>Score moyen par task (sur 100)</h3>
          <svg class="spark" viewBox="0 0 ${W} ${H}" role="img" aria-label="Scores moyens : ${pts.join(", ")}">
          <g stroke="var(--line)"><line x1="40" y1="20" x2="510" y2="20"/><line x1="40" y1="95" x2="510" y2="95"/><line x1="40" y1="170" x2="510" y2="170"/></g>
          <g fill="var(--ink-soft)" font-size="11" font-family="JetBrains Mono, monospace"><text x="4" y="24">100</text><text x="12" y="99">50</text><text x="20" y="174">0</text></g>
          <path d="${line}" fill="none" stroke="var(--mint)" stroke-width="3"/>${pts.map((v, i) => `<circle cx="${xs[i].toFixed(0)}" cy="${y(v).toFixed(0)}" r="5" fill="var(--mint)"><title>${v}</title></circle><text x="${xs[i].toFixed(0)}" y="${(y(v) - 10).toFixed(0)}" text-anchor="middle" font-size="12" font-weight="700" fill="var(--ink)">${v}</text>`).join("")}</svg></div>
          <div class="panel"><h3>Derniers examens</h3>${ex.slice(-8).reverse().map((x) => `<div class="err"><span>${esc(x.e.title.replace("Practice Assessment · ", ""))}<br><span class="muted">${esc(x.h.at)}${x.h.restarted ? " · recommencé" : ""}</span></span><span class="score-chip">${x.h.scores.join(" · ")}</span></div>`).join("")}</div></div>`;
      }
    } else if (progTab === "exos") {
      body = taskIds.length ? `<div class="card"><table class="tbl"><tr><th>Exo</th><th>Meilleure</th><th>Dernière</th><th>Essais</th><th></th></tr>${taskIds.map((id) => { const t = P.tasks[id]; return `<tr><td>${esc(TITLE[id] || id)}</td><td class="score-chip ${t.best >= 80 ? "ok-t" : ""}">${t.best}/100</td><td class="score-chip">${t.last}/100</td><td>${t.n}</td><td><a class="pill sm ghost" href="#exo-${id}">Refaire</a></td></tr>`; }).join("")}</table></div>` : `<p class="empty">Aucun exo soumis pour l'instant.</p>`;
    } else if (progTab === "errors") {
      body = errs.length ? `<div class="panel"><h3>Les thèmes où tu perds des points</h3><p class="muted">Compté à chaque soumission sous 80/100. Relis le réflexe du thème qui revient le plus.</p>${errs.map(([g, n]) => `<div class="err"><span>${esc(g)}</span><span class="chip ko">${n} fois</span></div>`).join("")}</div>` : `<p class="empty">Rien pour l'instant.</p>`;
    } else {
      body = `<div class="card"><h3>Ta progression est dans ce navigateur</h3><p class="muted">Elle reste sur cet ordinateur, dans Chrome. Exporte-la de temps en temps : si tu changes d'ordinateur ou si tu vides Chrome, tu pourras la réimporter.</p>
        <div class="btnrow"><button class="pill sm" id="exp">Exporter (fichier .json)</button><label class="pill sm ghost" style="cursor:pointer">Importer<input type="file" id="imp" accept="application/json,.json" hidden></label><button class="pill sm ghost" id="rst">Tout remettre à zéro</button></div><p id="saveMsg" class="muted"></p></div>`;
    }
    view().innerHTML = `<section class="ws on">${band("Progression", tabs)}<div class="wrap"><div class="sect">${body}</div></div></section>`;
    $$(".ptabs button").forEach((b) => (b.onclick = () => { progTab = b.dataset.t; renderProgress(); }));
    if (progTab === "save") {
      $("#exp").onclick = () => {
        const blob = new Blob([JSON.stringify({ kata: P, attempt: load(LSA, null) }, null, 1)], { type: "application/json" });
        const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "kata-lab-progression-" + today() + ".json"; a.click();
        setTimeout(() => URL.revokeObjectURL(a.href), 2000);
      };
      $("#imp").onchange = async (ev) => {
        try {
          const j = JSON.parse(await ev.target.files[0].text());
          if (!j.kata || !j.kata.v) throw new Error("fichier inconnu");
          P = Object.assign(P0(), j.kata); persist(); if (j.attempt) save(LSA, j.attempt);
          $("#saveMsg").textContent = "✓ Progression importée.";
        } catch (e) { $("#saveMsg").textContent = "Ce fichier ne ressemble pas à une sauvegarde Kata Lab."; }
      };
      $("#rst").onclick = () => { if (confirm("Effacer toute ta progression ? Exporte-la d'abord si tu veux la garder.")) { P = P0(); persist(); save(LSA, null); renderProgress(); } };
    }
  }

  /* ============================================================ connexion */
  function renderConnexion() {
    const key = E.Key.get(), exp = E.Key.expiry();
    view().innerHTML = `<section class="ws on">${band("Connexion", `<p class="lead" style="padding-bottom:28px">La clé GitHub permet au site d'allumer ton Codespace, où tourne le vrai Spark. Tu la colles une seule fois : elle reste dans ce navigateur, sur ton ordinateur.</p>`)}
      <div class="wrap"><div class="sect" style="display:grid;gap:18px">
      <div class="card"><h3>Ta clé</h3>
        <div class="kv"><b>Clé enregistrée</b><span>${key ? "Oui (" + esc(key.slice(0, 11)) + "…)" : "Non"}</span><b>Expire le</b><span>${exp ? esc(exp) : "Pas indiqué"}</span><b>Compte GitHub</b><span id="who">-</span></div>
        <div class="field"><label for="k">${key ? "Remplacer la clé" : "Colle ta clé ici"} (elle commence par <code>github_pat_</code>)</label><input id="k" type="password" autocomplete="off" placeholder="github_pat_…"></div>
        <div class="field"><label for="kexp">Date d'expiration de la clé (affichée par GitHub quand tu la crées)</label><input id="kexp" type="date" value="${esc(exp)}" style="max-width:220px"></div>
        <div class="btnrow"><button class="pill sm" id="ksave">Enregistrer et tester</button>${key ? '<button class="pill sm ghost" id="ktest">Tester</button><button class="pill sm ghost" id="kdel">Effacer la clé</button>' : ""}</div>
        <p id="kmsg" class="muted"></p></div>
      <div class="card"><h3>Ton Codespace (le vrai Spark)</h3>
        <p class="muted" style="margin-top:0">Il s'allume tout seul quand tu ouvres un exo PySpark et s'éteint seul après 30 minutes sans utilisation. S'il a été supprimé (après 30 jours sans servir), le site le recrée : la première fois, compte environ 5 minutes.</p>
        <div class="kv" id="csinfo"><b>État</b><span>-</span></div>
        <div class="btnrow" style="margin-top:12px"><button class="pill sm ghost" id="csCheck">Vérifier</button><button class="pill sm ghost" id="csOn">Allumer maintenant</button><button class="pill sm ghost" id="csOff">Éteindre</button><button class="pill sm ghost" id="csNew">Recréer le Codespace</button></div>
        <p id="csmsg" class="muted"></p></div>
      <div class="card"><h3>Créer une nouvelle clé (5 minutes)</h3>
        <ol class="steps-guide">
          <li>Ouvre <a href="https://github.com/settings/personal-access-tokens/new" target="_blank" rel="noopener">github.com/settings/personal-access-tokens/new</a> (connecté à ton compte <b>gitabdelhub</b>).</li>
          <li><b>Token name</b> : <code>kata-lab</code>. <b>Expiration</b> : choisis la plus longue durée proposée (ou « No expiration » si GitHub la propose).</li>
          <li><b>Repository access</b> : <i>Only select repositories</i>, puis choisis <code>gitabdelhub/kata-lab</code>.</li>
          <li><b>Permissions</b>, partie <i>Repositories</i> : <code>Codespaces</code> = Read and write, <code>Codespaces lifecycle admin</code> = Read and write, <code>Codespaces metadata</code> = Read-only.</li>
          <li>Partie <i>Account</i> (si elle est proposée) : <code>Codespaces</code> = Read and write, <code>Codespaces user secrets</code> : rien.</li>
          <li>Clique <b>Generate token</b>, copie la clé, colle-la ci-dessus avec sa date d'expiration, puis <b>Enregistrer et tester</b>.</li>
          <li>Ne l'envoie à personne. Si tu penses qu'elle a fuité : supprime-la sur GitHub et crée-en une autre.</li>
        </ol></div>
      </div></div></section>`;
    const msg = (id, t, ok) => { const el = $("#" + id); el.textContent = t; el.className = ok === true ? "ok-t" : ok === false ? "ko-t" : "muted"; };
    const test = async () => {
      msg("kmsg", "Test en cours…");
      try { const u = await E.whoami(); $("#who").textContent = u.login; msg("kmsg", "✓ GitHub accepte ta clé (compte " + u.login + ").", true); renderAlerts(); return true; }
      catch (e) { msg("kmsg", e.message, false); return false; }
    };
    $("#ksave").onclick = async () => {
      const v = $("#k").value.trim();
      if (v) E.Key.set(v);
      E.Key.setExpiry($("#kexp").value);
      if (!E.Key.get()) return msg("kmsg", "Colle d'abord ta clé.", false);
      await test(); renderAlerts();
    };
    if ($("#ktest")) $("#ktest").onclick = test;
    if ($("#kdel")) $("#kdel").onclick = () => { if (confirm("Effacer la clé de ce navigateur ?")) { E.Key.clear(); renderConnexion(); renderAlerts(); } };
    const STATES = { Available: "Allumé", Shutdown: "Éteint", Starting: "En train de s'allumer", ShuttingDown: "En train de s'éteindre", Provisioning: "En création", Queued: "En file d'attente", Rebuilding: "En reconstruction", Failed: "En erreur" };
    const check = async () => {
      msg("csmsg", "Vérification…");
      try {
        const s = await E.codespaceStatus();
        $("#csinfo").innerHTML = s.exists ? `<b>État</b><span>${esc(STATES[s.state] || s.state)}</span><b>Nom</b><span>${esc(s.name)}</span><b>Correction Spark</b><span>${s.runner ? (s.runner.ready ? "Prête (Spark " + esc(s.runner.spark) + ")" : "Spark démarre") : s.state === "Available" ? "Ne répond pas encore" : "-"}</span><b>Ouvrir</b><span><a href="${esc(s.webUrl)}" target="_blank" rel="noopener">dans VS Code (navigateur) ↗</a></span>` : `<b>État</b><span>Pas encore créé : il sera créé à ton premier exo PySpark.</span>`;
        msg("csmsg", "");
      } catch (e) { msg("csmsg", e.message, false); }
    };
    $("#csCheck").onclick = check;
    $("#csOn").onclick = async () => { try { await E.ensureSpark((t) => msg("csmsg", t + "…")); msg("csmsg", "✓ Spark est prêt.", true); check(); } catch (e) { msg("csmsg", e.message, false); } };
    $("#csOff").onclick = async () => { try { msg("csmsg", "Extinction…"); await E.stopCodespace(); msg("csmsg", "✓ Demande d'extinction envoyée.", true); setTimeout(check, 4000); } catch (e) { msg("csmsg", e.message, false); } };
    $("#csNew").onclick = async () => {
      if (!confirm("Supprimer le Codespace actuel et en créer un neuf ? (À faire seulement s'il est en erreur.)")) return;
      try { msg("csmsg", "Suppression…"); await E.deleteCodespace(); msg("csmsg", "Création du nouveau Codespace (environ 5 minutes)…"); await E.ensureSpark((t) => msg("csmsg", t + "…")); msg("csmsg", "✓ Nouveau Codespace prêt.", true); check(); } catch (e) { msg("csmsg", e.message, false); }
    };
    if (key) { test(); check(); }
  }

  /* ============================================================ espace d'examen */
  let cm = null, cmSilent = false;
  const W = { on: false };
  function attemptFor(mode, id) { const a = load(LSA, null); return a && a.key === mode + ":" + id && !a.finished ? a : null; }
  function saveAttempt() {
    if (!W.on) return;
    save(LSA, { key: W.key, mode: W.mode, id: W.id, drafts: W.drafts, results: W.results, clock: W.clock, recorded: W.recorded, lastSub: W.lastSub, at: Date.now() });
  }
  let saveT = null;
  const saveSoon = () => { clearTimeout(saveT); saveT = setTimeout(saveAttempt, 400); };

  function pasteWarn() {
    let el = $("#pastewarn");
    if (!el) { el = document.createElement("div"); el.id = "pastewarn"; el.className = "pastewarn"; $("#ed").appendChild(el); }
    el.textContent = "Coller un texte venu d’ailleurs est désactivé, comme au vrai test. Dans ton propre code, copier-coller marche.";
    el.hidden = false; clearTimeout(el._t); el._t = setTimeout(() => (el.hidden = true), 3500);
  }
  function ensureCM() {
    if (cm) return;
    cm = CodeMirror($("#cm"), {
      lineNumbers: true, indentUnit: 4, tabSize: 4, indentWithTabs: false, matchBrackets: true, autoCloseBrackets: P.autoClose !== false, viewportMargin: 30,
      extraKeys: {
        Tab: (c) => (c.somethingSelected() ? c.indentSelection("add") : c.replaceSelection("    ", "end")),
        "Shift-Tab": (c) => c.indentSelection("subtract"),
        "Ctrl-Enter": () => runTests(false), "Cmd-Enter": () => runTests(false),
      },
    });
    // Copier-coller bloqué depuis l'extérieur de l'éditeur, comme au vrai test.
    // Ce que tu copies dans ton propre code reste permis.
    // On garde les derniers morceaux copiés dans l'éditeur (même après « Recommencer »),
    // et on accepte aussi tout texte qui se trouve déjà dans ton code.
    const OWN_K = "kata.owncopy";
    const norm = (x) => String(x || "").replace(/\r\n?/g, "\n").replace(/\s+$/, "");
    let own = [];
    try { own = JSON.parse(sessionStorage.getItem(OWN_K) || "[]"); } catch (_) {}
    const remember = (c) => {
      let txt = c.getSelection();
      if (!txt) txt = c.listSelections().map((r) => c.getLine(r.head.line)).join("\n"); // copie de la ligne entière
      txt = norm(txt);
      if (!txt) return;
      own = [txt].concat(own.filter((x) => x !== txt)).slice(0, 40);
      try { sessionStorage.setItem(OWN_K, JSON.stringify(own)); } catch (_) {}
    };
    const isOwn = (txt) => {
      const x = norm(txt);
      if (!x || own.includes(x)) return true;
      if (norm(cm.getValue()).includes(x)) return true;
      for (const k in W.drafts || {}) if (norm(W.drafts[k]).includes(x)) return true;
      return false;
    };
    cm.on("copy", remember); cm.on("cut", remember);
    // Un gros bloc qui arrive d'un coup sans événement « coller » (presse-papiers du clavier
    // sur téléphone, historique Windows, glisser depuis une autre fenêtre) : traité comme un collage.
    // Taper au clavier n'ajoute jamais plus d'une ligne ou 20 caractères d'un coup.
    const bigInsert = (x) => x.replace(/\s/g, "").length > 20 || /\n[^\n]*\S/.test(x);
    cm.on("beforeChange", (c, ch) => {
      const ins = ch.text.join("\n");
      const o = ch.origin || "";
      const pasted = o === "paste" || o === "drop" || ((/^\+input/.test(o) || /^\*compose/.test(o)) && bigInsert(ins));
      if (!pasted) return;
      if (isOwn(ins)) return;
      ch.cancel();
      pasteWarn();
    });
    // Filet de sécurité au niveau du navigateur : collage ou dépôt qui contourne CodeMirror.
    const inp = cm.getInputField();
    const guardIn = (e) => {
      if (!/^insertFrom(Paste|Drop|Yank|PasteAsQuotation)$/.test(e.inputType || "")) return;
      const txt = e.data || (e.dataTransfer && e.dataTransfer.getData("text/plain")) || "";
      if (!txt || isOwn(txt)) return;
      e.preventDefault(); pasteWarn();
    };
    inp.addEventListener("beforeinput", guardIn, true);
    cm.getWrapperElement().addEventListener("drop", (e) => {
      const txt = (e.dataTransfer && e.dataTransfer.getData("text/plain")) || "";
      if (txt && !isOwn(txt)) { e.preventDefault(); e.stopPropagation(); pasteWarn(); }
    }, true);
    cm.on("change", () => {
      if (cmSilent || cm.getOption("readOnly")) return;
      const t = W.tasks[W.cur];
      if (t.project && W.pfile) { const parts = projSplit(W.drafts[W.cur]); parts[W.pfile] = cm.getValue(); W.drafts[W.cur] = projJoin(t, parts); }
      else W.drafts[W.cur] = cm.getValue();
      saveSoon();
    });
  }
  /* tasks « projet » : plusieurs fichiers de code, rangés dans une seule chaîne avec des marqueurs */
  const PMARK = /^# ==== (.+?) ====$/;
  function projSplit(code) {
    const out = {}; let cur = null;
    for (const line of (code || "").split("\n")) { const m = line.match(PMARK); if (m) { cur = m[1]; out[cur] = []; } else if (cur) out[cur].push(line); }
    for (const k in out) out[k] = out[k].join("\n").replace(/^\n+|\n+$/g, "") + "\n";
    return out;
  }
  function projJoin(t, parts) { return t.project.files.map((p) => "# ==== " + p + " ====\n" + (parts[p] || "").replace(/\n+$/, "") + "\n").join("\n"); }
  function setEditor(text, readOnly, lang) {
    cmSilent = true;
    cm.setOption("mode", lang === "sql" ? "text/x-pgsql" : lang === "text" ? null : "python");
    cm.setOption("readOnly", readOnly ? "nocursor" : false);
    cm.getWrapperElement().classList.toggle("cm-readonly", !!readOnly);
    cm.setValue(text); cm.clearHistory();
    cmSilent = false;
    setTimeout(() => cm.refresh(), 0);
  }

  let keepDrafts = null;
  async function openWorkspace(mode, id, force) {
    const key = mode + ":" + id;
    if (W.on && W.key === key && !force) return;
    stopClock();
    let ids, title, minutes;
    if (mode === "exam") {
      const e = exam(id); if (!e) return goHash("examens");
      ids = e.tasks; title = e.title; minutes = e.mini ? e.minutes : P.dur || 70;
    } else {
      if (!CAT.tasks[id]) return goHash("pratiquer");
      ids = [id]; title = "Exo · " + CAT.tasks[id].name; minutes = CAT.tasks[id].minutes;
    }
    const tasks = await Promise.all(ids.map(getTask));
    const prev = force ? null : attemptFor(mode, id);
    if (force) {
      const old = load(LSA, null);
      if (old && old.key === key && mode === "exam" && !old.recorded && old.lastSub && Object.keys(old.lastSub).length) {
        recordExam(id, tasks.map((_, i) => old.lastSub[i] || 0), true);
      }
      save(LSA, null);
    }
    Object.assign(W, {
      on: true, key, mode, id, tasks, title, cur: 0, side: "desc", open: {}, showDiff: false, busy: false, recorded: false,
      drafts: keepDrafts && keepDrafts.key === key ? keepDrafts.drafts : prev ? prev.drafts : tasks.map((t) => t.starter),
      results: prev ? prev.results : {},
      clock: prev ? prev.clock : { endsAt: null, pausedLeft: null, mode: mode === "exam" ? "strict" : "train", baseMin: minutes, dur: minutes * 60000 },
      hints: {}, fr: false, maxHints: null,
    });
    if (mode === "exo" && P.cur) {
      const cs = findSession(P.cur.id), st = cs && cs.steps[P.cur.step];
      if (st && st.type === "exo" && st.task === id && st.hints != null) W.maxHints = st.hints;
    }
    keepDrafts = null;
    W.lastSub = (prev && prev.lastSub) || {};
    if (prev) W.recorded = !!prev.recorded;
    ensureCM();
    $("#asmTitle").textContent = title;
    $("#modal").hidden = true; $("#morebox").hidden = true; $("#umpire").hidden = true;
    $("#diff").textContent = "VIEW DIFF";
    $$(".asm-side button").forEach((x) => x.classList.toggle("on", x.dataset.side === "desc"));
    $("#showSol").hidden = mode !== "exo" || !solOK(id);
    $("#restartKeep").hidden = mode !== "exo";
    $("#stopExo").hidden = mode !== "exo";
    $("#restart").textContent = mode === "exo" ? "Recommencer à zéro" : "Recommencer";
    showTask(0);
    renderClock();
    markDay();
    await prepare(!!(prev && (prev.clock.endsAt || prev.clock.pausedLeft != null)));
  }
  function closeWorkspace() { W.on = false; stopClock(); clearInterval(pingT); $("#ov").hidden = true; }

  function treeHtml(t) {
    if (!t.files && !t.project) return "";
    let h = "";
    if (t.project) {
      const seenP = new Set();
      h += `<div class="lbl">Code</div>`;
      t.project.files.forEach((p) => {
        const parts = p.split("/");
        for (let d = 1; d < parts.length; d++) { const k = parts.slice(0, d).join("/"); if (!seenP.has(k)) { seenP.add(k); h += `<div class="dir in${Math.min(d - 1, 2)}">▾ ${esc(parts[d - 1])}/</div>`; } }
        h += `<button class="in${Math.min(parts.length - 1, 2)} ${W.fileOpen === null && W.pfile === p ? "on" : ""}" data-c="${esc(p)}">${esc(parts[parts.length - 1])}</button>`;
      });
      if (!t.files) return h;
    }
    const root = t.files.root;
    const paths = Object.keys(t.files.files).sort();
    const seen = new Set(); h += `<div class="lbl">Files</div><div class="dir">▾ ${esc(root)}/</div>`;
    paths.forEach((p, i) => {
      const parts = p.split("/");
      for (let d = 1; d < parts.length; d++) {
        const k = parts.slice(0, d).join("/");
        if (!seen.has(k)) { seen.add(k); h += `<div class="dir in${Math.min(d, 2)}">▾ ${esc(parts[d - 1])}/</div>`; }
      }
      h += `<button class="in${Math.min(parts.length, 2)} ${W.fileOpen === p ? "on" : ""}" data-p="${esc(p)}">${esc(parts[parts.length - 1])}</button>`;
    });
    if (!t.project) h += `<button class="${W.fileOpen === null ? "on" : ""}" data-p="">${FILE[t.lang]}</button>`;
    return h;
  }
  function renderFiles() {
    const t = W.tasks[W.cur];
    $("#ed").classList.toggle("nofiles", !t.files && !t.project);
    if (!t.files && !t.project) return;
    const f = $("#files"); f.innerHTML = treeHtml(t);
    $$("button", f).forEach((b) => (b.onclick = () => {
      if (b.dataset.c) {
        W.fileOpen = null; W.pfile = b.dataset.c;
        $("#ftab").textContent = W.pfile.split("/").pop();
        setEditor(projSplit(W.drafts[W.cur])[W.pfile] || "", false, t.lang);
        renderFiles(); return;
      }
      const p = b.dataset.p || null; W.fileOpen = p;
      if (p) { $("#ftab").textContent = p.split("/").pop(); setEditor(t.files.files[p], true, "text"); }
      else { $("#ftab").textContent = FILE[t.lang]; setEditor(W.drafts[W.cur], false, t.lang); }
      renderFiles();
    }));
  }
  function renderTaskTabs() {
    const el = $("#tasks");
    if (W.mode !== "exam") { el.innerHTML = ""; return; }
    el.innerHTML = W.tasks.map((t, i) => { return `<button role="tab" data-q="${i}" class="${i === W.cur ? "on" : ""} ${W.lastSub[i] != null ? (W.lastSub[i] === 100 ? "full" : "part") : ""}">TASK ${i + 1}</button>`; }).join("");
    $$("button", el).forEach((b) => (b.onclick = () => showTask(+b.dataset.q)));
  }
  function showTask(i) {
    W.cur = i; W.fileOpen = null;
    const t = W.tasks[i];
    $("#lang").textContent = LANG[t.lang];
    if (t.project) { W.pfile = t.project.main; $("#ftab").textContent = W.pfile.split("/").pop(); setEditor(projSplit(W.drafts[i])[W.pfile] || "", false, t.lang); }
    else { W.pfile = null; $("#ftab").textContent = FILE[t.lang]; setEditor(W.drafts[i], false, t.lang); }
    renderFiles(); renderTaskTabs(); renderPaper(); renderTests(); updScore();
  }
  function renderPaper() {
    const t = W.tasks[W.cur], p = $("#paper"), exo = W.mode === "exo";
    if (W.side === "desc") {
      let extra = "";
      if (exo) {
        const all = t.hints || [], lim = W.maxHints == null ? all.length : W.maxHints;
        const hs = all.slice(0, lim), fr = t.summary_fr && lim > 0;
        extra = `<div class="hintbox">${fr ? '<button data-fr="1">Aide à la lecture (FR)</button>' : ""}${hs.map((_, k) => `<button data-h="${k}">Indice ${k + 1}</button>`).join("")}</div>`;
        if (W.maxHints != null && lim < all.length) extra += `<p class="muted" style="margin:6px 0 0">${lim === 0 ? "Pas d'indice dans cette séance : tu t'entraînes comme le jour J." : "Les indices s'effacent : " + lim + " indice dans cette séance."} Tu les retrouveras en refaisant l'exo depuis la Bibliothèque.</p>`;
        if (W.fr) extra += `<div class="fr"><b>En français :</b> ${esc(t.summary_fr)}</div>`;
        if (hasNote(t.id)) extra += `<details class="mynote-d"><summary>Ta fiche sur cet exo <span>(ouvre-la seulement si tu bloques)</span></summary><div class="mynote">${noteForm(t.id)}</div></details>`;
        const fs = ficheSecFor(t.id);
        if (fs) extra += `<p class="fichelink">Une notion t'échappe ? <a href="#fiche-${fs.lang}-${fs.id}" target="_blank" rel="noopener">Relis la fiche « ${esc(fs.t)} »</a> (s'ouvre dans un nouvel onglet, ton code reste ici).</p>`;
        extra += `<p class="fichelink">${solOK(t.id) ? "Le corrigé est dans MORE, Voir le corrigé." : "Le corrigé s'ouvre après 2 essais (SUBMIT ou Terminer)."}</p>`;
        const shown = W.hints[W.cur] || [];
        shown.forEach((k) => (extra += `<div class="hinttxt"><b>Indice ${k + 1} :</b> ${esc(hs[k])}</div>`));
      }
      const howOpen = exo && P.howto !== false;
      const how = t.howto ? `<details class="howto"${howOpen ? " open" : ""}><summary>Comment faire, exactement <span>(en français : où écrire, quoi renvoyer, ce que tu dois voir)</span></summary>${t.howto}</details>` : "";
      p.innerHTML = `<h2>${W.mode === "exam" ? "Task " + (W.cur + 1) + " · " : ""}${esc(t.name)}</h2>` + how + t.desc + extra;
      $$("[data-h]", p).forEach((b) => (b.onclick = () => { const a = W.hints[W.cur] || (W.hints[W.cur] = []); const k = +b.dataset.h; if (!a.includes(k)) a.push(k); renderPaper(); }));
      const hw = $("details.howto", p); if (hw && exo) hw.ontoggle = () => { P.howto = hw.open; persist(); };
      const fr = $("[data-fr]", p); if (fr) fr.onclick = () => { W.fr = !W.fr; renderPaper(); };
      bindNote(p);
    } else if (W.side === "info") {
      const total = t.visible.length + t.hidden_n;
      const strat = ""; // examen = conditions réelles : aucun temps conseillé, AB gère son temps seul
      p.innerHTML = `<h2>${W.mode === "exam" ? "Task " + (W.cur + 1) + " · " : ""}${esc(t.name)}</h2>
        <p>Cette task est notée sur 100. Ta note dépend uniquement des tests réussis : ${t.visible.length} tests visibles avec RUN TESTS, et ${t.hidden_n} tests cachés qui comptent seulement au SUBMIT (${total} tests au total).</p>
        <p>Tu peux soumettre plusieurs fois : ta note est celle de ta dernière soumission.</p>${strat}
        <h4>Ton chrono</h4><p>Il suit l'heure réelle : il ne ralentit pas si tu changes d'onglet, et il continue si tu fermes la page. ${W.clock.mode === "strict" ? "Mode strict : pas de pause, comme le vrai test." : "Mode entraînement : pause et temps en plus permis (SETTINGS)."} À 0, l'examen se termine et tes dernières soumissions sont notées.</p>
        <h4>Raccourci</h4><p><code>Ctrl + Entrée</code> lance RUN TESTS.</p>`;
    } else {
      const c = W.clock;
      p.innerHTML = `<h2>Settings</h2><h4>Mode du chrono</h4><div class="opt"><button id="sStrict" class="${c.mode === "strict" ? "on" : ""}">Strict, comme le vrai test</button><button id="sTrain" class="${c.mode === "train" ? "on" : ""}">Entraînement, pause permise</button>${c.mode === "train" ? `<button id="sPause">${c.pausedLeft == null ? "Mettre en pause" : "Reprendre"}</button><button id="sAdd5">Ajouter 5 min</button><button id="sAdd10">Ajouter 10 min</button>` : ""}</div>${c.mode === "strict" ? `<p style="font-size:14px;color:var(--as-dim)">Passe en mode entraînement pour mettre en pause ou ajouter du temps.</p>` : ""}
        ${W.mode === "exam" && !exam(W.id).mini ? `<h4>Durée au départ</h4><div class="opt" style="grid-template-columns:repeat(3,1fr)">${[60, 70, 90].map((d) => `<button data-dur="${d}" class="${(P.dur || 70) === d ? "on" : ""}">${d} min</button>`).join("")}</div><p style="font-size:14px;color:var(--as-dim)">La durée choisie s'applique quand tu recommences.</p>` : ""}
        ${W.mode === "exo" ? `<h4>Fiche UMPIRE</h4><div class="opt"><button id="sUmp" class="${P.ump ? "on" : ""}">${P.ump ? "Affichée avant chaque exo (conseillé)" : "Masquée"}</button></div>` : ""}
        <h4>Parenthèses et guillemets</h4><div class="opt"><button id="sClose" class="${P.autoClose !== false ? "on" : ""}">${P.autoClose !== false ? "Fermés automatiquement : quand tu tapes ( , ) s'ajoute" : "Pas de fermeture automatique : tu tapes toi-même ( et )"}</button></div><p style="font-size:14px;color:var(--as-dim)">Clique pour changer. Dans les deux cas, quand ton curseur touche une parenthèse, sa jumelle s'éclaire en bleu. Une parenthèse seule s'éclaire en rouge.</p>
        <h4>${W.mode === "exam" ? "Examen" : "Exo"}</h4><div class="opt"><button id="sRestart">Recommencer depuis le début</button></div>`;
      const on = (id, f) => { const b = $("#" + id); if (b) b.onclick = f; };
      on("sAdd5", () => addTime(5)); on("sAdd10", () => addTime(10));
      on("sStrict", () => { setMode("strict"); renderPaper(); }); on("sTrain", () => { setMode("train"); renderPaper(); });
      on("sPause", () => { togglePause(); renderPaper(); });
      on("sUmp", () => { P.ump = !P.ump; persist(); renderPaper(); });
      on("sClose", () => { P.autoClose = P.autoClose === false; persist(); if (cm) cm.setOption("autoCloseBrackets", P.autoClose); renderPaper(); });
      on("sRestart", restart);
      $$("[data-dur]", p).forEach((b) => (b.onclick = () => { P.dur = +b.dataset.dur; persist(); renderPaper(); }));
    }
    p.scrollTop = 0;
  }

  /* ---- tests ---- */
  function tbl(o, ref, diff) {
    if (!o) return `<div class="val">-</div>`;
    if (!("columns" in o)) return `<div class="val ${diff && ref && !E.valEq(o.value, ref.value) ? "diff" : ""}">${esc(fmtVal(o.value))}</div>`;
    const bad = (i, j, c) => diff && ref && (!ref.rows || !ref.rows[i] || !E.valEq(c, ref.rows[i][j]));
    const colsBad = diff && ref && ref.columns && ref.columns.join("|") !== o.columns.join("|");
    return `<table class="gtab"><tr>${o.columns.map((c, j) => `<th class="${colsBad && ref.columns[j] !== c ? "diff" : ""}">${esc(c)}</th>`).join("")}</tr>${o.rows.map((r, i) => `<tr>${r.map((c, j) => `<td class="${bad(i, j, c) ? "diff" : ""}">${esc(fmtVal(c, "cell"))}</td>`).join("")}</tr>`).join("")}${o.rows.length ? "" : `<tr><td colspan="${o.columns.length || 1}" style="color:var(--as-dim)">(empty)</td></tr>`}</table>`;
  }
  function inputHtml(t, inp) {
    if (t.lang === "sql") return Object.entries(inp.tables).map(([n, tb]) => `<h5>${esc(n)}</h5>` + tbl({ columns: tb.columns.map((c) => c[0]), rows: tb.rows })).join("");
    return t.params.filter((p) => p !== "spark").map((p) => {
      const v = inp[p];
      if (v && typeof v === "object" && v.__df__) {
        const cols = v.__df__.schema.split(/,(?![^(]*\))/).map((s) => s.trim().split(/\s+/)[0].replace(/`/g, ""));
        return `<h5>${esc(p)}</h5>` + tbl({ columns: cols, rows: v.__df__.rows });
      }
      if (v && typeof v === "object" && v.__dir__) return `<h5>${esc(p)}</h5>` + Object.entries(v.__dir__).map(([f, c]) => `<div style="font:600 14px var(--f-mono);margin:8px 0 4px">${esc(p)}/${esc(f)}</div><pre class="exv">${esc(c)}</pre>`).join("");
      return `<h5>${esc(p)}</h5><div class="val">${esc(fmtVal(v))}</div>`;
    }).join("");
  }
  function verdict(r) {
    if (!r) return ["lock", "-"];
    if (r.pass) return ["ok", "Passed ✓"];
    if (r.tle) return ["ko", "Execution time limit exceeded ✗"];
    if (!r.ok) return ["ko", "Runtime error ✗"];
    return ["ko", "Wrong answer ✗"];
  }
  function renderTests() {
    const t = W.tasks[W.cur], R = W.results[W.cur], box = $("#tscroll");
    if (W.busy) return;
    if (!R) { box.innerHTML = `<div class="asm-status idle">Run sample tests to see output</div>`; return; }
    if (R.error) { box.innerHTML = `<div class="asm-status bad">⚠ ${esc(R.error)}</div>${R.retry ? '<button class="btn-blue" id="retryEnv">Rallumer et relancer</button>' : ""}`; const b = $("#retryEnv"); if (b) b.onclick = async () => { await prepare(true); runTests(R.sub); }; return; }
    const pass = R.res.filter((x) => x.pass).length, tot = R.res.length;
    let h = `<div class="asm-status ${pass === tot ? "good" : "bad"}">${pass === tot ? "✓" : "⚠"} Tests passed: ${pass}/${tot}.${R.sub ? `<span class="sub">Submitted · score ${R.score}/100</span>` : ""}</div>`;
    t.visible.forEach((x, i) => {
      const r = R.res[i], k = W.cur + "-" + i;
      if (W.open[k] == null) W.open[k] = !r.pass && !R.res.slice(0, i).some((y) => !y.pass);
      const pane = W.open[k + "p"] || "ret";
      const [cls, lab] = verdict(r);
      const ret = r.ok ? `<div class="twocol"><div><h5 class="blue">Expected return value</h5>${tbl(x.expected)}</div><div class="kbar v" data-split="two" role="separator" aria-orientation="vertical" tabindex="0" title="Glisse pour agrandir. Double-clic : taille d'origine."><i></i></div><div><h5 class="blue">Your return value</h5>${tbl(r.output, x.expected, W.showDiff)}</div></div>`
        : `<h5 class="blue">Expected return value</h5>${tbl(x.expected)}<h5 class="blue">Your return value</h5><div class="errbox">${esc(r.error)}</div>`;
      h += `<div class="tcase ${W.open[k] ? "" : "closed"}"><button data-k="${k}"><span class="car">▾</span>Test ${i + 1}<span class="res ${cls}">${lab}</span></button>
        <div class="tin"><nav><button data-p="${k}" data-v="in" class="${pane === "in" ? "on" : ""}">Input</button><button data-p="${k}" data-v="ret" class="${pane === "ret" ? "on" : ""}">Return Value</button><button data-p="${k}" data-v="con" class="${pane === "con" ? "on" : ""}">Console Output</button></nav><div class="kbar v" data-split="tin" role="separator" aria-orientation="vertical" tabindex="0" title="Glisse pour agrandir. Double-clic : taille d'origine."><i></i></div>
        <div class="pane">${pane === "in" ? inputHtml(t, x.input) : pane === "con" ? `<div class="val">${r.stdout ? esc(r.stdout) : "Empty"}</div>` : ret}</div></div></div>`;
    });
    if (R.sub) {
      R.res.slice(t.visible.length).forEach((r, j) => {
        const [cls, lab] = verdict(r);
        h += `<div class="tcase closed hiddenT"><button disabled><span class="car">▾</span>Test ${t.visible.length + j + 1} <span style="font-weight:500;color:var(--as-dim);font-size:15px">· hidden</span><span class="res ${cls}">${lab}</span></button></div>`;
      });
    }
    box.innerHTML = h;
    $$("[data-k]", box).forEach((b) => (b.onclick = () => { W.open[b.dataset.k] = !W.open[b.dataset.k]; renderTests(); }));
    $$("[data-p]", box).forEach((b) => (b.onclick = () => { W.open[b.dataset.p + "p"] = b.dataset.v; renderTests(); }));
  }
  function updScore() { $("#scoreb").textContent = taskScore(W.cur) + "/100"; }
  const slim = (r) => ({ pass: r.pass, ok: r.ok, tle: !!r.tle, error: r.error, stdout: r.stdout, output: r.output });

  async function runTests(submit) {
    if (!W.on || W.busy) return;
    if (W.clock.endsAt && left() <= 0 && !isOver()) return;
    const ti = W.cur, t = W.tasks[ti];
    const code = W.drafts[ti];
    const tests = submit ? t.visible.concat(hiddenOf(t)) : t.visible;
    W.busy = true;
    $("#run").disabled = true; $("#submit").disabled = true;
    $("#tscroll").innerHTML = `<div class="asm-status idle">${submit ? "Submitting… hidden tests running" : "Running tests…"}</div>`;
    let R;
    try {
      const res = await E.runTests(t, code, tests);
      const passed = res.filter((x) => x.pass).length;
      R = { sub: submit, res: res.map(slim), score: Math.round((100 * passed) / tests.length) };
    } catch (e) {
      R = { sub: false, error: e.message, retry: ["lost", "warming", "nokey", "port", "spark"].includes(e.code) && t.lang === "pyspark" };
      if (e.code === "nokey" || e.code === "badkey") R.error += " Va dans Connexion (bouton ? en bas).";
    }
    W.busy = false;
    $("#run").disabled = false; $("#submit").disabled = false;
    if (!W.on) return;
    W.results[ti] = R;
    if (submit && !R.error) {
      W.lastSub[ti] = R.score;
      if (W.mode === "exo") {
        recordTask(t.id, R.score);
        if (R.score < 80) recordErrors(t.tags);
        $("#showSol").hidden = !solOK(t.id);
      }
    }
    if (W.cur === ti) { renderTests(); updScore(); }
    renderTaskTabs();
    // Exo réussi à 100 : le chrono s'arrête et le résultat (note + temps) s'affiche
    if (submit && !R.error && W.mode === "exo" && R.score === 100 && !W.recorded) setTimeout(() => { if (W.on) finishScreen(true); }, 700);
    saveAttempt();
  }
  function taskScore(i) { return W.lastSub[i] || 0; }

  /* ---- chrono réel (heure de l'appareil) ---- */
  let tick = null;
  const isOver = () => W.mode === "exo" && !!W.clock.over;
  const elapsed = () => { const c = W.clock; return c.dur + (c.added || 0) - left(); };
  const fmtDur = (ms) => { const t = Math.max(0, Math.round(ms / 1000)); return Math.floor(t / 60) + " min " + pad(t % 60) + " s"; };
  const left = () => { const c = W.clock; return c.pausedLeft != null ? c.pausedLeft : c.endsAt ? c.endsAt - Date.now() : c.dur; };
  function fmtLeft(ms) { ms = Math.max(0, ms); if (ms >= 10 * 60000) return Math.ceil(ms / 60000) + "m left"; const t = Math.ceil(ms / 1000); return Math.floor(t / 60) + "m " + pad(t % 60) + "s left"; }
  function renderClock() {
    if (!W.on) return;
    const l = left(), c = W.clock;
    if (isOver()) { const t = Math.round(-l / 1000); $("#time").textContent = "Temps dépassé · +" + Math.floor(t / 60) + "m " + pad(t % 60) + "s"; $("#timer").classList.add("low"); return; }
    $("#time").textContent = (c.pausedLeft != null ? "Paused · " : "") + fmtLeft(l);
    $("#timer").classList.toggle("low", l < 5 * 60000);
    $("#timer").classList.toggle("paused", c.pausedLeft != null);
    if (c.endsAt && c.pausedLeft == null && l <= 0) { stopClock(); if (W.mode === "exo") overtimeAsk(); else finishScreen(true); }
  }
  function overtimeAsk() {
    const m = $("#modal"), b = $("#mbox");
    b.className = "box";
    b.innerHTML = `<h3>Temps écoulé</h3><p style="margin:0;color:var(--as-dim)">Les ${W.clock.baseMin} min prévues sont passées. Tu peux continuer avec ton code : le chrono compte le temps en plus, et à la fin tu verras combien de temps tu as mis au total.</p><div class="row2"><button id="mStop">Terminer maintenant</button><button class="primary" id="mGo">Continuer mon code</button></div>`;
    m.hidden = false;
    $("#mGo").onclick = () => { m.hidden = true; W.clock.over = true; clearInterval(tick); tick = setInterval(renderClock, 250); renderClock(); saveAttempt(); };
    $("#mStop").onclick = () => finishScreen(true);
  }
  function startClock(fresh) {
    const c = W.clock;
    if (fresh || (!c.endsAt && c.pausedLeft == null)) { c.endsAt = Date.now() + c.dur; c.pausedLeft = null; }
    clearInterval(tick); tick = setInterval(renderClock, 250); renderClock(); saveAttempt();
  }
  function stopClock() { clearInterval(tick); tick = null; }
  function addTime(min) { const c = W.clock; if (c.mode !== "train") return; c.added = (c.added || 0) + min * 60000; if (c.pausedLeft != null) c.pausedLeft += min * 60000; else if (c.endsAt) c.endsAt += min * 60000; renderClock(); saveAttempt(); }
  function setMode(m) { const c = W.clock; c.mode = m; if (m === "strict" && c.pausedLeft != null) { c.endsAt = Date.now() + c.pausedLeft; c.pausedLeft = null; } renderClock(); saveAttempt(); }
  function togglePause() { const c = W.clock; if (c.mode !== "train" || !c.endsAt) return; if (c.pausedLeft == null) c.pausedLeft = c.endsAt - Date.now(); else { c.endsAt = Date.now() + c.pausedLeft; c.pausedLeft = null; } renderClock(); saveAttempt(); }

  /* ---- préparation de l'environnement ---- */
  let pingT = null;
  async function prepare(resume) {
    const langs = new Set(W.tasks.map((t) => t.lang));
    const steps = [];
    if (langs.has("pyspark")) steps.push(["spark", "Allumage de ton Codespace et de Spark"]);
    if (langs.has("sql")) steps.push(["sql", "Démarrage de PostgreSQL"]);
    if (langs.has("python")) steps.push(["python", "Démarrage de Python"]);
    steps.push(["load", W.mode === "exam" ? "Chargement de l'examen" : "Chargement de l'exo"]);
    const ov = $("#ov"); ov.hidden = false;
    $("#ovt").textContent = "Préparation de l'environnement";
    $("#ovsub").textContent = resume ? "Ton chrono continue : il suit l'heure réelle." : "Le chrono démarre quand tout est prêt.";
    $("#ovextra").innerHTML = "";
    const state = {};
    const draw = (sub) => {
      $("#steps").innerHTML = steps.map(([k, n]) => `<div class="${state[k] === "done" ? "done" : state[k] === "cur" ? "cur" : ""}"><span class="dot"></span>${esc(n)}${state[k] === "cur" && k === "spark" && sub ? ` <span class="muted">· ${esc(sub)}</span>` : ""}</div>`).join("");
      $("#bar").style.width = Math.round((100 * steps.filter(([k]) => state[k] === "done").length) / steps.length) + "%";
    };
    draw();
    const jobs = [];
    let sparkErr = null;
    if (langs.has("pyspark")) {
      state.spark = "cur";
      jobs.push(E.ensureSpark((txt) => draw(txt)).then(() => { state.spark = "done"; draw(); }).catch((e) => { sparkErr = e; state.spark = "err"; draw(); }));
    }
    for (const l of ["sql", "python"]) if (langs.has(l)) { state[l] = "cur"; jobs.push(E.warm(l).then(() => { state[l] = "done"; draw(); }).catch(() => { state[l] = "done"; draw(); })); }
    draw();
    await Promise.all(jobs);
    if (!W.on) return;
    state.load = "done"; draw();
    if (sparkErr) {
      const e = sparkErr;
      const conn = ["nokey", "badkey", "perm"].includes(e.code);
      $("#ovt").textContent = "PySpark n'est pas prêt";
      $("#ovextra").innerHTML = `<p class="err">${esc(e.message)}</p>${e.code === "port" ? '<p class="muted" style="margin:0">Ouvre le Codespace une fois dans un nouvel onglet (il se connecte en 30 secondes), puis reviens ici et clique Réessayer.</p>' : ""}
        <div class="btnrow"><button class="pill sm" id="ovRetry">Réessayer</button>${e.webUrl || (e.cs && e.cs.web_url) ? `<a class="pill sm ghost" target="_blank" rel="noopener" href="${esc(e.webUrl || e.cs.web_url)}">Ouvrir le Codespace ↗</a>` : ""}${conn ? '<a class="pill sm ghost" href="#connexion">Connexion</a>' : ""}<button class="pill sm ghost" id="ovGo">Commencer quand même</button></div>
        <p class="muted" style="margin:0;font-size:13px">« Commencer quand même » : tu peux lire et écrire, mais les tests PySpark ne tourneront qu'une fois Spark prêt.</p>`;
      $("#ovRetry").onclick = () => prepare(resume);
      $("#ovGo").onclick = () => { ov.hidden = true; afterPrepare(resume); };
      return;
    }
    setTimeout(() => { if (!W.on) return; ov.hidden = true; afterPrepare(resume); }, 300);
  }
  function afterPrepare(resume) {
    clearInterval(pingT);
    if (W.tasks.some((t) => t.lang === "pyspark")) pingT = setInterval(E.ping, 90000);
    if (resume) { startClock(false); return; }
    if (W.mode === "exo" && P.ump && phaseUmp()) showUmpire(); else startClock(true);
  }
  const phaseUmp = () => true;
  function showUmpire() {
    const u = $("#umpire"); u.hidden = false;
    const t = W.tasks[0];
    u.innerHTML = `<div class="box"><div class="top"><h3>Avant de coder : UMPIRE, 2 min</h3>${minitimer("ump", 120)}</div>
      <p class="muted" style="margin:0">Lis l'énoncé à gauche, puis réponds en quelques mots. Ton chrono démarre quand tu cliques « Je commence ».</p>
      ${[["U", "Understand", "Entrée exacte, sortie exacte (colonnes, tri) ?"], ["M", "Match", "Quel réflexe ? (when, groupBy, Window, fichiers…)"], ["P", "Plan", "Les étapes, dans l'ordre"], ["E", "Evaluate", "Cas limites : null, vide, égalité, bornes"]].map(([k, n, ph]) => `<div class="row"><b>${k} · ${n}</b><textarea placeholder="${ph}"></textarea></div>`).join("")}
      <p class="muted" style="margin:0;font-size:13px">Implement et Review, c'est pendant et après le code : relis la consigne avant SUBMIT.</p>
      <div class="btnrow" style="justify-content:flex-end"><button class="btn-blue" id="umpGo">Je commence</button></div></div>`;
    bindMinitimer("ump");
    $("#umpB").click();
    $("#umpGo").onclick = () => { u.hidden = true; clearTimers(); startClock(true); cm.focus(); };
  }

  /* ---- fin ---- */
  function recordExam(eid, scores, restarted) {
    const e = P.exams[eid] || (P.exams[eid] = { hist: [] });
    e.hist.push({ at: today(), ts: Date.now(), scores, strict: W.clock && W.clock.mode === "strict", min: W.clock && W.clock.baseMin, restarted: !!restarted, mini: !!exam(eid).mini });
    e.hist = e.hist.slice(-30);
    persist();
  }
  function finishScreen(timeUp) {
    const m = $("#modal"), b = $("#mbox");
    if (!timeUp && W.clock.endsAt && (left() > 0 || isOver())) {
      b.className = "box";
      b.innerHTML = `<h3>${W.mode === "exam" ? "Finish test?" : "Terminer l'exo ?"}</h3><p style="margin:0;color:var(--as-dim)">${isOver() ? "Temps total : " + fmtDur(elapsed()) + "." : "Il te reste " + fmtLeft(left()) + "."} ${W.mode === "exam" ? "Les tasks non soumises comptent 0." : "Ta note est celle de ta dernière soumission."}</p><div class="row2"><button id="mNo">Continuer</button><button class="primary" id="mYes">${W.mode === "exam" ? "Finish test" : "Terminer"}</button></div>`;
      m.hidden = false; $("#mNo").onclick = () => (m.hidden = true); $("#mYes").onclick = () => finishScreen(true);
      return;
    }
    stopClock();
    const scores = W.tasks.map((_, i) => taskScore(i));
    if (!W.recorded) {
      W.recorded = true;
      if (W.mode === "exam") {
        recordExam(W.id, scores);
        W.tasks.forEach((t, i) => { if (scores[i] < 80) { recordTask(t.id, scores[i]); recordErrors(t.tags); } else recordTask(t.id, scores[i]); });
      } else if (W.lastSub[0] == null) {
        recordTask(W.tasks[0].id, 0);
      }
    }
    save(LSA, null);
    const hash = (W.mode === "exam" ? "exam-" : "exo-") + W.id;
    const insess = P.cur && (inSessionStep(hash) || isMiniOfStep(W.id));
    const over = isOver(), took = W.mode === "exo" && W.clock.endsAt ? elapsed() : null;
    const outOfTime = W.clock.endsAt && left() <= 0 && !over;
    if (took != null && P.tasks[W.id]) { P.tasks[W.id].lastTime = took; persist(); }
    if (W.mode === "exo") { P.ended = P.ended || {}; P.ended[W.id] = Date.now(); persist(); }
    // Marge : un exo ne part en révision que s'il dépasse le temps prévu de plus de 2 min (ou 10 % si c'est plus)
    const baseMs = W.clock.baseMin * 60000, tolMs = Math.max(120000, Math.round(baseMs * 0.1));
    const slow = W.mode === "exo" && took != null && took > baseMs + tolMs;
    const inTol = W.mode === "exo" && took != null && took > baseMs && !slow;
    if (slow) slowReview(W.id);
    const revSoon = W.mode === "exo" && (slow || scores[0] < 80);
    const dayHere = inDay(W.mode, W.id);
    b.className = "box";
    b.innerHTML = `<h3>${outOfTime ? "Time is up" : "Résultat"}</h3>${W.tasks.map((t, i) => `<div class="r"><span>${W.mode === "exam" ? "Task " + (i + 1) + " · " : ""}${esc(t.name)}</span><b>${scores[i]}/100</b></div>`).join("")}
      ${took != null ? `<div class="r"><span>Ton temps</span><b>${fmtDur(took)}${took > W.clock.baseMin * 60000 ? " (prévu " + W.clock.baseMin + " min)" : ""}</b></div>` : ""}
      <p style="margin:0;color:var(--as-dim);font-size:14px">${W.mode === "exam" ? "L'analyse guidée te montre le corrigé de chaque task et t'aide à comprendre tes erreurs." : scores[0] >= 80 ? (slow ? "Réussi, mais plus de " + Math.round(tolMs / 60000) + " min au-delà du temps prévu : cet exo reviendra en révision dans " + INTERVALS[0] + " séances, pour le refaire plus vite." : inTol ? "Réussi, dans la marge de temps (jusqu'à " + Math.round(tolMs / 60000) + " min de plus). Pas de révision." : "Réussi (80 ou plus).") : solOK(W.id) ? "Sous 80 : cet exo reviendra en révision dans 2 séances. Regarde le corrigé, puis refais-le de mémoire." : "Sous 80 : recommence, tu peux y arriver. Le corrigé s'ouvre après 2 essais."}</p>
      ${W.mode === "exo" ? `<div class="mynote${revSoon ? " hot" : ""}"><b>Ta fiche sur cet exo, avec tes mots</b><p>${revSoon ? (dayHere && scores[0] < 80 ? "Écris au moins une ligne : l'exo est alors coché dans ta séance, et il reviendra en révision avec ta fiche." : "Écris-la maintenant, quand c'est frais : elle reviendra avec l'exo en révision.") : "Optionnel : 3 lignes pour t'en souvenir dans 2 mois."}</p>${noteForm(W.id)}</div>` : ""}
      <div class="row2"><button id="mBack">Retour au site</button>${W.mode === "exo" ? '<button id="mKeep">Recommencer avec mon code</button><button id="mAgain">Recommencer à zéro</button>' : '<button id="mAgain">Recommencer</button>'}${W.mode === "exo" ? (solOK(W.id) ? '<button id="mSol">Voir le corrigé</button>' : "") : `<button ${insess || dayHere ? "" : 'class="primary"'} id="mAna">Analyse guidée</button>`}${dayHere ? '<button class="primary" id="mDay">Retour à la séance</button>' : ""}${insess ? `<button class="primary" id="mNext">${isMiniOfStep(W.id) ? "Retour à la leçon" : esc(nextLabel())}</button>` : ""}</div>`;
    m.hidden = false;
    bindNote(b);
    $("#mBack").onclick = () => { m.hidden = true; closeWorkspace(); goHash(P.cur ? "accueil" : backHash()); };
    if ($("#mDay")) $("#mDay").onclick = () => { m.hidden = true; closeWorkspace(); goHash("accueil"); };
    $("#mAgain").onclick = () => { m.hidden = true; restart(true); };
    if ($("#mKeep")) $("#mKeep").onclick = () => { m.hidden = true; restart(true, true); };
    if ($("#mSol")) $("#mSol").onclick = () => showSolution();
    if ($("#mAna")) $("#mAna").onclick = () => { m.hidden = true; closeWorkspace(); goHash("analyse-" + W.id); };
    if ($("#mNext")) $("#mNext").onclick = () => { m.hidden = true; closeWorkspace(); if (isMiniOfStep(W.id)) goHash("reflexe-" + findSession(P.cur.id).steps[P.cur.step].reflex); else sessNext(); };
  }
  function isMiniOfStep(tid) {
    if (!P.cur) return false;
    const st = findSession(P.cur.id).steps[P.cur.step];
    return st.type === "learn" && reflex(st.reflex).mini === tid;
  }
  function showSolution() {
    const t = W.tasks[W.cur], m = $("#modal"), b = $("#mbox");
    const sub = Object.keys(W.lastSub).length > 0;
    if (!sub && W.clock.endsAt && (left() > 0 || isOver()) && !confirm("Tu n'as pas encore soumis. Regarder le corrigé maintenant ? (Conseil : soumets d'abord, même incomplet.)")) return;
    if (W.mode === "exo") {
      P.solSeen[t.id] = Date.now();
      if (!P.review.some((r) => r.task === t.id)) P.review.push({ task: t.id, stage: 0, due: P.sessCount + INTERVALS[0] });
      persist();
    }
    b.className = "box wide";
    b.innerHTML = `<h3>Corrigé · ${esc(t.name)}</h3>${corrigeHtml(t)}<p style="margin:0;color:var(--as-dim);font-size:14px">Ne le recopie pas : ferme-le et réécris la solution de mémoire, puis SUBMIT.</p><div class="row2"><button class="primary" id="mClose">Fermer</button></div>`;
    m.hidden = false; $("#mClose").onclick = () => { m.hidden = true; if (!W.clock.endsAt || (left() <= 0 && !isOver())) finishScreen(true); };
  }
  function restart(noConfirm, keep) {
    if (!noConfirm && !confirm("Recommencer depuis le début ? Ton code actuel sera remis à zéro. Tes notes passées restent dans ta Progression.")) return;
    keepDrafts = keep ? { key: W.key, drafts: W.drafts.slice() } : null;
    if (W.mode === "exam" && !W.recorded && Object.keys(W.lastSub).length) { recordExam(W.id, W.tasks.map((_, i) => taskScore(i)), true); W.recorded = true; }
    const mode = W.mode, id = W.id;
    save(LSA, null); W.on = false;
    openWorkspace(mode, id, true);
  }

  /* ---- boutons fixes de l'espace d'examen ---- */
  function bindWorkspace() {
    $$(".asm-side button").forEach((b) => (b.onclick = () => { W.side = b.dataset.side; $$(".asm-side button").forEach((x) => x.classList.toggle("on", x === b)); renderPaper(); }));
    $("#run").onclick = () => runTests(false);
    $("#submit").onclick = () => runTests(true);
    $("#diff").onclick = () => { W.showDiff = !W.showDiff; $("#diff").textContent = W.showDiff ? "HIDE DIFF" : "VIEW DIFF"; renderTests(); };
    $("#moreBtn").onclick = () => { const d = $("#morebox"); d.hidden = !d.hidden; $("#moreBtn").setAttribute("aria-expanded", String(!d.hidden)); };
    $("#restart").onclick = () => { $("#morebox").hidden = true; restart(); };
    $("#restartKeep").onclick = () => { $("#morebox").hidden = true; restart(true, true); };
    $("#finish").onclick = () => { $("#morebox").hidden = true; finishScreen(false); };
    $("#stopExo").onclick = () => finishScreen(true);
    $("#showSol").onclick = () => { $("#morebox").hidden = true; showSolution(); };
    $("#leave").onclick = () => {
      saveAttempt();
      const running = W.clock.endsAt && (left() > 0 || isOver());
      if (running && !confirm("Quitter l'espace ? Ton code est gardé et le chrono continue (il suit l'heure réelle). Tu pourras reprendre.")) return;
      closeWorkspace();
      goHash(P.cur ? "accueil" : backHash());
    };
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") $("#morebox").hidden = true; });
    window.addEventListener("beforeunload", saveAttempt);
  }

  /* ============================================================ barre de séance + routage */
  function renderSessbar(asm) {
    const bar = $("#sessbar");
    bar.hidden = !P.cur || asm;
    if (!P.cur) return;
    const s = findSession(P.cur.id);
    $("#sdots").innerHTML = s.steps.map((_, i) => `<i class="${i <= P.cur.step ? "on" : ""}"></i>`).join("");
    $("#stxt").textContent = "Séance " + (s.si + 1) + " · Étape " + (P.cur.step + 1) + " sur " + s.steps.length + " : " + s.steps[P.cur.step].title;
    const here = inSessionStep((location.hash || "#").slice(1));
    $("#snext").textContent = here ? nextLabel() : "Revenir à l'étape " + (P.cur.step + 1);
    $("#snext").onclick = () => (here ? sessNext() : goHash(stepHash(s.steps[P.cur.step])));
  }
  /* ============================================================ lire la consigne */
  let rdTimer = null;
  function shuffled(a) { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; }
  function rdP(id) { return (CAT.read || []).find((d) => d.id === id); }
  function renderReadList() {
    const L = CAT.read || [];
    P.read = P.read || {};
    const done = L.filter((d) => P.read[d.id]).length;
    const next = L.find((d) => !P.read[d.id]);
    view().innerHTML = `<section class="ws on">${band("Lire la consigne", `<p class="lead" style="padding-bottom:28px">Le jour J, la difficulté est souvent de comprendre l'énoncé, pas d'écrire le code. Chaque exo : un long énoncé en anglais au format du test, puis 4 questions qui vérifient que tu as bien lu. 8 minutes, une fois par semaine.</p>`, bib("lire"))}
      <div class="wrap"><div class="sect">
        <div class="card" style="margin-bottom:20px"><div class="btnrow" style="justify-content:space-between"><div><b>${done} exo${done > 1 ? "s" : ""} sur ${L.length} faits</b><br><span class="muted">Méthode : lis tout une fois, puis souligne chaque règle et chaque mot-piège avant de répondre.</span></div>${next ? `<a class="pill" href="#lire-${next.id}">Continuer : ${esc(next.title)}</a>` : ""}</div></div>
        <div class="grid3">${L.map((d, i) => {
          const r = P.read[d.id];
          return `<div class="ex"><span class="src">Exo ${i + 1}</span><h3>${esc(d.title)}</h3><span class="muted">${esc(d.focus)}</span>${r ? `<span class="done-badge">Meilleur score : ${r.best}/${d.questions.length}</span>` : ""}<a class="pill sm" href="#lire-${d.id}">Ouvrir</a></div>`;
        }).join("")}</div>
      </div></div></section>`;
  }
  function renderRead(id) {
    const d = rdP(id);
    if (!d) return goHash("lire");
    P.read = P.read || {};
    const L = CAT.read, i = L.indexOf(d);
    if (rdTimer) clearInterval(rdTimer);
    const t0 = Date.now(), total = 8 * 60;
    const qs = d.questions.map((q, k) => `<div class="card rd-q" data-q="${k}"><b>${k + 1}. ${esc(q.q)}</b>
        <div class="rd-opts">${shuffled(q.o.map((o, j) => [o, j])).map(([o, j]) => `<label class="rd-opt"><input type="radio" name="q${k}" value="${j}"> <span>${esc(o)}</span></label>`).join("")}</div>
        <div class="rd-why" hidden></div></div>`).join("");
    view().innerHTML = `<section class="ws on">${band(esc(d.title), `<p class="lead" style="padding-bottom:28px">${esc(d.focus)}. Lis l'énoncé comme le jour J, puis réponds sans relire le code d'une task.</p>`, bib("lire"))}
      <div class="wrap"><div class="sect">
        <div class="btnrow" style="justify-content:space-between;margin-bottom:12px"><span class="chip">Exo ${i + 1} sur ${L.length} · 8 min conseillées</span><b id="rdClock">8:00</b></div>
        <div class="card rd-text">${d.text}</div>
        <h3 style="margin:22px 0 10px">Les questions</h3>
        ${qs}
        <div class="btnrow" style="margin-top:16px"><button class="pill" id="rdCheck">Vérifier mes réponses</button><span id="rdScore" class="muted"></span></div>
        <div class="card" id="rdKeys" hidden style="margin-top:18px;background:var(--mint-soft);border-color:transparent"><h3>Les mots-pièges à retenir</h3><ul>${d.keys.map((k) => `<li>${esc(k)}</li>`).join("")}</ul></div>
        <div class="btnrow" style="margin-top:18px">${L[i + 1] ? `<a class="pill sm ghost" href="#lire-${L[i + 1].id}">Exo suivant : ${esc(L[i + 1].title)}</a>` : ""}<a class="pill sm ghost" href="#lire">Tous les exos</a></div>
      </div></div></section>`;
    rdTimer = setInterval(() => {
      const el = $("#rdClock");
      if (!el) { clearInterval(rdTimer); rdTimer = null; return; }
      const left = total - Math.floor((Date.now() - t0) / 1000);
      el.textContent = left >= 0 ? Math.floor(left / 60) + ":" + String(left % 60).padStart(2, "0") : "Temps conseillé dépassé";
      el.style.color = left < 60 ? "var(--bad, #c0392b)" : "";
    }, 1000);
    $("#rdCheck").onclick = () => {
      let ok = 0, miss = 0;
      d.questions.forEach((q, k) => {
        const box = view().querySelector(`.rd-q[data-q="${k}"]`);
        const sel = box.querySelector("input:checked");
        if (!sel) { miss++; return; }
        const good = +sel.value === q.a;
        if (good) ok++;
        box.classList.toggle("ok", good); box.classList.toggle("ko", !good);
        const why = box.querySelector(".rd-why");
        why.hidden = false;
        why.innerHTML = (good ? "<b>✓ Juste.</b> " : `<b>✗ Réponse : ${esc(q.o[q.a])}.</b> `) + esc(q.why);
      });
      if (miss) { $("#rdScore").textContent = "Réponds aux " + miss + " question" + (miss > 1 ? "s" : "") + " restante" + (miss > 1 ? "s" : "") + " avant de vérifier."; return; }
      if (rdTimer) { clearInterval(rdTimer); rdTimer = null; }
      const prev = P.read[d.id];
      P.read[d.id] = { best: Math.max(ok, prev ? prev.best : 0), last: ok, at: today() };
      persist();
      $("#rdScore").textContent = `Score : ${ok}/${d.questions.length}. ` + (ok === d.questions.length ? "Parfait, tu as lu comme il faut." : "Relis les phrases des réponses ratées : c'est exactement là que se cachent les tests.");
      $("#rdKeys").hidden = false;
      view().querySelectorAll(".rd-opt input").forEach((x) => (x.disabled = true));
    };
  }
  /* ============================================================ parcours DSA */
  function dsaP(id) { return (CAT.dsa || []).find((d) => d.id === id); }
  function dsaDone(d) { return d.exos.filter((t) => P.tasks[t] && P.tasks[t].best >= 80).length; }
  function dsaCardsOn(d) { return d.cards.every((_, j) => P.cards[d.id + "-" + j]); }
  function renderDsaList() {
    const L = CAT.dsa || [];
    const done = L.filter((d) => dsaDone(d) === d.exos.length).length;
    const next = L.find((d) => dsaDone(d) < d.exos.length);
    view().innerHTML = `<section class="ws on">${band("DSA", `<p class="lead" style="padding-bottom:28px">Les 13 patterns que tout informaticien doit connaître, reliés au data engineering. Chaque pattern : une fiche, un exemple guidé, les pièges, puis 2 exos vérifiés. Rythme conseillé : un pattern par semaine, dans un créneau de 30 min.</p>`, bib("dsa"))}
      <div class="wrap"><div class="sect">
        <div class="card" style="margin-bottom:20px"><div class="btnrow" style="justify-content:space-between"><div><b>${done} pattern${done > 1 ? "s" : ""} sur ${L.length} maîtrisé${done > 1 ? "s" : ""}</b><br><span class="muted">Un pattern est maîtrisé quand ses 2 exos ont au moins 80/100.</span></div>${next ? `<a class="pill" href="#dsa-${next.id}">Continuer : ${esc(next.title)}</a>` : ""}</div></div>
        <div class="grid3">${L.map((d, i) => {
          const n = dsaDone(d);
          return `<div class="ex"><span class="src">Pattern ${i + 1}</span><h3>${esc(d.title)}</h3><span class="muted">${esc(d.why)}</span>${n ? `<span class="done-badge">${n === d.exos.length ? "✓ maîtrisé" : n + " exo sur " + d.exos.length + " réussi"}</span>` : ""}<a class="pill sm" href="#dsa-${d.id}">Ouvrir</a></div>`;
        }).join("")}</div>
      </div></div></section>`;
  }
  function renderDsa(id) {
    const d = dsaP(id);
    if (!d) return goHash("dsa");
    const L = CAT.dsa, i = L.indexOf(d);
    const toc = L.map((x, k) => `<a href="#dsa-${x.id}" class="${x.id === id ? "on" : ""}">${esc(x.title)} <span>${k + 1}</span></a>`).join("");
    const exo = (t) => { const m = CAT.tasks[t] || {}, s = P.tasks[t]; return `<div class="btnrow" style="margin-top:8px"><a class="pill sm" href="#exo-${t}">${esc(m.name || t)} · ${m.minutes || 15} min</a>${s ? `<span class="muted">Ta meilleure note : ${s.best}/100</span>` : ""}</div>`; };
    view().innerHTML = `<section class="ws on">${band(esc(d.title), `<p class="lead" style="padding-bottom:28px">${esc(d.why)}</p>`, bib("dsa"))}
      <div class="wrap"><div class="sect learn"><aside class="toc"><span class="lbl">Patterns DSA</span>${toc}</aside>
      <div class="panel lesson"><span class="chip">Pattern ${i + 1} sur ${L.length} · Python</span>
        <div class="reveal" style="margin-top:14px"><b>En data engineering :</b> ${esc(d.de)}</div>
        <h2 style="font-size:28px;margin:18px 0 10px">La fiche</h2>
        <ul>${d.body.map((x) => `<li>${x}</li>`).join("")}</ul>
        <h3 style="margin-top:18px">Exemple guidé</h3><p class="muted" style="margin:0 0 8px">Lis-le, puis réécris-le de mémoire sur papier avant de faire les exos.</p>${codeBlock(d.code)}
        <h3>Les pièges</h3><ul class="traps">${d.traps.map((x) => `<li>${x}</li>`).join("")}</ul>
        <div class="card" style="margin-top:20px;background:var(--mint-soft);border-color:transparent">
          <h3>Les 2 exos · avec les vrais tests</h3>
          <p class="muted" style="margin:0 0 6px">Avant de coder : dis à voix haute le pattern et la complexité visée. Les indices sont dans l'énoncé si tu bloques.</p>
          ${d.exos.map(exo).join("")}
        </div>
        <div class="btnrow" style="margin-top:20px">${dsaCardsOn(d) ? `<span class="done-badge" style="color:var(--ok)">✓ Ses ${d.cards.length} cartes sont dans tes révisions</span>` : `<button class="pill sm ghost" id="dsaCards">Ajouter ses ${d.cards.length} cartes à mes révisions</button>`}
          ${L[i + 1] ? `<a class="pill sm" href="#dsa-${L[i + 1].id}">Pattern suivant : ${esc(L[i + 1].title)}</a>` : ""}</div>
      </div></div></div></section>`;
    const b = $("#dsaCards");
    if (b) b.onclick = () => { d.cards.forEach((_, j) => { const k = d.id + "-" + j; if (!P.cards[k]) P.cards[k] = { due: P.sessCount + 1, lvl: 0 }; }); persist(); renderDsa(id); };
  }

  /* ============================================================ live coding */
  const LSL = "kata.live";
  const REC = { mr: null, chunks: [], url: null, name: "", stream: null, t0: 0 };
  function liveQ(id) { return ((CAT.live || {}).questions || []).find((q) => q.id === id); }
  function liveHist(id) { return (P.live || []).filter((h) => h.id === id); }
  function recBox() {
    const on = REC.mr && REC.mr.state === "recording";
    const can = !!(navigator.mediaDevices && window.MediaRecorder);
    return `<div class="card lv-rec"><div class="lv-rec-row"><b>${on ? '<span class="lv-dot"></span>Enregistrement en cours' : "Enregistre ta voix"}</b>
      ${can ? `<button class="pill sm ${on ? "ghost" : ""}" id="lvRec">${on ? "Arrêter l'enregistrement" : "Démarrer l'enregistrement"}</button>` : `<span class="muted">Ton navigateur ne permet pas l'enregistrement ici : utilise le dictaphone de ton téléphone.</span>`}</div>
      <p class="muted" style="margin:8px 0 0;font-size:14px">L'audio reste sur ton appareil, rien n'est envoyé. Réécoute-le après : on entend tout de suite les silences et les phrases floues.</p>
      ${REC.url && !on ? `<audio controls src="${REC.url}" style="width:100%;margin-top:12px"></audio><a class="pill sm ghost" style="margin-top:10px" download="${REC.name}" href="${REC.url}">Télécharger l'audio</a>` : ""}</div>`;
  }
  async function toggleRec(redraw) {
    if (REC.mr && REC.mr.state === "recording") { REC.mr.stop(); return; }
    try {
      REC.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (e) { alert("Micro refusé ou indisponible. Autorise le micro pour ce site, ou enregistre-toi avec ton téléphone."); return; }
    REC.chunks = []; REC.mr = new MediaRecorder(REC.stream);
    REC.mr.ondataavailable = (e) => { if (e.data.size) REC.chunks.push(e.data); };
    REC.mr.onstop = () => {
      if (REC.url) URL.revokeObjectURL(REC.url);
      const type = REC.mr.mimeType || "audio/webm";
      REC.url = URL.createObjectURL(new Blob(REC.chunks, { type }));
      REC.name = "live-coding-" + today() + (type.includes("mp4") ? ".m4a" : ".webm");
      REC.stream.getTracks().forEach((t) => t.stop());
      redraw();
    };
    REC.mr.start(1000); redraw();
  }
  function renderLiveList() {
    const L = CAT.live;
    if (!L) return goHash("accueil");
    const hist = (P.live || []).slice().reverse();
    view().innerHTML = `<section class="ws on">${band("Live coding", `<p class="lead" style="padding-bottom:28px">Après le test en ligne viennent l'entretien RH, le live coding, puis l'entretien final. Ici tu t'entraînes au live : une consigne dite à l'oral, tu clarifies, tu annonces ton plan, tu codes en parlant, puis tu réponds aux relances. Une fois par semaine, 40 min, et tu t'enregistres.</p>`)}
      <div class="wrap"><div class="sect">${flash ? `<p class="sc-done" style="margin:0 0 16px">✓ ${esc(flash)}</p>` : ""}
        <div class="card" style="margin-bottom:20px"><h3 style="margin-bottom:10px">Comment ça se passe</h3>
          <ol class="lv-how">${L.phases.map((p) => `<li><b>${esc(p.title)} · ${p.min} min.</b> ${esc(p.say)}</li>`).join("")}</ol>
          <div class="btnrow" style="margin-top:14px"><button class="pill" id="lvRand">Tirer une question au hasard</button><span class="muted">La consigne est en anglais, comme en entretien. Réponds en anglais si tu peux, sinon en français.</span></div></div>
        <div class="grid3">${L.questions.map((q) => {
          const h = liveHist(q.id), last = h[h.length - 1];
          return `<div class="ex"><span class="src">${esc(q.lang)}</span><h3>${esc(q.title)}</h3><span class="muted">${esc(q.prompt.slice(0, 120))}${q.prompt.length > 120 ? "…" : ""}</span>${last ? `<span class="done-badge">✓ fait ${h.length} fois · dernière grille ${last.score}/${L.rubric.length}</span>` : ""}<a class="pill sm" href="#live-${q.id}">Commencer</a></div>`;
        }).join("")}</div>
        ${hist.length ? `<div class="card" style="margin-top:20px"><h3 style="margin-bottom:10px">Tes lives</h3><table class="tbl"><tr><th>Date</th><th>Question</th><th>Grille</th><th>À améliorer</th></tr>${hist.slice(0, 20).map((h) => `<tr><td>${esc(h.at)}</td><td>${esc((liveQ(h.id) || {}).title || h.id)}</td><td>${h.score}/${L.rubric.length}</td><td>${esc(h.note || "")}</td></tr>`).join("")}</table></div>` : ""}
      </div></div></section>`;
    flash = "";
    $("#lvRand").onclick = () => {
      const qs = L.questions, n = (q) => liveHist(q.id).length, min = Math.min(...qs.map(n));
      const pool = qs.filter((q) => n(q) === min);
      goHash("live-" + pool[Math.floor(Math.random() * pool.length)].id);
    };
  }
  function renderLive(id) {
    const L = CAT.live, q = L && liveQ(id);
    if (!q) return goHash("live");
    let run = load(LSL, null);
    if (!run || run.id !== id) { run = { id, phase: 0, ends: Date.now() + L.phases[0].min * 60000, t0: Date.now(), fu: 0, shown: {} }; save(LSL, run); }
    const task = CAT.tasks[q.task] || {};
    const draw = () => {
      clearTimers();
      const end = run.phase >= L.phases.length;
      const ph = L.phases[Math.min(run.phase, L.phases.length - 1)];
      const steps = L.phases.map((p, i) => `<span class="lv-step ${i < run.phase ? "done" : i === run.phase ? "on" : ""}">${i + 1}. ${esc(p.title)} <small>${p.min} min</small></span>`).join("") + `<span class="lv-step ${end ? "on" : ""}">Bilan</span>`;
      const quote = `<blockquote class="lv-quote"><span class="lbl">L'intervieweur</span>${esc(q.prompt)}</blockquote>`;
      let body = "";
      if (end) {
        body = `<h3>Bilan : coche ce qui est vrai, honnêtement</h3><div class="lv-rubric">${L.rubric.map((r, i) => `<label><input type="checkbox" data-r="${i}"> ${esc(r)}</label>`).join("")}</div>
          <label class="field" style="margin-top:12px"><span>La chose que je ferai mieux au prochain live</span><textarea id="lvNote" rows="2" placeholder="Ex. : annoncer la complexité avant de coder"></textarea></label>
          <div class="btnrow" style="margin-top:12px"><button class="pill" id="lvSave">Enregistrer mon bilan</button></div>`;
      } else if (ph.id === "clarify") {
        body = quote + `<p class="muted">Ne lis pas encore l'énoncé complet. Pose tes questions à voix haute, comme si l'intervieweur était en face.</p>
          <button class="pill sm ghost" id="lvShowQ">${run.shown.clarify ? "Masquer" : "Voir"} les questions qu'un bon candidat pose</button>
          ${run.shown.clarify ? `<ul class="lv-qa">${q.clarify.map(([a, b]) => `<li><b>${esc(a)}</b><br><span class="muted">${esc(b)}</span></li>`).join("")}</ul>` : ""}`;
      } else if (ph.id === "plan") {
        body = quote + `<ul class="lv-check"><li><b>U</b>nderstand : reformule en une phrase.</li><li><b>M</b>atch : quel pattern (fenêtre, tas, pile, BFS, îlots, jointure as-of…) ?</li><li><b>P</b>lan : les étapes, dans l'ordre, à voix haute.</li><li>Annonce la complexité en temps et en mémoire.</li><li>Demande « Est-ce que ce plan vous va ? » avant de coder.</li></ul>`;
      } else if (ph.id === "code") {
        body = quote + `<p>Code dans l'éditeur avec les vrais tests. Il s'ouvre dans un nouvel onglet : garde cet onglet pour le chrono et l'enregistrement.</p>
          <div class="btnrow"><a class="pill" href="#exo-${q.task}" target="_blank" rel="noopener">Ouvrir l'éditeur : ${esc(task.name || q.task)}</a></div>
          <p class="muted" style="margin-top:10px">Parle en codant : « je groupe par…, je trie par… parce que… ». Un silence de plus de 30 secondes, c'est le signal pour dire où tu en es.</p>`;
      } else if (ph.id === "test") {
        body = quote + `<ul class="lv-check"><li>Déroule ton code à la main sur l'exemple, ligne par ligne.</li><li>Un cas vide ou nul : que renvoie ton code ?</li><li>Un cas d'égalité ou de doublon : quel départage ?</li><li>Lance les tests seulement maintenant, et commente chaque échec à voix haute.</li></ul>`;
      } else {
        const f = q.followups, k = Math.min(run.fu, f.length - 1);
        body = `<p class="muted">Relance ${k + 1} sur ${f.length}. Réponds à voix haute avant de regarder les points clés.</p>
          <blockquote class="lv-quote"><span class="lbl">L'intervieweur</span>${esc(f[k][0])}</blockquote>
          ${run.shown["f" + k] ? `<div class="reveal">${esc(f[k][1])}</div>` : `<button class="pill sm ghost" id="lvShowF">Voir les points clés d'une bonne réponse</button>`}
          ${k < f.length - 1 ? `<div class="btnrow" style="margin-top:12px"><button class="pill sm" id="lvNextF">Relance suivante</button></div>` : ""}`;
      }
      view().innerHTML = `<section class="ws on">${band("Live · " + esc(q.title), `<p class="lead" style="padding-bottom:28px">${esc(q.lang)} · 40 min · tout à voix haute</p>`, `<div class="biblinks"><a href="#live">‹ Toutes les questions</a></div>`)}
        <div class="wrap"><div class="sect">
          <div class="lv-steps">${steps}</div>
          <div class="lv-grid"><div class="card">
            ${end ? "" : `<div class="lv-head"><div><span class="eyebrow">Phase ${run.phase + 1} sur ${L.phases.length}</span><h2 style="margin:4px 0 6px">${esc(ph.title)}</h2><p class="muted" style="margin:0">${esc(ph.say)}</p></div><div class="lv-clock" id="lvClock">--:--</div></div>`}
            <div class="lv-body">${body}</div>
            <div class="btnrow" style="margin-top:20px">${run.phase > 0 ? `<button class="pill sm ghost" id="lvPrev">Phase précédente</button>` : ""}${end ? "" : `<button class="pill sm" id="lvNext">${run.phase === L.phases.length - 1 ? "Terminer et faire mon bilan" : "Phase suivante : " + esc(L.phases[run.phase + 1].title)}</button>`}<button class="pill sm ghost" id="lvReset">Recommencer</button></div>
          </div><div>${recBox()}<div class="card" style="margin-top:16px"><span class="muted" style="font-size:14px">Temps total</span><div class="lv-total" id="lvTotal">0 min</div></div></div></div>
        </div></div></section>`;
      const tick = () => {
        const c = $("#lvClock"); if (c) {
          const left = Math.round((run.ends - Date.now()) / 1000), a = Math.abs(left);
          c.textContent = (left < 0 ? "+" : "") + pad(Math.floor(a / 60)) + ":" + pad(a % 60);
          c.classList.toggle("over", left < 0);
        }
        const t = $("#lvTotal"); if (t) t.textContent = Math.floor((Date.now() - run.t0) / 60000) + " min";
      };
      tick(); const iv = setInterval(tick, 1000); timers.push(() => clearInterval(iv));
      const go = (i) => { run.phase = i; run.ends = Date.now() + (L.phases[i] ? L.phases[i].min * 60000 : 0); save(LSL, run); draw(); };
      const on = (s, f) => { const e = $(s); if (e) e.onclick = f; };
      on("#lvNext", () => go(run.phase + 1));
      on("#lvPrev", () => go(run.phase - 1));
      on("#lvReset", () => { if (confirm("Recommencer ce live depuis le début ?")) { run = { id, phase: 0, ends: Date.now() + L.phases[0].min * 60000, t0: Date.now(), fu: 0, shown: {} }; save(LSL, run); draw(); } });
      on("#lvShowQ", () => { run.shown.clarify = !run.shown.clarify; save(LSL, run); draw(); });
      on("#lvShowF", () => { run.shown["f" + Math.min(run.fu, q.followups.length - 1)] = true; save(LSL, run); draw(); });
      on("#lvNextF", () => { run.fu++; save(LSL, run); draw(); });
      on("#lvRec", () => toggleRec(draw));
      on("#lvSave", () => {
        const score = $$("[data-r]").filter((x) => x.checked).length;
        (P.live = P.live || []).push({ at: today(), id, score, note: ($("#lvNote").value || "").trim().slice(0, 200), min: Math.round((Date.now() - run.t0) / 60000) });
        markDay(); persist(); save(LSL, null);
        flash = "Live enregistré. Réécoute ton audio aujourd'hui, et note une phrase que tu dirais autrement.";
        goHash("live");
      });
    };
    draw();
  }

  function route() {
    clearTimers();
    let h = (location.hash || "#accueil").slice(1);
    let m;
    const asm = /^(exam|exo)-/.test(h);
    $("#v-examen").classList.toggle("on", asm);
    document.body.classList.toggle("in-asm", asm);
    const nv = /^(exos|pratiquer)/.test(h) ? "pratiquer" : /^(examens|analyse-)/.test(h) ? "examens" : /^(fiche|apprendre|reflexe-|dsa|lire|live|progression|guide)/.test(h) ? "fiches" : h === "connexion" ? "connexion" : "accueil";
    $$("[data-nav]").forEach((a) => a.classList.toggle("on", a.dataset.nav === nv));
    $("#streakN").textContent = streak() + (streak() > 1 ? " jours" : " jour");
    renderSessbar(asm);
    renderAlerts();
    if (!asm && W.on) closeWorkspace();
    if (!asm) window.scrollTo(0, 0);
    if ((m = h.match(/^exam-(\w+)$/))) return openWorkspace("exam", m[1]);
    if ((m = h.match(/^exo-(\w+)$/))) return openWorkspace("exo", m[1]);
    if ((m = h.match(/^reflexe-(\w+)$/))) return renderLesson(m[1]);
    if ((m = h.match(/^analyse-(\w+)$/))) return renderAnalysis(m[1]);
    if (h === "seance") return goHash("accueil");
    if (h === "parcours") return renderParcours();
    if ((m = h.match(/^fiche-(pyspark|sql|python)(?:-(\w+))?$/))) return renderFiche(m[1], m[2]);
    if (h === "fiches") return renderFiches();
    if (h === "pratiquer") return renderPratiquer();
    if (h === "revision") return renderRevision();
    if (h === "exos") return renderPratiquer();
    if (h === "examens") return renderExams();
    if (h === "apprendre") return renderReflexes();
    if (h === "progression") return renderProgress();
    if (h === "connexion") return renderConnexion();
    if ((m = h.match(/^live-(\w+)$/))) return renderLive(m[1]);
    if (h === "live") return renderLiveList();
    if (h === "guide") return renderGuide();
    if ((m = h.match(/^dsa-(\w+)$/))) return renderDsa(m[1]);
    if (h === "dsa") return renderDsaList();
    if ((m = h.match(/^lire-(\w+)$/))) return renderRead(m[1]);
    if (h === "lire") return renderReadList();
    renderHome();
  }

  /* ============================================================ zones redimensionnables (glisser les barres) */
  // Chaque barre [data-split] règle une variable CSS posée sur <html> ; la taille est gardée dans ce navigateur.
  const SPLITS = {
    paper: { v: "--paper-w", axis: "x", min: 220, max: () => { const r = $(".asm-body").getBoundingClientRect(), side = $(".asm-side").getBoundingClientRect().width; return r.width - side - 12 - 340; } },
    ed: { v: "--ed-h", axis: "y", min: 90, max: () => (window.innerWidth > 760 ? $(".asm-right").getBoundingClientRect().height - 12 - 90 : 1400) },
    files: { v: "--files-w", axis: "x", min: 80, max: () => Math.max(220, $(".asm-ed").getBoundingClientRect().width - 200) },
    tin: { v: "--tin-w", axis: "x", min: 100, max: (bar) => bar.parentElement.getBoundingClientRect().width - 180 },
    two: { v: "--two-l", axis: "x", min: 100, max: (bar) => bar.parentElement.getBoundingClientRect().width - 110 },
  };
  const PANES_K = "kata.panes";
  let PANES = {};
  try { PANES = JSON.parse(localStorage.getItem(PANES_K) || "{}") || {}; } catch (_) {}
  function applyPanes() {
    const root = document.documentElement.style;
    for (const k in SPLITS) { if (PANES[k]) root.setProperty(SPLITS[k].v, PANES[k] + "px"); else root.removeProperty(SPLITS[k].v); }
  }
  function savePanes() { try { localStorage.setItem(PANES_K, JSON.stringify(PANES)); } catch (_) {} }
  let paneRaf = 0;
  function refreshCM() { if (paneRaf) return; paneRaf = requestAnimationFrame(() => { paneRaf = 0; if (cm) cm.refresh(); }); }
  function setPane(k, bar, size) {
    const S = SPLITS[k];
    let max = S.max(bar);
    if (!(max > S.min)) max = S.min;
    PANES[k] = Math.round(Math.max(S.min, Math.min(max, size)));
    applyPanes(); refreshCM();
  }
  function bindSplitters() {
    applyPanes();
    document.addEventListener("pointerdown", (e) => {
      const bar = e.target.closest && e.target.closest("[data-split]");
      if (!bar || e.button !== 0) return;
      const k = bar.dataset.split, S = SPLITS[k];
      const prev = bar.previousElementSibling;
      if (!S || !prev) return;
      e.preventDefault();
      try { bar.setPointerCapture(e.pointerId); } catch (_) {}
      bar.classList.add("dragging"); document.body.classList.add(S.axis === "x" ? "resizing-x" : "resizing-y");
      const start = prev.getBoundingClientRect();
      const move = (ev) => setPane(k, bar, S.axis === "x" ? ev.clientX - start.left : ev.clientY - start.top);
      const up = () => {
        bar.removeEventListener("pointermove", move); bar.removeEventListener("pointerup", up); bar.removeEventListener("pointercancel", up);
        bar.classList.remove("dragging"); document.body.classList.remove("resizing-x", "resizing-y");
        savePanes(); refreshCM();
      };
      bar.addEventListener("pointermove", move); bar.addEventListener("pointerup", up); bar.addEventListener("pointercancel", up);
    });
    document.addEventListener("dblclick", (e) => {
      const bar = e.target.closest && e.target.closest("[data-split]");
      if (!bar) return;
      delete PANES[bar.dataset.split]; applyPanes(); savePanes(); refreshCM();
    });
    document.addEventListener("keydown", (e) => {
      const bar = e.target.closest && e.target.closest("[data-split]");
      if (!bar) return;
      const k = bar.dataset.split, S = SPLITS[k], prev = bar.previousElementSibling;
      const less = S.axis === "x" ? "ArrowLeft" : "ArrowUp", more = S.axis === "x" ? "ArrowRight" : "ArrowDown";
      if (e.key !== less && e.key !== more) return;
      e.preventDefault();
      const r = prev.getBoundingClientRect();
      setPane(k, bar, (S.axis === "x" ? r.width : r.height) + (e.key === more ? 30 : -30));
      savePanes();
    });
    window.addEventListener("resize", refreshCM);
  }

  async function init() {
    try {
      CAT = await (await fetch("content/catalog.json", { cache: "no-cache" })).json();
    } catch (e) {
      view().innerHTML = `<div class="wrap"><p class="alert ko">Le site n'a pas pu charger ses exercices. Vérifie ta connexion puis recharge la page.</p></div>`;
      return;
    }
    TITLE = Object.fromEntries(Object.entries(CAT.tasks).map(([k, v]) => [k, v.name]));
    buildOrder();
    seedMethodCards(); persist();
    bindWorkspace();
    bindSplitters();
    window.addEventListener("hashchange", route);
    route();
  }
  init();
})();
