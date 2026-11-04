from kit import folder, rng

ID = "f11t1"
NAME = "Carrier Scan Manifests"
LANG = "pyspark"
PARAMS = ["spark", "input_dir"]
MINUTES = 22
TAGS = ["consigne longue", "en-têtes variables", "lignes de commentaire", "dernier état"]
DESC = """
<p>Our logistics hub works with several delivery carriers. Every carrier drops its scan manifests in <code>input_dir/&lt;carrier&gt;/</code>, in any sub-folder it likes, as files ending with <code>.csv</code>. A manifest lists parcel scans: each time a parcel is scanned, the carrier writes its id, its weight in kilograms, a status and the scan time (<code>yyyy-MM-dd HH:mm:ss</code>).</p>
<p>The carriers never agreed on a format. The separator is always a semicolon, but each carrier orders the columns as it wants and writes the header in its own case (<code>PARCEL_ID</code>, <code>Status</code>…); the four column names are always <code>parcel_id</code>, <code>weight_kg</code>, <code>status</code> and <code>scanned_at</code> once you ignore case and spaces. Some exports start with one or more comment lines beginning with <code>#</code> before the header, and statuses are written in any case. Lines whose time cannot be read are scanner noise and are ignored.</p>
<p>Parcel ids are only unique within a carrier: <code>P1</code> at one carrier and <code>P1</code> at another carrier are two different parcels. The <b>final status</b> of a parcel is the status of its most recent scan. If two scans of a parcel have the same time, <code>DELIVERED</code> wins over <code>RETURNED</code>, which wins over anything else. The weight of a parcel is the weight written on its final scan.</p>
<p>Your task is to return, for each carrier and each day (the date of the final scan), the columns <code>carrier</code>, <code>day</code> (date), <code>delivered</code> (long, parcels whose final status is <code>DELIVERED</code>), <code>returned</code> (long, final status <code>RETURNED</code>), <code>open</code> (long, any other final status) and <code>delivered_kg</code> (double, total weight of the delivered parcels, rounded to 1 decimal, <code>0.0</code> if none). Sort by <code>carrier</code>, then <code>day</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
import os
from pyspark.sql import SparkSession, DataFrame, functions as F


def solve(spark: SparkSession, input_dir: str) -> DataFrame:
    # write your code here
    return spark.read.option("header", True).option("sep", ";").csv(input_dir)
"""
SOLUTION = """
import os
from functools import reduce
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def solve(spark, input_dir):
    parts = []
    for carrier in sorted(os.listdir(input_dir)):
        for root, _, files in os.walk(os.path.join(input_dir, carrier)):
            for name in files:
                if not name.endswith(".csv"):
                    continue
                d = (spark.read.option("header", True).option("sep", ";").option("comment", "#")
                     .csv(os.path.join(root, name)))
                d = d.toDF(*[c.strip().lower() for c in d.columns])
                parts.append(d.select(F.lit(carrier).alias("carrier"), F.trim("parcel_id").alias("parcel_id"),
                                      F.trim("weight_kg").try_cast("double").alias("kg"),
                                      F.upper(F.trim("status")).alias("status"),
                                      F.try_to_timestamp(F.trim("scanned_at"), F.lit("yyyy-MM-dd HH:mm:ss")).alias("ts")))
    df = reduce(lambda a, b: a.unionByName(b), parts).filter(F.col("ts").isNotNull())
    prio = F.when(F.col("status") == "DELIVERED", 0).when(F.col("status") == "RETURNED", 1).otherwise(2)
    w = Window.partitionBy("carrier", "parcel_id").orderBy(F.col("ts").desc(), prio)
    last = df.withColumn("rn", F.row_number().over(w)).filter("rn = 1")
    return (last.groupBy("carrier", F.to_date("ts").alias("day")).agg(
                F.sum(F.when(F.col("status") == "DELIVERED", 1).otherwise(0)).cast("long").alias("delivered"),
                F.sum(F.when(F.col("status") == "RETURNED", 1).otherwise(0)).cast("long").alias("returned"),
                F.sum(F.when(~F.col("status").isin("DELIVERED", "RETURNED"), 1).otherwise(0)).cast("long").alias("open"),
                F.round(F.coalesce(F.sum(F.when(F.col("status") == "DELIVERED", F.col("kg"))), F.lit(0.0)), 1).alias("delivered_kg"))
            .orderBy("carrier", "day"))
"""
MUTANTS = [
    """
import os
from functools import reduce
from pyspark.sql import functions as F
from pyspark.sql.window import Window
def solve(spark, input_dir):
    parts = []
    for carrier in sorted(os.listdir(input_dir)):
        for root, _, files in os.walk(os.path.join(input_dir, carrier)):
            for name in files:
                if not name.endswith(".csv"): continue
                d = spark.read.option("header", True).option("sep", ";").option("comment", "#").csv(os.path.join(root, name))
                d = d.toDF(*[c.strip().lower() for c in d.columns])
                parts.append(d.select(F.lit(carrier).alias("carrier"), F.trim("parcel_id").alias("parcel_id"), F.trim("weight_kg").try_cast("double").alias("kg"), F.upper(F.trim("status")).alias("status"), F.try_to_timestamp(F.trim("scanned_at"), F.lit("yyyy-MM-dd HH:mm:ss")).alias("ts")))
    df = reduce(lambda a, b: a.unionByName(b), parts).filter(F.col("ts").isNotNull())
    prio = F.when(F.col("status") == "DELIVERED", 0).when(F.col("status") == "RETURNED", 1).otherwise(2)
    w = Window.partitionBy("parcel_id").orderBy(F.col("ts").desc(), prio)
    last = df.withColumn("rn", F.row_number().over(w)).filter("rn = 1")
    return last.groupBy("carrier", F.to_date("ts").alias("day")).agg(F.sum(F.when(F.col("status") == "DELIVERED", 1).otherwise(0)).cast("long").alias("delivered"), F.sum(F.when(F.col("status") == "RETURNED", 1).otherwise(0)).cast("long").alias("returned"), F.sum(F.when(~F.col("status").isin("DELIVERED", "RETURNED"), 1).otherwise(0)).cast("long").alias("open"), F.round(F.coalesce(F.sum(F.when(F.col("status") == "DELIVERED", F.col("kg"))), F.lit(0.0)), 1).alias("delivered_kg")).orderBy("carrier", "day")
""",
    """
import os
from functools import reduce
from pyspark.sql import functions as F
from pyspark.sql.window import Window
def solve(spark, input_dir):
    parts = []
    for carrier in sorted(os.listdir(input_dir)):
        for root, _, files in os.walk(os.path.join(input_dir, carrier)):
            for name in files:
                if not name.endswith(".csv"): continue
                d = spark.read.option("header", True).option("sep", ";").option("comment", "#").csv(os.path.join(root, name))
                d = d.toDF(*[c.strip().lower() for c in d.columns])
                parts.append(d.select(F.lit(carrier).alias("carrier"), F.trim("parcel_id").alias("parcel_id"), F.trim("weight_kg").try_cast("double").alias("kg"), F.upper(F.trim("status")).alias("status"), F.try_to_timestamp(F.trim("scanned_at"), F.lit("yyyy-MM-dd HH:mm:ss")).alias("ts")))
    df = reduce(lambda a, b: a.unionByName(b), parts).filter(F.col("ts").isNotNull())
    w = Window.partitionBy("carrier", "parcel_id").orderBy(F.col("ts").desc())
    last = df.withColumn("rn", F.row_number().over(w)).filter("rn = 1")
    return last.groupBy("carrier", F.to_date("ts").alias("day")).agg(F.sum(F.when(F.col("status") == "DELIVERED", 1).otherwise(0)).cast("long").alias("delivered"), F.sum(F.when(F.col("status") == "RETURNED", 1).otherwise(0)).cast("long").alias("returned"), F.sum(F.when(~F.col("status").isin("DELIVERED", "RETURNED"), 1).otherwise(0)).cast("long").alias("open"), F.round(F.coalesce(F.sum(F.when(F.col("status") == "DELIVERED", F.col("kg"))), F.lit(0.0)), 1).alias("delivered_kg")).orderBy("carrier", "day")
""",
]
COLS = ["parcel_id", "weight_kg", "status", "scanned_at"]


