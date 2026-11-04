from kit import folder, rng

ID = "f18t1"
NAME = "Purchase Orders Project (EDI)"
LANG = "pyspark"
PARAMS = ["spark", "input_dir"]
MINUTES = 25
TAGS = ["projet multi-fichiers", "consigne longue", "format EDI", "remplacement et annulation"]
PROJECT = {"files": ["pipeline/edi.py", "pipeline/orders.py", "pipeline/report.py"], "main": "pipeline/report.py"}
DESC = """
<p>This task is a small project. The editor contains a package <code>pipeline</code> with three files: <code>edi.py</code> cuts the text of a file into segments, <code>orders.py</code> turns segments into orders, and <code>report.py</code> holds <code>solve</code>. Only <code>solve</code> is tested, but keep each step in its own file and import it. Use the file list on the left of the editor to switch between files.</p>
<p>Our stores send their purchase orders to suppliers in EDI, an old text format still used everywhere in retail. Files end with <code>.edi</code> and are at any depth of <code>input_dir</code>. A file is a sequence of <b>segments</b>, each ending with a <code>'</code>; there may be line breaks between segments, which mean nothing. Inside a segment, elements are separated by <code>+</code> and the parts of an element by <code>:</code>. The first element is the segment tag. If one of the characters <code>' + : ?</code> is needed inside a value, it is written after a <code>?</code> (<code>?+</code> means a literal <code>+</code>).</p>
<p>A file holds one or more <b>messages</b>; a message starts with a <code>UNH</code> segment and ends with a <code>UNT</code> segment, and segments outside messages are envelopes to ignore. In a message, <code>BGM+220+&lt;order number&gt;+&lt;function&gt;</code> gives the order number and what the message does: <code>9</code> is a new order, <code>5</code> replaces the whole order with this one, <code>1</code> cancels it. <code>DTM+137:&lt;yyyyMMddHHmm&gt;:203</code> is the time the message was written. <code>NAD+BY+&lt;store&gt;</code> is the buyer store (other <code>NAD</code> segments are other parties). Then each order line starts with a <code>LIN</code> segment and is followed by its <code>QTY</code> and <code>PRI</code> segments: <code>QTY+21:&lt;n&gt;</code> is the ordered quantity (other qualifiers, such as <code>QTY+192</code> for free goods, are not ordered) and <code>PRI+AAA:&lt;price&gt;</code> the unit price.</p>
<p>Messages arrive in no particular order. For each order number, only the message written last counts: if it cancels the order, the order does not exist any more.</p>
<p>Your task is to return, for each store with at least one order, the columns <code>store</code>, <code>orders</code> (long), <code>lines</code> (long), <code>units</code> (long, total ordered quantity) and <code>value</code> (double, total of quantity times unit price, rounded to 2 decimals), sorted by <code>store</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
# ==== pipeline/edi.py ====
def segments(text):
    \"\"\"Cut an EDI text into segments.
    Return a list of segments; a segment is a list of elements and an
    element is a list of parts, e.g. "QTY+21:5'" -> [["QTY"], ["21", "5"]].\"\"\"
    # write your code here
    return []

# ==== pipeline/orders.py ====
from pipeline.edi import segments


def messages(text):
    \"\"\"Return the messages of one file as dicts with the keys
    order, function, written (yyyyMMddHHmm), store and lines
    (a list of (quantity, unit_price)).\"\"\"
    # write your code here
    return []

# ==== pipeline/report.py ====
from pyspark.sql import SparkSession, DataFrame, functions as F
from pipeline.orders import messages


def solve(spark: SparkSession, input_dir: str) -> DataFrame:
    # write your code here
    return spark.read.text(input_dir)
"""
SOLUTION = """
# ==== pipeline/edi.py ====
def segments(text):
    out, seg, esc = [], [[""]], False
    for ch in text:
        if esc:
            seg[-1][-1] += ch
            esc = False
        elif ch == "?":
            esc = True
        elif ch == "'":
            if seg[0][0].strip():
                out.append(seg)
            seg = [[""]]
        elif ch == "+":
            seg.append([""])
        elif ch == ":":
            seg[-1].append("")
        elif ch not in "\\r\\n":
            seg[-1][-1] += ch
    return out

# ==== pipeline/orders.py ====
from pipeline.edi import segments


def part(seg, i, j=0):
    return seg[i][j] if i < len(seg) and j < len(seg[i]) else ""


def messages(text):
    out, msg = [], None
    for seg in segments(text):
        tag = seg[0][0].strip()
        if tag == "UNH":
            msg = {"order": None, "function": "9", "written": "", "store": None, "lines": []}
        elif msg is None:
            continue
        elif tag == "BGM":
            msg["order"] = part(seg, 2)
            msg["function"] = part(seg, 3) or "9"
        elif tag == "DTM" and part(seg, 1) == "137":
            msg["written"] = part(seg, 1, 1)
        elif tag == "NAD" and part(seg, 1) == "BY":
            msg["store"] = part(seg, 2)
        elif tag == "LIN":
            msg["lines"].append([0, 0.0])
        elif tag == "QTY" and part(seg, 1) == "21" and msg["lines"]:
            msg["lines"][-1][0] = int(part(seg, 1, 1))
        elif tag == "PRI" and part(seg, 1) == "AAA" and msg["lines"]:
            msg["lines"][-1][1] = float(part(seg, 1, 1))
        elif tag == "UNT":
            out.append(msg)
            msg = None
    return out

# ==== pipeline/report.py ====
import os
from pyspark.sql import functions as F
from pipeline.orders import messages


def solve(spark, input_dir):
    latest = {}
    for root, _, files in os.walk(input_dir):
        for name in files:
            if name.endswith(".edi"):
                with open(os.path.join(root, name)) as fh:
                    for m in messages(fh.read()):
                        old = latest.get(m["order"])
                        if old is None or m["written"] > old["written"]:
                            latest[m["order"]] = m
    rows = [(m["store"], m["order"], q, p) for m in latest.values() if m["function"] != "1" for q, p in m["lines"]]
    df = spark.createDataFrame(rows, "store string, po string, qty long, price double")
    return (df.groupBy("store").agg(F.countDistinct("po").alias("orders"), F.count("*").alias("lines"),
                                    F.sum("qty").alias("units"), F.round(F.sum(F.col("qty") * F.col("price")), 2).alias("value"))
            .orderBy("store"))
"""
MUTANTS = [
    SOLUTION.replace('if old is None or m["written"] > old["written"]:', 'if True:'),
    SOLUTION.replace('for m in latest.values() if m["function"] != "1"', 'for m in latest.values()'),
    SOLUTION.replace('elif tag == "QTY" and part(seg, 1) == "21" and msg["lines"]:', 'elif tag == "QTY" and msg["lines"]:'),
    SOLUTION.replace('        elif ch == "?":\n            esc = True\n', ''),
]


