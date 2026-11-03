/* Exécute le code Python de l'élève dans Pyodide (Python 3 dans le navigateur). */
importScripts("../vendor/pyodide/pyodide.js");
const HARNESS = `
import json, sys, io, math, traceback

def _norm(v):
    if isinstance(v, float):
        if math.isnan(v): return "NaN"
        if math.isinf(v): return "Infinity" if v > 0 else "-Infinity"
        return v
    if isinstance(v, (list, tuple)): return [_norm(x) for x in v]
    if isinstance(v, (set, frozenset)):
        try: return sorted(_norm(x) for x in v)
        except TypeError: return [_norm(x) for x in v]
    if isinstance(v, dict): return {str(k): _norm(x) for k, x in v.items()}
    if v is None or isinstance(v, (bool, int, str)): return v
    return str(v)

def kata_run(code, entry, params_json, input_json):
    params = json.loads(params_json); inp = json.loads(input_json)
    out = io.StringIO(); old = sys.stdout; sys.stdout = out
    r = {}
    try:
        ns = {"__name__": "solution"}
        exec(compile(code, "<solution>", "exec"), ns)
        if entry not in ns:
            raise NameError("La fonction %s() est introuvable dans ton code." % entry)
        res = ns[entry](*[inp[p] for p in params])
        r = {"ok": True, "output": {"value": _norm(res)}}
    except BaseException as e:
        tb = traceback.format_exception(type(e), e, e.__traceback__)
        keep = [l for l in tb if 'File "<solution>"' in l or not l.startswith("  File")]
        r = {"ok": False, "error": "".join(keep)[-2500:]}
    finally:
        sys.stdout = old
    r["stdout"] = out.getvalue()[-4000:]
    return json.dumps(r)
`;
let py = null;
const ready = (async () => {
  py = await loadPyodide({ indexURL: new URL("../vendor/pyodide/", self.location).href });
  py.runPython(HARNESS);
  postMessage({ type: "ready" });
})().catch(e => postMessage({ type: "fatal", error: String(e) }));

onmessage = async (e) => {
  await ready;
  const { id, code, entry, params, input } = e.data;
  const t0 = performance.now();
  let res;
  try {
    res = JSON.parse(py.globals.get("kata_run")(code, entry, JSON.stringify(params), JSON.stringify(input)));
  } catch (err) {
    res = { ok: false, error: String(err), stdout: "" };
  }
  res.ms = Math.round(performance.now() - t0);
  postMessage({ id, result: res });
};
