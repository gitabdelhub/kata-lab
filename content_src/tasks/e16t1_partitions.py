from kit import folder, rng

ID = "e16t1"
NAME = "Partitioned Sales Folders"
LANG = "pyspark"
PARAMS = ["spark", "input_dir"]
MINUTES = 20
TAGS = ["partitions Hive", "basePath", "colonnes de partition", "fichiers vides"]
DESC = """
<p>A retail chain stores its sales in a data lake with <b>Hive-style partitions</b>:</p>
<pre class="exv">input_dir/
  year=YYYY/
    month=MM/
      day=DD/
        store=&lt;store_id&gt;/
          part-&lt;n&gt;.csv</pre>
<p>Each CSV file has a header and the columns <code>sale_id</code>, <code>sku</code>, <code>qty</code> and <code>unit_price</code>. The date and the store are <b>not</b> columns of the files: they come only from the folder names. Some files only contain the header. Folders whose name does not have the form <code>key=value</code> (for example <code>_tmp</code>) must be ignored, as well as files that do not end with <code>.csv</code>.</p>
<p>A sale can be written in several files of the same store and day (the job was replayed): rows with the same <code>store</code>, day and <code>sale_id</code> are the same sale and count once. Rows with a <code>qty</code> or <code>unit_price</code> that is not a number are ignored.</p>
<p>Your task is to return, for each store and day, the columns <code>store</code> (string), <code>sale_date</code> (date), <code>sales</code> (long, number of distinct sales), <code>units</code> (long) and <code>revenue</code> (double, <code>sum(qty * unit_price)</code> rounded to 2 decimals), sorted by <code>sale_date</code>, then <code>store</code>.</p>
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


def solve(spark, input_dir):
    parts = []
    for root, dirs, files in os.walk(input_dir):
        rel = os.path.relpath(root, input_dir)
        keys = {}
        ok = True
        for piece in ([] if rel == "." else rel.split(os.sep)):
            m = re.fullmatch(r"(\\w+)=(.+)", piece)
            if not m:
                ok = False
                break
            keys[m.group(1)] = m.group(2)
        if not ok or set(keys) != {"year", "month", "day", "store"}:
            continue
        for name in files:
            if not name.endswith(".csv"):
                continue
            d = spark.read.option("header", True).csv(os.path.join(root, name))
            if not d.columns:
                continue
            parts.append(d.select(
                F.lit(keys["store"]).alias("store"),
                F.to_date(F.lit(f"{keys['year']}-{keys['month']}-{keys['day']}")).alias("sale_date"),
                F.trim("sale_id").alias("sale_id"),
                F.expr("try_cast(qty AS INT)").alias("qty"),
                F.expr("try_cast(unit_price AS DOUBLE)").alias("price")))
    schema = "store string, sale_date date, sales long, units long, revenue double"
    if not parts:
        return spark.createDataFrame([], schema)
    df = reduce(lambda a, b: a.unionByName(b), parts)
    df = df.filter(F.col("qty").isNotNull() & F.col("price").isNotNull()).dropDuplicates(["store", "sale_date", "sale_id"])
    return (df.groupBy("store", "sale_date").agg(
                F.count("*").alias("sales"), F.sum("qty").cast("long").alias("units"),
                F.round(F.sum(F.col("qty") * F.col("price")), 2).alias("revenue"))
            .orderBy("sale_date", "store"))
"""
MUTANTS = [
    """
from pyspark.sql import functions as F
def solve(spark, input_dir):
    df = spark.read.option("header", True).option("pathGlobFilter", "*.csv").csv(input_dir)
    df = df.select(F.col("store").cast("string").alias("store"), F.make_date("year", "month", "day").alias("sale_date"), F.trim("sale_id").alias("sale_id"), F.expr("try_cast(qty AS INT)").alias("qty"), F.expr("try_cast(unit_price AS DOUBLE)").alias("price"))
    df = df.filter(F.col("qty").isNotNull() & F.col("price").isNotNull())
    return df.groupBy("store", "sale_date").agg(F.count("*").alias("sales"), F.sum("qty").cast("long").alias("units"), F.round(F.sum(F.col("qty") * F.col("price")), 2).alias("revenue")).orderBy("sale_date", "store")
""",
    """
from pyspark.sql import functions as F
def solve(spark, input_dir):
    df = spark.read.option("header", True).option("pathGlobFilter", "*.csv").csv(input_dir)
    df = df.select(F.col("store").cast("string").alias("store"), F.make_date("year", "month", "day").alias("sale_date"), F.trim("sale_id").alias("sale_id"), F.expr("try_cast(qty AS INT)").alias("qty"), F.expr("try_cast(unit_price AS DOUBLE)").alias("price"))
    df = df.filter(F.col("qty").isNotNull() & F.col("price").isNotNull()).dropDuplicates(["sale_id"])
    return df.groupBy("store", "sale_date").agg(F.count("*").alias("sales"), F.sum("qty").cast("long").alias("units"), F.round(F.sum(F.col("qty") * F.col("price")), 2).alias("revenue")).orderBy("sale_date", "store")
""",
]
H = "sale_id,sku,qty,unit_price"


def csv(rows):
    return H + "\n" + "".join(",".join(map(str, r)) + "\n" for r in rows)


def tests():
    t = [folder({"year=2026/month=03/day=01/store=S01/part-0.csv": csv([["1", "A", 2, 10.0], ["2", "B", 1, 5.5]]),
                 "year=2026/month=03/day=01/store=S01/part-1.csv": csv([["2", "B", 1, 5.5], ["3", "C", "x", 1]]),
                 "year=2026/month=03/day=01/store=S02/part-0.csv": csv([]),
                 "year=2026/month=03/day=02/store=S02/part-0.csv": csv([["1", "A", 3, 9.99]]),
                 "year=2026/month=03/day=02/store=S02/_SUCCESS": "",
                 "_tmp/year=2026/month=03/day=02/store=S02/part-9.csv": csv([["99", "Z", 100, 100]])}),
         folder({"year=2025/month=12/day=31/store=7/a.csv": csv([["1", "A", 1, 1.0], ["1", "A", 1, 1.0]]),
                 "year=2026/month=01/day=01/store=7/a.csv": csv([["1", "A", 2, 2.5]])})]
    r = rng(1601)
    for _ in range(6):
        files, made = {}, {}
        for day in r.sample(["01", "02", "03"], r.randint(1, 3)):
            for st in r.sample(["S01", "S02", "S03"], r.randint(1, 3)):
                for p in range(r.randint(1, 2)):
                    rows = []
                    for _ in range(r.randint(0, 5)):
                        sid = str(r.randint(1, 8))
                        key = (day, st, sid)
                        if key not in made:
                            made[key] = [sid, r.choice("ABC"), r.choice([1, 2, 3, "n/a"]), r.choice([9.99, 5.0, 12.5, "?"])]
                        rows.append(made[key])
                    files[f"year=2026/month=03/day={day}/store={st}/part-{p}.csv"] = csv(rows)
        if r.random() < 0.5:
            files["_tmp/x.csv"] = csv([["1", "A", 5, 5]])
        t.append(folder(files))
    return [{"input_dir": x} for x in t]
