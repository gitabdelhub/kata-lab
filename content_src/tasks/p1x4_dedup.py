from kit import df, rng

ID = "p1x4"
NAME = "Deduplicate rides and driver gaps"
LANG = "pyspark"
PARAMS = ["spark", "rides_df"]
MINUTES = 20
TAGS = ["Window", "row_number", "lag", "dédoublonnage"]
SUMMARY_FR = "Une course peut être envoyée plusieurs fois. Garde la copie reçue en premier (received_at le plus petit, puis source alphabétique). Ensuite, pour chaque chauffeur, calcule les minutes depuis sa course précédente (null pour la première). Trie par driver_id puis started_at."
DESC = """
<p>Rides are sent to the data platform by two systems, <code>"app"</code> and <code>"backoffice"</code>, so the same ride can arrive several times. <code>rides_df</code> has the columns:</p>
<ul><li><code>ride_id</code> - the ID of the ride (string);</li><li><code>driver_id</code> - the driver (string);</li><li><code>started_at</code> - when the ride started (timestamp);</li><li><code>source</code> - <code>"app"</code> or <code>"backoffice"</code>;</li><li><code>received_at</code> - when the platform received this copy (timestamp).</li></ul>
<p>Your task is to:</p>
<ol><li>keep one copy of each <code>ride_id</code>: the one with the earliest <code>received_at</code>; if two copies were received at the same time, keep the one whose <code>source</code> comes first alphabetically;</li><li>for each driver, compute <code>gap_minutes</code>: the number of whole minutes between the <code>started_at</code> of the ride and the <code>started_at</code> of the previous ride of the same driver (null for the first ride of a driver).</li></ol>
<p>Return <code>ride_id</code>, <code>driver_id</code>, <code>started_at</code>, <code>source</code> and <code>gap_minutes</code> (integer), sorted by <code>driver_id</code>, then <code>started_at</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F
from pyspark.sql.window import Window


def solve(spark: SparkSession, rides_df: DataFrame) -> DataFrame:
    # write your code here
    return rides_df
"""
SOLUTION = """
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def solve(spark, rides_df):
    w1 = Window.partitionBy("ride_id").orderBy("received_at", "source")
    rides = rides_df.withColumn("rn", F.row_number().over(w1)).filter("rn = 1").drop("rn")
    w2 = Window.partitionBy("driver_id").orderBy("started_at")
    prev = F.lag("started_at").over(w2)
    gap = ((F.unix_timestamp("started_at") - F.unix_timestamp(prev)) / 60).cast("int")
    return (rides.withColumn("gap_minutes", gap)
            .select("ride_id", "driver_id", "started_at", "source", "gap_minutes")
            .orderBy("driver_id", "started_at"))
"""
MUTANTS = [
    """
from pyspark.sql import functions as F
from pyspark.sql.window import Window
def solve(spark, rides_df):
    rides = rides_df.dropDuplicates(["ride_id"])
    w2 = Window.partitionBy("driver_id").orderBy("started_at")
    gap = ((F.unix_timestamp("started_at") - F.unix_timestamp(F.lag("started_at").over(w2))) / 60).cast("int")
    return rides.withColumn("gap_minutes", gap).select("ride_id", "driver_id", "started_at", "source", "gap_minutes").orderBy("driver_id", "started_at")
""",
    """
from pyspark.sql import functions as F
from pyspark.sql.window import Window
def solve(spark, rides_df):
    w1 = Window.partitionBy("ride_id").orderBy("received_at")
    rides = rides_df.withColumn("rn", F.row_number().over(w1)).filter("rn = 1").drop("rn")
    w2 = Window.partitionBy("driver_id").orderBy("started_at")
    gap = ((F.unix_timestamp("started_at") - F.unix_timestamp(F.lag("started_at").over(w2))) / 60).cast("int")
    return rides.withColumn("gap_minutes", gap).select("ride_id", "driver_id", "started_at", "source", "gap_minutes").orderBy("driver_id", "started_at")
""",
]
HINTS = [
    "Étape 1 : row_number() sur Window.partitionBy(\"ride_id\").orderBy(\"received_at\", \"source\"), garde rn = 1. dropDuplicates ne choisit pas quelle copie il garde.",
    "Étape 2 : F.lag(\"started_at\").over(Window.partitionBy(\"driver_id\").orderBy(\"started_at\")). Différence en secondes avec F.unix_timestamp, divise par 60, cast(\"int\").",
]
S = "ride_id STRING, driver_id STRING, started_at TIMESTAMP, source STRING, received_at TIMESTAMP"


def tests():
    t = [df(S, [["R1", "D1", "2026-03-01 08:00:00", "app", "2026-03-01 08:30:00"],
                ["R1", "D1", "2026-03-01 08:00:00", "backoffice", "2026-03-01 08:10:00"],
                ["R2", "D1", "2026-03-01 08:45:30", "app", "2026-03-01 09:00:00"],
                ["R3", "D2", "2026-03-01 09:00:00", "backoffice", "2026-03-01 09:20:00"],
                ["R3", "D2", "2026-03-01 09:00:00", "app", "2026-03-01 09:20:00"]]),
         df(S, [["X", "D9", "2026-03-02 23:50:00", "app", "2026-03-03 00:00:00"], ["Y", "D9", "2026-03-03 00:20:00", "app", "2026-03-03 00:30:00"]])]
    r = rng(7)
    for k in range(5):
        rows = []
        for i in range(6 + 3 * k):
            d = f"D{r.randint(1, 3)}"
            mins = 360 + i * 47 + r.randint(0, 40)
            st = f"2026-03-01 {mins // 60:02d}:{mins % 60:02d}:{r.choice([0, 30]):02d}"
            for c in range(r.choice([1, 1, 2, 3])):
                rec = f"2026-03-04 {r.randint(0, 2):02d}:{r.choice([0, 15]):02d}:00"
                rows.append([f"R{k}{i}", d, st, r.choice(["app", "backoffice"]), rec])
        r.shuffle(rows)
        t.append(df(S, rows))
    return [{"rides_df": x} for x in t]
