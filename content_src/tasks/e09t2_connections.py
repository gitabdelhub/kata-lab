from kit import df, rng

ID = "e09t2"
NAME = "Valid Flight Connections"
LANG = "pyspark"
PARAMS = ["spark", "flights_df"]
MINUTES = 20
TAGS = ["auto-jointure", "condition sur le temps", "alias", "exclure les annulés"]
DESC = """
<p>A travel website proposes itineraries with one connection. <code>flights_df</code> has the columns <code>flight_id</code> (string), <code>origin</code>, <code>destination</code> (strings, airport codes), <code>departs_at</code>, <code>arrives_at</code> (timestamps) and <code>status</code> (<code>"scheduled"</code> or <code>"cancelled"</code>).</p>
<p>A <b>connection</b> is a pair of two different scheduled flights <code>(first, second)</code> where:</p>
<ul><li>the second flight leaves from the airport where the first one lands;</li><li>the layover, <code>second.departs_at - first.arrives_at</code>, is between <code>45</code> and <code>240</code> minutes, both included;</li><li>the second flight does <b>not</b> go back to the origin of the first flight.</li></ul>
<p>Airport codes must be trimmed and upper-cased. Your task is to return the columns <code>first_flight</code>, <code>second_flight</code>, <code>origin</code>, <code>via</code>, <code>destination</code> and <code>layover_min</code> (long), sorted by <code>origin</code>, <code>destination</code>, <code>layover_min</code>, then <code>first_flight</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F


def solve(spark: SparkSession, flights_df: DataFrame) -> DataFrame:
    # write your code here
    return flights_df
"""
SOLUTION = """
from pyspark.sql import functions as F


def solve(spark, flights_df):
    f = (flights_df.filter(F.col("status") == "scheduled")
         .withColumn("origin", F.upper(F.trim("origin")))
         .withColumn("destination", F.upper(F.trim("destination"))))
    a, b = f.alias("a"), f.alias("b")
    lay = (F.unix_timestamp("b.departs_at") - F.unix_timestamp("a.arrives_at")) / 60
    j = a.join(b, (F.col("a.destination") == F.col("b.origin")) & (F.col("a.flight_id") != F.col("b.flight_id")))
    j = j.withColumn("layover_min", lay.cast("long"))
    j = j.filter(lay.between(45, 240) & (F.col("b.destination") != F.col("a.origin")))
    return (j.select(F.col("a.flight_id").alias("first_flight"), F.col("b.flight_id").alias("second_flight"),
                     F.col("a.origin").alias("origin"), F.col("a.destination").alias("via"),
                     F.col("b.destination").alias("destination"), "layover_min")
            .orderBy("origin", "destination", "layover_min", "first_flight"))
"""
MUTANTS = [
    """
from pyspark.sql import functions as F
def solve(spark, flights_df):
    f = flights_df.withColumn("origin", F.upper(F.trim("origin"))).withColumn("destination", F.upper(F.trim("destination")))
    a, b = f.alias("a"), f.alias("b")
    lay = (F.unix_timestamp("b.departs_at") - F.unix_timestamp("a.arrives_at")) / 60
    j = a.join(b, F.col("a.destination") == F.col("b.origin")).withColumn("layover_min", lay.cast("long")).filter(lay.between(45, 240) & (F.col("b.destination") != F.col("a.origin")))
    return j.select(F.col("a.flight_id").alias("first_flight"), F.col("b.flight_id").alias("second_flight"), F.col("a.origin").alias("origin"), F.col("a.destination").alias("via"), F.col("b.destination").alias("destination"), "layover_min").orderBy("origin", "destination", "layover_min", "first_flight")
""",
    """
from pyspark.sql import functions as F
def solve(spark, flights_df):
    f = flights_df.filter(F.col("status") == "scheduled").withColumn("origin", F.upper(F.trim("origin"))).withColumn("destination", F.upper(F.trim("destination")))
    a, b = f.alias("a"), f.alias("b")
    lay = (F.unix_timestamp("b.departs_at") - F.unix_timestamp("a.arrives_at")) / 60
    j = a.join(b, F.col("a.destination") == F.col("b.origin")).withColumn("layover_min", lay.cast("long")).filter((lay > 45) & (lay < 240) & (F.col("b.destination") != F.col("a.origin")))
    return j.select(F.col("a.flight_id").alias("first_flight"), F.col("b.flight_id").alias("second_flight"), F.col("a.origin").alias("origin"), F.col("a.destination").alias("via"), F.col("b.destination").alias("destination"), "layover_min").orderBy("origin", "destination", "layover_min", "first_flight")
""",
    """
from pyspark.sql import functions as F
def solve(spark, flights_df):
    f = flights_df.filter(F.col("status") == "scheduled").withColumn("origin", F.upper(F.trim("origin"))).withColumn("destination", F.upper(F.trim("destination")))
    a, b = f.alias("a"), f.alias("b")
    lay = (F.unix_timestamp("b.departs_at") - F.unix_timestamp("a.arrives_at")) / 60
    j = a.join(b, F.col("a.destination") == F.col("b.origin")).withColumn("layover_min", lay.cast("long")).filter(lay.between(45, 240))
    return j.select(F.col("a.flight_id").alias("first_flight"), F.col("b.flight_id").alias("second_flight"), F.col("a.origin").alias("origin"), F.col("a.destination").alias("via"), F.col("b.destination").alias("destination"), "layover_min").orderBy("origin", "destination", "layover_min", "first_flight")
""",
]
F_ = "flight_id string, origin string, destination string, departs_at timestamp, arrives_at timestamp, status string"


