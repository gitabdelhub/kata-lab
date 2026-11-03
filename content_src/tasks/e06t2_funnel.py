from kit import df, rng

ID = "e06t2"
NAME = "Daily Checkout Funnel"
LANG = "pyspark"
PARAMS = ["spark", "events_df"]
MINUTES = 20
TAGS = ["entonnoir", "ordre des étapes", "min par étape", "comptage distinct"]
DESC = """
<p>The product team follows a checkout funnel with three steps: <code>view</code>, then <code>cart</code>, then <code>purchase</code>. <code>events_df</code> has the columns <code>user_id</code> (string), <code>event</code> (string) and <code>event_at</code> (timestamp). Event names must be trimmed and lower-cased; other events are ignored.</p>
<p>The funnel is computed <b>per user and per calendar day</b> of <code>event_at</code>:</p>
<ul><li>a user <b>viewed</b> on a day if they have at least one <code>view</code> that day;</li><li>a user <b>carted</b> if they have a <code>cart</code> event <b>after</b> (or at the same time as) their first <code>view</code> of the day;</li><li>a user <b>purchased</b> if they have a <code>purchase</code> event after (or at the same time as) their first <code>cart</code> that counts for <i>carted</i>.</li></ul>
<p>Events of a step that happen before the previous step do not count. Your task is to return, for every day with at least one viewer, the columns <code>day</code> (date), <code>viewed</code>, <code>carted</code>, <code>purchased</code> (long, numbers of distinct users) and <code>conversion_pct</code> (double, <code>100 * purchased / viewed</code> rounded to 1 decimal), sorted by <code>day</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F


def solve(spark: SparkSession, events_df: DataFrame) -> DataFrame:
    # write your code here
    return events_df
"""
SOLUTION = """
from pyspark.sql import functions as F


def solve(spark, events_df):
    e = (events_df.withColumn("event", F.lower(F.trim("event")))
         .withColumn("day", F.to_date("event_at")))
    k = ["user_id", "day"]
    v = e.filter("event = 'view'").groupBy(*k).agg(F.min("event_at").alias("v"))
    c = (e.filter("event = 'cart'").join(v, k)
         .filter(F.col("event_at") >= F.col("v")).groupBy(*k).agg(F.min("event_at").alias("c")))
    p = (e.filter("event = 'purchase'").join(c, k)
         .filter(F.col("event_at") >= F.col("c")).select(*k).distinct().withColumn("p", F.lit(1)))
    f = v.join(c, k, "left").join(p, k, "left")
    return (f.groupBy("day").agg(
                F.count("*").alias("viewed"),
                F.count("c").alias("carted"),
                F.count("p").alias("purchased"))
            .withColumn("conversion_pct", F.round(100.0 * F.col("purchased") / F.col("viewed"), 1))
            .orderBy("day"))
"""
MUTANTS = [
    """
from pyspark.sql import functions as F
def solve(spark, events_df):
    e = events_df.withColumn("event", F.lower(F.trim("event"))).withColumn("day", F.to_date("event_at"))
    g = e.groupBy("user_id", "day").agg(F.max(F.when(F.col("event") == "view", 1)).alias("v"), F.max(F.when(F.col("event") == "cart", 1)).alias("c"), F.max(F.when(F.col("event") == "purchase", 1)).alias("p")).filter("v = 1")
    return g.groupBy("day").agg(F.count("*").alias("viewed"), F.count("c").alias("carted"), F.count(F.when(F.col("c").isNotNull(), F.col("p"))).alias("purchased")).withColumn("conversion_pct", F.round(100.0 * F.col("purchased") / F.col("viewed"), 1)).orderBy("day")
""",
    """
from pyspark.sql import functions as F
def solve(spark, events_df):
    e = events_df.withColumn("event", F.lower(F.trim("event"))).withColumn("day", F.to_date("event_at"))
    k = ["user_id", "day"]
    v = e.filter("event = 'view'").groupBy(*k).agg(F.min("event_at").alias("v"))
    c = e.filter("event = 'cart'").join(v, k).filter(F.col("event_at") >= F.col("v")).groupBy(*k).agg(F.min("event_at").alias("c"))
    p = e.filter("event = 'purchase'").join(v, k).filter(F.col("event_at") >= F.col("v")).select(*k).distinct().withColumn("p", F.lit(1))
    f = v.join(c, k, "left").join(p, k, "left")
    return f.groupBy("day").agg(F.count("*").alias("viewed"), F.count("c").alias("carted"), F.count("p").alias("purchased")).withColumn("conversion_pct", F.round(100.0 * F.col("purchased") / F.col("viewed"), 1)).orderBy("day")
""",
    """
from pyspark.sql import functions as F
def solve(spark, events_df):
    e = events_df.withColumn("event", F.lower(F.trim("event"))).withColumn("day", F.to_date("event_at"))
    k = ["user_id", "day"]
    v = e.filter("event = 'view'").groupBy(*k).agg(F.min("event_at").alias("v"))
    c = e.filter("event = 'cart'").join(v, k).filter(F.col("event_at") > F.col("v")).groupBy(*k).agg(F.min("event_at").alias("c"))
    p = e.filter("event = 'purchase'").join(c, k).filter(F.col("event_at") > F.col("c")).select(*k).distinct().withColumn("p", F.lit(1))
    f = v.join(c, k, "left").join(p, k, "left")
    return f.groupBy("day").agg(F.count("*").alias("viewed"), F.count("c").alias("carted"), F.count("p").alias("purchased")).withColumn("conversion_pct", F.round(100.0 * F.col("purchased") / F.col("viewed"), 1)).orderBy("day")
""",
]
E = "user_id string, event string, event_at timestamp"


def tests():
    t = [{"events_df": df(E, [["u1", "view", "2026-03-01 10:00:00"], ["u1", "cart", "2026-03-01 10:05:00"], ["u1", "purchase", "2026-03-01 10:06:00"],
                              ["u2", "cart", "2026-03-01 09:00:00"], ["u2", " VIEW", "2026-03-01 09:30:00"], ["u2", "purchase", "2026-03-01 09:40:00"],
                              ["u3", "view", "2026-03-01 12:00:00"], ["u3", "view", "2026-03-01 12:01:00"], ["u4", "purchase", "2026-03-01 08:00:00"],
                              ["u1", "view", "2026-03-02 08:00:00"], ["u1", "cart", "2026-03-02 08:00:00"], ["u1", "purchase", "2026-03-02 08:00:00"]])},
         {"events_df": df(E, [["a", "view", "2026-03-05 23:59:00"], ["a", "cart", "2026-03-06 00:01:00"], ["b", "view", "2026-03-05 10:00:00"], ["b", "cart", "2026-03-05 11:00:00"],
                              ["b", "purchase", "2026-03-05 10:30:00"], ["b", "cart", "2026-03-05 10:10:00"], ["b", "search", "2026-03-05 10:00:00"]])}]
    r = rng(602)
    for _ in range(6):
        rows = [[f"u{r.randint(1, 6)}", r.choice(["view", "view", "cart", "purchase", "Cart ", "search"]), f"2026-03-0{r.randint(1, 3)} {r.randint(8, 12):02d}:{r.choice(['00', '15', '30', '45'])}:00"] for _ in range(r.randint(4, 30))]
        t.append({"events_df": df(E, rows)})
    return t