def esc(v):
    return "".join("?" + c if c in "'+:?" else c for c in v)


def message(ref, po, fn, written, store, lines, extra=False):
    seg = [f"UNH+{ref}+ORDERS:D:96A:UN", f"BGM+220+{esc(po)}+{fn}", f"DTM+137:{written}:203", f"NAD+BY+{esc(store)}", "NAD+SU+SUPPLIER-7"]
    if extra:
        seg.append("FTX+AAI+++Deliver before 10?:00?, ring twice")
    for i, (sku, q, p, free) in enumerate(lines, 1):
        seg += [f"LIN+{i}++{sku}:EN", f"QTY+21:{q}"]
        if free:
            seg.append(f"QTY+192:{free}")
        seg.append(f"PRI+AAA:{p}")
    seg.append(f"UNT+{len(seg) + 1}+{ref}")
    return seg


def edi(msgs, newline=True):
    seg = ["UNB+UNOA:2+STORES+SUPPLIER+260304:1000+1"] + [s for m in msgs for s in m] + ["UNZ+1+1"]
    return ("'\n" if newline else "'").join(seg) + "'"


def tests():
    t = [folder({"in/2026-03-04/a.edi": edi([message("1", "PO-100", "9", "202603040900", "CASA-01", [("111", 10, "2.50", 0), ("222", 4, "1.25", 2)], extra=True),
                                                message("2", "PO-101", "9", "202603040905", "RABAT+02", [("111", 3, "2.50", 0)])]),
                 "in/2026-03-04/b.edi": edi([message("3", "PO-100", "5", "202603041100", "CASA-01", [("111", 12, "2.50", 0)]),
                                                message("4", "PO-102", "9", "202603041000", "CASA-01", [("333", 1, "9.99", 0)])], newline=False),
                 "in/2026-03-03/z.edi": edi([message("9", "PO-100", "9", "202603031700", "CASA-01", [("999", 99, "1.00", 0)])]),
                 "in/2026-03-05/c.edi": edi([message("5", "PO-102", "1", "202603050800", "CASA-01", [])]),
                 "in/2026-03-05/c.edi.bak": "garbage"}),
         folder({"x.edi": edi([message("1", "A?1", "9", "202601010000", "S", [("1", 2, "0.5", 1)])])})]
    r = rng(3181)
    for _ in range(6):
        files = {}
        for k in range(r.randint(1, 4)):
            msgs = []
            for j in range(r.randint(1, 3)):
                po = f"PO-{r.randint(1, 4)}"
                fn = r.choice(["9", "9", "5", "1"])
                lines = [(r.choice(["111", "222"]), r.randint(1, 9), r.choice(["2.50", "0.99", "10.00"]), r.choice([0, 0, 3])) for _ in range(r.randint(1, 3))]
                msgs.append(message(f"{k}{j}", po, fn, f"20260304{r.randint(8, 17):02d}{r.choice(['00', '15', '30'])}", r.choice(["CASA-01", "FES?03"]), lines, extra=r.random() < 0.3))
            files[f"d{r.randint(1, 2)}/f{k}.edi"] = edi(msgs, newline=r.random() < 0.5)
        t.append(folder(files))
    return [{"input_dir": x} for x in t]
