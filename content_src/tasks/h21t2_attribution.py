from kit import df, rng, ts

ID = "h21t2"
NAME = "Last-Touch Attribution"
LANG = "pyspark"
PARAMS = ["spark", "visits_df", "purchases_df"]
MINUTES = 25
TAGS = ["consigne longue", "jointure sur un intervalle de temps", "dernier contact", "row_number", "valeur par défaut"]
DESC = """
<p>Marketing wants to know which source brings revenue. <code>visits_df</code> has the columns <code>user_id</code>, <code>ts</code> (timestamp) and <code>utm_source</code> (string, can be <code>null</code> or empty). <code>purchases_df</code> has <code>order_id</code>, <code>user_id</code>, <code>ts</code> (timestamp) and <code>amount</code> (double).</p>
<p>Each purchase is credited to the <b>last tagged visit</b> of the same user before it: a visit with a non-empty <code>utm_source</code>, whose time is at most the purchase time and at least 7 days (604800 seconds) before it, both limits included. Sources are compared after trimming spaces and putting them in lower case (<code>" Google"</code> is <code>google</code>). If two candidate visits have the same time, take the source first in alphabetical order. A purchase without any candidate visit is credited to <code>"direct"</code>.</p>
<p>Your task is to return, for each source with at least one purchase, the columns <code>source</code>, <code>purchases</code> (long), <code>buyers</code> (long, distinct users) and <code>revenue</code> (double, rounded to 2 decimals), sorted by <code>revenue</code> from the highest, then <code>source</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, Window, functions as F


def solve(spark: SparkSession, visits_df: DataFrame, purchases_df: DataFrame) -> DataFrame:
    # write your code here
    return purchases_df
"""
SOLUTION = """
from pyspark.sql import Window, functions as F


def solve(spark, visits_df, purchases_df):
    v = (visits_df.withColumn("src", F.lower(F.trim("utm_source")))
         .where(F.col("src").isNotNull() & (F.col("src") != ""))
         .select(F.col("user_id").alias("v_user"), F.col("ts").cast("long").alias("v_sec"), "src"))
    p = purchases_df.withColumn("p_sec", F.col("ts").cast("long"))
    cond = (p.user_id == v.v_user) & (v.v_sec <= p.p_sec) & (v.v_sec >= p.p_sec - 604800)
    j = p.join(v, cond, "left")
    w = Window.partitionBy("order_id").orderBy(F.col("v_sec").desc_nulls_last(), F.col("src").asc())
    best = (j.withColumn("rn", F.row_number().over(w)).where(F.col("rn") == 1)
            .withColumn("source", F.coalesce("src", F.lit("direct"))))
    out = best.groupBy("source").agg(F.count("*").alias("purchases"), F.countDistinct("user_id").alias("buyers"),
                                     F.round(F.sum("amount"), 2).alias("revenue"))
    return out.orderBy(F.col("revenue").desc(), "source")
"""
MUTANTS = [
    SOLUTION.replace(" & (v.v_sec >= p.p_sec - 604800)", ""),
    SOLUTION.replace("(v.v_sec <= p.p_sec)", "(v.v_sec < p.p_sec)"),
    SOLUTION.replace('    v = (visits_df.withColumn("src", F.lower(F.trim("utm_source")))', '    v = (visits_df.withColumn("src", F.col("utm_source"))'),
    SOLUTION.replace('         .where(F.col("src").isNotNull() & (F.col("src") != ""))\n', ''),
    SOLUTION.replace('F.col("src").asc()', 'F.col("src").desc()'),
]
SV = "user_id string, ts timestamp, utm_source string"
SP = "order_id string, user_id string, ts timestamp, amount double"
D = 24 * 60


def tests():
    t = [{"visits_df": df(SV, [["u1", ts(0), "Google"], ["u1", ts(60), None], ["u1", ts(120), " google "], ["u2", ts(0), "newsletter"],
                                ["u3", ts(0), "ads"], ["u3", ts(0), "Affiliate"], ["u4", ts(500), "ads"], ["u4", ts(400), "Mail"]]),
          "purchases_df": df(SP, [["o1", "u1", ts(120), 50.0], ["o2", "u2", ts(7 * D), 30.0], ["o3", "u2", ts(7 * D + 1), 20.0],
                                  ["o4", "u3", ts(10), 15.5], ["o5", "u4", ts(400), 9.99], ["o6", "u5", ts(0), 1.0]])},
         {"visits_df": df(SV, [["a", ts(0), "fb"], ["a", ts(30), ""], ["a", ts(40), "  "], ["b", ts(0), "FB"]]),
          "purchases_df": df(SP, [["p1", "a", ts(50), 10.0], ["p2", "a", ts(60), 5.0], ["p3", "b", ts(5), 2.5]])}]
    r = rng(4212)
    for _ in range(6):
        vis, pur = [], []
        for u in ["u1", "u2", "u3", "u4"]:
            for _ in range(r.randint(0, 4)):
                vis.append([u, ts(r.choice([0, 100, 3 * D, 6 * D, 7 * D, 9 * D])), r.choice(["Google", "google ", "ads", "ADS", "", None, "mail"])])
            for k in range(r.randint(0, 3)):
                pur.append([f"{u}-{k}", u, ts(r.choice([0, 100, 7 * D, 8 * D, 10 * D])), float(r.choice([5, 12.5, 99.9]))])
        if not pur:
            pur.append(["z", "u1", ts(0), 1.0])
        t.append({"visits_df": df(SV, vis), "purchases_df": df(SP, pur)})
    return t
