from kit import df, rng

ID = "f11t2"
NAME = "Payment Retries in EUR"
LANG = "pyspark"
PARAMS = ["spark", "attempts_df", "rates_df"]
MINUTES = 22
TAGS = ["consigne longue", "première réussite", "taux de change as-of", "plusieurs règles cachées"]
DESC = """
<p>When a card payment fails, our payment service retries it automatically, up to several times. Every try is logged in <code>attempts_df</code> with the columns <code>payment_id</code>, <code>merchant</code>, <code>attempt_at</code> (timestamp), <code>status</code>, <code>amount</code> (double) and <code>currency</code>. The merchant team wants to know how well retries work and how much money they bring, in euros.</p>
<p>A payment is <b>successful</b> as soon as one of its tries has the status <code>succeeded</code>; whatever is logged after its first success (duplicate notifications from the bank, for example) must be ignored. A payment that never succeeded is <b>failed</b> if its last try is <code>failed</code>; a payment whose last try is anything else is still in progress and does not count at all. The amount and the currency of a payment are those of its <b>first</b> try, because later tries are sometimes logged with a rounded amount.</p>
<p><code>rates_df</code> has the columns <code>currency</code>, <code>day</code> (date) and <code>eur_rate</code> (double: 1 unit of the currency is worth <code>eur_rate</code> euros). Rates are not published every day: a successful payment is converted with the most recent rate of its currency published on or before the day of its first success. Euros are never in <code>rates_df</code> and have a rate of 1. A successful payment with no known rate is still counted as successful, but brings no euros.</p>
<p>Your task is to return one row per merchant with at least one successful or failed payment, with the columns <code>merchant</code>, <code>succeeded</code> (long), <code>failed</code> (long), <code>avg_tries</code> (double: average number of tries up to and including the first success, over successful payments, rounded to 2 decimals, <code>null</code> if none) and <code>revenue_eur</code> (double, sum of the converted amounts of the successful payments, rounded to 2 decimals, <code>0.0</code> if none). Sort by <code>merchant</code>. Statuses may be written in any case.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F
from pyspark.sql.window import Window


def solve(spark: SparkSession, attempts_df: DataFrame, rates_df: DataFrame) -> DataFrame:
    # write your code here
    return attempts_df
"""
SOLUTION = """
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def solve(spark, attempts_df, rates_df):
    a = attempts_df.withColumn("status", F.lower(F.trim("status")))
    w = Window.partitionBy("payment_id").orderBy("attempt_at")
    a = (a.withColumn("n", F.row_number().over(w))
         .withColumn("first_amount", F.first("amount").over(w))
         .withColumn("first_currency", F.first("currency").over(w)))
    first_ok = (a.filter(F.col("status") == "succeeded").groupBy("payment_id")
                .agg(F.min("n").alias("tries"), F.min("attempt_at").alias("ok_at")))
    last = (a.withColumn("rk", F.row_number().over(Window.partitionBy("payment_id").orderBy(F.col("attempt_at").desc())))
            .filter("rk = 1").select("payment_id", "merchant", F.col("status").alias("last_status"), "first_amount", "first_currency"))
    p = last.join(first_ok, "payment_id", "left")
    p = p.withColumn("kind", F.when(F.col("tries").isNotNull(), "ok").when(F.col("last_status") == "failed", "ko"))
    p = p.filter(F.col("kind").isNotNull())
    ok = p.filter(F.col("kind") == "ok").withColumn("day", F.to_date("ok_at"))
    r = rates_df.select(F.col("currency").alias("rc"), F.col("day").alias("rday"), "eur_rate")
    j = ok.join(r, (ok.first_currency == r.rc) & (r.rday <= ok.day), "left")
    j = (j.withColumn("rk", F.row_number().over(Window.partitionBy("payment_id").orderBy(F.col("rday").desc_nulls_last())))
         .filter("rk = 1")
         .withColumn("rate", F.when(F.col("first_currency") == "EUR", F.lit(1.0)).otherwise(F.col("eur_rate")))
         .withColumn("eur", F.col("first_amount") * F.col("rate")))
    okagg = j.groupBy("merchant").agg(F.count("*").alias("succeeded"), F.round(F.avg("tries"), 2).alias("avg_tries"),
                                      F.round(F.coalesce(F.sum("eur"), F.lit(0.0)), 2).alias("revenue_eur"))
    koagg = p.filter(F.col("kind") == "ko").groupBy("merchant").agg(F.count("*").alias("failed"))
    out = okagg.join(koagg, "merchant", "full")
    return (out.select("merchant", F.coalesce("succeeded", F.lit(0)).cast("long").alias("succeeded"),
                       F.coalesce("failed", F.lit(0)).cast("long").alias("failed"), "avg_tries",
                       F.coalesce("revenue_eur", F.lit(0.0)).alias("revenue_eur"))
            .orderBy("merchant"))
"""
MUTANTS = [
    SOLUTION.replace('.withColumn("first_amount", F.first("amount").over(w))', '.withColumn("first_amount", F.last("amount").over(w.rowsBetween(Window.unboundedPreceding, Window.unboundedFollowing)))'),
    SOLUTION.replace('(r.rday <= ok.day)', '(r.rday == ok.day)'),
    SOLUTION.replace('p = p.withColumn("kind", F.when(F.col("tries").isNotNull(), "ok").when(F.col("last_status") == "failed", "ko"))',
                     'p = p.withColumn("kind", F.when(F.col("tries").isNotNull(), "ok").otherwise("ko"))'),
]
A = "payment_id string, merchant string, attempt_at timestamp, status string, amount double, currency string"
R = "currency string, day date, eur_rate double"


