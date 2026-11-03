"""Construit docs/content/ à partir de content_src/.

Pour chaque task : exécute la solution de référence sur toutes les entrées de
test (vrai Spark local, vrai PostgreSQL 16, Python 3), enregistre les sorties
attendues, vérifie que chaque "mutant" (erreur fréquente) échoue au moins un
test, et que le code de départ ne passe pas tout.

    /home/user/venv/bin/python tools/build.py [id_task ...]

Variables : KATA_PG="host=/tmp port=5433 user=postgres dbname=postgres"
"""
import base64
import datetime as dt
import decimal
import importlib.util
import io
import contextlib
import json
import math
import os
import sys
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "content_src"))
sys.path.insert(0, os.path.join(ROOT, "runner"))
OUT = os.path.join(ROOT, "docs", "content")
PG = os.environ.get("KATA_PG", "host=/tmp port=5433 user=postgres dbname=postgres")

_spark = None


def spark():
    global _spark
    if _spark is None:
        from pyspark.sql import SparkSession

        _spark = (SparkSession.builder.master("local[2]").config("spark.ui.enabled", "false")
                  .config("spark.sql.shuffle.partitions", "2").config("spark.sql.session.timeZone", "UTC").config("spark.ui.showConsoleProgress", "false")
                  .getOrCreate())
        _spark.sparkContext.setLogLevel("ERROR")
    return _spark


# ---------------- comparaison (même règle que docs/assets/engines.js) ----------------
def is_num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def val_eq(a, b):
    if a is None or b is None:
        return a is None and b is None
    if is_num(a) and is_num(b):
        return abs(a - b) <= 1e-6 * max(1.0, abs(b))
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b or a == b and type(a) is type(b)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(val_eq(x, y) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return set(a) == set(b) and all(val_eq(a[k], b[k]) for k in a)
    return a == b


def canon(row):
    return json.dumps(row, sort_keys=True, default=str)


def out_eq(got, exp, ordered):
    if got is None:
        return False
    if "value" in exp:
        return "value" in got and val_eq(got["value"], exp["value"])
    if "columns" not in got or got["columns"] != exp["columns"]:
        return False
    a, b = got["rows"], exp["rows"]
    if len(a) != len(b):
        return False
    if not ordered:
        a, b = sorted(a, key=canon), sorted(b, key=canon)
    return all(val_eq(x, y) for x, y in zip(a, b))


# ---------------- moteurs ----------------
def pnorm(v):
    if isinstance(v, float) and math.isnan(v):
        return "NaN"
    if isinstance(v, (list, tuple)):
        return [pnorm(x) for x in v]
    if isinstance(v, (set, frozenset)):
        return sorted(pnorm(x) for x in v)
    if isinstance(v, dict):
        return {str(k): pnorm(x) for k, x in v.items()}
    return v


def run_python(code, entry, params, inp):
    ns = {"__name__": "solution"}
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(code, "<solution>", "exec"), ns)
        res = ns[entry](*[json.loads(json.dumps(inp[p])) for p in params])
    return {"value": pnorm(res)}


def sql_lit(v):
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def sql_setup(tabs):
    parts = []
    for name, t in tabs.items():
        cols = ", ".join(f"{c} {typ}" for c, typ in t["columns"])
        parts.append(f"CREATE TABLE {name} ({cols});")
        if t["rows"]:
            vals = ",\n".join("(" + ", ".join(sql_lit(v) for v in r) + ")" for r in t["rows"])
            parts.append(f"INSERT INTO {name} VALUES\n{vals};")
    return "\n".join(parts)


def snorm(v):
    if isinstance(v, decimal.Decimal):
        return float(v)
    if isinstance(v, dt.datetime):
        return v.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(v, dt.date):
        return v.isoformat()
    if v is None or isinstance(v, (bool, int, float, str)):
        return v
    raise TypeError(f"type SQL non géré dans une sortie : {type(v).__name__} ({v!r})")


_pg = None


def run_sql(code, inp):
    global _pg
    import psycopg

    if _pg is None:
        _pg = psycopg.connect(PG, autocommit=True)
    cur = _pg.cursor()
    cur.execute("DROP SCHEMA IF EXISTS kt CASCADE; CREATE SCHEMA kt; SET search_path TO kt;")
    cur.execute(sql_setup(inp["tables"]))
    cur.execute(code)
    last = None
    while True:
        if cur.description is not None:
            last = ([d.name for d in cur.description], [[snorm(x) for x in r] for r in cur.fetchall()])
        if not cur.nextset():
            break
    cur.execute("SET search_path TO public; DROP SCHEMA IF EXISTS kt CASCADE;")
    if last is None:
        raise RuntimeError("la requête ne renvoie aucune table")
    return {"columns": last[0], "rows": last[1]}


