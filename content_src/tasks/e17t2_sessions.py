from kit import df, rng

ID = "e17t2"
NAME = "Viewing Sessions"
LANG = "pyspark"
PARAMS = ["spark", "views_df", "gap_minutes"]
MINUTES = 20
TAGS = ["sessionisation", "lag", "somme cumulée d'indicateurs", "durée de session"]
DESC = """
<p><code>views_df</code> has one row per video started: <code>user_id</code> (string), <code>started_at</code> (timestamp) and <code>video_id</code> (string). A <b>session</b> of a user is a group of consecutive views where each view starts less than <code>gap_minutes</code> minutes after the previous view of the same user. A gap of exactly <code>gap_minutes</code> minutes or more starts a new session.</p>
<p>Your task is to return one row per session with the columns <code>user_id</code>, <code>session_no</code> (integer, 1 for the first session of the user, then 2, ...), <code>session_start</code> (timestamp of the first view), <code>views</code> (long), <code>distinct_videos</code> (long) and <code>span_minutes</code> (long, whole minutes between the first and the last view of the session), sorted by <code>user_id</code>, then <code>session_no</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F
from pyspark.sql.window import Window


def solve(spark: SparkSession, views_df: DataFrame, gap_minutes: int) -> DataFrame:
    # write your code here
    return views_df
"""
SOLUTION = """
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def solve(spark, views_df, gap_minutes):
    w = Window.partitionBy("user_id").orderBy("started_at")
    secs = F.col("started_at").cast("long")
    d = (views_df.withColumn("prev", F.lag(secs).over(w))
         .withColumn("new", F.when(F.col("prev").isNull() | (secs - F.col("prev") >= gap_minutes * 60), 1).otherwise(0))
         .withColumn("session_no", F.sum("new").over(w.rowsBetween(Window.unboundedPreceding, Window.currentRow))))
    return (d.groupBy("user_id", "session_no").agg(
                F.min("started_at").alias("session_start"), F.count("*").alias("views"),
                F.countDistinct("video_id").alias("distinct_videos"),
                ((F.max(secs) - F.min(secs)) / 60).cast("long").alias("span_minutes"))
            .select("user_id", F.col("session_no").cast("int"), "session_start", "views", "distinct_videos", "span_minutes")
            .orderBy("user_id", "session_no"))
"""
MUTANTS = [
    """
from pyspark.sql import functions as F
from pyspark.sql.window import Window
def solve(spark, views_df, gap_minutes):
    w = Window.partitionBy("user_id").orderBy("started_at")
    secs = F.col("started_at").cast("long")
    d = views_df.withColumn("prev", F.lag(secs).over(w)).withColumn("new", F.when(F.col("prev").isNull() | (secs - F.col("prev") > gap_minutes * 60), 1).otherwise(0)).withColumn("session_no", F.sum("new").over(w.rowsBetween(Window.unboundedPreceding, Window.currentRow)))
    return d.groupBy("user_id", "session_no").agg(F.min("started_at").alias("session_start"), F.count("*").alias("views"), F.countDistinct("video_id").alias("distinct_videos"), ((F.max(secs) - F.min(secs)) / 60).cast("long").alias("span_minutes")).select("user_id", F.col("session_no").cast("int"), "session_start", "views", "distinct_videos", "span_minutes").orderBy("user_id", "session_no")
""",
    """
from pyspark.sql import functions as F
from pyspark.sql.window import Window
def solve(spark, views_df, gap_minutes):
    w = Window.orderBy("started_at")
    secs = F.col("started_at").cast("long")
    d = views_df.withColumn("prev", F.lag(secs).over(Window.partitionBy("user_id").orderBy("started_at"))).withColumn("new", F.when(F.col("prev").isNull() | (secs - F.col("prev") >= gap_minutes * 60), 1).otherwise(0)).withColumn("session_no", F.sum("new").over(w.rowsBetween(Window.unboundedPreceding, Window.currentRow)))
    return d.groupBy("user_id", "session_no").agg(F.min("started_at").alias("session_start"), F.count("*").alias("views"), F.countDistinct("video_id").alias("distinct_videos"), ((F.max(secs) - F.min(secs)) / 60).cast("long").alias("span_minutes")).select("user_id", F.col("session_no").cast("int"), "session_start", "views", "distinct_videos", "span_minutes").orderBy("user_id", "session_no")
""",
]
S = "user_id string, started_at timestamp, video_id string"


def tests():
    t = [{"views_df": df(S, [["a", "2026-03-01 20:00:00", "v1"], ["a", "2026-03-01 20:10:00", "v2"], ["a", "2026-03-01 20:40:00", "v2"],
                             ["a", "2026-03-01 21:30:00", "v3"], ["b", "2026-03-01 08:00:00", "v1"]]), "gap_minutes": 30},
         {"views_df": df(S, [["z", "2026-03-02 10:00:00", "v1"], ["z", "2026-03-02 10:05:30", "v1"], ["z", "2026-03-02 10:20:00", "v2"]]), "gap_minutes": 5}]
    r = rng(1702)
    for _ in range(6):
        rows = []
        for u in r.sample(["a", "b", "c", "d"], r.randint(1, 4)):
            m = r.randint(0, 60)
            for _ in range(r.randint(1, 7)):
                m += r.choice([1, 5, 10, 15, 20, 45, 90])
                rows.append([u, f"2026-03-0{1 + m // 1440} {(m % 1440) // 60:02d}:{m % 60:02d}:00", f"v{r.randint(1, 4)}"])
        t.append({"views_df": df(S, rows), "gap_minutes": r.choice([10, 15, 20])})
    return t