def tests():
    t = [{"attempts_df": df(A, [["p1", "shopA", "2026-03-01 10:00:00", "failed", 100.0, "MAD"], ["p1", "shopA", "2026-03-01 10:05:00", "Succeeded", 100.0, "MAD"],
                                ["p1", "shopA", "2026-03-01 10:06:00", "failed", 100.0, "MAD"],
                                ["p2", "shopA", "2026-03-02 09:00:00", "succeeded", 20.0, "EUR"],
                                ["p3", "shopA", "2026-03-02 11:00:00", "failed", 5.0, "USD"], ["p3", "shopA", "2026-03-02 11:10:00", "FAILED", 5.0, "USD"],
                                ["p4", "shopB", "2026-03-03 08:00:00", "failed", 49.99, "USD"], ["p4", "shopB", "2026-03-03 08:30:00", "pending", 50.0, "USD"],
                                ["p5", "shopB", "2026-03-03 12:00:00", "failed", 30.4, "USD"], ["p5", "shopB", "2026-03-04 12:00:00", "succeeded", 30.0, "USD"], ["p6", "shopB", "2026-03-04 13:00:00", "succeeded", 7.0, "XOF"]]),
          "rates_df": df(R, [["MAD", "2026-02-27", 0.092], ["MAD", "2026-03-02", 0.093], ["USD", "2026-03-01", 0.92]])},
         {"attempts_df": df(A, [["q", "m", "2026-03-05 10:00:00", "pending", 10.0, "USD"]]), "rates_df": df(R, [["USD", "2026-03-01", 0.9]])}]
    r = rng(3112)
    for _ in range(6):
        rows = []
        for pid in range(r.randint(2, 7)):
            cur, amt, merch = r.choice(["EUR", "USD", "MAD", "XOF"]), r.choice([10.0, 25.5, 99.99]), r.choice(["shopA", "shopB"])
            for k in range(r.randint(1, 4)):
                rows.append([f"p{pid}", merch, f"2026-03-0{r.randint(1, 6)} {10 + k:02d}:{r.randint(0, 5)}0:00", r.choice(["failed", "succeeded", "FAILED", "pending"]),
                             amt if k == 0 else round(amt), cur])
        rates = [[c, f"2026-03-0{d}", round(r.uniform(0.001, 1.2), 4)] for c in ["USD", "MAD"] for d in r.sample(range(1, 7), r.randint(0, 3))]
        t.append({"attempts_df": df(A, rows), "rates_df": df(R, rates)})
    return t
