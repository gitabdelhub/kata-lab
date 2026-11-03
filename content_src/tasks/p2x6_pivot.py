from kit import df, rng

ID = "p2x6"
NAME = "Weekly Channel Pivot"
LANG = "pyspark"
PARAMS = ["spark", "visits_df"]
MINUTES = 20
TAGS = ["groupBy().pivot()", "liste de valeurs fixée", "fillna", "semaine ISO"]
SUMMARY_FR = "Construire un tableau : une ligne par semaine (le lundi), une colonne par canal (web, app, store, toujours dans cet ordre, même si un canal est absent), avec le nombre de visiteurs distincts, 0 si rien."
HINTS = ["F.date_trunc('week', ts) donne le lundi de la semaine ; F.to_date() pour garder une date.",
         "pivot('channel', ['web', 'app', 'store']) avec la liste FIXE : sinon une colonne manque quand un canal est absent.",
         "Normalise le canal avant (trim + lower) et fillna(0) après le pivot."]
DESC = """
<p>The marketing team wants a weekly report of visitors per channel. <code>visits_df</code> has the columns <code>visitor_id</code> (string), <code>channel</code> (string) and <code>visited_at</code> (timestamp).</p>
<p>Channel names are written by different systems: they must be trimmed and lower-cased. Only the channels <code>web</code>, <code>app</code> and <code>store</code> are reported; other channels are ignored.</p>
<p>A week starts on <b>Monday</b>. Your task is to return one row per week that has at least one reported visit, with the columns <code>week_start</code> (date, the Monday), <code>web</code>, <code>app</code>, <code>store</code> (long, the number of <b>distinct</b> visitors of the channel during the week, <code>0</code> if none) and <code>total</code> (long, the number of distinct visitors of the week on any reported channel). The three channel columns are always present, in this order. Sort by <code>week_start</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F


def solve(spark: SparkSession, visits_df: DataFrame) -> DataFrame:
    # write your code here
    return visits_df
"""
SOLUTION = """
from pyspark.sql import functions as F

CHANNELS = ["web", "app", "store"]


def solve(spark, visits_df):
    v = (visits_df.withColumn("channel", F.lower(F.trim("channel")))
         .filter(F.col("channel").isin(CHANNELS))
         .withColumn("week_start", F.to_date(F.date_trunc("week", "visited_at"))))
    piv = v.groupBy("week_start").pivot("channel", CHANNELS).agg(F.countDistinct("visitor_id")).fillna(0, CHANNELS)
    tot = v.groupBy("week_start").agg(F.countDistinct("visitor_id").alias("total"))
    return (piv.join(tot, "week_start")
            .select("week_start", *[F.col(c).cast("long") for c in CHANNELS], "total")
            .orderBy("week_start"))
"""
MUTANTS = [
    """
from pyspark.sql import functions as F
def solve(spark, visits_df):
    v = visits_df.withColumn("channel", F.lower(F.trim("channel"))).filter(F.col("channel").isin(["web", "app", "store"])).withColumn("week_start", F.to_date(F.date_trunc("week", "visited_at")))
    piv = v.groupBy("week_start").pivot("channel", ["web", "app", "store"]).agg(F.countDistinct("visitor_id")).fillna(0)
    return piv.withColumn("total", F.col("web") + F.col("app") + F.col("store")).select("week_start", *[F.col(c).cast("long") for c in ["web", "app", "store"]], F.col("total").cast("long")).orderBy("week_start")
""",
    """
from pyspark.sql import functions as F
def solve(spark, visits_df):
    v = visits_df.withColumn("channel", F.lower(F.trim("channel"))).filter(F.col("channel").isin(["web", "app", "store"])).withColumn("week_start", F.to_date(F.date_trunc("week", "visited_at")))
    piv = v.groupBy("week_start").pivot("channel", ["web", "app", "store"]).agg(F.count("visitor_id")).fillna(0)
    tot = v.groupBy("week_start").agg(F.count("visitor_id").alias("total"))
    return piv.join(tot, "week_start").select("week_start", *[F.col(c).cast("long") for c in ["web", "app", "store"]], "total").orderBy("week_start")
""",
    """
from pyspark.sql import functions as F
def solve(spark, visits_df):
    v = visits_df.filter(F.col("channel").isin(["web", "app", "store"])).withColumn("week_start", F.to_date(F.date_trunc("week", "visited_at")))
    piv = v.groupBy("week_start").pivot("channel", ["web", "app", "store"]).agg(F.countDistinct("visitor_id")).fillna(0)
    tot = v.groupBy("week_start").agg(F.countDistinct("visitor_id").alias("total"))
    return piv.join(tot, "week_start").select("week_start", *[F.col(c).cast("long") for c in ["web", "app", "store"]], "total").orderBy("week_start")
""",
]
V = "visitor_id string, channel string, visited_at timestamp"


def tests():
    t = [{"visits_df": df(V, [["v1", "web", "2026-03-02 10:00:00"], ["v1", " WEB", "2026-03-04 10:00:00"], ["v2", "app", "2026-03-08 23:59:00"],
                              ["v1", "app", "2026-03-03 08:00:00"], ["v3", "store", "2026-03-09 00:00:00"], ["v4", "email", "2026-03-09 11:00:00"]])},
         {"visits_df": df(V, [["a", "Store ", "2026-01-01 12:00:00"], ["b", "store", "2025-12-29 09:00:00"], ["a", "tv", "2026-01-12 09:00:00"]])}]
    r = rng(306)
    for _ in range(6):
        rows = [[f"v{r.randint(1, 6)}", r.choice(["web", " Web", "APP", "app", "store", "email", "Store "]), f"2026-03-{r.randint(1, 21):02d} {r.randint(0, 23):02d}:00:00"] for _ in range(r.randint(1, 14))]
        t.append({"visits_df": df(V, rows)})
    return t
