from kit import folder, rng
import json

ID = "h19t2"
NAME = "Nested Order Events"
LANG = "pyspark"
PARAMS = ["spark", "input_dir"]
MINUTES = 25
TAGS = ["consigne longue", "JSON imbriqué", "explode", "dernière version par commande", "lignes invalides", "top par groupe"]
DESC = """
<p>The order service writes events as JSON Lines files (<code>.jsonl</code>, one JSON object per line) in <code>input_dir</code> and its sub-folders. Other files are ignored. A line looks like:</p>
<pre>{"order_id": "o1", "ts": "2026-03-02T10:00:00", "status": "paid",
 "customer": {"id": "c1", "country": "ma"},
 "items": [{"sku": "A", "qty": 2, "price": 9.5}]}</pre>
<p>Each event is the full state of the order at time <code>ts</code>; the same order can appear many times (created, paid, refunded...). Only the event with the <b>latest</b> <code>ts</code> of an order counts, and the order is counted only if that latest status is <code>"paid"</code>. Lines that are not valid JSON, or that have no <code>order_id</code> or no <code>ts</code>, are ignored. An order can have an empty <code>items</code> list.</p>
<p>Country codes must be compared in upper case. Your task is to return, for each country with at least one counted order, the columns <code>country</code>, <code>orders</code> (long), <code>units</code> (long, total quantity), <code>revenue</code> (double, total of <code>qty * price</code>, rounded to 2 decimals) and <code>top_sku</code> (the sku with the highest total quantity in that country, the first in alphabetical order on a tie; <code>null</code> if the country has no item), sorted by <code>revenue</code> from the highest, then <code>country</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F


def solve(spark: SparkSession, input_dir: str) -> DataFrame:
    # write your code here
    return spark.read.json(input_dir)
"""
SOLUTION = """
import json
import os


def solve(spark, input_dir):
    latest = {}
    for root, dirs, files in os.walk(input_dir):
        for name in files:
            if not name.endswith(".jsonl"):
                continue
            with open(os.path.join(root, name)) as fh:
                for line in fh:
                    try:
                        ev = json.loads(line)
                    except ValueError:
                        continue
                    if not isinstance(ev, dict) or not ev.get("order_id") or not ev.get("ts"):
                        continue
                    oid = ev["order_id"]
                    if oid not in latest or ev["ts"] > latest[oid]["ts"]:
                        latest[oid] = ev
    stats = {}
    for ev in latest.values():
        if ev.get("status") != "paid":
            continue
        c = ev["customer"]["country"].upper()
        s = stats.setdefault(c, {"orders": 0, "units": 0, "revenue": 0.0, "sku": {}})
        s["orders"] += 1
        for it in ev.get("items") or []:
            s["units"] += it["qty"]
            s["revenue"] += it["qty"] * it["price"]
            s["sku"][it["sku"]] = s["sku"].get(it["sku"], 0) + it["qty"]
    rows = []
    for c, s in stats.items():
        top = min(s["sku"], key=lambda k: (-s["sku"][k], k)) if s["sku"] else None
        rows.append((c, s["orders"], s["units"], round(s["revenue"], 2), top))
    df = spark.createDataFrame(rows, "country string, orders long, units long, revenue double, top_sku string")
    return df.orderBy(df.revenue.desc(), "country")
"""
MUTANTS = [
    SOLUTION.replace('                    if oid not in latest or ev["ts"] > latest[oid]["ts"]:', '                    if oid not in latest:'),
    SOLUTION.replace('        c = ev["customer"]["country"].upper()', '        c = ev["customer"]["country"]'),
    SOLUTION.replace('        top = min(s["sku"], key=lambda k: (-s["sku"][k], k)) if s["sku"] else None', '        top = max(s["sku"], key=lambda k: s["sku"][k]) if s["sku"] else None'),
    SOLUTION.replace("    for root, dirs, files in os.walk(input_dir):", "    for root, dirs, files in [(input_dir, [], os.listdir(input_dir))]:"),
]


def ev(o, ts, st, cid, country, items):
    return json.dumps({"order_id": o, "ts": ts, "status": st, "customer": {"id": cid, "country": country},
                       "items": [{"sku": s, "qty": q, "price": p} for s, q, p in items]})


def tests():
    t = [folder({"day1/part-0.jsonl": "\n".join([ev("o1", "2026-03-02T10:00:00", "created", "c1", "ma", [("A", 2, 9.5)]),
                                                  ev("o1", "2026-03-02T10:05:00", "paid", "c1", "ma", [("A", 2, 9.5), ("B", 1, 3.0)]),
                                                  ev("o2", "2026-03-02T11:00:00", "paid", "c2", "MA", [("B", 3, 3.0)]),
                                                  "{not json", ev("o3", "2026-03-02T12:00:00", "paid", "c3", "sn", [])]) + "\n",
                 "day2/part-0.jsonl": "\n".join([ev("o2", "2026-03-03T09:00:00", "refunded", "c2", "MA", [("B", 3, 3.0)]),
                                                  ev("o4", "2026-03-03T09:00:00", "paid", "c4", "Sn", [("Z", 1, 100.0), ("Y", 1, 1.0)]),
                                                  json.dumps({"order_id": "o5", "status": "paid"})]) + "\n",
                 "day2/_SUCCESS": "", "day2/old.json": ev("o9", "2026-03-04T00:00:00", "paid", "c9", "fr", [("A", 9, 9.0)])}),
         folder({"a.jsonl": ev("x", "2026-01-01T00:00:00", "paid", "k", "tg", [("B", 2, 1.0), ("A", 2, 1.0)]) + "\n"})]
    r = rng(4192)
    for _ in range(6):
        files = {}
        stamps = iter(r.sample(range(600), 40))
        for f in range(r.randint(1, 3)):
            lines = []
            for _ in range(r.randint(2, 10)):
                o = f"o{r.randint(1, 6)}"
                lines.append(ev(o, f"2026-03-02T{(k := next(stamps)) // 60:02d}:{k % 60:02d}:00", r.choice(["paid", "paid", "created", "refunded"]),
                                "c", r.choice(["ma", "MA", "sn", "fr"]), [(r.choice("ABC"), r.randint(1, 3), r.choice([1.5, 10.0])) for _ in range(r.randint(0, 3))]))
                if r.random() < 0.1:
                    lines.append("oops")
            files[f"d{f}/part-{f}.jsonl"] = "\n".join(lines) + "\n"
        t.append(folder(files))
    return [{"input_dir": x} for x in t]
