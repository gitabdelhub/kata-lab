from kit import df, rng

ID = "e05t2"
NAME = "Payment Reconciliation"
LANG = "pyspark"
PARAMS = ["spark", "payments_df", "bank_df"]
MINUTES = 20
TAGS = ["left join", "clé normalisée", "tolérance", "statut CASE"]
DESC = """
<p>The finance team checks that every payment recorded in the internal system appears on the bank statement.</p>
<p><code>payments_df</code>: <code>payment_id</code> (string, unique), <code>ref</code> (string), <code>amount</code> (double) and <code>paid_on</code> (date).</p>
<p><code>bank_df</code>: <code>line_id</code> (string, unique), <code>ref</code> (string), <code>amount</code> (double) and <code>booked_on</code> (date).</p>
<p>References are typed by hand: they must be compared after trimming, upper-casing and removing every space and dash (<code>" inv-0042 "</code> is <code>"INV0042"</code>). Each normalized reference appears at most once in <code>bank_df</code>.</p>
<p>The status of a payment is:</p>
<ul><li><code>"MATCHED"</code> if the bank has a line with the same normalized reference, an amount that differs by at most <code>0.01</code> (compare the absolute difference <b>rounded to 2 decimals</b>, to avoid floating point surprises), and a booking date from <code>0</code> to <code>3</code> days after <code>paid_on</code>;</li><li><code>"AMOUNT_MISMATCH"</code> if the bank has a line with the same reference, but the amount differs by more than <code>0.01</code> (whatever the date);</li><li><code>"LATE"</code> if the reference and amount match but the booking date is not in the allowed range;</li><li><code>"MISSING"</code> if the bank has no line with this reference.</li></ul>
<p>Your task is to return <code>payment_id</code>, <code>ref</code> (normalized), <code>status</code> and <code>bank_amount</code> (the amount of the bank line, <code>null</code> if missing), sorted by <code>payment_id</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F


def solve(spark: SparkSession, payments_df: DataFrame, bank_df: DataFrame) -> DataFrame:
    # write your code here
    return payments_df
"""
SOLUTION = """
from pyspark.sql import functions as F


def norm(c):
    return F.regexp_replace(F.upper(F.trim(c)), "[ -]", "")


def solve(spark, payments_df, bank_df):
    p = payments_df.select("payment_id", norm("ref").alias("ref"), "amount", "paid_on")
    b = bank_df.select(norm("ref").alias("ref"), F.col("amount").alias("bank_amount"), "booked_on")
    j = p.join(b, "ref", "left")
    gap = F.datediff("booked_on", "paid_on")
    status = (F.when(F.col("bank_amount").isNull(), "MISSING")
              .when(F.round(F.abs(F.col("amount") - F.col("bank_amount")), 2) > 0.01, "AMOUNT_MISMATCH")
              .when(gap.between(0, 3), "MATCHED")
              .otherwise("LATE"))
    return j.select("payment_id", "ref", status.alias("status"), "bank_amount").orderBy("payment_id")
"""
MUTANTS = [
    """
from pyspark.sql import functions as F
def solve(spark, payments_df, bank_df):
    p = payments_df.select("payment_id", F.upper(F.trim("ref")).alias("ref"), "amount", "paid_on")
    b = bank_df.select(F.upper(F.trim("ref")).alias("ref"), F.col("amount").alias("bank_amount"), "booked_on")
    j = p.join(b, "ref", "left")
    gap = F.datediff("booked_on", "paid_on")
    st = F.when(F.col("bank_amount").isNull(), "MISSING").when(F.abs(F.col("amount") - F.col("bank_amount")) > 0.010000001, "AMOUNT_MISMATCH").when(gap.between(0, 3), "MATCHED").otherwise("LATE")
    return j.select("payment_id", "ref", st.alias("status"), "bank_amount").orderBy("payment_id")
""",
    """
from pyspark.sql import functions as F
def solve(spark, payments_df, bank_df):
    n = lambda c: F.regexp_replace(F.upper(F.trim(c)), "[ -]", "")
    p = payments_df.select("payment_id", n("ref").alias("ref"), "amount", "paid_on")
    b = bank_df.select(n("ref").alias("ref"), F.col("amount").alias("bank_amount"), "booked_on")
    j = p.join(b, "ref", "left")
    gap = F.datediff("booked_on", "paid_on")
    st = F.when(F.col("bank_amount").isNull(), "MISSING").when(F.col("amount") != F.col("bank_amount"), "AMOUNT_MISMATCH").when(gap.between(0, 3), "MATCHED").otherwise("LATE")
    return j.select("payment_id", "ref", st.alias("status"), "bank_amount").orderBy("payment_id")
""",
    """
from pyspark.sql import functions as F
def solve(spark, payments_df, bank_df):
    n = lambda c: F.regexp_replace(F.upper(F.trim(c)), "[ -]", "")
    p = payments_df.select("payment_id", n("ref").alias("ref"), "amount", "paid_on")
    b = bank_df.select(n("ref").alias("ref"), F.col("amount").alias("bank_amount"), "booked_on")
    j = p.join(b, "ref", "left")
    gap = F.abs(F.datediff("booked_on", "paid_on"))
    st = F.when(F.col("bank_amount").isNull(), "MISSING").when(F.abs(F.col("amount") - F.col("bank_amount")) > 0.010000001, "AMOUNT_MISMATCH").when(gap <= 3, "MATCHED").otherwise("LATE")
    return j.select("payment_id", "ref", st.alias("status"), "bank_amount").orderBy("payment_id")
""",
]
P = "payment_id string, ref string, amount double, paid_on date"
B = "line_id string, ref string, amount double, booked_on date"


def tests():
    t = [{"payments_df": df(P, [["p1", " inv-0042 ", 100.0, "2026-03-01"], ["p2", "INV0043", 50.0, "2026-03-01"], ["p3", "inv 0044", 75.5, "2026-03-01"],
                                ["p4", "INV-0045", 10.0, "2026-03-01"], ["p5", "INV0046", 20.0, "2026-03-05"]]),
          "bank_df": df(B, [["b1", "INV0042", 100.01, "2026-03-02"], ["b2", "inv-0043", 49.0, "2026-03-01"], ["b3", "INV0044", 75.5, "2026-03-05"], ["b4", "INV0046", 20.0, "2026-03-04"]])},
         {"payments_df": df(P, [["a", "x-1", 0.0, "2026-01-31"], ["b", "X 2", 1.0, "2026-01-31"]]),
          "bank_df": df(B, [["l1", "X1", 0.0, "2026-02-03"], ["l2", "X2", 1.02, "2026-01-31"]])}]
    r = rng(502)
    for _ in range(6):
        refs = r.sample(range(1, 30), r.randint(2, 9))
        pays, bank = [], []
        for i, k in enumerate(refs):
            amt = round(r.uniform(1, 300), 2)
            pays.append([f"p{i:02d}", r.choice([f"INV-{k:04d}", f" inv{k:04d}", f"INV {k:04d}"]), amt, f"2026-03-{r.randint(4, 9):02d}"])
            if r.random() < 0.8:
                bank.append([f"b{i}", f"INV{k:04d}", round(amt + r.choice([0, 0, 0.01, 0.02, -1.0]), 2), f"2026-03-{r.randint(1, 15):02d}"])
        t.append({"payments_df": df(P, pays), "bank_df": df(B, bank)})
    return t
