from kit import folder, rng

ID = "f12t1"
NAME = "Till Receipts Project"
LANG = "pyspark"
PARAMS = ["spark", "input_dir"]
MINUTES = 25
TAGS = ["projet multi-fichiers", "consigne longue", "parsing de texte", "contrôle de total"]
PROJECT = {"files": ["pipeline/receipts.py", "pipeline/report.py"], "main": "pipeline/report.py"}
DESC = """
<p>This task is a small project. The editor contains a package <code>pipeline</code> with two files: <code>receipts.py</code>, where you parse the text of a receipt, and <code>report.py</code>, where <code>solve</code> builds the report. Only <code>solve</code> is tested, but you are expected to keep the parsing in <code>receipts.py</code> and import it, as in a real code base. Use the file list on the left of the editor to switch between files.</p>
<p>The tills of our shops print receipts as plain text, and the shops upload the text of each day's receipts into <code>input_dir</code>, in files ending with <code>.txt</code> (at any depth). A file contains one or more receipts; two receipts are separated by a line made only of <code>=</code> signs. A receipt starts with a <code>STORE</code> line and a <code>DATE</code> line (<code>yyyy-MM-dd HH:mm</code>), then a line of dashes, then one line per item, then another line of dashes and finally a <code>TOTAL</code> line. An item line reads <code>2 x Milk 1L @ 1.20</code>: the quantity, the letter <code>x</code>, the product name (which can itself contain spaces or the letter x), the sign <code>@</code> and the unit price. A refunded item is printed with a negative quantity. Typists added spaces here and there.</p>
<p>The tills are old and some receipts were printed with a paper jam: an item line is missing, so the items no longer add up to the printed total. A receipt is <b>valid</b> when the sum of quantity times unit price over its items is equal to its <code>TOTAL</code> to the cent; any other receipt is <b>flagged</b> and contributes nothing except to the flagged count.</p>
<p>Your task is to return, for each store and day (date of the <code>DATE</code> line), the columns <code>store</code>, <code>day</code> (date), <code>receipts</code> (long, valid receipts), <code>items</code> (long, total quantity over valid receipts, refunds included), <code>revenue</code> (double, sum of the totals of valid receipts, rounded to 2 decimals) and <code>flagged</code> (long), sorted by <code>store</code>, then <code>day</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
# ==== pipeline/receipts.py ====
def parse_receipt(text):
    \"\"\"Parse the text of ONE receipt.
    Return a dict with the keys store, day (yyyy-MM-dd), items (total quantity),
    total (float) and valid (bool).\"\"\"
    # write your code here
    return None

# ==== pipeline/report.py ====
from pyspark.sql import SparkSession, DataFrame, functions as F
from pipeline.receipts import parse_receipt


def solve(spark: SparkSession, input_dir: str) -> DataFrame:
    # write your code here
    return spark.read.text(input_dir)
"""
SOLUTION = """
# ==== pipeline/receipts.py ====
import re


def parse_receipt(text):
    store = day = None
    total = None
    items = 0
    amount = 0.0
    for raw in text.splitlines():
        line = raw.strip()
        if not line or set(line) <= {"-"}:
            continue
        if line.upper().startswith("STORE"):
            store = line[5:].strip()
        elif line.upper().startswith("DATE"):
            day = line[4:].strip()[:10]
        elif line.upper().startswith("TOTAL"):
            total = float(line[5:].strip())
        elif "@" in line:
            left, price = line.rsplit("@", 1)
            m = re.match(r"\\s*(-?\\d+)\\s*x\\s", left + " ")
            qty = int(m.group(1))
            items += qty
            amount += qty * float(price.strip())
    valid = total is not None and round(amount * 100) == round(total * 100)
    return {"store": store, "day": day, "items": items, "total": total, "valid": valid}

# ==== pipeline/report.py ====
import os
from pyspark.sql import functions as F
from pipeline.receipts import parse_receipt


def solve(spark, input_dir):
    rows = []
    for root, _, files in os.walk(input_dir):
        for name in files:
            if not name.endswith(".txt"):
                continue
            with open(os.path.join(root, name)) as fh:
                chunk = []
                for line in fh.read().splitlines() + ["="]:
                    if line.strip() and set(line.strip()) == {"="}:
                        if any(l.strip() for l in chunk):
                            r = parse_receipt("\\n".join(chunk))
                            rows.append((r["store"], r["day"], r["items"], r["total"], r["valid"]))
                        chunk = []
                    else:
                        chunk.append(line)
    df = spark.createDataFrame(rows, "store string, day string, items int, total double, valid boolean")
    ok = F.col("valid")
    return (df.groupBy("store", F.to_date("day").alias("day")).agg(
                F.sum(F.when(ok, 1).otherwise(0)).cast("long").alias("receipts"),
                F.sum(F.when(ok, F.col("items")).otherwise(0)).cast("long").alias("items"),
                F.round(F.sum(F.when(ok, F.col("total")).otherwise(0.0)), 2).alias("revenue"),
                F.sum(F.when(ok, 0).otherwise(1)).cast("long").alias("flagged"))
            .orderBy("store", "day"))
"""
MUTANTS = [
    SOLUTION.replace("valid = total is not None and round(amount * 100) == round(total * 100)", "valid = total is not None"),
    SOLUTION.replace("items += qty", "items += abs(qty)"),
    SOLUTION.replace("for name in files:\n            if not name.endswith(\".txt\"):\n                continue", "for name in files[:1]:\n            if not name.endswith(\".txt\"):\n                continue"),
]


