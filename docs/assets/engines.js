/* Kata Lab : moteurs de correction.
   - Python : Pyodide dans un Web Worker (dans la page)
   - SQL    : PGlite (PostgreSQL) dans un Web Worker (dans la page)
   - PySpark: le Codespace de l'élève, allumé par l'API GitHub, qui fait tourner runner/server.py
*/
(function () {
  "use strict";
  const REPO = "gitabdelhub/kata-lab";
  const PORT = 8765;
  const LS_KEY = "kata.key";
  const LS_EXP = "kata.keyExpiry";
  const SS_SPARK = "kata.spark";

  /* ------------------------------------------------------------ comparaison */
  const isNum = (x) => typeof x === "number";
  function valEq(a, b) {
    if (a === null || a === undefined || b === null || b === undefined) return (a === null || a === undefined) && (b === null || b === undefined);
    if (isNum(a) && isNum(b)) return Math.abs(a - b) <= 1e-6 * Math.max(1, Math.abs(b));
    if (typeof a === "boolean" || typeof b === "boolean") return a === b;
    if (Array.isArray(a) && Array.isArray(b)) return a.length === b.length && a.every((x, i) => valEq(x, b[i]));
    if (typeof a === "object" && typeof b === "object") {
      const ka = Object.keys(a).sort(), kb = Object.keys(b).sort();
      return ka.length === kb.length && ka.every((k, i) => k === kb[i] && valEq(a[k], b[k]));
    }
    return a === b;
  }
  const canon = (row) => JSON.stringify(row, (k, v) => (v && typeof v === "object" && !Array.isArray(v) ? Object.keys(v).sort().reduce((o, x) => ((o[x] = v[x]), o), {}) : v));
  function outEq(got, exp, ordered) {
    if (!got) return false;
    if ("value" in exp) return "value" in got && valEq(got.value, exp.value);
    if (!got.columns || got.columns.length !== exp.columns.length || got.columns.some((c, i) => c !== exp.columns[i])) return false;
    let a = got.rows, b = exp.rows;
    if (a.length !== b.length) return false;
    if (!ordered) {
      const s = (r) => r.slice().sort((x, y) => (canon(x) < canon(y) ? -1 : canon(x) > canon(y) ? 1 : 0));
      a = s(a); b = s(b);
    }
    return a.every((r, i) => valEq(r, b[i]));
  }

  /* ------------------------------------------------------------ workers */
  function makeWorker(url, type) {
    const st = { w: null, ready: null, pending: new Map(), seq: 0 };
    st.start = () => {
      if (st.w) return st.ready;
      const w = (st.w = type === "module" ? new Worker(url, { type: "module" }) : new Worker(url));
      let started = false;
      st.ready = new Promise((res, rej) => {
        w.onmessage = (e) => {
          const m = e.data;
          if (m.type === "ready") { started = true; return res(); }
          if (m.type === "fatal") return rej(new Error(m.error));
          const p = st.pending.get(m.id);
          if (p) { st.pending.delete(m.id); clearTimeout(p.timer); p.res(m.result); }
        };
        w.onerror = (e) => {
          if (e && e.preventDefault) e.preventDefault();
          if (!started) return rej(new Error(e.message || "worker error"));
          // Le moteur a planté après son démarrage : on le jette, il redémarre au prochain RUN
          if (st.w === w) st.kill("Le moteur s'est arrêté. Relance RUN TESTS : il redémarre tout seul.");
        };
      });
      // Démarrage raté (réseau, mémoire...) : on oublie ce worker pour pouvoir réessayer
      st.ready.catch(() => { if (st.w === w) st.kill(); });
      return st.ready;
    };
    st.kill = (why) => {
      if (st.w) st.w.terminate();
      st.w = null; st.ready = null;
      for (const p of st.pending.values()) { clearTimeout(p.timer); p.res({ ok: false, error: why || "Arrêté", stdout: "" }); }
      st.pending.clear();
    };
    st.call = async (msg, limitS) => {
      // 2 essais de démarrage avant d'abandonner
      try { await st.start(); }
      catch (e1) {
        try { await st.start(); }
        catch (e2) { return { ok: false, error: "Le moteur n'a pas pu démarrer (" + (e2.message || "worker error") + "). Relance RUN TESTS ; si ça continue, recharge la page : ton code est gardé.", stdout: "" }; }
      }
      const id = ++st.seq;
      return new Promise((res) => {
        const timer = setTimeout(() => {
          st.pending.delete(id);
          st.kill(); // relance au prochain appel
          res({ ok: false, tle: true, error: "Execution time limit exceeded (" + limitS + " s)", stdout: "" });
        }, limitS * 1000 + 1500);
        st.pending.set(id, { res, timer });
        st.w.postMessage(Object.assign({ id }, msg));
      });
    };
    return st;
  }
  const base = document.currentScript ? new URL(".", document.currentScript.src).href : "assets/";
  const PY = makeWorker(base + "py-worker.js", "classic");
  const SQL = makeWorker(base + "sql-worker.js", "module");

  function sqlLit(v) {
    if (v === null || v === undefined) return "NULL";
    if (typeof v === "boolean") return v ? "TRUE" : "FALSE";
    if (typeof v === "number") return String(v);
    return "'" + String(v).replace(/'/g, "''") + "'";
  }
  function sqlSetup(tables) {
    const parts = [];
    for (const [name, t] of Object.entries(tables)) {
      parts.push(`CREATE TABLE ${name} (${t.columns.map(([c, ty]) => c + " " + ty).join(", ")});`);
      if (t.rows.length) parts.push(`INSERT INTO ${name} VALUES\n` + t.rows.map((r) => "(" + r.map(sqlLit).join(", ") + ")").join(",\n") + ";");
    }
    return parts.join("\n");
  }

  /* ------------------------------------------------------------ Codespace */
  const Key = {
    get: () => { try { return localStorage.getItem(LS_KEY) || ""; } catch (_) { return ""; } },
    set: (k) => { try { localStorage.setItem(LS_KEY, k.trim()); } catch (_) {} },
    clear: () => { try { localStorage.removeItem(LS_KEY); } catch (_) {} },
    expiry: () => { try { return localStorage.getItem(LS_EXP) || ""; } catch (_) { return ""; } },
    setExpiry: (d) => { try { localStorage.setItem(LS_EXP, d || ""); } catch (_) {} },
  };
  class KataError extends Error { constructor(code, msg, extra) { super(msg); this.code = code; Object.assign(this, extra || {}); } }

  async function gh(path, opt) {
    opt = opt || {};
    const key = Key.get();
    if (!key) throw new KataError("nokey", "Aucune clé GitHub enregistrée.");
    const headers = { Authorization: "Bearer " + key, Accept: "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28" };
    if (opt.body) headers["Content-Type"] = "application/json";
    let r;
    try {
      r = await fetch("https://api.github.com" + path, { method: opt.method || "GET", headers, body: opt.body ? JSON.stringify(opt.body) : undefined });
    } catch (e) {
      throw new KataError("network", "Pas de connexion à GitHub. Vérifie ton internet.");
    }
    const txt = await r.text();
    let j = {};
    try { j = txt ? JSON.parse(txt) : {}; } catch (_) {}
    if (!r.ok) {
      if (r.status === 401) throw new KataError("badkey", "GitHub refuse ta clé : elle est fausse ou expirée. Crée une nouvelle clé dans Connexion.");
      if (r.status === 403 || r.status === 404) throw new KataError("perm", "Ta clé n'a pas la permission nécessaire (" + (j.message || r.status) + "). Vérifie les permissions dans Connexion.", { status: r.status, path });
      throw new KataError("api", "GitHub : " + (j.message || "erreur " + r.status), { status: r.status });
    }
    return j;
  }
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const portUrl = (cs) => "https://" + cs.name + "-" + PORT + ".app.github.dev";

  async function findCodespace() {
    const j = await gh(`/repos/${REPO}/codespaces`);
    const list = (j.codespaces || []).filter((c) => !c.repository || c.repository.full_name === REPO);
    list.sort((a, b) => (b.last_used_at || "").localeCompare(a.last_used_at || ""));
    return list[0] || null;
  }
  async function createCodespace() {
    const body = { ref: "main", idle_timeout_minutes: 120, retention_period_minutes: 43200, display_name: "kata-lab", devcontainer_path: ".devcontainer/devcontainer.json" };
    try {
      return await gh(`/repos/${REPO}/codespaces`, { method: "POST", body });
    } catch (e) {
      if (e.code === "api" || e.code === "perm") {
        body.machine = "basicLinux32gb";
        return await gh(`/repos/${REPO}/codespaces`, { method: "POST", body });
      }
      throw e;
    }
  }
  async function health(url, ms) {
    const ctl = new AbortController();
    const t = setTimeout(() => ctl.abort(), ms || 8000);
    try {
      const r = await fetch(url + "/health", { headers: { "X-Tunnel-Skip-AntiPhishing-Page": "true" }, signal: ctl.signal, cache: "no-store" });
      if (!r.ok) return null;
      return await r.json();
    } catch (_) { return null; } finally { clearTimeout(t); }
  }
  function cached() { try { return JSON.parse(sessionStorage.getItem(SS_SPARK) || "null"); } catch (_) { return null; } }
  function saveCache(c) { try { sessionStorage.setItem(SS_SPARK, JSON.stringify(c)); } catch (_) {} }

  /* Allume le Codespace si besoin et attend que Spark réponde.
     onStep(texte, fraction) sert à l'écran "Préparation de l'environnement". */
  async function ensureSpark(onStep) {
    onStep = onStep || (() => {});
    const c = cached();
    if (c && c.url) {
      const h = await health(c.url, 5000);
      if (h && h.ready) return c;
    }
    onStep("Recherche de ton Codespace", 0.05);
    let cs = await findCodespace();
    let first = false;
    if (!cs) {
      first = true;
      onStep("Création de ton Codespace (la première fois : environ 5 minutes)", 0.1);
      cs = await createCodespace();
    }
    const t0 = Date.now();
    let started = false;
    for (;;) {
      cs = await gh(`/user/codespaces/${cs.name}`);
      const st = cs.state;
      if (st === "Available") break;
      if ((st === "Shutdown" || st === "ShuttingDown") && !started) {
        if (st === "Shutdown") {
          onStep("Allumage de ton Codespace", 0.2);
          await gh(`/user/codespaces/${cs.name}/start`, { method: "POST" });
          started = true;
        }
      } else if (st === "Failed" || st === "Deleted" || st === "Unavailable") {
        throw new KataError("csfail", "Le Codespace est en erreur (" + st + "). Va dans Connexion et clique « Recréer le Codespace ».", { cs });
      } else {
        onStep(first ? "Construction du Codespace (" + st + ")" : "Allumage de ton Codespace (" + st + ")", first ? 0.25 : 0.3);
      }
      if (Date.now() - t0 > 12 * 60000) throw new KataError("cstimeout", "Le Codespace met trop de temps à démarrer. Réessaie dans une minute.", { cs });
      await sleep(3000);
    }
    const url = portUrl(cs);
    onStep("Démarrage de Spark", 0.6);
    const t1 = Date.now();
    for (;;) {
      const h = await health(url, 6000);
      if (h && h.ready) break;
      if (h && h.error) throw new KataError("spark", "Spark n'a pas pu démarrer : " + h.error, { cs });
      if (h) onStep("Démarrage de Spark (la JVM chauffe)", 0.8);
      const waited = Date.now() - t1;
      if (waited > (first ? 8 : 4) * 60000) {
        throw new KataError("port", "Le Codespace est allumé mais le serveur de correction ne répond pas encore.", { cs, webUrl: cs.web_url });
      }
      await sleep(3000);
    }
    const out = { url, name: cs.name, webUrl: cs.web_url, at: Date.now() };
    saveCache(out);
    onStep("Spark est prêt", 1);
    return out;
  }
  async function stopCodespace() {
    const c = cached();
    let name = c && c.name;
    if (!name) { const cs = await findCodespace(); name = cs && cs.name; }
    if (!name) return false;
    await gh(`/user/codespaces/${name}/stop`, { method: "POST" });
    saveCache(null);
    return true;
  }
  async function deleteCodespace() {
    const cs = await findCodespace();
    if (!cs) return false;
    await gh(`/user/codespaces/${cs.name}`, { method: "DELETE" });
    saveCache(null);
    return true;
  }
  async function codespaceStatus() {
    const cs = await findCodespace();
    if (!cs) return { exists: false };
    const h = cs.state === "Available" ? await health(portUrl(cs), 5000) : null;
    return { exists: true, name: cs.name, state: cs.state, webUrl: cs.web_url, runner: h, lastUsed: cs.last_used_at };
  }
  async function whoami() { return gh("/user"); }
  function ping() { const c = cached(); if (c && c.url) health(c.url, 5000); }

  async function sparkRun(task, code, tests) {
    let c = cached();
    if (!c) c = await ensureSpark();
    const body = { code, entry: task.entry, params: task.params, tests: tests.map((t) => ({ input: t.input })), limit_s: task.limit_s };
    const ctl = new AbortController();
    const timer = setTimeout(() => ctl.abort(), (task.limit_s * tests.length + 60) * 1000);
    let r;
    try {
      r = await fetch(c.url + "/run", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Kata-Key": Key.get(), "X-Tunnel-Skip-AntiPhishing-Page": "true" },
        body: JSON.stringify(body), signal: ctl.signal,
      });
    } catch (e) {
      saveCache(null);
      throw new KataError("lost", "Le Codespace ne répond plus (il s'est peut-être éteint). Relance les tests : le site va le rallumer.");
    } finally { clearTimeout(timer); }
    const j = await r.json().catch(() => ({}));
    if (r.status === 401) throw new KataError("badkey", j.error || "Clé refusée par le Codespace.");
    if (r.status === 503) throw new KataError("warming", j.error || "Spark démarre encore.");
    if (!r.ok) throw new KataError("runner", j.error || "Erreur du serveur de correction (" + r.status + ")");
    return j.results;
  }

  /* ------------------------------------------------------------ API publique */
  async function runTests(task, code, tests, onProgress) {
    // Certaines tasks ajoutent un petit code caché après celui de l'élève (API simulée, plusieurs sorties)
    // Tasks « projet » : fichiers mis bout à bout, imports locaux (package pipeline) retirés
    if (task.project && task.lang !== "sql") code = code.replace(/^[ \t]*(from[ \t]+pipeline(\.\w+)*[ \t]+import[^\n]*|import[ \t]+pipeline[^\n]*)$/gm, "");
    if (task.wrapper && task.lang !== "sql") code = code + "\n\n" + task.wrapper;
    onProgress = onProgress || (() => {});
    let results = [];
    if (task.lang === "pyspark") {
      results = await sparkRun(task, code, tests);
    } else if (task.lang === "sql") {
      for (let i = 0; i < tests.length; i++) {
        onProgress(i, tests.length);
        results.push(await SQL.call({ setup: sqlSetup(tests[i].input.tables), code }, task.limit_s));
      }
    } else {
      for (let i = 0; i < tests.length; i++) {
        onProgress(i, tests.length);
        results.push(await PY.call({ code, entry: task.entry, params: task.params, input: tests[i].input }, task.limit_s));
      }
    }
    return results.map((r, i) => Object.assign(r, { pass: !!r.ok && outEq(r.output, tests[i].expected, task.ordered) }));
  }
  function warm(lang) { return lang === "sql" ? SQL.start() : lang === "python" ? PY.start() : Promise.resolve(); }

  window.KataEngines = {
    runTests, warm, ensureSpark, stopCodespace, deleteCodespace, codespaceStatus, whoami, ping, Key, KataError,
    valEq, outEq, sqlSetup, hasSparkCache: () => !!cached(), REPO,
  };
})();
