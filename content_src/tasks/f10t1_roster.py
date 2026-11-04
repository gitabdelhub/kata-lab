from kit import folder, rng

ID = "f10t1"
NAME = "Seat Roster Sheets"
LANG = "pyspark"
PARAMS = ["spark", "input_dir"]
MINUTES = 22
TAGS = ["consigne longue", "grille lue en colonnes", "fichiers par dossier", "dédoublonnage"]
DESC = """
<p>Before the SaaS platform had an admin console, customer success managers kept track of the seats of each customer (a <i>tenant</i>) on paper roster sheets. The sheets were later typed into text files, keeping the original layout, and you must now load them so that billing can compare them with the platform.</p>
<p>Each tenant has its own folder in <code>input_dir</code>, named after the tenant, and every roster sheet of the tenant is a file whose name ends with <code>.sheet</code> somewhere inside that folder (sheets were sometimes filed in sub-folders by year). Anything else in those folders, like scanner logs, must be ignored.</p>
<p>On a sheet, managers did not write one user per line. They wrote each username <b>vertically</b>, one character per line, from top to bottom, and moved one column to the right for the next user. A short username leaves the rest of its column empty, and an empty cell was typed as a dot. When the typist reached the end of the meaningful characters of a line, she often stopped typing, so a line can be shorter than the others: the missing cells on the right are empty too. A column made only of empty cells is just a gap between users.</p>
<p>When a user was an administrator, the manager drew an <code>@</code> in the first cell of the column, just above the username. The <code>@</code> is not part of the name. Usernames were written with random capitals, but the platform treats them case-insensitively, so <code>JDoe</code> and <code>jdoe</code> are the same seat. The same user can of course appear on several sheets of a tenant; such a user is one seat, and is an administrator if they were marked as administrator on at least one sheet.</p>
<p>Your task is to return one row per tenant that has at least one seat, with the columns <code>tenant</code> (string, the folder name), <code>seats</code> (long, number of distinct users), <code>admins</code> (long, number of distinct users who are administrators) and <code>longest_user</code> (string, the lower-case username with the most characters; if several have the same length, the first in alphabetical order). Sort the rows by <code>tenant</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F


def solve(spark: SparkSession, input_dir: str) -> DataFrame:
    # write your code here
    return spark.read.text(input_dir)
"""
SOLUTION = """
import os
from pyspark.sql import functions as F


def solve(spark, input_dir):
    rows = []
    for tenant in sorted(os.listdir(input_dir)):
        base = os.path.join(input_dir, tenant)
        if not os.path.isdir(base):
            continue
        for root, _, files in os.walk(base):
            for name in files:
                if not name.endswith(".sheet"):
                    continue
                with open(os.path.join(root, name)) as fh:
                    lines = [l.rstrip("\\n").rstrip() for l in fh]
                width = max((len(l) for l in lines), default=0)
                grid = [l.ljust(width, ".") for l in lines]
                for c in range(width):
                    col = "".join(g[c] for g in grid).replace(".", "")
                    if not col:
                        continue
                    admin = col.startswith("@")
                    user = col.lstrip("@").lower()
                    if user:
                        rows.append((tenant, user, admin))
    df = spark.createDataFrame(rows, "tenant string, user string, admin boolean")
    users = df.groupBy("tenant", "user").agg(F.max(F.col("admin").cast("int")).alias("admin"))
    w_long = users.withColumn("len", F.length("user"))
    best = (w_long.groupBy("tenant").agg(F.min(F.struct((-F.col("len")).alias("l"), F.col("user").alias("u"))).alias("b")))
    agg = users.groupBy("tenant").agg(F.count("*").alias("seats"), F.sum("admin").cast("long").alias("admins"))
    return (agg.join(best, "tenant").select("tenant", "seats", "admins", F.col("b.u").alias("longest_user")).orderBy("tenant"))
"""
MUTANTS = [
    """
import os
from pyspark.sql import functions as F
def solve(spark, input_dir):
    rows = []
    for tenant in sorted(os.listdir(input_dir)):
        for root, _, files in os.walk(os.path.join(input_dir, tenant)):
            for name in files:
                if not name.endswith(".sheet"): continue
                lines = [l.rstrip() for l in open(os.path.join(root, name))]
                for l in lines:
                    u = l.replace(".", "")
                    if u: rows.append((tenant, u.lstrip("@").lower(), u.startswith("@")))
    df = spark.createDataFrame(rows, "tenant string, user string, admin boolean")
    users = df.groupBy("tenant", "user").agg(F.max(F.col("admin").cast("int")).alias("admin"))
    best = users.withColumn("len", F.length("user")).groupBy("tenant").agg(F.min(F.struct((-F.col("len")).alias("l"), F.col("user").alias("u"))).alias("b"))
    agg = users.groupBy("tenant").agg(F.count("*").alias("seats"), F.sum("admin").cast("long").alias("admins"))
    return agg.join(best, "tenant").select("tenant", "seats", "admins", F.col("b.u").alias("longest_user")).orderBy("tenant")
""",
    """
import os
from pyspark.sql import functions as F
def solve(spark, input_dir):
    rows = []
    for tenant in sorted(os.listdir(input_dir)):
        for root, _, files in os.walk(os.path.join(input_dir, tenant)):
            for name in files:
                if not name.endswith(".sheet"): continue
                lines = [l.rstrip() for l in open(os.path.join(root, name))]
                width = max((len(l) for l in lines), default=0)
                grid = [l.ljust(width, ".") for l in lines]
                for c in range(width):
                    col = "".join(g[c] for g in grid).replace(".", "")
                    if col: rows.append((tenant, col.lstrip("@"), col.startswith("@")))
    df = spark.createDataFrame(rows, "tenant string, user string, admin boolean")
    users = df.groupBy("tenant", "user").agg(F.max(F.col("admin").cast("int")).alias("admin"))
    best = users.withColumn("len", F.length("user")).groupBy("tenant").agg(F.min(F.struct((-F.col("len")).alias("l"), F.col("user").alias("u"))).alias("b"))
    agg = users.groupBy("tenant").agg(F.count("*").alias("seats"), F.sum("admin").cast("long").alias("admins"))
    return agg.join(best, "tenant").select("tenant", "seats", "admins", F.col("b.u").alias("longest_user")).orderBy("tenant")
""",
]


