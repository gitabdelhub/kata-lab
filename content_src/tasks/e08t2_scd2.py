from kit import df, rng

ID = "e08t2"
NAME = "Price History Versions"
LANG = "pyspark"
PARAMS = ["spark", "snapshots_df"]
MINUTES = 22
TAGS = ["SCD type 2", "gaps and islands", "lag + somme cumulée", "lead pour valid_to"]
DESC = """
<p>Every day, the catalog team stores a snapshot of all product prices. <code>snapshots_df</code> has the columns <code>snapshot_date</code> (date), <code>product_id</code> (string) and <code>price</code> (double). A product has at most one row per snapshot date, and a product can be missing from some snapshots.</p>
<p>The data warehouse needs a <b>history table</b> (slowly changing dimension of type 2): one row per <b>version</b> of the price of each product. A new version starts on every snapshot where the price of the product is different from its price in its <b>previous</b> snapshot (the previous date where the product appears). Days where the product is missing do not break a version.</p>
<p>Your task is to return the columns <code>product_id</code>, <code>price</code>, <code>valid_from</code> (date, the first snapshot of the version), <code>valid_to</code> (date, the day <b>before</b> the first snapshot of the next version, or <code>null</code> for the current version) and <code>is_current</code> (boolean), sorted by <code>product_id</code>, then <code>valid_from</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
<p><code>P1</code> costs <code>10</code>, then <code>12</code> from 3 March, then <code>10</code> again from 5 March: that is a third version, not the first one again.</p>
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F
from pyspark.sql.window import Window


def solve(spark: SparkSession, snapshots_df: DataFrame) -> DataFrame:
    # write your code here
    return snapshots_df
"""
SOLUTION = """
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def solve(spark, snapshots_df):
    w = Window.partitionBy("product_id").orderBy("snapshot_date")
    s = snapshots_df.withColumn("prev", F.lag("price").over(w))
    s = s.withColumn("new", F.when(F.col("prev").isNull() | (F.col("prev") != F.col("price")), 1).otherwise(0))
    s = s.withColumn("version", F.sum("new").over(w.rowsBetween(Window.unboundedPreceding, Window.currentRow)))
    v = s.groupBy("product_id", "version").agg(F.first("price").alias("price"), F.min("snapshot_date").alias("valid_from"))
    w2 = Window.partitionBy("product_id").orderBy("valid_from")
    v = v.withColumn("next", F.lead("valid_from").over(w2))
    return (v.select("product_id", "price", "valid_from", F.date_sub("next", 1).alias("valid_to"), F.col("next").isNull().alias("is_current"))
            .orderBy("product_id", "valid_from"))
"""
MUTANTS = [
    """
from pyspark.sql import functions as F
from pyspark.sql.window import Window
def solve(spark, snapshots_df):
    v = snapshots_df.groupBy("product_id", "price").agg(F.min("snapshot_date").alias("valid_from"))
    w2 = Window.partitionBy("product_id").orderBy("valid_from")
    v = v.withColumn("next", F.lead("valid_from").over(w2))
    return v.select("product_id", "price", "valid_from", F.date_sub("next", 1).alias("valid_to"), F.col("next").isNull().alias("is_current")).orderBy("product_id", "valid_from")
""",
    """
from pyspark.sql import functions as F
from pyspark.sql.window import Window
def solve(spark, snapshots_df):
    w = Window.partitionBy("product_id").orderBy("snapshot_date")
    s = snapshots_df.withColumn("prev", F.lag("price").over(w))
    s = s.withColumn("new", F.when(F.col("prev").isNull() | (F.col("prev") != F.col("price")), 1).otherwise(0))
    s = s.withColumn("version", F.sum("new").over(w.rowsBetween(Window.unboundedPreceding, Window.currentRow)))
    v = s.groupBy("product_id", "version").agg(F.first("price").alias("price"), F.min("snapshot_date").alias("valid_from"), F.max("snapshot_date").alias("last"))
    w2 = Window.partitionBy("product_id").orderBy("valid_from")
    v = v.withColumn("next", F.lead("valid_from").over(w2))
    return v.select("product_id", "price", "valid_from", F.when(F.col("next").isNotNull(), F.col("last")).alias("valid_to"), F.col("next").isNull().alias("is_current")).orderBy("product_id", "valid_from")
""",
]
S = "snapshot_date date, product_id string, price double"


def tests():
    t = [{"snapshots_df": df(S, [["2026-03-01", "P1", 10.0], ["2026-03-02", "P1", 10.0], ["2026-03-03", "P1", 12.0], ["2026-03-05", "P1", 10.0], ["2026-03-06", "P1", 10.0],
                                 ["2026-03-01", "P2", 5.0], ["2026-03-04", "P2", 5.0], ["2026-03-06", "P2", 5.5]])},
         {"snapshots_df": df(S, [["2026-01-10", "Z", 1.0]])}]
    r = rng(802)
    import datetime as dt
    for _ in range(6):
        rows = []
        for p in range(1, r.randint(2, 5)):
            price = r.choice([5.0, 10.0, 12.5])
            for d in sorted(r.sample(range(1, 20), r.randint(1, 9))):
                if r.random() < 0.35:
                    price = r.choice([5.0, 10.0, 12.5])
                rows.append([(dt.date(2026, 3, 1) + dt.timedelta(days=d)).isoformat(), f"P{p}", price])
        r.shuffle(rows)
        t.append({"snapshots_df": df(S, rows)})
    return t
