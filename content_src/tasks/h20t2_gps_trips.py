from kit import df, rng, ts

ID = "h20t2"
NAME = "Vehicle Trips from GPS Pings"
LANG = "pyspark"
PARAMS = ["spark", "pings_df"]
MINUTES = 25
TAGS = ["consigne longue", "sessionisation", "Window + lag", "doublons", "trajets d'un seul point écartés"]
DESC = """
<p>Our delivery vans send GPS pings. <code>pings_df</code> has the columns <code>vehicle_id</code>, <code>ts</code> (timestamp) and <code>speed_kmh</code> (double, <code>null</code> when the GPS had no fix). Pings without speed are ignored. The same ping can be sent twice: for a vehicle and a <code>ts</code>, keep one ping with the highest speed.</p>
<p>The pings of a vehicle, sorted by <code>ts</code>, are cut into <b>trips</b>: a ping starts a new trip when it comes more than 10 minutes (600 seconds) after the previous ping; a gap of exactly 600 seconds stays in the same trip. A trip made of a single ping is noise and is discarded. The duration of a trip goes from its first to its last ping.</p>
<p>Your task is to return, for each vehicle with at least one trip, the columns <code>vehicle_id</code>, <code>trips</code> (long), <code>total_minutes</code> (double, total duration of its trips in minutes, rounded to 1 decimal), <code>longest_minutes</code> (double, rounded to 1 decimal) and <code>max_speed</code> (double, highest speed over the pings of its trips), sorted by <code>vehicle_id</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, Window, functions as F


def solve(spark: SparkSession, pings_df: DataFrame) -> DataFrame:
    # write your code here
    return pings_df
"""
SOLUTION = """
from pyspark.sql import Window, functions as F


def solve(spark, pings_df):
    p = (pings_df.where(F.col("speed_kmh").isNotNull())
         .groupBy("vehicle_id", "ts").agg(F.max("speed_kmh").alias("speed")))
    w = Window.partitionBy("vehicle_id").orderBy("ts")
    p = p.withColumn("sec", F.col("ts").cast("long"))
    p = p.withColumn("gap", F.col("sec") - F.lag("sec").over(w))
    p = p.withColumn("new", F.when(F.col("gap").isNull() | (F.col("gap") > 600), 1).otherwise(0))
    p = p.withColumn("trip", F.sum("new").over(w.rowsBetween(Window.unboundedPreceding, 0)))
    trips = (p.groupBy("vehicle_id", "trip")
             .agg(F.count("*").alias("n"), ((F.max("sec") - F.min("sec")) / 60).alias("minutes"), F.max("speed").alias("vmax"))
             .where(F.col("n") > 1))
    return (trips.groupBy("vehicle_id")
            .agg(F.count("*").alias("trips"), F.round(F.sum("minutes"), 1).alias("total_minutes"),
                 F.round(F.max("minutes"), 1).alias("longest_minutes"), F.max("vmax").alias("max_speed"))
            .orderBy("vehicle_id"))
"""
MUTANTS = [
    SOLUTION.replace('(F.col("gap") > 600)', '(F.col("gap") >= 600)'),
    SOLUTION.replace('             .where(F.col("n") > 1))', '             )'),
    SOLUTION.replace('    p = (pings_df.where(F.col("speed_kmh").isNotNull())\n         .groupBy("vehicle_id", "ts").agg(F.max("speed_kmh").alias("speed")))', '    p = pings_df.withColumnRenamed("speed_kmh", "speed")'),
    SOLUTION.replace('    p = (pings_df.where(F.col("speed_kmh").isNotNull())\n', '    p = (pings_df\n'),
]
S = "vehicle_id string, ts timestamp, speed_kmh double"


def tests():
    t = [{"pings_df": df(S, [["v1", ts(0), 30.0], ["v1", ts(5), 50.0], ["v1", ts(15), 45.0], ["v1", ts(15), 61.0], ["v1", ts(26), 20.0],
                             ["v1", ts(30), None], ["v1", ts(36), 25.0], ["v1", ts(80), 90.0], ["v2", ts(0), 10.0], ["v2", ts(100), None], ["v2", ts(200), 10.0]])},
         {"pings_df": df(S, [["a", ts(0), 1.0], ["a", ts(10), None], ["a", ts(20), 2.0], ["b", ts(0), 5.0], ["b", ts(0), 5.0], ["b", ts(1), 7.5]])}]
    r = rng(4202)
    for _ in range(6):
        rows = []
        for v in ["v1", "v2", "v3"][: r.randint(1, 3)]:
            m = 0
            for _ in range(r.randint(2, 15)):
                m += r.choice([0, 1, 5, 10, 11, 30])
                rows.append([v, ts(m), None if r.random() < 0.1 else float(r.choice([0, 12, 35, 50, 88]))])
        t.append({"pings_df": df(S, rows)})
    return t
