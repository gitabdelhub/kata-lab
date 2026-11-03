from kit import df, rng

ID = "p1m3"
NAME = "Orders per customer"
LANG = "pyspark"
PARAMS = ["spark", "orders_df"]
MINUTES = 5
TAGS = ["groupBy / agg", "orderBy"]
SUMMARY_FR = "Une ligne par client : nombre de commandes et total arrondi à 2 décimales. Trie par total décroissant puis customer_id."
DESC = """
<p><code>orders_df</code> has the columns <code>order_id</code> (string), <code>customer_id</code> (string) and <code>amount</code> (double).</p>
<p>Return one row per customer with <code>customer_id</code>, <code>n_orders</code> (number of orders) and <code>total</code> (sum of <code>amount</code>, rounded to 2 decimals), sorted by <code>total</code> descending, then <code>customer_id</code> ascending.</p>
<h4>Example</h4>{{EXAMPLE}}
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
    return (orders_df.groupBy("customer_id")
            .agg(F.count("*").alias("n_orders"), F.round(F.sum("amount"), 2).alias("total"))
            .orderBy(F.col("total").desc(), "customer_id"))
"""
MUTANTS = ["""
from pyspark.sql import functions as F
def solve(spark, orders_df):
    return orders_df.groupBy("customer_id").agg(F.count("*").alias("n_orders"), F.round(F.sum("amount"), 2).alias("total")).orderBy("total", "customer_id")
"""]
HINTS = ["groupBy(\"customer_id\").agg(F.count(\"*\").alias(...), F.round(F.sum(...), 2).alias(...))",
         "Tri décroissant : .orderBy(F.col(\"total\").desc(), \"customer_id\")."]
S = "order_id STRING, customer_id STRING, amount DOUBLE"


def tests():
    t = [df(S, [["O1", "C1", 10.0], ["O2", "C2", 25.5], ["O3", "C1", 15.5], ["O4", "C3", 5.0]]),
         df(S, [["O1", "B", 10.0], ["O2", "A", 10.0]])]
    r = rng(4)
    for k in range(4):
        t.append(df(S, [[f"O{i}", f"C{r.randint(1, 6)}", round(r.uniform(1, 90), 2)] for i in range(10 + 5 * k)]))
    return [{"orders_df": x} for x in t]
