from kit import df, rng

ID = "f14t2"
NAME = "Weekly Merchant Payouts"
LANG = "pyspark"
PARAMS = ["spark", "transactions_df", "until"]
MINUTES = 22
TAGS = ["consigne longue", "semaines sans activité", "réserve libérée 4 semaines plus tard", "grille de dates"]
DESC = """
<p>Our marketplace pays its merchants once a week. <code>transactions_df</code> has the columns <code>txn_id</code>, <code>merchant</code>, <code>created_at</code> (timestamp), <code>kind</code> (<code>sale</code>, <code>refund</code> or <code>fee</code>, in any case) and <code>amount</code> (double, always positive). The payment provider sometimes sends the same transaction twice; a <code>txn_id</code> is one transaction.</p>
<p>A payout week starts on a Monday and covers Monday to Sunday. The net of a week is its sales minus its refunds minus its fees. To protect itself against future refunds, the marketplace keeps a <b>reserve</b> of 10% of the sales of each week and gives it back to the merchant exactly 4 weeks later, with the payout of that later week. So the payout of a week is its net, minus 10% of its sales, plus 10% of the sales of the week 4 weeks before. This is true even for a week in which the merchant sold nothing: a quiet week can still have a payout because a reserve is released.</p>
<p>The report is produced on the date <code>until</code> (string <code>yyyy-MM-dd</code>); transactions after that day are not known yet.</p>
<p>Your task is to return, for each merchant, one row for every week from the week of its first transaction to the week that contains <code>until</code>, with the columns <code>merchant</code>, <code>week</code> (date of the Monday), <code>sales</code> (double, total sales of the week) and <code>payout</code> (double), both rounded to 2 decimals, sorted by <code>merchant</code>, then <code>week</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F
from pyspark.sql.window import Window


def solve(spark: SparkSession, transactions_df: DataFrame, until: str) -> DataFrame:
    # write your code here
    return transactions_df
"""
SOLUTION = """
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def solve(spark, transactions_df, until):
    last = F.to_date(F.lit(until))
    t = (transactions_df.filter(F.to_date("created_at") <= last).dropDuplicates(["txn_id"])
         .withColumn("kind", F.lower(F.trim("kind")))
         .withColumn("week", F.to_date(F.date_trunc("week", "created_at"))))
    agg = t.groupBy("merchant", "week").agg(
        F.sum(F.when(F.col("kind") == "sale", F.col("amount")).otherwise(0.0)).alias("sales"),
        F.sum(F.when(F.col("kind") == "sale", F.col("amount")).otherwise(-F.col("amount"))).alias("net"))
    grid = (t.groupBy("merchant").agg(F.min("week").alias("first"))
            .withColumn("week", F.explode(F.sequence("first", F.to_date(F.date_trunc("week", last)), F.expr("interval 1 week"))))
            .select("merchant", "week"))
    g = grid.join(agg, ["merchant", "week"], "left").fillna(0.0, ["sales", "net"])
    w = Window.partitionBy("merchant").orderBy("week")
    released = F.coalesce(F.lag("sales", 4).over(w), F.lit(0.0)) * 0.1
    return (g.withColumn("payout", F.round(F.col("net") - F.col("sales") * 0.1 + released, 2))
            .select("merchant", "week", F.round("sales", 2).alias("sales"), "payout")
            .orderBy("merchant", "week"))
"""
MUTANTS = [
    SOLUTION.replace('g = grid.join(agg, ["merchant", "week"], "left").fillna(0.0, ["sales", "net"])', 'g = agg'),
    SOLUTION.replace('.dropDuplicates(["txn_id"])', ''),
    SOLUTION.replace('.withColumn("kind", F.lower(F.trim("kind")))', ''),
    SOLUTION.replace('t = (transactions_df.filter(F.to_date("created_at") <= last)', 't = (transactions_df'),
]
S = "txn_id string, merchant string, created_at timestamp, kind string, amount double"


def tests():
    t = [{"transactions_df": df(S, [["t1", "m1", "2026-03-02 10:00:00", "sale", 100.0], ["t2", "m1", "2026-03-08 23:30:00", "Sale", 50.0],
                                    ["t2", "m1", "2026-03-08 23:30:00", "Sale", 50.0], ["t3", "m1", "2026-03-04 12:00:00", "FEE", 3.0],
                                    ["t4", "m1", "2026-03-17 09:00:00", "refund", 20.0], ["t5", "m2", "2026-03-23 09:00:00", "sale", 80.0],
                                    ["t6", "m2", "2026-04-15 09:00:00", "sale", 999.0], ["t7", "m2", "2026-04-10 09:00:00", "sale", 500.0]]), "until": "2026-04-08"},
         {"transactions_df": df(S, [["a", "x", "2026-01-05 08:00:00", "sale", 10.0]]), "until": "2026-02-02"}]
    r = rng(3142)
    for _ in range(6):
        rows = []
        for i in range(r.randint(3, 12)):
            rows.append([f"t{i}", r.choice(["m1", "m2"]), f"2026-03-{r.randint(1, 31):02d} {r.randint(0, 23):02d}:00:00",
                         r.choice(["sale", "sale", "Sale", "refund", "FEE"]), r.choice([10.0, 49.9, 200.0, 3.5])])
        if r.random() < 0.6:
            rows.append(list(rows[0]))
        t.append({"transactions_df": df(S, rows), "until": f"2026-04-{r.randint(5, 25):02d}"})
    return t
