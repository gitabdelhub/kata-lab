"""Adapte les examens d'entraînement d'octobre (coach/examen2 à examen7) au format Kata Lab.

Usage : python tools/port_october.py /chemin/vers/coach
Écrit content_src/october/<id>.json (énoncé, solution de référence, tests d'origine, sorties attendues
d'origine) et un petit module content_src/tasks/<id>.py par question. Le build vérifie ensuite que la
solution de référence redonne exactement les sorties attendues d'origine sur tous les tests.
"""
import datetime as dt
import decimal
import importlib.util
import json
import os
import re
import sys

import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "content_src", "october")
TASKS = os.path.join(ROOT, "content_src", "tasks")
EXAMS = {2: "e10", 3: "e11", 4: "e12", 5: "e13", 6: "e14", 7: "e15"}
LANG_OF = {1: "pyspark", 2: "pyspark", 3: "sql", 4: "python"}


def conv(v):
    if isinstance(v, dt.datetime):
        return v.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(v, dt.date):
        return v.isoformat()
    if isinstance(v, decimal.Decimal):
        return float(v)
    if isinstance(v, (list, tuple)):
        return [conv(x) for x in v]
    if isinstance(v, dict):
        return {(k if isinstance(k, str) else json.dumps(k)): conv(x) for k, x in v.items()}
    return v