def csv(rows, order, case="lower", comments=0):
    head = ";".join({"lower": c, "upper": c.upper(), "title": c.title()}[case] for c in (COLS[i] for i in order))
    out = "".join(f"# export {k}\n" for k in range(comments)) + head + "\n"
    for r in rows:
        out += ";".join(str(r[i]) for i in order) + "\n"
    return out


def tests():
    t = [folder({"swiftx/2026/a.csv": csv([["P1", 2.5, "in_transit", "2026-03-01 08:00:00"], ["P1", 2.5, "Delivered", "2026-03-01 15:00:00"],
                                            ["P2", 1.0, "RETURNED", "2026-03-01 15:00:00"], ["P2", 1.0, "DELIVERED", "2026-03-01 15:00:00"],
                                            ["P3", 4.0, "out_for_delivery", "2026-03-02 09:00:00"]], [0, 1, 2, 3], "upper", 2),
                 "swiftx/b.csv": csv([["2026-03-02 18:30:00", "P3", "delivered", 4.1], ["garbage", "P9", "delivered", 9]], [3, 0, 2, 1], "title"),
                 "swiftx/readme.txt": "not a manifest\n",
                 "colis/m.csv": csv([["P1", 7.0, "RETURNED", "2026-03-01 10:00:00"]], [2, 3, 1, 0], "lower", 1)}),
         folder({"z/x.csv": csv([["A", 1, "created", "2026-03-05 10:00:00"]], [0, 1, 2, 3])})]
    r = rng(3111)
    for _ in range(6):
        files = {}
        for c in r.sample(["swiftx", "colis", "dhx"], r.randint(1, 3)):
            for k in range(r.randint(1, 3)):
                rows = []
                for _ in range(r.randint(1, 6)):
                    rows.append([f"P{r.randint(1, 5)}", r.choice([0.5, 1.2, 3.0, 10.25]), r.choice(["created", "IN_TRANSIT", "delivered", "Delivered", "returned"]),
                                 r.choice([f"2026-03-0{r.randint(1, 3)} {r.choice(['08', '12', '18'])}:00:00", "n/a"])])
                order = r.sample(range(4), 4)
                files[f"{c}/{r.choice(['', 'in/'])}f{k}.csv"] = csv(rows, order, r.choice(["lower", "upper", "title"]), r.randint(0, 2))
        t.append(folder(files))
    return [{"input_dir": x} for x in t]
