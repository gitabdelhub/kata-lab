from kit import folder, rng

ID = "p2x2"
NAME = "Schema Drift Across Exports"
LANG = "pyspark"
PARAMS = ["spark", "input_dir"]
MINUTES = 22
TAGS = ["lire un dossier", "unionByName(allowMissingColumns)", "renommer des colonnes", "dates de fichier"]
SUMMARY_FR = "Des exports CSV mensuels dont le schéma a changé (colonnes renommées, ajoutées, ordre différent). Les réunir avec les bons noms, compléter les colonnes absentes, puis calculer le total par client et par mois."
HINTS = ["Lis chaque fichier séparément, normalise les noms (trim, lower, et le dictionnaire de renommage), ajoute currency = NULL quand elle manque, puis unionByName.",
         "Le mois vient du NOM du fichier (orders_2026_01.csv), pas d'une colonne.",
         "currency absente = 'MAD' : F.coalesce(F.col('currency'), F.lit('MAD')) après l'union."]
DESC = """
<p>A shop exports its orders every month to <code>input_dir</code>, in files named <code>orders_YYYY_MM.csv</code>. Over time, the export changed:</p>
<ul><li>column names can have spaces and capital letters (<code>" Customer "</code>);</li><li>in old files the amount column is called <code>total</code>, in new files <code>amount</code>; the customer column is called <code>client</code> in old files and <code>customer</code> in new files;</li><li>the column <code>currency</code> only exists in recent files; when it is missing, the currency is <code>"MAD"</code>;</li><li>the columns are not always in the same order, and some files have extra columns that must be ignored.</li></ul>
<p>Every file has a header. Amounts are decimal numbers written as text; a value that is not a number counts as <code>0</code>. Customer names must be trimmed. Files whose name does not match <code>orders_YYYY_MM.csv</code> are ignored.</p>
<p>Your task is to return the total amount per customer, month and currency, with the columns <code>customer</code> (string), <code>month</code> (string, <code>"YYYY-MM"</code>), <code>currency</code> (string) and <code>total</code> (double, rounded to 2 decimals), sorted by <code>customer</code>, <code>month</code>, then <code>currency</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
import os
from pyspark.sql import SparkSession, DataFrame, functions as F


def solve(spark: SparkSession, input_dir: str) -> DataFrame:
    # write your code here
    return spark.read.option("header", True).csv(input_dir)
"""
SOLUTION = """
import os
import re
from functools import reduce
from pyspark.sql import functions as F

RENAME = {"total": "amount", "client": "customer"}


def solve(spark, input_dir):
    parts = []
    for name in sorted(os.listdir(input_dir)):
        m = re.fullmatch(r"orders_(\\d{4})_(\\d{2})\\.csv", name)
        if not m:
            continue
        d = spark.read.option("header", True).csv(os.path.join(input_dir, name))
        cols = [RENAME.get(c.strip().lower(), c.strip().lower()) for c in d.columns]
        d = d.toDF(*cols)
        if "currency" not in cols:
            d = d.withColumn("currency", F.lit(None).cast("string"))
        parts.append(d.select("customer", "amount", "currency").withColumn("month", F.lit(m.group(1) + "-" + m.group(2))))
    df = reduce(lambda a, b: a.unionByName(b), parts)
    df = df.withColumn("currency", F.coalesce(F.col("currency"), F.lit("MAD")))
    amount = F.coalesce(F.expr("try_cast(trim(amount) AS DOUBLE)"), F.lit(0.0))
    return (df.groupBy(F.trim("customer").alias("customer"), "month", "currency")
            .agg(F.round(F.sum(amount), 2).alias("total"))
            .orderBy("customer", "month", "currency"))
"""
MUTANTS = [
    """
import os, re
from functools import reduce
from pyspark.sql import functions as F
def solve(spark, input_dir):
    parts = []
    for name in sorted(os.listdir(input_dir)):
        m = re.fullmatch(r"orders_(\\d{4})_(\\d{2})\\.csv", name)
        if not m:
            continue
        d = spark.read.option("header", True).csv(os.path.join(input_dir, name))
        d = d.toDF(*[c.strip().lower() for c in d.columns])
        if "total" in d.columns: d = d.withColumnRenamed("total", "amount")
        if "client" in d.columns: d = d.withColumnRenamed("client", "customer")
        if "currency" not in d.columns: d = d.withColumn("currency", F.lit("MAD"))
        parts.append(d.select(d.columns[0], d.columns[1], "currency").toDF("customer", "amount", "currency").withColumn("month", F.lit(m.group(1) + "-" + m.group(2))))
    df = reduce(lambda a, b: a.union(b), parts)
    amount = F.coalesce(F.expr("try_cast(trim(amount) AS DOUBLE)"), F.lit(0.0))
    return df.groupBy(F.trim("customer").alias("customer"), "month", "currency").agg(F.round(F.sum(amount), 2).alias("total")).orderBy("customer", "month", "currency")
""",
    """
import os, re
from functools import reduce
from pyspark.sql import functions as F
RENAME = {"total": "amount", "client": "customer"}
def solve(spark, input_dir):
    parts = []
    for name in sorted(os.listdir(input_dir)):
        m = re.fullmatch(r"orders_(\\d{4})_(\\d{2})\\.csv", name)
        if not m:
            continue
        d = spark.read.option("header", True).csv(os.path.join(input_dir, name))
        cols = [RENAME.get(c.strip().lower(), c.strip().lower()) for c in d.columns]
        d = d.toDF(*cols)
        keep = [c for c in ("customer", "amount", "currency") if c in cols]
        parts.append(d.select(*keep).withColumn("month", F.lit(m.group(1) + "-" + m.group(2))))
    df = reduce(lambda a, b: a.unionByName(b, allowMissingColumns=True), parts)
    df = df.withColumn("currency", F.coalesce(F.col("currency"), F.lit("MAD")))
    return df.groupBy(F.trim("customer").alias("customer"), "month", "currency").agg(F.round(F.sum(F.expr("try_cast(trim(amount) AS DOUBLE)")), 2).alias("total")).orderBy("customer", "month", "currency")
""",
]
LAYOUTS = [
    (["client", "total"], False), ([" Client ", "Total", "note"], False), (["total", "client"], False),
    (["customer", "amount", "currency"], True), (["Currency", " customer", "AMOUNT"], True), (["amount", "customer", "channel", "currency"], True),
]


