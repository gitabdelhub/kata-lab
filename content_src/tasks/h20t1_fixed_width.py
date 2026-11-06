from kit import folder, rng

ID = "h20t1"
NAME = "Settlement Files with Trailers"
LANG = "pyspark"
PARAMS = ["spark", "input_dir"]
MINUTES = 25
TAGS = ["consigne longue", "largeur fixe", "en-tête / détail / pied", "contrôle des totaux", "fichiers rejetés en entier"]
DESC = """
<p>Banks send us settlement files in <code>input_dir</code> (files ending with <code>.dat</code>; other files are ignored). They are <b>fixed-width</b> text files, one record per line, and the first character gives the record type:</p>
<ul><li>Header <code>H</code>: characters 2-9 are the settlement date <code>yyyyMMdd</code>, characters 10-14 the bank code.</li>
<li>Detail <code>D</code>: characters 2-11 are the account number, characters 12-22 the amount in cents (11 digits with leading zeros), character 23 the sign (<code>+</code> or <code>-</code>), characters 24-26 the currency.</li>
<li>Trailer <code>T</code>: characters 2-7 are the number of detail lines (6 digits), characters 8-22 the sum of the signed detail amounts in cents (14 digits after a sign character at position 8).</li></ul>
<p>Characters are counted from 1. Lines can have trailing spaces, and empty lines must be skipped. A file is <b>valid</b> only if it has exactly one header as its first record, exactly one trailer as its last record, and the trailer count and total match its detail lines. An invalid file is ignored completely.</p>
<p>Your task is to return, for each bank and settlement date found in valid files, the columns <code>bank</code>, <code>settle_date</code> (date), <code>files</code> (long), <code>accounts</code> (long, number of distinct accounts) and <code>net</code> (double, sum of the signed amounts in currency units, that is cents / 100, rounded to 2 decimals), sorted by <code>bank</code>, then <code>settle_date</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
import os
from pyspark.sql import SparkSession, DataFrame, functions as F


def solve(spark: SparkSession, input_dir: str) -> DataFrame:
    # write your code here
    return spark.read.text(input_dir)
"""
SOLUTION = """
import os
from pyspark.sql import functions as F


def parse(path):
    with open(path) as fh:
        recs = [ln.rstrip() for ln in fh if ln.strip()]
    if len(recs) < 2 or recs[0][0] != "H" or recs[-1][0] != "T":
        return None
    if any(r[0] in "HT" for r in recs[1:-1]):
        return None
    head, trail, details = recs[0], recs[-1], recs[1:-1]
    rows = []
    total = 0
    for d in details:
        if d[0] != "D":
            return None
        cents = int(d[11:22]) * (-1 if d[22] == "-" else 1)
        total += cents
        rows.append((d[1:11], cents))
    count = int(trail[1:7])
    t_total = int(trail[8:22]) * (-1 if trail[7] == "-" else 1)
    if count != len(details) or t_total != total:
        return None
    day = head[1:9]
    return head[9:14], day[:4] + "-" + day[4:6] + "-" + day[6:8], rows


def solve(spark, input_dir):
    out = []
    for name in sorted(os.listdir(input_dir)):
        if not name.endswith(".dat"):
            continue
        res = parse(os.path.join(input_dir, name))
        if res is None:
            continue
        bank, day, rows = res
        for acc, cents in rows:
            out.append((bank, day, name, acc, cents))
        if not rows:
            out.append((bank, day, name, None, 0))
    df = spark.createDataFrame(out, "bank string, day string, file string, account string, cents long")
    return (df.groupBy("bank", F.to_date("day").alias("settle_date"))
              .agg(F.countDistinct("file").alias("files"), F.countDistinct("account").alias("accounts"),
                   F.round(F.sum("cents") / 100, 2).alias("net"))
              .orderBy("bank", "settle_date"))
"""
MUTANTS = [
    SOLUTION.replace("        cents = int(d[11:22]) * (-1 if d[22] == \"-\" else 1)", "        cents = int(d[11:22])"),
    SOLUTION.replace("    if count != len(details) or t_total != total:", "    if count != len(details):"),
    SOLUTION.replace("        recs = [ln.rstrip() for ln in fh if ln.strip()]", "        recs = [ln.rstrip() for ln in fh]"),
    SOLUTION.replace('F.countDistinct("account").alias("accounts")', 'F.count("account").alias("accounts")'),
]


def H(day, bank):
    return f"H{day}{bank}"


def D(acc, cents, cur="EUR"):
    return f"D{acc}{abs(cents):011d}{'-' if cents < 0 else '+'}{cur}"


def T(n, total):
    return f"T{n:06d}{'-' if total < 0 else '+'}{abs(total):014d}"


def fil(day, bank, items, bad=0):
    lines = [H(day, bank)] + [D(a, c) for a, c in items] + [T(len(items) + (1 if bad == 1 else 0), sum(c for a, c in items) + (5 if bad == 2 else 0))]
    return "\n".join(lines) + "\n"


def tests():
    t = [folder({"bnk1_a.dat": fil("20260302", "BMCE1", [("0000000001", 12550), ("0000000002", -2000), ("0000000001", 100)]),
                 "bnk1_b.dat": H("20260302", "BMCE1") + "   \n\n" + D("0000000003", 99) + "\n" + T(1, 99) + "\n",
                 "bnk2.dat": fil("20260302", "ATW01", [("0000000009", 5000)], bad=2),
                 "bnk3.dat": fil("20260303", "ATW01", [("0000000009", -5000)]),
                 "bnk4.dat": fil("20260303", "ATW01", [("0000000007", 1)], bad=1),
                 "notes.txt": "H20260302XXXXX\n"}),
         folder({"x.dat": D("0000000001", 5) + "\n" + T(1, 5) + "\n", "y.dat": fil("20260101", "SGMA1", []),
                 "z.dat": H("20260101", "SGMA1") + "\n" + D("0000000001", 5) + "\n" + H("20260101", "SGMA1") + "\n" + T(1, 5) + "\n"})]
    r = rng(4201)
    for _ in range(6):
        files = {}
        for i in range(r.randint(1, 5)):
            items = [(f"{r.randint(1, 4):010d}", r.choice([-3000, -150, 99, 100, 12345])) for _ in range(r.randint(0, 5))]
            files[f"f{i}.dat"] = fil(f"2026030{r.randint(1, 3)}", r.choice(["BMCE1", "ATW01"]), items, bad=r.choice([0, 0, 0, 1, 2]))
        t.append(folder(files))
    return [{"input_dir": x} for x in t]
