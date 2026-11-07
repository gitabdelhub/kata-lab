"""Génère content_src/tasks/kNN_*.py depuis la banque kursad-can/data-engineering-interview-practice (MIT).

    python3 tools/import_kursad.py chemin/vers/pyspark/03_pyspark_questions_and_solutions.ipynb
"""
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Questions non notables automatiquement : sortie libre ou seulement physique (partitions)
SKIP = {1: "n'importe quelles 10 lignes", 73: "seulement le partitionnement", 74: "seulement le partitionnement",
        76: "égalités libres à la limite des 10",
        # hors sujet pour le test CodeSignal (noté sur le résultat seulement) : choix d'AB du 7 nov 2026
        30: "comptage approximatif", 38: "broadcast", 66: "audit du schéma", 70: "quarantaine de JSON cassé",
        72: "répartition par partition", 75: "cache", 80: "explain"}
ORDERED = {14, 15}  # seules sorties dont l'ordre est imposé et sans égalité possible
CATS = {1: ("Bases", ["bases DataFrame", "select", "filtre"]), 2: ("Filtres", ["filtre", "tri", "expression"]),
        3: ("Agrégation", ["groupBy", "agrégation"]), 4: ("Jointures", ["jointure", "join"]),
        5: ("Fenêtres", ["window", "row_number", "lag"]), 6: ("Dates", ["dates", "timestamps", "événements"]),
        7: ("Qualité", ["nettoyage", "null", "doublon", "cdc", "json"]), 8: ("ETL", ["etl production", "agrégation"])}
MIN = {1: 6, 2: 7, 3: 8, 4: 10, 5: 12, 6: 12, 7: 12, 8: 10}


def md_inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)


def section(md, name, stop):
    m = re.search(r"\*\*" + re.escape(name) + r":\*\*(.*?)(?=\*\*(?:" + stop + r"):\*\*|$)", md, re.S)
    return m.group(1).strip() if m else ""


def to_html(md):
    task = section(md, "Task", "Requirements|Available datasets and columns|Expected output")
    req = section(md, "Requirements", "Available datasets and columns|Expected output")
    avail = section(md, "Available datasets and columns", "Expected output")
    exp = section(md, "Expected output", "Solution")
    out = f"<p>{md_inline(task)}</p>"
    if req:
        out += "<ul>" + "".join(f"<li>{md_inline(x[2:])}</li>" for x in req.splitlines() if x.startswith("- ")) + "</ul>"
    out += "<p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul>"
    out += "".join(f"<li>{md_inline(x[2:])}</li>" for x in avail.splitlines() if x.startswith("- ")) + "</ul>"
    out += f"<p><b>Expected output:</b> {md_inline(exp)}</p>"
    return out


def main(nb_path):
    nb = json.load(open(nb_path, encoding="utf-8"))
    cells = nb["cells"]
    cat = 0
    made = 0
    for i, c in enumerate(cells):
        s = "".join(c["source"])
        m0 = re.match(r"## (\d)\. ", s)
        if m0:
            cat = int(m0.group(1))
        m = re.match(r"### Q(\d+) — (.*)", s)
        if not m:
            continue
        n, title = int(m.group(1)), m.group(2).strip()
        if n in SKIP:
            continue
        code = "".join(cells[i + 1]["source"])
        code = "\n".join(ln for ln in code.splitlines() if not ln.strip().startswith("result.show(")).strip()
        if n == 15:  # égalités sur (country, signup_date) dans les données : on ajoute customer_id pour un ordre unique
            code = code.replace("orderBy('country','signup_date')", "orderBy('country','signup_date','customer_id')")
            s = s.replace("without introducing a third tie-breaker.", "and break remaining ties with `customer_id` ascending.")
            s = s.replace("Records tied on both keys have no additional specified order.", "Records tied on both keys are ordered by `customer_id` ascending.")
        code = "\n".join(part.strip() for ln in code.splitlines() for part in ln.split(";"))
        ds = re.findall(r"- `(\w+)`:", section(s, "Available datasets and columns", "Expected output"))
        params = ["spark"] + ds
        body = "\n".join("    " + ln if ln.strip() else "" for ln in code.splitlines())
        sol = ("from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\n"
               f"def solve({', '.join(params)}):\n{body}\n    return result\n")
        hint = ", ".join(f"{d}: DataFrame" for d in ds)
        starter = ("from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\n"
                   f"def solve(spark: SparkSession, {hint}) -> DataFrame:\n    # write your code here\n    return {ds[0]}\n")
        tid = f"k{n:02d}"
        slug = re.sub(r"[^a-z0-9]+", "", title.lower())[:14]
        src = f'''from kursad import inputs, SRC

ID = {tid!r}
NAME = {title!r}
LANG = "pyspark"
PARAMS = {params!r}
MINUTES = {MIN[cat]}
ORDERED = {n in ORDERED}
TAGS = {CATS[cat][1] + ["banque DE"]!r}
SOURCE = SRC + " · Q{n:02d}"
IO = [("input", "DataFrame {', '.join(ds)}")]
DESC = {(to_html(s) + "<h4>Example</h4>{{EXAMPLE}}")!r}
STARTER = {starter!r}
SOLUTION = {sol!r}


def tests():
    return inputs({ds!r}, ID)
'''
        open(os.path.join(ROOT, "content_src", "tasks", f"{tid}_{slug}.py"), "w", encoding="utf-8").write(src)
        made += 1
    print(made, "tasks écrites ;", len(SKIP), "écartées :", SKIP)


if __name__ == "__main__":
    main(sys.argv[1])
