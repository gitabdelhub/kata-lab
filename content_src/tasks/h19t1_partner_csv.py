from kit import folder, rng

ID = "h19t1"
NAME = "Partner CSV Drops"
LANG = "pyspark"
PARAMS = ["spark", "input_dir"]
MINUTES = 25
TAGS = ["consigne longue", "en-têtes dans le désordre", "colonne optionnelle", "virgule décimale", "dédoublonnage par fichier le plus récent"]
DESC = """
<p>Our payment partners drop CSV files in <code>input_dir</code>, one folder per partner: <code>&lt;partner&gt;/&lt;yyyy-MM-dd&gt;.csv</code>. Only files ending with <code>.csv</code> are data; anything else is ignored. Every file has a header line, but each partner writes the columns in its own order, sometimes with spaces or capital letters around the names (<code>" Amount "</code> is the column <code>amount</code>).</p>
<p>The columns <code>txn_id</code>, <code>amount</code> and <code>currency</code> are always present. The column <code>fee</code> is optional: when a file has no <code>fee</code> column, or when the value is empty, the fee is 0. Amounts and fees can use a comma as decimal separator (<code>12,50</code> is 12.50). A row whose <code>amount</code> is not a number after that fix is <b>rejected</b>.</p>
<p>Partners re-send transactions: for a partner, the same <code>txn_id</code> can appear in several files. Keep only the row coming from the file with the latest date in its name (the same <code>txn_id</code> never appears twice in one file). Rejected rows are not candidates.</p>
<p>Your task is to return, for each partner folder that contains at least one CSV file, the columns <code>partner</code>, <code>files</code> (long, number of CSV files, including files with only a header), <code>rejected</code> (long, number of rejected rows over all its files), <code>txns</code> (long, number of kept transactions) and <code>net</code> (double, total of <code>amount - fee</code> of the kept transactions, rounded to 2 decimals, 0.0 when there is none), sorted by <code>partner</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
import os
from pyspark.sql import SparkSession, DataFrame, functions as F


def solve(spark: SparkSession, input_dir: str) -> DataFrame:
    # write your code here
    return spark.read.csv(input_dir, header=True)
"""
SOLUTION = """
import csv
import os


def to_number(text):
    text = (text or "").strip().replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None


def solve(spark, input_dir):
    rows = []
    for partner in sorted(os.listdir(input_dir)):
        pdir = os.path.join(input_dir, partner)
        if not os.path.isdir(pdir):
            continue
        files = [f for f in sorted(os.listdir(pdir)) if f.endswith(".csv")]
        if not files:
            continue
        rejected = 0
        best = {}                       # txn_id -> (date du fichier, net)
        for name in files:
            day = name[:-4]
            with open(os.path.join(pdir, name), newline="") as fh:
                reader = csv.reader(fh)
                header = next(reader, None)
                if header is None:
                    continue
                cols = [h.strip().lower() for h in header]
                for values in reader:
                    if not values:
                        continue
                    rec = dict(zip(cols, values))
                    amount = to_number(rec.get("amount"))
                    if amount is None:
                        rejected += 1
                        continue
                    fee = to_number(rec.get("fee")) if (rec.get("fee") or "").strip() else 0.0
                    tid = rec["txn_id"].strip()
                    if tid not in best or day > best[tid][0]:
                        best[tid] = (day, amount - (fee or 0.0))
        net = round(sum(v[1] for v in best.values()), 2)
        rows.append((partner, len(files), rejected, len(best), net))
    return spark.createDataFrame(rows, "partner string, files long, rejected long, txns long, net double").orderBy("partner")
"""
MUTANTS = [
    SOLUTION.replace('    text = (text or "").strip().replace(",", ".")', '    text = (text or "").strip()'),
    SOLUTION.replace("                cols = [h.strip().lower() for h in header]", "                cols = [h.strip() for h in header]"),
    SOLUTION.replace("                    if tid not in best or day > best[tid][0]:", "                    if tid not in best:"),
    SOLUTION.replace("rows.append((partner, len(files), rejected", "rows.append((partner, len([f for f in files if len(open(os.path.join(pdir, f)).read().splitlines()) > 1]), rejected"),
]


def tests():
    t = [folder({"acme/2026-03-01.csv": "txn_id,amount,currency,fee\nT1,100,EUR,1.5\nT2,\"12,50\",EUR,\nT3,abc,EUR,0\n",
                 "acme/2026-03-02.csv": " Currency ,TXN_ID, Amount \nEUR,T1,90\nEUR,T4,10\n",
                 "acme/readme.txt": "not data\n",
                 "bolt/2026-02-28.csv": "amount,txn_id,currency\n5,B1,MAD\n",
                 "bolt/2026-03-10.csv": "amount,txn_id,currency\n",
                 "zeta/notes.md": "# nothing\n"}),
         folder({"pay/2026-01-10.csv": "txn_id,amount,currency,fee\nX,10,EUR,2\nY,n/a,EUR,1\n",
                 "pay/2026-01-09.csv": "txn_id,amount,currency,fee\nX,99,EUR,0\nY,7,EUR,\"0,5\"\n",
                 "pay/2026-01-11.csv": "txn_id,amount,currency,fee\nX,,EUR,0\n"})]
    r = rng(4191)
    for _ in range(6):
        files = {}
        for p in ["acme", "bolt", "cash"][: r.randint(1, 3)]:
            for d in r.sample(range(1, 20), r.randint(1, 4)):
                cols = ["txn_id", "amount", "currency"] + (["fee"] if r.random() < 0.6 else [])
                r.shuffle(cols)
                head = ",".join(r.choice([c, c.upper(), " " + c + " "]) for c in cols)
                lines = []
                for tid in r.sample(range(1, 12), r.randint(0, 5)):
                    vals = {"txn_id": f"T{tid}", "amount": r.choice(["10", "12.5", "\"7,25\"", "x", "", "100"]), "currency": "EUR",
                            "fee": r.choice(["", "1", "\"0,5\""])}
                    lines.append(",".join(vals[c] for c in cols))
                files[f"{p}/2026-03-{d:02d}.csv"] = head + "\n" + "".join(l + "\n" for l in lines)
            files[f"{p}/_SUCCESS"] = ""
        t.append(folder(files))
    return [{"input_dir": x} for x in t]