def run_pyspark(code, entry, params, inp):
    import tempfile
    import shutil
    import server  # runner/server.py : même construction des entrées et même normalisation

    s = spark()
    tmp = tempfile.mkdtemp(prefix="kbuild_")
    try:
        ns = {"__name__": "solution"}
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(code, "<solution>", "exec"), ns)
            res = ns[entry](*server.build_args(s, params, inp, tmp))
            if hasattr(res, "collect") and hasattr(res, "columns"):
                return server.df_to_table(res)
            return {"value": server.norm(res)}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def run(task, code, inp):
    lang = task["lang"]
    if task.get("wrapper") and lang != "sql":
        code = code + "\n\n" + task["wrapper"]
    if lang == "python":
        return run_python(code, task["entry"], task["params"], inp)
    if lang == "sql":
        return run_sql(code, inp)
    return run_pyspark(code, task["entry"], task["params"], inp)


def safe_run(task, code, inp):
    try:
        return run(task, code, inp)
    except Exception:
        return None


def esc(x):
    return str(x).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def cell(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (list, dict)):
        return esc(json.dumps(v, ensure_ascii=False))
    return esc(v)


def html_table(cols, rows):
    head = "".join(f"<th>{esc(c)}</th>" for c in cols)
    body = "".join("<tr>" + "".join(f"<td>{cell(v)}</td>" for v in r) + "</tr>" for r in rows)
    return f'<div class="tblw"><table><tr>{head}</tr>{body}</table></div>'


def html_value(v):
    return f"<pre class=\"exv\">{esc(json.dumps(v, ensure_ascii=False))}</pre>"


def render_input(task, inp):
    out = []
    if task["lang"] == "sql":
        for name, t in inp["tables"].items():
            out.append(f"<p>Table <code>{esc(name)}</code>:</p>" + html_table([c for c, _ in t["columns"]], t["rows"]))
        return "".join(out)
    for p in task["params"]:
        if p == "spark":
            continue
        v = inp[p]
        if isinstance(v, dict) and "__df__" in v:
            cols = [c.strip().split()[0].strip("`") for c in split_ddl(v["__df__"]["schema"])]
            out.append(f"<p><code>{esc(p)}</code>:</p>" + html_table(cols, v["__df__"]["rows"]))
        elif isinstance(v, dict) and "__dir__" in v:
            files = "".join(f"<p class=\"exf\"><code>{esc(p)}/{esc(k)}</code></p><pre class=\"exv\">{esc(c)}</pre>"
                            for k, c in v["__dir__"].items())
            out.append(files)
        else:
            out.append(f"<p><code>{esc(p)} = {esc(json.dumps(v, ensure_ascii=False))}</code></p>")
    return "".join(out)


def split_ddl(ddl):
    from kit import split_top
    return split_top(ddl)


def render_output(exp):
    if "value" in exp:
        return html_value(exp["value"])
    return html_table(exp["columns"], exp["rows"])


LIMITS = {"pyspark": ("pyspark", "2 GB"), "sql": ("psql", "1 GB"), "python": ("py3", "1 GB")}


def b64(obj):
    return base64.b64encode(json.dumps(obj, ensure_ascii=False).encode()).decode()


# ---------------- chargement ----------------
DEFAULTS = {"python": ("solution", 4), "sql": (None, 10), "pyspark": ("solve", 30)}


