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