def tests():
    t = [{"flights_df": df(F_, [["AT1", "LFW", "CMN", "2026-03-01 06:00:00", "2026-03-01 10:00:00", "scheduled"], ["AT2", "CMN", "CDG", "2026-03-01 10:45:00", "2026-03-01 14:00:00", "scheduled"],
                                 ["AT3", "cmn ", "LFW", "2026-03-01 11:00:00", "2026-03-01 15:00:00", "scheduled"], ["AT4", "CMN", "JFK", "2026-03-01 14:00:00", "2026-03-01 22:00:00", "scheduled"],
                                 ["AT5", "CMN", "DSS", "2026-03-01 14:01:00", "2026-03-01 17:00:00", "scheduled"], ["AT6", "CMN", "MAD", "2026-03-01 12:00:00", "2026-03-01 13:30:00", "cancelled"],
                                 ["AT7", "CMN", "LHR", "2026-03-01 10:30:00", "2026-03-01 13:00:00", "scheduled"]])},
         {"flights_df": df(F_, [["X1", "DSS", "ABJ", "2026-03-02 08:00:00", "2026-03-02 10:00:00", "scheduled"], ["X2", "ABJ", "ACC", "2026-03-02 13:59:00", "2026-03-02 15:00:00", "scheduled"],
                                 ["X3", "ABJ", "ACC", "2026-03-02 14:00:00", "2026-03-02 15:00:00", "cancelled"]])}]
    r = rng(902)
    aps = ["LFW", "CMN", "DSS", "ABJ"]
    for _ in range(6):
        rows = []
        for i in range(r.randint(4, 14)):
            o, d = r.sample(aps, 2)
            h, m = r.randint(5, 18), r.choice([0, 15, 30, 45])
            dur = r.choice([60, 90, 120, 180])
            dep = h * 60 + m
            arr = dep + dur
            rows.append([f"F{i}", r.choice([o, o.lower() + " "]), d, f"2026-03-01 {dep // 60:02d}:{dep % 60:02d}:00", f"2026-03-01 {arr // 60:02d}:{arr % 60:02d}:00", r.choice(["scheduled"] * 4 + ["cancelled"])])
        t.append({"flights_df": df(F_, rows)})
    return t