def load(path):
    sys.path.insert(0, os.path.dirname(path))
    spec = importlib.util.spec_from_file_location("m_" + os.path.basename(path)[:-3] + str(abs(hash(path))), path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    sys.path.pop(0)
    return m


def section(md, q):
    parts = re.split(r"^## ", md, flags=re.M)
    for p in parts:
        if p.startswith(f"Question {q}:"):
            head, _, body = p.partition("\n")
            title = re.sub(r"\s*\([^)]*\)\s*$", "", head.split(":", 1)[1]).strip()
            body = re.sub(r"\n---\s*$", "", body.strip())
            return title, body
    raise SystemExit(f"question {q} introuvable")


def to_html(body):
    html = markdown.markdown(body, extensions=["tables", "fenced_code"])
    return html.replace("<table>", '<table class="mdt">')


def signature(code, names):
    for line in code.splitlines():
        m = re.match(r"def (\w+)\((.*)\)(\s*->\s*[\w\[\], ]+)?:", line)
        if m and m.group(1) in names:
            params = [re.split(r"[:=]", p)[0].strip() for p in m.group(2).split(",") if p.strip()]
            return m.group(1), params, line
    raise SystemExit("signature introuvable")


SQL_TYPES = [(r"DECIMAL", "NUMERIC"), (r"DATETIME", "TIMESTAMP"), (r"TINYINT\(1\)", "BOOLEAN"), (r"\bDOUBLE\b", "DOUBLE PRECISION")]


def ddl_cols(ddl):
    m = re.match(r"\s*CREATE TABLE (\w+)\s*\((.*)\)\s*$", ddl, re.S | re.I)
    name, body = m.group(1), m.group(2)
    cols, depth, cur = [], 0, ""
    for ch in body:
        depth += ch == "("
        depth -= ch == ")"
        if ch == "," and depth == 0:
            cols.append(cur)
            cur = ""
        else:
            cur += ch
    cols.append(cur)
    out = []
    for c in cols:
        c = c.strip()
        if not c or re.match(r"(PRIMARY|UNIQUE|FOREIGN|KEY|CONSTRAINT|INDEX)\b", c, re.I):
            continue
        parts = c.split(None, 1)
        typ = re.split(r"\s+(NOT|NULL|PRIMARY|DEFAULT|UNIQUE|REFERENCES|CHECK)\b", parts[1], flags=re.I)[0].strip()
        for a, b in SQL_TYPES:
            typ = re.sub(a, b, typ, flags=re.I)
        out.append([parts[0], typ])
    return name, out


def kind_conv(v, k):
    if v is None:
        return None
    if k == "dec":
        return float(v)
    if k == "int":
        return int(v)
    return conv(v)


# ---------------- API simulées des questions 4 (code caché ajouté après celui de l'élève) ----------------
W_EX2 = '''
import json as _kjson
def __kata_entry__(case):
    pages = {c: b for c, b in case["pages"]}
    calls = []
    def fetch_page(cursor):
        calls.append(cursor)
        if len(calls) > 50:
            raise RuntimeError("more than 50 calls: infinite loop?")
        if cursor not in pages:
            raise ValueError(f"invalid cursor: {cursor!r}")
        return _kjson.dumps(pages[cursor])
    try:
        result = ingest_users(fetch_page)
    except Exception as exc:
        result = {"error": type(exc).__name__ + ": " + str(exc)}
    return {"result": result, "calls": calls}
'''
W_EX3 = '''
class ApiError(Exception):
    def __init__(self, status, retry_after=None):
        super().__init__(f"HTTP {status}")
        self.status = status
        self.retry_after = retry_after
class _KataUnexpectedCall(RuntimeError):
    pass
def __kata_entry__(case):
    remaining = {p: [list(o) for o in outs] for p, outs in case["script"]}
    calls, sleeps = [], []
    def fetch_page(page):
        calls.append(page)
        if len(calls) > 50:
            raise _KataUnexpectedCall("more than 50 calls: infinite loop?")
        if not remaining.get(page):
            raise _KataUnexpectedCall(f"unexpected call: page {page!r} (no outcome left)")
        o = remaining[page].pop(0)
        if o[0] == "ok":
            return o[1]
        if o[0] == "http":
            raise ApiError(o[1], o[2])
        raise TimeoutError("read timed out")
    import time as _ktime
    real = _ktime.sleep
    _ktime.sleep = lambda s: sleeps.append(f"time.sleep({s}) FORBIDDEN")
    try:
        kw = {} if case["max_attempts"] is None else {"max_attempts": case["max_attempts"]}
        try:
            result = sync_orders(fetch_page, sleeps.append, **kw)
        except _KataUnexpectedCall as exc:
            result = {"error": str(exc)}
        except Exception as exc:
            result = {"raises": [type(exc).__name__, getattr(exc, "status", None)]}
    finally:
        _ktime.sleep = real
    return {"result": result, "calls": calls, "sleeps": sleeps}
'''
W_EX5 = '''
def _kata_inv(invoice_id, amount, currency, status="paid"):
    return {"invoice_id": invoice_id, "amount": amount, "currency": currency, "status": status}
def __kata_entry__(case):
    calls = []
    pages = {p: r for p, r in case.get("pages", [])}
    ps = case["args"]["page_size"]
    raise_on = {p: (n, m) for p, n, m in case.get("raise_on", [])}
    def fetch_page(page, page_size):
        calls.append(page if page_size == ps else [page, "page_size=%r" % (page_size,)])
        if len(calls) > 200:
            raise RuntimeError("more than 200 calls: endless loop?")
        if page in raise_on:
            n, m = raise_on[page]
            raise {"TimeoutError": TimeoutError, "ConnectionError": ConnectionError}.get(n, RuntimeError)(m)
        if case.get("generator") == "infinite_overlapping":
            results = [_kata_inv(f"INV-{page}", float(page), "EUR"), _kata_inv(f"INV-{page + 1}", float(page + 1), "EUR")]
        else:
            results = pages.get(page, [])
        return {"page": page, "page_size": ps, "total_count": case.get("total_count", 0), "results": [dict(r) for r in results]}
    try:
        result = load_invoices(fetch_page, **case["args"])
    except Exception as exc:
        result = {"raises": [type(exc).__name__]}
    return {"result": result, "calls": calls}
'''
W_EX7 = '''
import copy as _kcopy
def __kata_entry__(case):
    calls = []
    def fetch_batch():
        calls.append("fetch_batch()")
        if case.get("raise"):
            n, m = case["raise"]
            raise {"TimeoutError": TimeoutError, "ConnectionError": ConnectionError, "ValueError": ValueError}.get(n, RuntimeError)(m)
        return _kcopy.deepcopy(case["response"])
    try:
        result = ingest_events(fetch_batch)
    except Exception as exc:
        result = {"raises": [type(exc).__name__]}
    return {"result": result, "calls": calls}
'''
W_EX4Q2 = '''
from pyspark.sql import functions as _KF
def __kata_entry__(customers_raw_df):
    valid, rejected = solve(customers_raw_df)
    v = valid.select("customer_id", "email", _KF.col("age").cast("string").alias("age"), "country",
                     _KF.lit(None).cast("string").alias("reject_reason"), _KF.lit("valid").alias("output"))
    r = rejected.select("customer_id", "email", _KF.col("age").cast("string").alias("age"), "country",
                        "reject_reason", _KF.lit("rejected").alias("output"))
    return v.unionByName(r)
'''


def port_q4(e, cm, ref, case):
    """Retourne (params, input, expected_bank) pour une question 4."""
    if e == 2:
        inp = {"case": {"pages": [[c, conv(b)] for c, b in case["pages"].items()]}}
        return ["case"], inp, {"__subset__": {"result": conv(case["expected"]), "calls": conv(case["calls"])}}
    if e == 3:
        exp = case["expected"]
        exp = {"raises": list(exp["raises"])} if isinstance(exp, dict) else conv(exp)
        inp = {"case": {"script": [[p, conv(o)] for p, o in case["script"].items()], "max_attempts": case["max_attempts"]}}
        return ["case"], inp, {"__subset__": {"result": exp, "calls": conv(case["calls"]), "sleeps": conv(case["sleeps"])}}
    if e == 5:
        c = {"args": case["args"], "total_count": case.get("total_count", 0), "pages": [[p, conv(r)] for p, r in case.get("pages", {}).items()]}
        if "raise_on" in case:
            c["raise_on"] = [[p, type(x).__name__, str(x)] for p, x in case["raise_on"].items()]
        if "generator" in case:
            c["generator"] = case["generator"].__name__
        sub = {"result": conv(case["expected"])}
        if "expected_calls" in case:
            sub["calls"] = conv(case["expected_calls"])
        return ["case"], {"case": c}, {"__subset__": sub}
    if e == 7:
        c = {"response": conv(case.get("response"))}
        if "raise" in case:
            c["raise"] = [type(case["raise"]).__name__, str(case["raise"])]
        sub = {"result": conv(case["expected"])}
        if "expected_calls" in case:
            sub["calls"] = conv(case["expected_calls"])
        return ["case"], {"case": c}, {"__subset__": sub}
    if e == 4:
        exp = case.get("expected", [case.get("records"), case.get("errors")])
        return ["ndjson_text"], {"ndjson_text": case["text"]}, conv(exp)
    if e == 6:
        return ["raw_body"], {"raw_body": json.dumps(case["body"])}, conv(case["expected"])
    raise SystemExit(e)


def main(coach):
    os.makedirs(OUT, exist_ok=True)
    for e, eid in EXAMS.items():
        d = os.path.join(coach, f"examen{e}")
        md = open(os.path.join(d, "enonce.md"), encoding="utf-8").read()
        for q in range(1, 5):
            tid = f"{eid}t{q}"
            lang = LANG_OF[q]
            title, body = section(md, q)
            cm = load(os.path.join(d, "tests", f"q{q}_cases.py"))
            wrapper, entry = "", None
            tests, bank = [], []
            ordered = True
            if lang == "pyspark":
                rp = os.path.join(d, "tests", f"q{q}_reference_try.py")  # version compatible Spark ANSI si elle existe
                if not os.path.exists(rp):
                    rp = os.path.join(d, "tests", f"q{q}_reference.py")
                ref = open(rp, encoding="utf-8").read()
                entry, params, sig = signature(ref, ["solve"])
                schemas = dict(cm.INPUTS)
                outs = getattr(cm, "OUTPUTS", None)
                if outs:
                    ordered = all(o.get("ordered", True) for o in outs)
                else:
                    ordered = getattr(cm, "ORDERED", True)
                multi = outs and len(outs) > 1
                if multi:
                    wrapper, entry = W_EX4Q2, "__kata_entry__"
                    cols = ["customer_id", "email", "age", "country", "reject_reason", "output"]
                else:
                    cols = outs[0]["columns"] if outs else cm.EXPECTED_COLUMNS
                for case in cm.CASES:
                    inp = {}
                    for p in params:
                        if p in schemas:
                            inp[p] = {"__df__": {"schema": schemas[p], "rows": conv(case["inputs"][p])}}
                        else:
                            inp[p] = conv(case.get("args", {})[p])
                    tests.append(inp)
                    exp = case["expected"]
                    if multi:
                        v, r = exp
                        rows = [[x[0], x[1], None if x[2] is None else str(x[2]), x[3], None, "valid"] for x in conv(v)]
                        rows += [list(x) + ["rejected"] for x in conv(r)]
                        bank.append({"__table__": {"columns": cols, "rows": rows}})
                    else:
                        if exp and isinstance(exp[0], list) and (not exp[0] or isinstance(exp[0][0], (list, tuple))):
                            exp = exp[0]
                        bank.append({"__table__": {"columns": cols, "rows": conv(exp)}})
                ret = "solve" if not multi else None
                first_df = [p for p in params if p in schemas][0]
                starter = ("from pyspark.sql import DataFrame, Window\nfrom pyspark.sql import functions as F\n\n\n"
                           + sig + "\n    # write your code here\n    return " + (f"{first_df}, {first_df}" if multi else first_df) + "\n")
                solution = ref
            elif lang == "sql":
                solution = open(os.path.join(d, "tests", "q3_reference_postgres.sql"), encoding="utf-8").read()
                ddls = cm.DDL if hasattr(cm, "DDL") else [t[1] for t in cm.TABLES]
                cols_by_table = dict(ddl_cols(x) for x in ddls)
                kinds = getattr(cm, "COLUMN_KINDS", None) or cm.KINDS
                ordered = getattr(cm, "ORDERED", True)
                params = []
                for case in cm.CASES:
                    tabs = {name: {"columns": cols_by_table[name], "rows": conv((case.get("data") or case.get("tables")).get(name, []))} for name in cols_by_table}
                    tests.append({"tables": tabs})
                    rows = [[kind_conv(v, k) for v, k in zip(r, kinds)] for r in case["expected"]]
                    bank.append({"__table__": {"columns": cm.EXPECTED_COLUMNS, "rows": rows}})
                starter = "/* Write your PostgreSQL query here */\n"
            else:
                ref = open(os.path.join(d, "tests", "q4_reference.py"), encoding="utf-8").read()
                names = re.findall(r"^def ([a-z]\w*)\(", ref, re.M)
                fn, _, sig = signature(ref, [n for n in names if not n.startswith("_")])
                wrapper = {2: W_EX2, 3: W_EX3, 5: W_EX5, 7: W_EX7}.get(e, "")
                for case in cm.CASES:
                    params, inp, exp = port_q4(e, cm, ref, case)
                    tests.append(inp)
                    bank.append(exp)
                entry = "__kata_entry__" if wrapper else fn
                if not wrapper:
                    params = [signature(ref, [fn])[1][0]]
                starter = sig + "\n    # write your code here\n    return None\n"
                solution = ref
            note = ""
            if lang == "sql":
                note = "<p class=\"muted\">Write a PostgreSQL query.</p>"
            if wrapper and lang == "python":
                note = "<p class=\"muted\">The functions described in the task (the API) are provided by the tests: you only write your function.</p>"
            if wrapper and lang == "pyspark":
                note = "<p class=\"muted\">In the test results, both DataFrames are shown in one table: the column <code>output</code> says if a row comes from <code>valid</code> or from <code>rejected</code>.</p>"
            doc = {"ID": tid, "NAME": title, "LANG": lang, "PARAMS": params, "ENTRY": entry, "ORDERED": ordered,
                   "DESC": to_html(body) + note, "STARTER": starter, "SOLUTION": solution, "WRAPPER": wrapper,
                   "MINUTES": 22, "SOURCE": f"Examen d'entraînement d'octobre n°{e}, question {q}",
                   "TAGS": [], "VISIBLE": 1, "tests": tests, "bank": bank}
            json.dump(doc, open(os.path.join(OUT, tid + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
            mod = os.path.join(TASKS, f"{tid}_october.py")
            open(mod, "w", encoding="utf-8").write(
                '"""Question adaptée d\'un examen d\'octobre : données dans content_src/october/."""\n'
                f'from kit import october\n\nglobals().update(october("{tid}"))\n')
            print(tid, lang, title, len(tests), "tests")


if __name__ == "__main__":
    main(sys.argv[1])
