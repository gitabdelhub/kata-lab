/* Exécute la requête de l'élève dans PGlite (vrai PostgreSQL compilé pour le navigateur). */
import { PGlite } from "../vendor/pglite/index.js";

const keep = (v) => v;
const num = (v) => (v === null ? null : Number(v));
let db = null;
const ready = (async () => {
  db = await PGlite.create({
    parsers: { 1082: keep, 1083: keep, 1114: keep, 1184: keep, 1700: num, 20: num, 1186: keep },
  });
  await db.exec("SET TIME ZONE 'UTC';");
  postMessage({ type: "ready" });
})().catch((e) => postMessage({ type: "fatal", error: String(e) }));

onmessage = async (e) => {
  await ready;
  const { id, setup, code } = e.data;
  const t0 = performance.now();
  let result;
  try {
    await db.exec("DROP SCHEMA IF EXISTS kt CASCADE; CREATE SCHEMA kt; SET search_path TO kt;");
    await db.exec(setup);
    const res = await db.exec(code, { rowMode: "array" });
    let last = null;
    for (const r of res) if (r.fields && r.fields.length) last = r;
    if (!last) throw new Error("Ta requête ne renvoie aucune table. Il manque peut-être le SELECT final.");
    result = { ok: true, output: { columns: last.fields.map((f) => f.name), rows: last.rows.map((r) => Array.from(r)) } };
  } catch (err) {
    result = { ok: false, error: String((err && err.message) || err) };
    try { await db.exec("ROLLBACK;"); } catch (_) {}
  }
  try { await db.exec("SET search_path TO public; DROP SCHEMA IF EXISTS kt CASCADE;"); } catch (_) {}
  result.ms = Math.round(performance.now() - t0);
  result.stdout = "";
  postMessage({ id, result });
};
