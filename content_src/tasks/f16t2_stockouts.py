from kit import df, rng

ID = "f16t2"
NAME = "Stock-out Days"
LANG = "pyspark"
PARAMS = ["spark", "snapshots_df", "start", "end"]
MINUTES = 22
TAGS = ["consigne longue", "valeur reportée (forward fill)", "grille de jours", "plus longue série"]
DESC = """
<p>The supply team wants to know which products were missing from the shelves, and for how long. Store systems send stock counts in <code>snapshots_df</code>, with the columns <code>store</code>, <code>sku</code>, <code>taken_at</code> (timestamp) and <code>on_hand</code> (integer). A count is only sent when the stock changes, so on a day without a count the stock is the one of the most recent count before it; when several counts are taken on the same day, the stock of that day is the last one.</p>
<p>A day is a <b>stock-out day</b> for a product in a store when its stock of that day is 0 (or less, because of counting errors). Before the first count of a product in a store, nothing is known and no day can be a stock-out day.</p>
<p>The analysis covers the days from <code>start</code> to <code>end</code> included (strings <code>yyyy-MM-dd</code>); counts taken before <code>start</code> still tell the stock at the beginning of the period, and counts after <code>end</code> are ignored.</p>
<p>Your task is to return, for each store and product with at least one stock-out day in the period, the columns <code>store</code>, <code>sku</code>, <code>stockout_days</code> (long) and <code>longest_stockout</code> (long, largest number of consecutive stock-out days), sorted by <code>stockout_days</code> descending, then <code>store</code>, then <code>sku</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F
from pyspark.sql.window import Window


def solve(spark: SparkSession, snapshots_df: DataFrame, start: str, end: str) -> DataFrame:
    # write your code here
    return snapshots_df
"""
SOLUTION = """
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def solve(spark, snapshots_df, start, end):
    s, e = F.to_date(F.lit(start)), F.to_date(F.lit(end))
    d = snapshots_df.withColumn("day", F.to_date("taken_at")).filter(F.col("day") <= e)
    last = Window.partitionBy("store", "sku", "day").orderBy(F.col("taken_at").desc())
    d = d.withColumn("rn", F.row_number().over(last)).filter("rn = 1").select("store", "sku", "day", "on_hand")
    grid = (d.groupBy("store", "sku").agg(F.min("day").alias("first"))
            .withColumn("day", F.explode(F.sequence("first", e))).select("store", "sku", "day"))
    w = Window.partitionBy("store", "sku").orderBy("day").rowsBetween(Window.unboundedPreceding, Window.currentRow)
    g = (grid.join(d, ["store", "sku", "day"], "left")
         .withColumn("stock", F.last("on_hand", ignorenulls=True).over(w))
         .filter((F.col("day") >= s) & (F.col("stock") <= 0)))
    isl = Window.partitionBy("store", "sku").orderBy("day")
    g = g.withColumn("grp", F.date_sub("day", F.row_number().over(isl)))
    runs = g.groupBy("store", "sku", "grp").agg(F.count("*").alias("len"))
    return (runs.groupBy("store", "sku").agg(F.sum("len").alias("stockout_days"), F.max("len").alias("longest_stockout"))
            .orderBy(F.col("stockout_days").desc(), "store", "sku"))
"""
MUTANTS = [
    SOLUTION.replace('.withColumn("stock", F.last("on_hand", ignorenulls=True).over(w))', '.withColumn("stock", F.col("on_hand"))'),
    SOLUTION.replace('orderBy(F.col("taken_at").desc())', 'orderBy(F.col("taken_at"))'),
    SOLUTION.replace('g = g.withColumn("grp", F.date_sub("day", F.row_number().over(isl)))', 'g = g.withColumn("grp", F.lit(0))'),
    SOLUTION.replace('(F.col("stock") <= 0)', '(F.col("stock") == 0)'),
]
S = "store string, sku string, taken_at timestamp, on_hand int"


def tests():
    t = [{"snapshots_df": df(S, [["S1", "milk", "2026-02-27 08:00:00", 0], ["S1", "milk", "2026-03-03 09:00:00", 12], ["S1", "milk", "2026-03-05 10:00:00", 0],
                                 ["S1", "milk", "2026-03-05 18:00:00", 4], ["S1", "milk", "2026-03-07 08:00:00", -1], ["S1", "milk", "2026-03-20 08:00:00", 0],
                                 ["S1", "tea", "2026-03-06 08:00:00", 0], ["S1", "tea", "2026-03-06 07:00:00", 9], ["S2", "milk", "2026-03-02 08:00:00", 5]]),
          "start": "2026-03-01", "end": "2026-03-10"},
         {"snapshots_df": df(S, [["A", "x", "2026-01-01 10:00:00", 1], ["A", "x", "2026-01-02 10:00:00", 0], ["A", "x", "2026-01-02 11:00:00", 3]]),
          "start": "2026-01-01", "end": "2026-01-05"}]
    r = rng(3162)
    for _ in range(6):
        rows = []
        for st in r.sample(["S1", "S2"], r.randint(1, 2)):
            for sku in r.sample(["milk", "tea", "rice"], r.randint(1, 3)):
                for _ in range(r.randint(1, 5)):
                    rows.append([st, sku, f"2026-03-{r.randint(1, 14):02d} {r.randint(6, 20):02d}:00:00", r.choice([0, 0, 3, 10, -2])])
        t.append({"snapshots_df": df(S, rows), "start": "2026-03-04", "end": "2026-03-12"})
    return t
