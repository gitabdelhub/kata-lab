from kit import df, rng

ID = "f13t2"
NAME = "Win-back Audience"
LANG = "pyspark"
PARAMS = ["spark", "orders_df", "consent_df", "as_of"]
MINUTES = 22
TAGS = ["consigne longue", "consentement au plus tard", "anti-jointure", "plusieurs filtres"]
DESC = """
<p>Marketing wants to send a win-back email to good customers who stopped buying. The audience must be computed for the date <code>as_of</code> (a string <code>yyyy-MM-dd</code>); anything that happened after the end of that day is unknown at that date and must be ignored.</p>
<p><code>orders_df</code> has the columns <code>order_id</code>, <code>customer_id</code>, <code>ordered_at</code> (timestamp), <code>amount</code> (double) and <code>status</code>. Only orders with the status <code>completed</code> (any case) are real purchases: refunded or cancelled orders do not count, and neither does their amount. Because of a sync bug, the same order can appear twice with the same <code>order_id</code>; it is one order.</p>
<p>A customer is a <b>good customer</b> if they have at least 2 real purchases, and they <b>stopped buying</b> if their last real purchase is more than 90 days before <code>as_of</code> (90 days exactly is not enough; count whole days between the date of the purchase and <code>as_of</code>).</p>
<p>Finally, the law only allows emails to customers who agreed. <code>consent_df</code> has the columns <code>customer_id</code>, <code>changed_at</code> (timestamp) and <code>consent</code> (string <code>in</code> or <code>out</code>). Customers who never changed their consent are opted in by default; otherwise their most recent consent change known at <code>as_of</code> decides.</p>
<p>Your task is to return the audience with the columns <code>customer_id</code>, <code>purchases</code> (long), <code>last_purchase</code> (date), <code>days_since</code> (integer) and <code>lifetime_value</code> (double, total amount of the real purchases, rounded to 2 decimals), sorted by <code>lifetime_value</code> descending, then <code>customer_id</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F
from pyspark.sql.window import Window


def solve(spark: SparkSession, orders_df: DataFrame, consent_df: DataFrame, as_of: str) -> DataFrame:
    # write your code here
    return orders_df
"""
SOLUTION = """
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def solve(spark, orders_df, consent_df, as_of):
    day = F.to_date(F.lit(as_of))
    o = (orders_df.filter((F.lower(F.trim("status")) == "completed") & (F.to_date("ordered_at") <= day))
         .dropDuplicates(["order_id"]))
    c = (o.groupBy("customer_id").agg(F.count("*").alias("purchases"), F.max(F.to_date("ordered_at")).alias("last_purchase"),
                                      F.round(F.sum("amount"), 2).alias("lifetime_value"))
         .withColumn("days_since", F.datediff(day, "last_purchase"))
         .filter((F.col("purchases") >= 2) & (F.col("days_since") > 90)))
    w = Window.partitionBy("customer_id").orderBy(F.col("changed_at").desc())
    k = (consent_df.filter(F.to_date("changed_at") <= day).withColumn("rn", F.row_number().over(w)).filter("rn = 1")
         .filter(F.lower(F.trim("consent")) == "out").select("customer_id"))
    return (c.join(k, "customer_id", "left_anti")
            .select("customer_id", "purchases", "last_purchase", F.col("days_since").cast("int"), "lifetime_value")
            .orderBy(F.col("lifetime_value").desc(), "customer_id"))
"""
MUTANTS = [
    SOLUTION.replace('.filter((F.col("purchases") >= 2) & (F.col("days_since") > 90)))', '.filter((F.col("purchases") >= 2) & (F.col("days_since") >= 90)))'),
    SOLUTION.replace('k = (consent_df.filter(F.to_date("changed_at") <= day)', 'k = (consent_df'),
    SOLUTION.replace('         .dropDuplicates(["order_id"]))', '         )'),
    SOLUTION.replace("o = (orders_df.filter((F.lower(F.trim(\"status\")) == \"completed\") & (F.to_date(\"ordered_at\") <= day))", "o = (orders_df.filter(F.to_date(\"ordered_at\") <= day)"),
]
O = "order_id string, customer_id string, ordered_at timestamp, amount double, status string"
C = "customer_id string, changed_at timestamp, consent string"


def tests():
    t = [{"orders_df": df(O, [["o1", "c1", "2025-10-01 10:00:00", 120.0, "completed"], ["o2", "c1", "2025-11-20 10:00:00", 80.5, "COMPLETED"],
                              ["o2", "c1", "2025-11-20 10:00:00", 80.5, "COMPLETED"], ["o3", "c2", "2025-09-01 10:00:00", 60.0, "completed"],
                              ["o4", "c2", "2025-09-15 10:00:00", 999.0, "refunded"], ["o5", "c3", "2025-08-01 10:00:00", 40.0, "completed"],
                              ["o6", "c3", "2025-08-02 10:00:00", 45.0, "completed"], ["o7", "c4", "2025-07-01 10:00:00", 10.0, "completed"],
                              ["o8", "c4", "2025-12-01 09:00:00", 10.0, "completed"], ["o9", "c5", "2025-06-01 10:00:00", 300.0, "completed"],
                              ["o10", "c5", "2025-06-05 10:00:00", 200.0, "completed"], ["o10", "c5", "2025-06-05 10:00:00", 200.0, "completed"], ["o11", "c1", "2026-03-10 10:00:00", 50.0, "completed"]]),
          "consent_df": df(C, [["c3", "2025-12-01 10:00:00", "out"], ["c5", "2025-12-01 10:00:00", "out"], ["c5", "2026-01-10 10:00:00", "in"],
                               ["c1", "2026-02-20 10:00:00", "out"]]), "as_of": "2026-03-01"},
         {"orders_df": df(O, [["a", "x", "2025-12-01 10:00:00", 1.0, "completed"], ["b", "x", "2025-12-01 11:00:00", 2.0, "completed"], ["c", "y", "2025-11-30 10:00:00", 5.0, "completed"], ["d", "y", "2025-10-30 10:00:00", 6.0, "completed"]]),
          "consent_df": df(C, []), "as_of": "2026-03-01"}]
    r = rng(3132)
    for _ in range(6):
        rows = []
        for i in range(r.randint(4, 14)):
            m = r.randint(5, 11)
            rows.append([f"o{i}", f"c{r.randint(1, 3)}", f"2025-{m:02d}-{r.randint(1, 28):02d} 10:00:00", r.choice([10.0, 25.25, 99.9]), r.choice(["completed", "Completed", "completed", "refunded", "cancelled"])])
        done = [x for x in rows if x[4].lower() == "completed"]
        if done and r.random() < 0.6:
            rows.append(list(done[0]))
        cons = [[f"c{r.randint(1, 5)}", f"2026-0{r.randint(1, 4)}-{r.randint(1, 28):02d} 10:00:00", r.choice(["in", "out", "OUT"])] for _ in range(r.randint(0, 5))]
        t.append({"orders_df": df(O, rows), "consent_df": df(C, cons), "as_of": "2026-03-01"})
    return t
