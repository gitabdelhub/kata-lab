from kit import folder, rng

ID = "e05t1"
NAME = "Bank Statement Files"
LANG = "pyspark"
PARAMS = ["spark", "input_dir"]
MINUTES = 20
TAGS = ["deux formats de fichiers", "séparateur ;", "virgule décimale", "dates dd/MM/yyyy"]
DESC = """
<p>A company downloads its bank statements every day. The files are stored in <code>input_dir/&lt;bank&gt;/</code>, but each bank uses its own format:</p>
<ul><li>files ending with <code>.csv</code> use a comma <code>,</code> as separator and a dot as decimal separator (<code>1250.50</code>);</li><li>files ending with <code>.txt</code> use a semicolon <code>;</code> as separator and a <b>comma</b> as decimal separator (<code>1250,50</code>);</li><li>other files are ignored.</li></ul>
<p>Every file has a header with the columns <code>date</code>, <code>ref</code> and <code>amount</code>, in this order. Dates are written <code>dd/MM/yyyy</code>. A positive amount is a credit, a negative amount is a debit. Lines with an invalid date or an invalid amount are ignored.</p>
<p>The same transaction can be downloaded twice (in two files of the same bank): two lines of the same bank with the same <code>ref</code> are the same transaction and are counted once.</p>
<p>Your task is to return, for every bank and day, the columns <code>bank</code> (string), <code>day</code> (date), <code>transactions</code> (long), <code>credits</code> and <code>debits</code> (double, sums rounded to 2 decimals, <code>debits</code> is written as a <b>positive</b> number, <code>0.0</code> if none), sorted by <code>bank</code>, then <code>day</code>.</p>
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
from functools import reduce
from pyspark.sql import functions as F


def solve(spark, input_dir):
    parts = []
    for bank in sorted(os.listdir(input_dir)):
        bdir = os.path.join(input_dir, bank)
        for name in sorted(os.listdir(bdir)):
            if name.endswith(".csv"):
                sep, dec = ",", "."
            elif name.endswith(".txt"):
                sep, dec = ";", ","
            else:
                continue
            d = spark.read.option("header", True).option("sep", sep).csv(os.path.join(bdir, name))
            d = d.toDF("date", "ref", "amount")
            amt = F.regexp_replace(F.trim("amount"), ",", ".") if dec == "," else F.trim("amount")
            parts.append(d.select(F.lit(bank).alias("bank"),
                                  F.expr("try_to_date(trim(date), 'dd/MM/yyyy')").alias("day"),
                                  F.trim("ref").alias("ref"),
                                  amt.alias("amount_s")))
    df = reduce(lambda a, b: a.unionByName(b), parts)
    df = df.withColumn("amount", F.expr("try_cast(amount_s AS DOUBLE)"))
    df = df.filter(F.col("day").isNotNull() & F.col("amount").isNotNull()).dropDuplicates(["bank", "ref"])
    return (df.groupBy("bank", "day").agg(
                F.count("*").alias("transactions"),
                F.round(F.sum(F.when(F.col("amount") > 0, F.col("amount")).otherwise(0.0)), 2).alias("credits"),
                F.round(-F.sum(F.when(F.col("amount") < 0, F.col("amount")).otherwise(0.0)), 2).alias("debits"))
            .orderBy("bank", "day"))
"""
MUTANTS = [
    """
import os
from functools import reduce
from pyspark.sql import functions as F
def solve(spark, input_dir):
    parts = []
    for bank in sorted(os.listdir(input_dir)):
        for name in sorted(os.listdir(os.path.join(input_dir, bank))):
            if name.endswith(".csv"): sep = ","
            elif name.endswith(".txt"): sep = ";"
            else: continue
            d = spark.read.option("header", True).option("sep", sep).csv(os.path.join(input_dir, bank, name)).toDF("date", "ref", "amount")
            parts.append(d.select(F.lit(bank).alias("bank"), F.expr("try_to_date(trim(date), 'dd/MM/yyyy')").alias("day"), F.trim("ref").alias("ref"), F.trim("amount").alias("amount_s")))
    df = reduce(lambda a, b: a.unionByName(b), parts).withColumn("amount", F.expr("try_cast(amount_s AS DOUBLE)"))
    df = df.filter(F.col("day").isNotNull() & F.col("amount").isNotNull()).dropDuplicates(["bank", "ref"])
    return df.groupBy("bank", "day").agg(F.count("*").alias("transactions"), F.round(F.sum(F.when(F.col("amount") > 0, F.col("amount")).otherwise(0.0)), 2).alias("credits"), F.round(-F.sum(F.when(F.col("amount") < 0, F.col("amount")).otherwise(0.0)), 2).alias("debits")).orderBy("bank", "day")
""",
    """
import os
from functools import reduce
from pyspark.sql import functions as F
def solve(spark, input_dir):
    parts = []
    for bank in sorted(os.listdir(input_dir)):
        for name in sorted(os.listdir(os.path.join(input_dir, bank))):
            if name.endswith(".csv"): sep, dec = ",", "."
            elif name.endswith(".txt"): sep, dec = ";", ","
            else: continue
            d = spark.read.option("header", True).option("sep", sep).csv(os.path.join(input_dir, bank, name)).toDF("date", "ref", "amount")
            amt = F.regexp_replace(F.trim("amount"), ",", ".") if dec == "," else F.trim("amount")
            parts.append(d.select(F.lit(bank).alias("bank"), F.expr("try_to_date(trim(date), 'dd/MM/yyyy')").alias("day"), F.trim("ref").alias("ref"), amt.alias("amount_s")))
    df = reduce(lambda a, b: a.unionByName(b), parts).withColumn("amount", F.expr("try_cast(amount_s AS DOUBLE)"))
    df = df.filter(F.col("day").isNotNull() & F.col("amount").isNotNull())
    return df.groupBy("bank", "day").agg(F.count("*").alias("transactions"), F.round(F.sum(F.when(F.col("amount") > 0, F.col("amount")).otherwise(0.0)), 2).alias("credits"), F.round(-F.sum(F.when(F.col("amount") < 0, F.col("amount")).otherwise(0.0)), 2).alias("debits")).orderBy("bank", "day")
""",
    """
import os
from functools import reduce
from pyspark.sql import functions as F
def solve(spark, input_dir):
    parts = []
    for bank in sorted(os.listdir(input_dir)):
        for name in sorted(os.listdir(os.path.join(input_dir, bank))):
            if name.endswith(".csv"): sep, dec = ",", "."
            elif name.endswith(".txt"): sep, dec = ";", ","
            else: continue
            d = spark.read.option("header", True).option("sep", sep).csv(os.path.join(input_dir, bank, name)).toDF("date", "ref", "amount")
            amt = F.regexp_replace(F.trim("amount"), ",", ".") if dec == "," else F.trim("amount")
            parts.append(d.select(F.lit(bank).alias("bank"), F.to_date(F.trim("date")).alias("day"), F.trim("ref").alias("ref"), amt.alias("amount_s")))
    df = reduce(lambda a, b: a.unionByName(b), parts).withColumn("amount", F.expr("try_cast(amount_s AS DOUBLE)"))
    df = df.filter(F.col("amount").isNotNull()).dropDuplicates(["bank", "ref"])
    return df.groupBy("bank", "day").agg(F.count("*").alias("transactions"), F.round(F.sum(F.when(F.col("amount") > 0, F.col("amount")).otherwise(0.0)), 2).alias("credits"), F.round(-F.sum(F.when(F.col("amount") < 0, F.col("amount")).otherwise(0.0)), 2).alias("debits")).orderBy("bank", "day")
""",
]