def receipt(store, when, items, jam=False, spaces=False):
    total = round(sum(q * p for _, q, p in items), 2)
    shown = items[:-1] if jam and len(items) > 1 else items
    sp = "   " if spaces else " "
    lines = [f"STORE{sp}{store}", f"DATE {when}", "-" * 24]
    lines += [f"{q}{sp}x {n}{sp}@{sp}{p:.2f}" for n, q, p in shown]
    lines += ["-" * 24, f"TOTAL {total:.2f}"]
    return "\n".join(lines)


def file(*recs):
    return "\n========\n".join(recs) + "\n"


def tests():
    t = [folder({"s01/2026-03-04.txt": file(receipt("S01", "2026-03-04 09:12", [("Milk 1L", 2, 1.20), ("Bread", 1, 0.95)]),
                                             receipt("S01", "2026-03-04 18:40", [("Box x6 eggs", 1, 3.10), ("Milk 1L", -1, 1.20)], spaces=True),
                                             receipt("S01", "2026-03-04 19:00", [("Rice", 1, 2.00), ("Tea", 2, 1.50)], jam=True)),
                 "s02/day.txt": file(receipt("S02", "2026-03-04 10:00", [("Water", 6, 0.35)])),
                 "s02/upload.log": "uploaded 1 file\n"}),
         folder({"a/b/c.txt": file(receipt("X", "2026-03-05 23:59", [("Gum", 1, 0.5), ("Gum", 1, 0.5)], jam=True))})]
    r = rng(3121)
    prods = [("Milk 1L", 1.20), ("Bread", 0.95), ("Box x6 eggs", 3.10), ("Rice", 2.00), ("Tea", 1.50), ("Water", 0.35)]
    for _ in range(6):
        files = {}
        for k in range(r.randint(1, 4)):
            recs = []
            for _ in range(r.randint(1, 3)):
                its = [(n, r.choice([1, 1, 2, 3, -1]), p) for n, p in r.sample(prods, r.randint(1, 4))]
                recs.append(receipt(r.choice(["S01", "S02"]), f"2026-03-0{r.randint(4, 6)} {r.randint(8, 21):02d}:00", its, jam=r.random() < 0.25, spaces=r.random() < 0.3))
            files[f"{r.choice(['s01', 's02', 'x/y'])}/f{k}.txt"] = file(*recs)
        t.append(folder(files))
    return [{"input_dir": x} for x in t]
