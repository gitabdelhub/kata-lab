from kit import df, rng, day

ID = "h22t2"
NAME = "Daily Signups by Channel"
LANG = "pyspark"
PARAMS = ["spark", "events_df"]
MINUTES = 25
TAGS = ["consigne longue", "pivot", "calendrier complet", "jours manquants à zéro", "noms à nettoyer"]
DESC = """
<p>The growth team wants a daily table of signups per channel. <code>events_df</code> has the columns <code>day</code> (date), <code>channel</code> (string, messy) and <code>signups</code> (long, can be <code>null</code>, which counts as 0). The same day and channel can appear on several rows: add them up.</p>
<p>Channels are cleaned by trimming spaces and putting them in lower case, then grouped into four columns: <code>email</code> for <code>email</code>, <code>e-mail</code> and <code>newsletter</code>; <code>paid</code> for <code>paid</code>, <code>cpc</code> and <code>ads</code>; <code>organic</code> for <code>organic</code> and <code>seo</code>; <code>other</code> for everything else, including a <code>null</code> channel.</p>
<p>The table must have <b>one row for every day</b> from the first to the last day found in <code>events_df</code>, even days without any event, and the four columns must always exist, with 0 when there is nothing.</p>
<p>Your task is to return the columns <code>day</code> (date), <code>email</code>, <code>paid</code>, <code>organic</code>, <code>other</code> and <code>total</code> (all long), sorted by <code>day</code>.</p>
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

GROUPS = ["email", "paid", "organic", "other"]


def solve(spark, events_df):
    c = F.lower(F.trim("channel"))
    grp = (F.when(c.isin("email", "e-mail", "newsletter"), "email")
            .when(c.isin("paid", "cpc", "ads"), "paid")
            .when(c.isin("organic", "seo"), "organic")
            .otherwise("other"))
    e = events_df.withColumn("grp", grp).withColumn("n", F.coalesce("signups", F.lit(0)))
    wide = e.groupBy("day").pivot("grp", GROUPS).agg(F.sum("n"))
    bounds = events_df.agg(F.min("day").alias("lo"), F.max("day").alias("hi"))
    days = bounds.select(F.explode(F.sequence("lo", "hi")).alias("day"))
    out = days.join(wide, "day", "left").fillna(0, GROUPS)
    out = out.select("day", *[F.col(g).cast("long").alias(g) for g in GROUPS])
    return out.withColumn("total", sum(F.col(g) for g in GROUPS)).orderBy("day")
"""
MUTANTS = [
    SOLUTION.replace('    out = days.join(wide, "day", "left").fillna(0, GROUPS)', '    out = wide.fillna(0, GROUPS)'),
    SOLUTION.replace('    c = F.lower(F.trim("channel"))', '    c = F.lower(F.col("channel"))'),
    SOLUTION.replace('    e = events_df.withColumn("grp", grp)', '    e = events_df.where(F.col("channel").isNotNull()).withColumn("grp", grp)'),
    SOLUTION.replace('.withColumn("n", F.coalesce("signups", F.lit(0)))', '.withColumn("n", F.col("signups"))').replace('.fillna(0, GROUPS)', ''),
]
S = "day date, channel string, signups long"


def tests():
    t = [{"events_df": df(S, [[day(0), "Email", 3], [day(0), " newsletter ", 2], [day(0), "CPC", 5], [day(0), None, 1], [day(1), "seo", None],
                              [day(3), "ads", 4], [day(3), "Ads ", 1], [day(3), "tiktok", 7], [day(3), "organic", 2]])},
         {"events_df": df(S, [[day(10), "paid", 1], [day(12), "paid", 2]])}]
    r = rng(4222)
    for _ in range(6):
        rows = []
        for _ in range(r.randint(1, 14)):
            rows.append([day(r.randint(0, 9)), r.choice(["email", " E-mail", "newsletter", "cpc", "ADS", "seo", "Organic ", "tiktok", None, "paid"]),
                         r.choice([None, 0, 1, 4, 10])])
        t.append({"events_df": df(S, rows)})
    return t
