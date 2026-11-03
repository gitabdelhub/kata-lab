from kit import df, rng

ID = "e07t2"
NAME = "Consumption from Counters"
LANG = "pyspark"
PARAMS = ["spark", "readings_df"]
MINUTES = 20
TAGS = ["lag", "remise à zéro du compteur", "doublons", "agrégat par jour"]
DESC = """
<p>Smart meters send the value of a <b>cumulative</b> counter (in kWh) several times a day. <code>readings_df</code> has the columns <code>meter_id</code> (string), <code>read_at</code> (timestamp) and <code>counter</code> (double, can be <code>null</code> when the meter could not read it).</p>
<p>The consumption between two consecutive valid readings of the same meter (ordered by <code>read_at</code>) is computed like this:</p>
<ul><li>readings with a <code>null</code> counter are ignored; if a meter sends several readings with the same <code>read_at</code>, only the one with the <b>highest</b> counter is kept;</li><li>normally, the consumption is <code>counter - previous counter</code>;</li><li>if the counter is <b>lower</b> than the previous one, the meter was reset to <code>0</code>: the consumption is the new <code>counter</code> itself;</li><li>the first valid reading of a meter has no consumption.</li></ul>
<p>The consumption is assigned to the <b>day of the later reading</b>. Your task is to return, for every meter and day that has at least one consumption, the columns <code>meter_id</code>, <code>day</code> (date), <code>kwh</code> (double, rounded to 3 decimals) and <code>resets</code> (long, the number of resets detected that day), sorted by <code>meter_id</code>, then <code>day</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F
from pyspark.sql.window import Window


def solve(spark: SparkSession, readings_df: DataFrame) -> DataFrame:
    # write your code here
    return readings_df
"""
SOLUTION = """
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def solve(spark, readings_df):
    r = (readings_df.filter(F.col("counter").isNotNull())
         .groupBy("meter_id", "read_at").agg(F.max("counter").alias("counter")))
    w = Window.partitionBy("meter_id").orderBy("read_at")
    r = r.withColumn("prev", F.lag("counter").over(w)).filter(F.col("prev").isNotNull())
    reset = F.col("counter") < F.col("prev")
    r = r.withColumn("kwh", F.when(reset, F.col("counter")).otherwise(F.col("counter") - F.col("prev"))).withColumn("reset", reset.cast("int"))
    return (r.groupBy("meter_id", F.to_date("read_at").alias("day"))
            .agg(F.round(F.sum("kwh"), 3).alias("kwh"), F.sum("reset").cast("long").alias("resets"))
            .orderBy("meter_id", "day"))
"""
MUTANTS = [
    """
from pyspark.sql import functions as F
from pyspark.sql.window import Window
def solve(spark, readings_df):
    w = Window.partitionBy("meter_id").orderBy("read_at")
    r = readings_df.withColumn("prev", F.lag("counter").over(w)).filter(F.col("prev").isNotNull() & F.col("counter").isNotNull())
    reset = F.col("counter") < F.col("prev")
    r = r.withColumn("kwh", F.when(reset, F.col("counter")).otherwise(F.col("counter") - F.col("prev"))).withColumn("reset", reset.cast("int"))
    return r.groupBy("meter_id", F.to_date("read_at").alias("day")).agg(F.round(F.sum("kwh"), 3).alias("kwh"), F.sum("reset").cast("long").alias("resets")).orderBy("meter_id", "day")
""",
    """
from pyspark.sql import functions as F
from pyspark.sql.window import Window
def solve(spark, readings_df):
    r = readings_df.filter(F.col("counter").isNotNull()).groupBy("meter_id", "read_at").agg(F.max("counter").alias("counter"))
    w = Window.partitionBy("meter_id").orderBy("read_at")
    r = r.withColumn("prev", F.lag("counter").over(w)).filter(F.col("prev").isNotNull())
    reset = F.col("counter") < F.col("prev")
    r = r.withColumn("kwh", F.greatest(F.col("counter") - F.col("prev"), F.lit(0.0))).withColumn("reset", reset.cast("int"))
    return r.groupBy("meter_id", F.to_date("read_at").alias("day")).agg(F.round(F.sum("kwh"), 3).alias("kwh"), F.sum("reset").cast("long").alias("resets")).orderBy("meter_id", "day")
""",
    """
from pyspark.sql import functions as F
from pyspark.sql.window import Window
def solve(spark, readings_df):
    r = readings_df.filter(F.col("counter").isNotNull()).groupBy("meter_id", "read_at").agg(F.max("counter").alias("counter")).withColumn("day", F.to_date("read_at"))
    w = Window.partitionBy("meter_id", "day").orderBy("read_at")
    r = r.withColumn("prev", F.lag("counter").over(w)).filter(F.col("prev").isNotNull())
    reset = F.col("counter") < F.col("prev")
    r = r.withColumn("kwh", F.when(reset, F.col("counter")).otherwise(F.col("counter") - F.col("prev"))).withColumn("reset", reset.cast("int"))
    return r.groupBy("meter_id", "day").agg(F.round(F.sum("kwh"), 3).alias("kwh"), F.sum("reset").cast("long").alias("resets")).orderBy("meter_id", "day")
""",
]
R = "meter_id string, read_at timestamp, counter double"


def tests():
    t = [{"readings_df": df(R, [["m1", "2026-03-01 00:00:00", 100.0], ["m1", "2026-03-01 12:00:00", 104.5], ["m1", "2026-03-01 18:00:00", None],
                                ["m1", "2026-03-02 06:00:00", 2.0], ["m1", "2026-03-02 12:00:00", 3.25], ["m2", "2026-03-01 23:00:00", 50.0],
                                ["m2", "2026-03-02 01:00:00", 51.0], ["m2", "2026-03-02 01:00:00", 50.5]])},
         {"readings_df": df(R, [["z", "2026-01-01 00:00:00", 10.0], ["z", "2026-01-01 00:00:00", None], ["y", "2026-01-01 00:00:00", 5.0], ["z", "2026-01-02 00:00:00", 4.0]])}]
    r = rng(702)
    for _ in range(6):
        rows = []
        for m in range(1, r.randint(2, 4)):
            c = round(r.uniform(0, 500), 3)
            for h in sorted(r.sample(range(0, 72), r.randint(2, 9))):
                c = round(r.uniform(0, 5), 3) if r.random() < 0.15 else round(c + r.uniform(0, 8), 3)
                rows.append([f"m{m}", f"2026-03-0{1 + h // 24} {h % 24:02d}:00:00", c if r.random() < 0.9 else None])
                if r.random() < 0.1:
                    rows.append([f"m{m}", f"2026-03-0{1 + h // 24} {h % 24:02d}:00:00", round(c - 0.5, 3)])
        t.append({"readings_df": df(R, rows)})
    return t
