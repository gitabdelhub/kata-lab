from kit import df, rng

ID = "p1x2"
NAME = "Clean order amounts"
LANG = "pyspark"
PARAMS = ["spark", "orders_df"]
MINUTES = 15
ORDERED = False
TAGS = ["nettoyage", "regexp_replace", "try_cast", "lower / trim"]
SUMMARY_FR = "Les montants sont du texte sale (virgule décimale, espaces, MAD, vide, texte). Transforme-les en nombre, 0 si illisible. Status en minuscules sans espaces. Garde seulement les commandes dont le status est paid ou shipped."
DESC = """
<p>An e-commerce site exports its orders as text. <code>orders_df</code> has three string columns:</p>
<ul><li><code>order_id</code> - the ID of the order;</li><li><code>status</code> - for example <code>"PAID"</code>, <code>" shipped "</code>, <code>"Cancelled"</code>;</li><li><code>amount</code> - the amount typed by sellers: <code>"45.50"</code>, <code>"30,00"</code>, <code>" 12 MAD"</code>, <code>""</code>, <code>"n/a"</code> or null.</li></ul>
<p>Your task is to return the orders whose status is <code>paid</code> or <code>shipped</code>, with the columns <code>order_id</code>, <code>status</code> and <code>amount</code>, where:</p>
<ol><li><code>status</code> is trimmed and lower-cased;</li><li><code>amount</code> is a double: remove surrounding spaces and the suffix <code>MAD</code> (any case), replace a decimal comma by a dot, then convert;</li><li>an amount that still cannot be converted (empty, text, null) becomes <code>0.0</code>.</li></ol>
<p>Row order does not matter.</p>
<h4>Example</h4>{{EXAMPLE}}
<p><b>Note:</b> with Spark 4, <code>.cast("double")</code> on a text like <code>"n/a"</code> raises an error. Use <code>try_cast</code>, which returns null instead.</p>
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F


def solve(spark: SparkSession, orders_df: DataFrame) -> DataFrame:
    # write your code here
    return orders_df
"""
SOLUTION = """
from pyspark.sql import functions as F


def solve(spark, orders_df):
    status = F.lower(F.trim(F.col("status")))
    txt = F.regexp_replace(F.trim(F.col("amount")), "(?i)\\\\s*mad$", "")
    txt = F.regexp_replace(txt, ",", ".")
    amount = F.coalesce(F.expr("try_cast(_t AS DOUBLE)"), F.lit(0.0))
    return (orders_df
            .withColumn("status", status)
            .withColumn("_t", txt)
            .withColumn("amount", amount)
            .drop("_t")
            .filter(F.col("status").isin("paid", "shipped"))
            .select("order_id", "status", "amount"))
"""
MUTANTS = [
    """
from pyspark.sql import functions as F
def solve(spark, orders_df):
    d = orders_df.withColumn("status", F.lower(F.trim("status")))
    d = d.withColumn("amount", F.coalesce(F.expr("try_cast(trim(amount) AS DOUBLE)"), F.lit(0.0)))
    return d.filter(F.col("status").isin("paid", "shipped")).select("order_id", "status", "amount")
""",
    """
from pyspark.sql import functions as F
def solve(spark, orders_df):
    d = orders_df.withColumn("status", F.lower(F.col("status")))
    t = F.regexp_replace(F.regexp_replace(F.trim("amount"), "(?i)\\\\s*mad$", ""), ",", ".")
    d = d.withColumn("amount", F.coalesce(t.try_cast("double"), F.lit(0.0)))
    return d.filter(F.col("status").isin("paid", "shipped")).select("order_id", "status", "amount")
""",
]
HINTS = [
    "Fais le nettoyage en étapes : trim, puis regexp_replace pour enlever MAD, puis regexp_replace(',', '.').",
    "F.expr(\"try_cast(col AS DOUBLE)\") renvoie null si ce n'est pas un nombre. F.coalesce(x, F.lit(0.0)) remplace le null par 0.",
]
S = "order_id STRING, status STRING, amount STRING"


def tests():
    t = [df(S, [["O1", "PAID", "45.50"], ["O2", " shipped ", "30,00"], ["O3", "Cancelled", "12"], ["O4", "paid", " 12 MAD"], ["O5", "Paid", "n/a"]]),
         df(S, [["O6", "shipped", ""], ["O7", "paid", None], ["O8", "refunded", "5"], ["O9", " PAID", "7mad"]])]
    r = rng(3)
    for k in range(5):
        rows = []
        for i in range(12 + 3 * k):
            st = r.choice(["PAID", " paid", "Shipped ", "cancelled", "REFUNDED", "paid"])
            am = r.choice([f"{r.uniform(1, 500):.2f}", f"{r.randint(1, 99)},{r.randint(0, 99):02d}", f" {r.randint(1, 50)} MAD", f"{r.randint(1, 9)}Mad", "", "n/a", None, "abc"])
            rows.append([f"K{k}{i}", st, am])
        t.append(df(S, rows))
    return [{"orders_df": x} for x in t]
