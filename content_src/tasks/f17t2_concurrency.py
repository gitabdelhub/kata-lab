from kit import df, rng

ID = "f17t2"
NAME = "Peak Concurrent Viewers"
LANG = "pyspark"
PARAMS = ["spark", "streams_df", "as_of"]
MINUTES = 22
TAGS = ["consigne longue", "balayage +1/-1", "égalités de temps", "flux encore ouverts"]
DESC = """
<p>For every live channel, the operations team needs the largest number of people who were watching at the same moment, to size the servers. Each viewing is a row of <code>streams_df</code> with the columns <code>stream_id</code>, <code>channel</code>, <code>started_at</code> and <code>ended_at</code> (timestamps). The player reports a viewing again when the connection drops and comes back, so the same <code>stream_id</code> can appear twice with the same values; it is one viewing. <code>ended_at</code> is <code>null</code> for a viewing that is still going on: it lasts until <code>as_of</code> (string <code>yyyy-MM-dd HH:mm:ss</code>), the time the report is made. Viewings that start after <code>as_of</code> are tests of the monitoring and must be ignored.</p>
<p>A viewer is watching from <code>started_at</code> included to <code>ended_at</code> excluded. So a viewer who leaves at 20:00:00 and one who joins at 20:00:00 are never watching at the same time, and a viewing whose end is equal to its start (a click by mistake) is never watching.</p>
<p>Your task is to return, for each channel with at least one viewing, the columns <code>channel</code>, <code>peak</code> (long, largest number of simultaneous viewers) and <code>peak_at</code> (timestamp, the first moment this number was reached), sorted by <code>channel</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F
from pyspark.sql.window import Window


def solve(spark: SparkSession, streams_df: DataFrame, as_of: str) -> DataFrame:
    # write your code here
    return streams_df
"""
SOLUTION = """
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def solve(spark, streams_df, as_of):
    now = F.to_timestamp(F.lit(as_of))
    s = (streams_df.dropDuplicates(["stream_id"]).filter(F.col("started_at") <= now)
         .withColumn("ended_at", F.coalesce("ended_at", now)))
    ev = (s.select("channel", F.col("started_at").alias("t"), F.lit(1).alias("d"))
          .unionByName(s.select("channel", F.col("ended_at").alias("t"), F.lit(-1).alias("d"))))
    ev = ev.groupBy("channel", "t").agg(F.sum("d").alias("d"))
    w = Window.partitionBy("channel").orderBy("t").rowsBetween(Window.unboundedPreceding, Window.currentRow)
    ev = ev.withColumn("live", F.sum("d").over(w))
    best = Window.partitionBy("channel").orderBy(F.col("live").desc(), "t")
    return (ev.withColumn("rn", F.row_number().over(best)).filter("rn = 1")
            .select("channel", F.col("live").cast("long").alias("peak"), F.col("t").alias("peak_at"))
            .orderBy("channel"))
"""
MUTANTS = [
    SOLUTION.replace('    ev = ev.groupBy("channel", "t").agg(F.sum("d").alias("d"))\n    w = Window.partitionBy("channel").orderBy("t")',
                     '    w = Window.partitionBy("channel").orderBy("t", F.col("d").desc())'),
    SOLUTION.replace('s = (streams_df.dropDuplicates(["stream_id"])', 's = (streams_df'),
    SOLUTION.replace('orderBy(F.col("live").desc(), "t")', 'orderBy(F.col("live").desc(), F.col("t").desc())'),
    SOLUTION.replace('.filter(F.col("started_at") <= now)', ''),
]
S = "stream_id string, channel string, started_at timestamp, ended_at timestamp"


def tests():
    t = [{"streams_df": df(S, [["s1", "news", "2026-03-04 19:00:00", "2026-03-04 20:00:00"], ["s2", "news", "2026-03-04 20:00:00", "2026-03-04 21:00:00"],
                               ["s3", "news", "2026-03-04 20:30:00", None], ["s3", "news", "2026-03-04 20:30:00", None],
                               ["s4", "news", "2026-03-04 19:30:00", "2026-03-04 19:30:00"], ["s5", "sport", "2026-03-04 18:00:00", "2026-03-04 22:00:00"],
                               ["s6", "sport", "2026-03-04 18:30:00", "2026-03-04 19:00:00"], ["s7", "sport", "2026-03-04 21:00:00", None],
                               ["s8", "sport", "2026-03-04 22:30:00", None], ["s9", "sport", "2026-03-04 22:40:00", None], ["s10", "sport", "2026-03-04 22:45:00", None]]),
          "as_of": "2026-03-04 22:00:00"},
         {"streams_df": df(S, [["a", "kids", "2026-03-01 10:00:00", "2026-03-01 10:00:00"], ["b", "kids", "2026-03-01 11:00:00", "2026-03-01 11:30:00"], ["c", "kids", "2026-03-01 13:00:00", "2026-03-01 14:00:00"], ["d", "kids", "2026-03-01 13:05:00", "2026-03-01 14:00:00"]]),
          "as_of": "2026-03-01 12:00:00"}]
    r = rng(3172)
    for _ in range(6):
        rows = []
        for i in range(r.randint(2, 9)):
            a = r.randint(0, 8) * 15
            e = None if r.random() < 0.2 else a + r.choice([0, 15, 30, 60])
            ts = lambda m: f"2026-03-04 {18 + m // 60:02d}:{m % 60:02d}:00"
            rows.append([f"s{i}", r.choice(["news", "sport"]), ts(a), None if e is None else ts(e)])
        if r.random() < 0.6:
            rows.append(list(rows[0]))
        t.append({"streams_df": df(S, rows), "as_of": "2026-03-04 20:00:00"})
    return t
