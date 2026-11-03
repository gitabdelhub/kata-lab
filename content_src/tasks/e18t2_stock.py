from kit import df, rng

ID = "e18t2"
NAME = "Stock Value with Last Known Cost"
LANG = "pyspark"
PARAMS = ["spark", "moves_df"]
MINUTES = 20
TAGS = ["last ignorenulls", "remplir vers l'avant", "stock cumulé", "dernière ligne par jour"]
DESC = """
<p>A warehouse records every stock movement in <code>moves_df</code>: <code>sku</code> (string), <code>moved_at</code> (timestamp), <code>qty</code> (integer, positive for an arrival, negative for a departure) and <code>unit_cost</code> (double, only filled on some rows, <code>null</code> otherwise).</p>
<p>For each movement, the <b>known cost</b> is the last non null <code>unit_cost</code> of the same sku at or before this movement (in <code>moved_at</code> order). The <b>stock</b> after a movement is the sum of <code>qty</code> of this movement and of all the earlier movements of the sku.</p>
<p>Your task is to return, for each sku and each day with at least one movement, the stock and its value at the end of the day: columns <code>sku</code>, <code>day</code> (date), <code>stock</code> (long) and <code>stock_value</code> (double, <code>stock * known cost</code> of the last movement of the day, rounded to 2 decimals, <code>null</code> when no cost is known yet), sorted by <code>sku</code>, then <code>day</code>. Two movements of a sku never have the same <code>moved_at</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F
from pyspark.sql.window import Window


def solve(spark: SparkSession, moves_df: DataFrame) -> DataFrame:
    # write your code here
    return moves_df
"""
SOLUTION = """
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def solve(spark, moves_df):
    w = Window.partitionBy("sku").orderBy("moved_at").rowsBetween(Window.unboundedPreceding, Window.currentRow)
    d = (moves_df.withColumn("cost", F.last("unit_cost", ignorenulls=True).over(w))
         .withColumn("stock", F.sum("qty").over(w))
         .withColumn("day", F.to_date("moved_at")))
    last = Window.partitionBy("sku", "day").orderBy(F.col("moved_at").desc())
    return (d.withColumn("rn", F.row_number().over(last)).filter("rn = 1")
            .select("sku", "day", F.col("stock").cast("long"), F.round(F.col("stock") * F.col("cost"), 2).alias("stock_value"))
            .orderBy("sku", "day"))
"""
MUTANTS = [
    """
from pyspark.sql import functions as F
from pyspark.sql.window import Window
def solve(spark, moves_df):
    w = Window.partitionBy("sku").orderBy("moved_at").rowsBetween(Window.unboundedPreceding, Window.currentRow)
    d = moves_df.withColumn("cost", F.last("unit_cost").over(w)).withColumn("stock", F.sum("qty").over(w)).withColumn("day", F.to_date("moved_at"))
    last = Window.partitionBy("sku", "day").orderBy(F.col("moved_at").desc())
    return d.withColumn("rn", F.row_number().over(last)).filter("rn = 1").select("sku", "day", F.col("stock").cast("long"), F.round(F.col("stock") * F.col("cost"), 2).alias("stock_value")).orderBy("sku", "day")
""",
    """
from pyspark.sql import functions as F
from pyspark.sql.window import Window
def solve(spark, moves_df):
    w = Window.partitionBy("sku").orderBy("moved_at").rowsBetween(Window.unboundedPreceding, Window.currentRow)
    d = moves_df.withColumn("cost", F.last("unit_cost", ignorenulls=True).over(w)).withColumn("day", F.to_date("moved_at"))
    return d.groupBy("sku", "day").agg(F.sum("qty").cast("long").alias("stock"), F.max_by("cost", "moved_at").alias("cost")).select("sku", "day", "stock", F.round(F.col("stock") * F.col("cost"), 2).alias("stock_value")).orderBy("sku", "day")
""",
]
S = "sku string, moved_at timestamp, qty int, unit_cost double"


def tests():
    t = [{"moves_df": df(S, [["A", "2026-03-01 08:00:00", 10, None], ["A", "2026-03-01 09:00:00", 5, 2.0], ["A", "2026-03-01 17:00:00", -3, None],
                             ["A", "2026-03-03 10:00:00", -4, None], ["A", "2026-03-03 11:00:00", 20, 2.5], ["B", "2026-03-02 12:00:00", 7, None]])},
         {"moves_df": df(S, [["Z", "2026-03-05 23:59:00", 1, 9.99], ["Z", "2026-03-06 00:01:00", 1, None]])}]
    r = rng(1802)
    for _ in range(6):
        rows = []
        for sku in r.sample("ABCD", r.randint(1, 4)):
            m = r.randint(0, 600)
            for _ in range(r.randint(1, 8)):
                m += r.choice([30, 120, 400, 1500])
                rows.append([sku, f"2026-03-{1 + m // 1440:02d} {(m % 1440) // 60:02d}:{m % 60:02d}:00", r.choice([5, 10, -2, -4, 3]), r.choice([None, None, 1.5, 2.0, 3.25])])
        t.append({"moves_df": df(S, rows)})
    return t