def f_csv(rows):
    return "date,ref,amount\n" + "\n".join(f"{d},{r},{a}" for d, r, a in rows) + "\n"


def f_txt(rows):
    return "date;ref;amount\n" + "\n".join(f"{d};{r};{str(a).replace('.', ',')}" for d, r, a in rows) + "\n"


def tests():
    t = [folder({"atlas/2026-03-01.csv": f_csv([["01/03/2026", "T1", "1250.50"], ["01/03/2026", "T2", "-300"], ["02/03/2026", "T3", "-20.25"], ["31/02/2026", "T4", "10"]]),
                 "atlas/2026-03-02.csv": f_csv([["02/03/2026", "T3", "-20.25"], ["02/03/2026", "T5", "abc"]]),
                 "sahel/releve.txt": f_txt([["01/03/2026", "S1", "99.9"], ["01/03/2026", "S2", "-0.1"], [" 01/03/2026 ", "S3", "1000.5"]]),
                 "sahel/readme.pdf": "binary"}),
         folder({"nord/a.txt": f_txt([["15/04/2026", "N1", "-12.5"], ["15/04/2026", "N1", "-12.5"]]), "nord/b.csv": f_csv([["15/04/2026", "N2", "0"]])})]
    r = rng(501)
    for _ in range(6):
        files, made = {}, {}
        for bank in r.sample(["atlas", "sahel", "nord"], r.randint(1, 3)):
            for k in range(r.randint(1, 3)):
                rows = []
                for _ in range(r.randint(1, 6)):
                    ref = f"{bank[0].upper()}{r.randint(1, 9)}"
                    key = (bank, ref)
                    if key not in made:
                        made[key] = [f"{r.randint(1, 3):02d}/03/2026" if r.random() < 0.9 else "2026-03-01", ref, round(r.uniform(-500, 500), 2)]
                    rows.append(made[key])
                ext = r.choice(["csv", "txt"])
                files[f"{bank}/f{k}.{ext}"] = f_csv(rows) if ext == "csv" else f_txt(rows)
        t.append(folder(files))
    return [{"input_dir": x} for x in t]