def sheet(users, height=None):
    """users: list of (name, admin). Builds a vertical grid, trailing dots trimmed on some lines."""
    cols = [("@" if a else "") + n for n, a in users]
    h = height or max(len(c) for c in cols)
    lines = []
    for r in range(h):
        line = "".join(c[r] if r < len(c) else "." for c in cols)
        lines.append(line)
    return lines


def render(lines, trim):
    out = []
    for l in lines:
        out.append(l.rstrip(".") if trim else l)
    return "\n".join(out) + "\n"


def tests():
    t = [folder({"acme/2025/q1.sheet": render(sheet([("JDoe", True), ("amy", False), ("Bob", False)]), True),
                 "acme/2026/q1.sheet": render(sheet([("jdoe", False), ("Carla", True), ("", False), ("amy", False)]), False),
                 "acme/scan.log": "jdoe\nzed\n",
                 "globex/r.sheet": render(sheet([("Li", False), ("Ng", False)]), True)}),
         folder({"t1/a.sheet": render(sheet([("x", True)]), False), "t2/notes.txt": "nothing\n"})]
    r = rng(3101)
    names = ["ana", "Bo", "carl", "Dina", "ed", "FayE", "gus", "hiro", "ivy", "jo"]
    for _ in range(6):
        files = {}
        for tn in r.sample(["acme", "globex", "initech"], r.randint(1, 3)):
            for k in range(r.randint(1, 3)):
                us = [(r.choice(names) if r.random() > 0.15 else "", r.random() < 0.3) for _ in range(r.randint(1, 5))]
                us = [(n.upper() if r.random() < 0.3 else n, a and bool(n)) for n, a in us]
                if all(not n for n, _ in us):
                    us.append(("solo", False))
                lines = sheet(us, None)
                files[f"{tn}/{r.choice(['', '2025/', '2026/'])}s{k}.sheet"] = render(lines, r.random() < 0.5)
            if r.random() < 0.4:
                files[f"{tn}/readme.txt"] = "ignore me\n"
        t.append(folder(files))
    return [{"input_dir": x} for x in t]
