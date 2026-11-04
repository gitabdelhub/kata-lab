from kit import df, rng

ID = "f15t2"
NAME = "Shopping Sessions"
LANG = "pyspark"
PARAMS = ["spark", "events_df"]
MINUTES = 22
TAGS = ["consigne longue", "sessionisation", "lag et somme cumulée", "jour de début de session"]
DESC = """
<p>The product team wants to know how often a visit to our shop ends with a purchase. The website logs every action in <code>events_df</code>, with the columns <code>user_id</code>, <code>ts</code> (timestamp) and <code>event</code> (<code>view</code>, <code>add_to_cart</code> or <code>purchase</code>). Events without a user (visitors who refused cookies) cannot be grouped and are ignored, and the tracker sometimes sends the same event twice (same user, time and event), which counts once.</p>
<p>We have no notion of visit in the logs, so we build <b>sessions</b>: the events of a user, taken in time order, belong to the same session as long as the gap between two consecutive events is at most 30 minutes; a longer gap starts a new session. A session can last several hours if the user keeps clicking, and it can cross midnight: a session belongs to the day on which it <b>started</b>, even if its purchase happened after midnight. A session is <b>converted</b> if it contains at least one purchase.</p>
<p>Your task is to return one row per day with at least one session, with the columns <code>day</code> (date), <code>sessions</code> (long), <code>converted</code> (long) and <code>conversion_rate</code> (double, converted sessions divided by sessions, rounded to 3 decimals), sorted by <code>day</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F
from pyspark.sql.window import Window


def solve(spark: SparkSession, events_df: DataFrame) -> DataFrame:
    # write your code here
    return events_df
"""
SOLUTION = """
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def solve(spark, events_df):
    e = events_df.filter(F.col("user_id").isNotNull()).dropDuplicates(["user_id", "ts", "event"])
    w = Window.partitionBy("user_id").orderBy("ts")
    gap = F.col("ts").cast("long") - F.lag("ts").over(w).cast("long")
    e = e.withColumn("new", F.when(F.lag("ts").over(w).isNull() | (gap > 30 * 60), 1).otherwise(0))
    e = e.withColumn("sid", F.sum("new").over(w.rowsBetween(Window.unboundedPreceding, Window.currentRow)))
    s = e.groupBy("user_id", "sid").agg(F.to_date(F.min("ts")).alias("day"),
                                         F.max(F.when(F.lower("event") == "purchase", 1).otherwise(0)).alias("conv"))
    return (s.groupBy("day").agg(F.count("*").alias("sessions"), F.sum("conv").cast("long").alias("converted"))
            .withColumn("conversion_rate", F.round(F.col("converted") / F.col("sessions"), 3))
            .orderBy("day"))
"""
MUTANTS = [
    SOLUTION.replace("(gap > 30 * 60)", "(gap >= 30 * 60)"),
    SOLUTION.replace('F.to_date(F.min("ts")).alias("day")', 'F.to_date(F.max("ts")).alias("day")'),
    SOLUTION.replace('w = Window.partitionBy("user_id").orderBy("ts")', 'w = Window.orderBy("ts")'),
]
S = "user_id string, ts timestamp, event string"


def tests():
    t = [{"events_df": df(S, [["u1", "2026-03-04 10:00:00", "view"], ["u1", "2026-03-04 10:30:00", "add_to_cart"], ["u1", "2026-03-04 10:45:00", "purchase"],
                              ["u1", "2026-03-04 11:16:00", "view"], ["u2", "2026-03-04 23:50:00", "view"], ["u2", "2026-03-05 00:10:00", "purchase"],
                              ["u3", "2026-03-04 10:10:00", "view"], ["u3", "2026-03-04 10:10:00", "view"], [None, "2026-03-04 10:20:00", "purchase"],
                              ["u4", "2026-03-05 08:00:00", "view"]])},
         {"events_df": df(S, [["a", "2026-03-01 09:00:00", "view"], ["b", "2026-03-01 09:20:00", "view"], ["a", "2026-03-01 09:40:00", "purchase"]])}]
    r = rng(3152)
    for _ in range(6):
        rows = []
        for u in range(r.randint(1, 4)):
            m = r.randint(0, 200)
            for _ in range(r.randint(1, 6)):
                m += r.choice([5, 20, 30, 31, 90])
                rows.append([f"u{u}", f"2026-03-0{4 + m // 1440} {(m // 60) % 24:02d}:{m % 60:02d}:00", r.choice(["view", "view", "add_to_cart", "purchase"])])
        if rows and r.random() < 0.5:
            rows.append(list(rows[-1]))
        if r.random() < 0.4:
            rows.append([None, "2026-03-04 01:00:00", "purchase"])
        t.append({"events_df": df(S, rows)})
    return t
