from kit import folder, rng

ID = "h21t1"
NAME = "Apply CDC Batches"
LANG = "pyspark"
PARAMS = ["spark", "input_dir"]
MINUTES = 25
TAGS = ["consigne longue", "ordre numérique des fichiers", "upsert", "champ vide = inchangé", "suppression"]
DESC = """
<p>A source database exports its changes (CDC) as CSV files in <code>input_dir</code>, named <code>batch_&lt;n&gt;.csv</code> where <code>n</code> is a whole number. Batches must be applied in the <b>numeric</b> order of <code>n</code> (<code>batch_2.csv</code> comes before <code>batch_10.csv</code>), and inside a file, row by row from top to bottom. Files with any other name (temporary files, manifests) are ignored.</p>
<p>Each file has the header <code>op,id,name,email,balance</code>. The column <code>op</code> says what to do with the customer <code>id</code>:</p>
<ul><li><code>I</code> (insert): the customer gets exactly the values of the row (an empty field becomes <code>null</code>). If the customer already exists, the row replaces it completely.</li>
<li><code>U</code> (update): only the fields that are <b>not empty</b> change; an empty field keeps the old value. An update of a customer that does not exist is ignored.</li>
<li><code>D</code> (delete): the customer is removed. Deleting a customer that does not exist does nothing.</li></ul>
<p>The table starts empty. Your task is to return the final table with the columns <code>id</code> (long), <code>name</code>, <code>email</code>, <code>balance</code> (double) and <code>last_batch</code> (long, the <code>n</code> of the last batch that inserted or updated this customer), sorted by <code>id</code>.</p>
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
import re


def solve(spark, input_dir):
    batches = []
    for name in os.listdir(input_dir):
        m = re.fullmatch(r"batch_(\\d+)\\.csv", name)
        if m:
            batches.append((int(m.group(1)), name))
    batches.sort()
    table = {}                      # id -> [name, email, balance, last_batch]
    for n, name in batches:
        with open(os.path.join(input_dir, name), newline="") as fh:
            for row in csv.DictReader(fh):
                op, cid = row["op"].strip(), int(row["id"])
                vals = [row["name"], row["email"], row["balance"]]
                if op == "I":
                    table[cid] = [v if v != "" else None for v in vals] + [n]
                elif op == "U":
                    if cid not in table:
                        continue
                    for i, v in enumerate(vals):
                        if v != "":
                            table[cid][i] = v
                    table[cid][3] = n
                elif op == "D":
                    table.pop(cid, None)
    rows = [(cid, r[0], r[1], float(r[2]) if r[2] is not None else None, r[3]) for cid, r in table.items()]
    return spark.createDataFrame(rows, "id long, name string, email string, balance double, last_batch long").orderBy("id")
"""
MUTANTS = [
    SOLUTION.replace("            batches.append((int(m.group(1)), name))", "            batches.append((m.group(1), name))"),
    SOLUTION.replace("                    for i, v in enumerate(vals):\n                        if v != \"\":\n                            table[cid][i] = v", "                    for i, v in enumerate(vals):\n                        table[cid][i] = v if v != \"\" else None"),
    SOLUTION.replace("                    if cid not in table:\n                        continue", "                    if cid not in table:\n                        table[cid] = [None, None, None, n]"),
    SOLUTION.replace('        m = re.fullmatch(r"batch_(\\d+)\\.csv", name)', '        m = re.match(r"batch_(\\d+)", name)'),
]
HEAD = "op,id,name,email,balance\n"


def tests():
    t = [folder({"batch_1.csv": HEAD + "I,1,Ana,ana@x.ma,100\nI,2,Bob,,50\nU,3,Cyd,c@x.ma,1\n",
                 "batch_2.csv": HEAD + "U,1,,ana@y.ma,\nD,2,,,\nI,4,Dan,d@x.ma,0\n",
                 "batch_10.csv": HEAD + "U,1,Anna,,120.5\nI,2,Bob,b@x.ma,\nD,9,,,\n",
                 "batch_3.csv.tmp": HEAD + "D,1,,,\n", "manifest.json": "{}"}),
         folder({"batch_9.csv": HEAD + "I,5,Eve,e@x.ma,10\n", "batch_11.csv": HEAD + "U,5,,,99\n", "batch_100.csv": HEAD + "I,5,Eve2,,\n",
                 "batch_20.csv": HEAD + "D,5,,,\nU,5,Ghost,,1\n"})]
    r = rng(4211)
    names = ["Ana", "Bob", "Cyd", "Dan", ""]
    for _ in range(6):
        files = {}
        for n in r.sample(range(1, 25), r.randint(2, 6)):
            lines = []
            for _ in range(r.randint(1, 6)):
                op = r.choice(["I", "I", "U", "U", "D"])
                lines.append(f"{op},{r.randint(1, 5)},{r.choice(names)},{r.choice(['a@x.ma', 'b@x.ma', ''])},{r.choice(['10', '2.5', ''])}")
            files[f"batch_{n}.csv"] = HEAD + "\n".join(lines) + "\n"
        files["batch_7.csv.tmp"] = HEAD + "D,1,,,\n"
        t.append(folder(files))
    return [{"input_dir": x} for x in t]
