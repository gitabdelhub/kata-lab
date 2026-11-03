from kit import folder, rng

ID = "e02t1"
NAME = "Latest Warehouse Snapshots"
LANG = "pyspark"
PARAMS = ["spark", "input_dir"]
MINUTES = 20
TAGS = ["lire un dossier", "os.walk", "unionByName", "colonnes dans le désordre"]
DESC = """
<p>A logistics company runs several warehouses. Every night, each warehouse uploads a stock snapshot as a CSV file. The files are stored in <code>input_dir</code> with this layout:</p>
<pre class="exv">input_dir/
  &lt;warehouse&gt;/
    &lt;YYYYMMDD&gt;.csv</pre>
<p>For example <code>input_dir/casa_north/20260302.csv</code> is the snapshot of warehouse <code>casa_north</code> on 2 March 2026. A warehouse folder can contain several snapshots.</p>
<p>Every file has a header line and the three columns <code>sku</code>, <code>qty</code> and <code>location</code>. <b>Each warehouse exports the columns in its own order</b> (for example <code>qty,sku,location</code>), and header names can contain spaces and capital letters. Values are also messy:</p>
<ul><li><code>sku</code> can have surrounding spaces and lower-case letters; SKUs are compared after trimming and upper-casing;</li><li><code>qty</code> is an integer written as text; an empty, non-numeric or negative quantity counts as <code>0</code>;</li><li>the same SKU can appear on several lines of one file (several locations): its quantity is the sum of these lines.</li></ul>
<p>Your task is to return, for each warehouse, the stock of its <b>latest</b> snapshot only, with the columns <code>warehouse</code>, <code>sku</code>, <code>qty</code> (integer) and <code>snapshot_date</code> (date), sorted by <code>warehouse</code>, then <code>sku</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
<p><code>casa_north</code> has two snapshots: only <code>20260302.csv</code> is used. In <code>rabat</code>, the columns come in another order, <code>a-7</code> appears twice (<code>5 + 2</code>) and <code>"x"</code> counts as <code>0</code>.</p>
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
        for name in sorted(files):
            if not name.endswith(".csv"):
                continue
            d = spark.read.option("header", True).csv(os.path.join(root, name))
            d = d.toDF(*[c.strip().lower() for c in d.columns])
            parts.append(d.select(
                F.lit(os.path.basename(root)).alias("warehouse"),
                F.to_date(F.lit(name[:8]), "yyyyMMdd").alias("snapshot_date"),
                F.upper(F.trim("sku")).alias("sku"),
                F.expr("try_cast(trim(qty) AS INT)").alias("qty")))
    df = reduce(lambda a, b: a.unionByName(b), parts)
    latest = df.groupBy("warehouse").agg(F.max("snapshot_date").alias("snapshot_date"))
    df = df.join(latest, ["warehouse", "snapshot_date"])
    qty = F.when(F.col("qty").isNull() | (F.col("qty") < 0), 0).otherwise(F.col("qty"))
    return (df.groupBy("warehouse", "sku", "snapshot_date")
            .agg(F.sum(qty).cast("int").alias("qty"))
            .select("warehouse", "sku", "qty", "snapshot_date")
            .orderBy("warehouse", "sku"))
"""
MUTANTS = [
    """
from pyspark.sql import functions as F
def solve(spark, input_dir):
    raw = spark.read.option("header", True).option("recursiveFileLookup", "true").csv(input_dir)
    d = raw.toDF(*[c.strip().lower() for c in raw.columns])
    path = F.col("_metadata.file_path")
    d = d.select(F.regexp_extract(path, r"/([^/]+)/(\\d{8})\\.csv$", 1).alias("warehouse"), F.to_date(F.regexp_extract(path, r"/([^/]+)/(\\d{8})\\.csv$", 2), "yyyyMMdd").alias("snapshot_date"),
                 F.upper(F.trim("sku")).alias("sku"), F.expr("try_cast(trim(qty) AS INT)").alias("qty"))
    latest = d.groupBy("warehouse").agg(F.max("snapshot_date").alias("snapshot_date"))
    d = d.join(latest, ["warehouse", "snapshot_date"])
    q = F.when(F.col("qty").isNull() | (F.col("qty") < 0), 0).otherwise(F.col("qty"))
    return d.groupBy("warehouse", "sku", "snapshot_date").agg(F.sum(q).cast("int").alias("qty")).select("warehouse", "sku", "qty", "snapshot_date").orderBy("warehouse", "sku")
""",
    """
import os
from functools import reduce
from pyspark.sql import functions as F
def solve(spark, input_dir):
    parts = []
    for root, _, files in os.walk(input_dir):
        for name in files:
            d = spark.read.option("header", True).csv(os.path.join(root, name))
            d = d.toDF(*[c.strip().lower() for c in d.columns])
            parts.append(d.select(F.lit(os.path.basename(root)).alias("warehouse"), F.to_date(F.lit(name[:8]), "yyyyMMdd").alias("snapshot_date"), F.upper(F.trim("sku")).alias("sku"), F.expr("try_cast(trim(qty) AS INT)").alias("qty")))
    df = reduce(lambda a, b: a.unionByName(b), parts)
    q = F.when(F.col("qty").isNull() | (F.col("qty") < 0), 0).otherwise(F.col("qty"))
    df = df.groupBy("warehouse", "sku").agg(F.sum(q).cast("int").alias("qty"), F.max("snapshot_date").alias("snapshot_date"))
    return df.select("warehouse", "sku", "qty", "snapshot_date").orderBy("warehouse", "sku")
""",
]
HEADS = [["sku", "qty", "location"], ["qty", "sku", "location"], ["location", "sku", "qty"], ["location", "qty", "sku"]]


def csv(head, rows, messy):
    names = [(" " + h.upper() + " ") if messy else h for h in head]
    out = [",".join(names)]
    for row in rows:
        d = dict(zip(["sku", "qty", "location"], row))
        out.append(",".join(d[h] for h in head))
    return "\n".join(out) + "\n"


def tests():
    t = [folder({"casa_north/20260301.csv": csv(HEADS[0], [["A-1", "10", "R1"], ["B-2", "4", "R2"]], False),
                 "casa_north/20260302.csv": csv(HEADS[0], [["A-1", "8", "R1"], ["c-3 ", "", "R3"]], False),
                 "rabat/20260302.csv": csv(HEADS[1], [["a-7", "5", "S1"], [" A-7", "2", "S2"], ["B-2", "x", "S1"]], True)}),
         folder({"fes/20260228.csv": csv(HEADS[2], [["Z-9", "-3", "L1"], ["Y-1", "12", "L1"]], True),
                 "fes/20260227.csv": csv(HEADS[3], [["Z-9", "100", "L1"]], False)})]
    r = rng(40)
    skus = ["A-1", "a-1 ", " B-2", "C-3", "d-4", "E-5"]
    for k in range(6):
        files = {}
        for wh in r.sample(["casa_north", "casa_south", "rabat", "fes", "tanger"], 2 + k % 3):
            head = r.choice(HEADS)
            messy = r.random() < 0.5
            for day in r.sample(["20260301", "20260302", "20260303", "20260304"], r.randint(1, 3)):
                rows = [[r.choice(skus), r.choice([str(r.randint(0, 40)), "", "-1", "n/a", str(r.randint(1, 9))]), f"L{r.randint(1, 3)}"] for _ in range(r.randint(1, 6))]
                files[f"{wh}/{day}.csv"] = csv(head, rows, messy)
        t.append(folder(files))
    return [{"input_dir": x} for x in t]