def load_task(path):
    spec = importlib.util.spec_from_file_location("t_" + os.path.basename(path)[:-3], path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    lang = m.LANG
    entry, limit = DEFAULTS[lang]
    t = {
        "id": m.ID, "name": m.NAME, "lang": lang,
        "entry": getattr(m, "ENTRY", entry), "params": getattr(m, "PARAMS", []),
        "limit_s": getattr(m, "LIMIT", limit), "ordered": getattr(m, "ORDERED", True),
        "desc": m.DESC.strip(), "starter": m.STARTER.lstrip("\n"), "solution": m.SOLUTION.strip() + "\n",
        "hints": getattr(m, "HINTS", []), "summary_fr": getattr(m, "SUMMARY_FR", ""),
        "tags": getattr(m, "TAGS", []), "minutes": getattr(m, "MINUTES", 20),
        "source": getattr(m, "SOURCE", "Kata Lab"), "visible_n": getattr(m, "VISIBLE", 2),
        "tests_in": m.tests(), "mutants": getattr(m, "MUTANTS", []), "io": getattr(m, "IO", []),
        # Vérifications en plus pour les banques : réponses officielles et solutions indépendantes
        "bank": m.expected() if hasattr(m, "expected") else None, "alts": getattr(m, "ALT", []),
        "wrapper": getattr(m, "WRAPPER", ""), "desc_raw": getattr(m, "DESC_RAW", False),
    }
    return t


def build_task(t):
    tests = []
    for i, inp in enumerate(t["tests_in"]):
        try:
            exp = run(t, t["solution"], inp)
        except Exception:
            raise SystemExit(f"[{t['id']}] la solution plante sur le test {i + 1}:\n{traceback.format_exc()}")
        tests.append({"input": inp, "expected": exp})
    problems = []
    if t["bank"] is not None:
        assert len(t["bank"]) == len(tests), f"[{t['id']}] expected() et tests() n'ont pas la même longueur"
        nb = 0
        for i, (x, want) in enumerate(zip(tests, t["bank"])):
            if want is None:
                continue
            nb += 1
            if isinstance(want, dict) and "__table__" in want:
                ok = out_eq(x["expected"], want["__table__"], t["ordered"])
            elif isinstance(want, dict) and "__subset__" in want:
                got = x["expected"].get("value")
                ok = isinstance(got, dict) and all(k in got and val_eq(got[k], v) for k, v in want["__subset__"].items())
            else:
                ok = out_eq(x["expected"], {"value": want}, True)
            if not ok:
                problems.append(f"test {i + 1} : la solution donne {x['expected']} mais la banque attend {want!r}")
        t["bank_n"] = nb
    for k, alt in enumerate(t["alts"]):
        for i, x in enumerate(tests):
            got = safe_run(t, alt, x["input"])
            if not out_eq(got, x["expected"], t["ordered"]):
                problems.append(f"la solution indépendante {k + 1} diffère au test {i + 1} : {got} au lieu de {x['expected']}")
                break
    if all(out_eq(safe_run(t, t["starter"], x["input"]), x["expected"], t["ordered"]) for x in tests):
        problems.append("le code de départ passe tous les tests")
    for k, mut in enumerate(t["mutants"]):
        if all(out_eq(safe_run(t, mut, x["input"]), x["expected"], t["ordered"]) for x in tests):
            problems.append(f"le mutant {k + 1} passe tous les tests")
    empty = [i + 1 for i, x in enumerate(tests) if x["expected"].get("rows") == []]
    vis = tests[: t["visible_n"]]
    if "{{EXAMPLE}}" in t["desc"]:
        ex = vis[0]
        if t["lang"] == "sql" or any(isinstance(v, dict) for v in ex["input"].values()):
            html = render_input(t, ex["input"]) + "<p>the output should be</p>" + render_output(ex["expected"])
        else:
            args = ", ".join(f"{p} = {json.dumps(ex['input'][p], ensure_ascii=False)}" for p in t["params"])
            html = (f"<p>For <code>{esc(args)}</code>, the output should be</p>" + render_output(ex["expected"]))
        t["desc"] = t["desc"].replace("{{EXAMPLE}}", html)
    lim, mem = LIMITS[t["lang"]]
    io_lines = "".join(f"<br><b>[{esc(k)}]</b> {v}" for k, v in t["io"])
    t["desc"] += (f'<div class="lim"><b>[execution time limit]</b> {t["limit_s"]:g} seconds ({lim})'
                  f'<br><b>[memory limit]</b> {mem}{io_lines}</div>')
    hid = tests[t["visible_n"]:]
    files = None
    first = vis[0]["input"] if vis else {}
    for p, v in first.items():
        if isinstance(v, dict) and "__dir__" in v:
            files = {"root": p, "files": v["__dir__"]}
    doc = {k: t[k] for k in ("id", "name", "lang", "entry", "params", "limit_s", "ordered", "desc", "starter",
                             "hints", "summary_fr", "tags", "minutes", "source")}
    if t["wrapper"]:
        doc["wrapper"] = t["wrapper"]
    doc.update(files=files, visible=vis, hidden_n=len(hid), hidden=b64(hid), solution=b64(t["solution"]))
    with open(os.path.join(OUT, "tasks", t["id"] + ".json"), "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, separators=(",", ":"))
    info = f"{t['id']:<10} {t['lang']:<8} {len(vis)}+{len(hid)} tests"
    if t.get("bank_n"):
        info += f", {t['bank_n']} réponses officielles vérifiées"
    if t["alts"]:
        info += f", {len(t['alts'])} solution(s) indépendante(s) d'accord"
    if empty:
        info += f"  (sortie vide aux tests {empty})"
    print(info + ("  !! " + " ; ".join(problems) if problems else "  ok"))
    return {"id": t["id"], "name": t["name"], "lang": t["lang"], "tags": t["tags"], "minutes": t["minutes"],
            "source": t["source"], "tests": len(tests)}, problems


def main():
    os.makedirs(os.path.join(OUT, "tasks"), exist_ok=True)
    only = set(sys.argv[1:])
    tdir = os.path.join(ROOT, "content_src", "tasks")
    index_path = os.path.join(OUT, "tasks_index.json")
    index = {}
    if only and os.path.exists(index_path):
        index = {x["id"]: x for x in json.load(open(index_path))}
    bad = 0
    for fn in sorted(os.listdir(tdir)):
        if not fn.endswith(".py"):
            continue
        t = load_task(os.path.join(tdir, fn))
        if only and t["id"] not in only:
            continue
        meta, problems = build_task(t)
        index[t["id"]] = meta
        bad += bool(problems)
    json.dump(sorted(index.values(), key=lambda x: x["id"]), open(index_path, "w"), ensure_ascii=False, indent=0)
    import course  # content_src/course.py : séances, réflexes, cartes, examens

    course.write(OUT, {x["id"]: x for x in index.values()})
    print("catalogue écrit." + (f"  {bad} task(s) à revoir" if bad else ""))
    if bad:
        sys.exit(1)


if __name__ == "__main__":
    main()
