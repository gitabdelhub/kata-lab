from kit import df, rng

ID = "e00t1"
NAME = "Late Deliveries per Courier"
LANG = "pyspark"
PARAMS = ["spark", "deliveries_df"]
MINUTES = 15
TAGS = ["groupBy / agg", "when / otherwise", "dates", "null"]
DESC = """
<p>A grocery delivery start-up promises a delivery time for every order. The operations manager wants to know which couriers are often late.</p>
<p>You are given <code>deliveries_df</code> with the following columns:</p>
<ul><li><code>delivery_id</code> - the ID of the delivery (string);</li><li><code>courier_id</code> - the courier in charge (string);</li><li><code>promised_at</code> - the promised delivery time (timestamp);</li><li><code>delivered_at</code> - the real delivery time (timestamp), null if the order was never delivered.</li></ul>
<p>A delivery is <b>late</b> if it was never delivered, or if it was delivered more than <code>10</code> minutes after <code>promised_at</code> (exactly 10 minutes is on time). The <b>delay</b> of a delivered order is the number of whole minutes (rounded toward zero) between <code>promised_at</code> and <code>delivered_at</code>; it is negative when the order arrived early.</p>
<p>Your task is to return one row per courier with at least <code>3</code> deliveries, with:</p>
<ol><li><code>courier_id</code>;</li><li><code>deliveries</code> - the number of deliveries;</li><li><code>late</code> - the number of late deliveries;</li><li><code>late_rate</code> - <code>late / deliveries</code>, rounded to 2 decimals;</li><li><code>worst_delay</code> - the largest delay among delivered orders (integer), or null if the courier delivered nothing.</li></ol>
<p>Sort by <code>late_rate</code> descending, then <code>courier_id</code> ascending.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F
from pyspark.sql.window import Window


def solve(spark: SparkSession, deliveries_df: DataFrame) -> DataFrame:
    # write your code here
    return deliveries_df
"""
SOLUTION = """
from pyspark.sql import functions as F


def solve(spark, deliveries_df):
    delay = ((F.unix_timestamp("delivered_at") - F.unix_timestamp("promised_at")) / 60).cast("int")
    d = (deliveries_df.withColumn("delay", delay)
         .withColumn("is_late", F.col("delivered_at").isNull()
                     | (F.unix_timestamp("delivered_at") - F.unix_timestamp("promised_at") > 600)))
    return (d.groupBy("courier_id")
            .agg(F.count("*").alias("deliveries"),
                 F.sum(F.when(F.col("is_late"), 1).otherwise(0)).alias("late"),
                 F.max("delay").alias("worst_delay"))
            .filter(F.col("deliveries") >= 3)
            .withColumn("late_rate", F.round(F.col("late") / F.col("deliveries"), 2))
            .select("courier_id", "deliveries", "late", "late_rate", "worst_delay")
            .orderBy(F.col("late_rate").desc(), "courier_id"))
"""
MUTANTS = [
    """
from pyspark.sql import functions as F
def solve(spark, deliveries_df):
    delay = ((F.unix_timestamp("delivered_at") - F.unix_timestamp("promised_at")) / 60).cast("int")
    d = deliveries_df.withColumn("delay", delay).withColumn("is_late", F.col("delay") > 10)
    return (d.groupBy("courier_id").agg(F.count("*").alias("deliveries"), F.sum(F.when(F.col("is_late"), 1).otherwise(0)).alias("late"), F.max("delay").alias("worst_delay"))
            .filter(F.col("deliveries") >= 3).withColumn("late_rate", F.round(F.col("late") / F.col("deliveries"), 2))
            .select("courier_id", "deliveries", "late", "late_rate", "worst_delay").orderBy(F.col("late_rate").desc(), "courier_id"))
""",
    """
from pyspark.sql import functions as F
def solve(spark, deliveries_df):
    delay = ((F.unix_timestamp("delivered_at") - F.unix_timestamp("promised_at")) / 60).cast("int")
    d = deliveries_df.withColumn("delay", delay).withColumn("is_late", F.col("delivered_at").isNull() | (F.unix_timestamp("delivered_at") - F.unix_timestamp("promised_at") >= 600))
    return (d.groupBy("courier_id").agg(F.count("*").alias("deliveries"), F.sum(F.when(F.col("is_late"), 1).otherwise(0)).alias("late"), F.max("delay").alias("worst_delay"))
            .filter(F.col("deliveries") >= 3).withColumn("late_rate", F.round(F.col("late") / F.col("deliveries"), 2))
            .select("courier_id", "deliveries", "late", "late_rate", "worst_delay").orderBy(F.col("late_rate").desc(), "courier_id"))
""",
]
S = "delivery_id STRING, courier_id STRING, promised_at TIMESTAMP, delivered_at TIMESTAMP"


def tests():
    t = [df(S, [["D1", "C1", "2026-03-01 12:00:00", "2026-03-01 12:05:00"], ["D2", "C1", "2026-03-01 13:00:00", "2026-03-01 13:25:00"],
                ["D3", "C1", "2026-03-01 14:00:00", None], ["D4", "C2", "2026-03-01 12:00:00", "2026-03-01 11:50:00"],
                ["D5", "C2", "2026-03-01 12:30:00", "2026-03-01 12:40:00"], ["D6", "C2", "2026-03-01 18:00:00", "2026-03-01 18:10:30"],
                ["D7", "C3", "2026-03-01 18:00:00", "2026-03-01 19:00:00"]]),
         df(S, [["A", "Z", "2026-03-02 10:00:00", None], ["B", "Z", "2026-03-02 11:00:00", None], ["C", "Z", "2026-03-02 12:00:00", None]])]
    r = rng(20)
    for k in range(6):
        rows = []
        for i in range(12 + 6 * k):
            h, m = r.randint(9, 21), r.randint(0, 59)
            prom = f"2026-03-0{1 + i % 5} {h:02d}:{m:02d}:00"
            dl = r.choice([None, -15, -1, 0, 5, 10, 11, 25, 60]) if r.random() < 0.95 else None
            if dl is None:
                dv = None
            else:
                tot = h * 60 + m + dl
                dv = f"2026-03-0{1 + i % 5} {tot // 60:02d}:{tot % 60:02d}:{r.choice(['00', '30']) if dl >= 0 else '00'}"
            rows.append([f"D{k}{i}", f"C{r.randint(1, 5)}", prom, dv])
        t.append(df(S, rows))
    return [{"deliveries_df": x} for x in t]