def csv(cols, rows, has_cur):
    out = [",".join(cols)]
    for cust, amt, cur in rows:
        vals = []
        for c in cols:
            k = c.strip().lower()
            vals.append(cust if k in ("client", "customer") else amt if k in ("total", "amount") else cur if k == "currency" else "web")
        out.append(",".join(vals))
    return "\n".join(out) + "\n"


def tests():
    t = [folder({"orders_2025_12.csv": "client,total\nAmina,100.5\n Omar ,20\nAmina,x\n",
                 "orders_2026_01.csv": " Currency ,AMOUNT,Customer\nEUR,10,Amina\nMAD,30.25,Omar\nEUR,5.5,Amina \n",
                 "notes.txt": "export v2 since January\n"}),
         folder({"orders_2026_02.csv": "total,client,note\n7,Sara,ok\n,Sara,empty\n", "orders_2026_2.csv": "client,total\nSara,999\n"})]
    r = rng(302)
    for k in range(6):
        files = {}
        for mo in r.sample(["2025_11", "2025_12", "2026_01", "2026_02", "2026_03"], r.randint(2, 4)):
            cols, has_cur = r.choice(LAYOUTS)
            rows = [[r.choice(["Amina", " Omar", "Sara ", "Kofi"]), r.choice([str(round(r.uniform(1, 300), 2)), "12", "", "n/a"]), r.choice(["MAD", "EUR"])] for _ in range(r.randint(1, 6))]
            files[f"orders_{mo}.csv"] = csv(cols, rows, has_cur)
        if k % 3 == 0:
            files["orders_backup.csv"] = "client,total\nX,1\n"
        t.append(folder(files))
    return [{"input_dir": x} for x in t]
