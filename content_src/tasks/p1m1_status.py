from kit import df, rng

ID = "p1m1"
NAME = "Payment status"
LANG = "pyspark"
PARAMS = ["spark", "payments_df"]
MINUTES = 5
ORDERED = False
TAGS = ["when / otherwise", "null"]
SUMMARY_FR = "Ajoute une colonne status : unknown si amount est null, refund si négatif, free si 0, sinon paid. L'ordre des lignes ne compte pas."
DESC = """
<p>You are given <code>payments_df</code> with the columns <code>payment_id</code> (string) and <code>amount</code> (double, can be null).</p>
<p>Return the same DataFrame with one more column <code>status</code>:</p>
<ul><li><code>"unknown"</code> if <code>amount</code> is null;</li><li><code>"refund"</code> if <code>amount</code> is negative;</li><li><code>"free"</code> if <code>amount</code> is exactly <code>0</code>;</li><li><code>"paid"</code> otherwise.</li></ul>
<p>The output columns are <code>payment_id</code>, <code>amount</code>, <code>status</code>. Row order does not matter.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F


def solve(spark: SparkSession, payments_df: DataFrame) -> DataFrame:
    # write your code here
    return payments_df
"""
SOLUTION = """
from pyspark.sql import functions as F


def solve(spark, payments_df):
    status = (F.when(F.col("amount").isNull(), "unknown")
               .when(F.col("amount") < 0, "refund")
               .when(F.col("amount") == 0, "free")
               .otherwise("paid"))
    return payments_df.withColumn("status", status)
"""
MUTANTS = [
    """
from pyspark.sql import functions as F
def solve(spark, payments_df):
    return payments_df.withColumn("status", F.when(F.col("amount") < 0, "refund").when(F.col("amount") == 0, "free").otherwise("paid"))
""",
]
HINTS = [
    "Un null ne passe aucun when. Si tu ne le traites pas en premier, il tombe dans otherwise.",
    "Enchaîne : F.when(cond1, v1).when(cond2, v2).otherwise(v3). Le premier when vrai gagne.",
]
S = "payment_id STRING, amount DOUBLE"


def tests():
    t = [df(S, [["P1", 120.0], ["P2", -15.5], ["P3", 0.0], ["P4", None]]),
         df(S, [["A", 0.01], ["B", -0.01]])]
    r = rng(1)
    for k in range(4):
        rows = []
        for i in range(8 + 3 * k):
            v = r.choice([None, 0.0, round(r.uniform(-50, 200), 2)])
            rows.append([f"X{k}{i}", v])
        t.append(df(S, rows))
    t.append(df(S, []))
    return [{"payments_df": x} for x in t]
