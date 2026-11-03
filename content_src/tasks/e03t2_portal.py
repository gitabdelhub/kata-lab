from kit import df, rng

ID = "e03t2"
NAME = "Patient Portal Sessions"
LANG = "pyspark"
PARAMS = ["spark", "events_df", "gap_minutes"]
MINUTES = 20
TAGS = ["sessions", "lag", "somme cumulée", "Window", "groupBy / agg"]
DESC = """
<p>Patients use an online portal to book appointments and read their results. The product team wants to understand how patients use it, session by session.</p>
<p>You are given <code>events_df</code> with the columns <code>patient_id</code> (string), <code>ts</code> (timestamp) and <code>page</code> (string), and an integer <code>gap_minutes</code>. Rows are not sorted, and a patient can have several events at the same timestamp.</p>
<p>For each patient, events are grouped into <b>sessions</b>: in time order, an event starts a new session when it comes <b>strictly more</b> than <code>gap_minutes</code> minutes after the previous event of the same patient. The first event of a patient always starts a session.</p>
<p>The <b>duration</b> of a session is the time between its first and its last event, in minutes (a session with one event lasts <code>0</code> minutes). A session is <b>converted</b> if one of its events has the page <code>"booking_confirmed"</code>.</p>
<p>Your task is to return one row per patient with:</p>
<ol><li><code>patient_id</code>;</li><li><code>sessions</code> - the number of sessions;</li><li><code>avg_minutes</code> - the average duration of the sessions, rounded to 1 decimal;</li><li><code>max_minutes</code> - the longest duration, rounded to 1 decimal;</li><li><code>converted</code> - the number of converted sessions.</li></ol>
<p>Sort by <code>patient_id</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
<p>For <code>p1</code>, the event at <code>10:45</code> comes 35 minutes after <code>10:10</code>, so it starts a second session.</p>
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F
from pyspark.sql.window import Window


def solve(spark: SparkSession, events_df: DataFrame, gap_minutes: int) -> DataFrame:
    # write your code here
    return events_df
"""
SOLUTION = """
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def solve(spark, events_df, gap_minutes):
    t = F.unix_timestamp("ts")
    w = Window.partitionBy("patient_id").orderBy("ts")
    e = events_df.withColumn("prev", F.lag(t).over(w))
    e = e.withColumn("new", F.when(F.col("prev").isNull() | (t - F.col("prev") > gap_minutes * 60), 1).otherwise(0))
    e = e.withColumn("session", F.sum("new").over(w.rowsBetween(Window.unboundedPreceding, 0)))
    s = (e.groupBy("patient_id", "session")
         .agg(((F.max(t) - F.min(t)) / 60).alias("minutes"),
              F.max(F.when(F.col("page") == "booking_confirmed", 1).otherwise(0)).alias("conv")))
    return (s.groupBy("patient_id")
            .agg(F.count("*").alias("sessions"),
                 F.round(F.avg("minutes"), 1).alias("avg_minutes"),
                 F.round(F.max("minutes"), 1).alias("max_minutes"),
                 F.sum("conv").alias("converted"))
            .orderBy("patient_id"))
"""
MUTANTS = [
    """
from pyspark.sql import functions as F
from pyspark.sql.window import Window
def solve(spark, events_df, gap_minutes):
    t = F.unix_timestamp("ts"); w = Window.partitionBy("patient_id").orderBy("ts")
    e = events_df.withColumn("prev", F.lag(t).over(w))
    e = e.withColumn("new", F.when(F.col("prev").isNull() | (t - F.col("prev") >= gap_minutes * 60), 1).otherwise(0))
    e = e.withColumn("session", F.sum("new").over(w.rowsBetween(Window.unboundedPreceding, 0)))
    s = e.groupBy("patient_id", "session").agg(((F.max(t) - F.min(t)) / 60).alias("minutes"), F.max(F.when(F.col("page") == "booking_confirmed", 1).otherwise(0)).alias("conv"))
    return s.groupBy("patient_id").agg(F.count("*").alias("sessions"), F.round(F.avg("minutes"), 1).alias("avg_minutes"), F.round(F.max("minutes"), 1).alias("max_minutes"), F.sum("conv").alias("converted")).orderBy("patient_id")
""",
    """
from pyspark.sql import functions as F
from pyspark.sql.window import Window
def solve(spark, events_df, gap_minutes):
    t = F.unix_timestamp("ts"); w = Window.partitionBy("patient_id").orderBy("ts")
    e = events_df.withColumn("prev", F.lag(t).over(w))
    e = e.withColumn("new", F.when(F.col("prev").isNull() | (t - F.col("prev") > gap_minutes * 60), 1).otherwise(0))
    e = e.withColumn("session", F.sum("new").over(w.rowsBetween(Window.unboundedPreceding, 0)))
    s = e.groupBy("patient_id", "session").agg(((F.max(t) - F.min(t)) / 60).alias("minutes"), F.sum(F.when(F.col("page") == "booking_confirmed", 1).otherwise(0)).alias("conv"))
    return s.groupBy("patient_id").agg(F.count("*").alias("sessions"), F.round(F.avg("minutes"), 1).alias("avg_minutes"), F.round(F.max("minutes"), 1).alias("max_minutes"), F.sum("conv").alias("converted")).orderBy("patient_id")
""",
]
S = "patient_id STRING, ts TIMESTAMP, page STRING"
PAGES = ["home", "results", "search", "booking_form", "booking_confirmed"]


def tests():
    t = [{"events_df": df(S, [["p1", "2026-03-01 10:00:00", "home"], ["p1", "2026-03-01 10:10:00", "booking_confirmed"], ["p1", "2026-03-01 10:45:00", "results"],
                              ["p2", "2026-03-01 09:00:00", "home"], ["p1", "2026-03-01 10:55:30", "home"], ["p2", "2026-03-01 09:30:00", "search"]]), "gap_minutes": 30},
         {"events_df": df(S, [["z", "2026-03-02 08:00:00", "booking_confirmed"], ["z", "2026-03-02 08:00:00", "booking_confirmed"], ["z", "2026-03-02 08:05:00", "home"]]), "gap_minutes": 5}]
    r = rng(51)
    for k in range(6):
        rows = []
        for p in ["p1", "p2", "p3", "p4"][: 1 + k % 4]:
            mins = r.randint(0, 120)
            for _ in range(r.randint(1, 9)):
                mins += r.choice([0, 1, 5, 12, 29, 30, 31, 90])
                rows.append([p, f"2026-03-0{1 + mins // 1440} {(mins % 1440) // 60:02d}:{mins % 60:02d}:{r.choice(['00', '20'])}", r.choice(PAGES)])
        r.shuffle(rows)
        t.append({"events_df": df(S, rows), "gap_minutes": r.choice([30, 15])})
    return t
