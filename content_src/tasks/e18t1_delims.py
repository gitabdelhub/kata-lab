from kit import folder, rng

ID = "e18t1"
NAME = "Supplier Price Files"
LANG = "pyspark"
PARAMS = ["spark", "input_dir"]
MINUTES = 20
TAGS = ["séparateur par fichier", "virgule décimale", "normaliser les en-têtes", "dernière version"]
DESC = """
<p>Suppliers drop price lists in <code>input_dir</code> as <code>.csv</code> files, each with a header. Each supplier uses its own format:</p>
<ul><li>some files use <code>,</code> as separator and <code>.</code> for decimals;</li><li>other files use <code>;</code> as separator and <code>,</code> for decimals (for example <code>12,50</code>).</li></ul>
<p>The separator of a file is <code>;</code> when its header line contains a <code>;</code>, otherwise <code>,</code>. Header names can have different case and spaces around them, but they are always <code>sku</code>, <code>price</code> and <code>valid_from</code> (a date <code>yyyy-MM-dd</code>). Rows whose price or date cannot be read are ignored. Values can have spaces around them.</p>
<p>Your task is to return, for each <code>sku</code>, the price of the row with the latest <code>valid_from</code>, with the columns <code>sku</code> (string, upper case), <code>price</code> (double, rounded to 2 decimals) and <code>valid_from</code> (date), sorted by <code>sku</code>. When two rows of the same sku have the same latest date, keep the highest price.</p>
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
from pyspark.sql.window import Window


def solve(spark, input_dir):
    parts = []
    for root, _, files in os.walk(input_dir):
        for name in files:
            if not name.endswith(".csv"):
                continue
            path = os.path.join(root, name)
            with open(path) as fh:
                header = fh.readline()
            sep = ";" if ";" in header else ","
            d = spark.read.option("header", True).option("sep", sep).csv(path)
            d = d.toDF(*[c.strip().lower() for c in d.columns])
            price = F.trim("price")
            if sep == ";":
                price = F.regexp_replace(price, ",", ".")
            parts.append(d.select(F.upper(F.trim("sku")).alias("sku"),
                                  price.try_cast("double").alias("price"),
                                  F.try_to_date(F.trim("valid_from"), "yyyy-MM-dd").alias("valid_from")))
    df = reduce(lambda a, b: a.unionByName(b), parts)
    df = df.filter(F.col("sku").isNotNull() & (F.col("sku") != "") & F.col("price").isNotNull() & F.col("valid_from").isNotNull())
    w = Window.partitionBy("sku").orderBy(F.col("valid_from").desc(), F.col("price").desc())
    return (df.withColumn("rn", F.row_number().over(w)).filter("rn = 1")
            .select("sku", F.round("price", 2).alias("price"), "valid_from").orderBy("sku"))
"""
MUTANTS = [
    """
import os
from functools import reduce
from pyspark.sql import functions as F
from pyspark.sql.window import Window
def solve(spark, input_dir):
    parts = []
    for root, _, files in os.walk(input_dir):
        for name in files:
            if not name.endswith(".csv"): continue
            path = os.path.join(root, name)
            sep = ";" if ";" in open(path).readline() else ","
            d = spark.read.option("header", True).option("sep", sep).csv(path)
            d = d.toDF(*[c.strip().lower() for c in d.columns])
            parts.append(d.select(F.upper(F.trim("sku")).alias("sku"), F.trim("price").try_cast("double").alias("price"), F.try_to_date(F.trim("valid_from"), "yyyy-MM-dd").alias("valid_from")))
    df = reduce(lambda a, b: a.unionByName(b), parts).filter(F.col("price").isNotNull() & F.col("valid_from").isNotNull())
    w = Window.partitionBy("sku").orderBy(F.col("valid_from").desc(), F.col("price").desc())
    return df.withColumn("rn", F.row_number().over(w)).filter("rn = 1").select("sku", F.round("price", 2).alias("price"), "valid_from").orderBy("sku")
""",
    """
import os
from functools import reduce
from pyspark.sql import functions as F
from pyspark.sql.window import Window
def solve(spark, input_dir):
    parts = []
    for root, _, files in os.walk(input_dir):
        for name in files:
            if not name.endswith(".csv"): continue
            path = os.path.join(root, name)
            sep = ";" if ";" in open(path).readline() else ","
            d = spark.read.option("header", True).option("sep", sep).csv(path)
            d = d.toDF(*[c.strip().lower() for c in d.columns])
            price = F.regexp_replace(F.trim("price"), ",", ".") if sep == ";" else F.trim("price")
            parts.append(d.select(F.upper(F.trim("sku")).alias("sku"), price.try_cast("double").alias("price"), F.try_to_date(F.trim("valid_from"), "yyyy-MM-dd").alias("valid_from")))
    df = reduce(lambda a, b: a.unionByName(b), parts).filter(F.col("price").isNotNull() & F.col("valid_from").isNotNull())
    return df.groupBy("sku").agg(F.max("valid_from").alias("valid_from"), F.round(F.max("price"), 2).alias("price")).select("sku", "price", "valid_from").orderBy("sku")
""",
]


def comma(rows, head="sku,price,valid_from"):
    return head + "\n" + "".join(",".join(r) + "\n" for r in rows)


def semi(rows, head="SKU ; Price ; Valid_From"):
    return head + "\n" + "".join(";".join(r) + "\n" for r in rows)


def tests():
    t = [folder({"acme.csv": comma([["a1", "10.00", "2026-01-01"], ["b2", "5.5", "2026-02-01"], ["c3", "n/a", "2026-03-01"]]),
                 "eu/zeta.csv": semi([["A1", "12,50", "2026-02-01"], [" b2 ", "4,99", "2026-01-15"], ["C3", "7,00", "2026-01-01"]]),
                 "readme.txt": "sku,price,valid_from\nA1,1.0,2030-01-01\n"}),
         folder({"x.csv": comma([["k", "1.0", "2026-05-01"], ["k", "3.0", "2026-05-01"], ["k", "9.0", "bad"]], head=" Sku , PRICE ,valid_from")})]
    r = rng(1801)
    for _ in range(6):
        files = {}
        for f in range(r.randint(1, 4)):
            rows = [[r.choice(["a1", "A1", "b2", "c3", "d4"]), str(r.choice([1.5, 2.25, 10.0, 7.99])), f"2026-0{r.randint(1, 4)}-1{r.randint(0, 9)}"] for _ in range(r.randint(1, 5))]
            if r.random() < 0.5:
                rows = [[s, p.replace(".", ","), d] for s, p, d in rows]
                files[f"s{f}.csv"] = semi(rows)
            else:
                files[f"s{f}.csv"] = comma(rows)
        t.append(folder(files))
    return [{"input_dir": x} for x in t]
