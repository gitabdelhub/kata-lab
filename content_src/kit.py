"""Petits outils pour écrire les tasks (entrées de tests)."""
import json
import random


def df(schema, rows):
    """Entrée PySpark : un DataFrame (schéma DDL Spark + lignes)."""
    return {"__df__": {"schema": schema, "rows": [list(r) for r in rows]}}


def folder(files):
    """Entrée PySpark : un dossier de fichiers {chemin relatif: contenu}."""
    return {"__dir__": dict(files)}


def split_top(s):
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


def table(cols, rows):
    """Entrée SQL : une table. cols = "id INT, day DATE, amount NUMERIC(10,2)"."""
    columns = []
    for part in split_top(cols):
        name, typ = part.split(None, 1)
        columns.append([name, typ])
    return {"columns": columns, "rows": [list(r) for r in rows]}


def tables(**kw):
    return {"tables": kw}


def rng(seed):
    return random.Random(seed)


def dump(x):
    return json.dumps(x, ensure_ascii=False)


# ---------------- banques externes (licence MIT, voir content_src/banks/) ----------------
import os as _os

BANKS = _os.path.join(_os.path.dirname(__file__), "banks")
EXERCISM = "exercism/problem-specifications (MIT)"
BLSQL = "shawlu95/Beyond-LeetCode-SQL (MIT)"


def exercism(slug, prop=None):
    """Cas officiels d'exercism : liste de (input, expected), sans les cas remplacés ni les cas d'erreur."""
    data = json.load(open(_os.path.join(BANKS, "exercism", slug + ".json"), encoding="utf-8"))
    leaves = []

    def walk(c):
        for x in c.get("cases", []):
            if "cases" in x:
                walk(x)
            else:
                leaves.append(x)
    walk(data)
    replaced = {x["reimplements"] for x in leaves if "reimplements" in x}
    out = []
    for x in leaves:
        if x["uuid"] in replaced or (prop and x["property"] != prop):
            continue
        if isinstance(x["expected"], dict) and "error" in x["expected"]:
            continue
        out.append((x["input"], x["expected"]))
    return out


def october(tid):
    """Charge une question adaptée d'un examen d'octobre (voir tools/port_october.py)."""
    d = json.load(open(_os.path.join(_os.path.dirname(__file__), "october", tid + ".json"), encoding="utf-8"))
    tests, bank = d.pop("tests"), d.pop("bank")
    d["tests"] = lambda: [json.loads(json.dumps(x)) for x in tests]
    d["expected"] = lambda: bank
    return d
