from kit import df, rng

ID = "e16t2"
NAME = "Pareto Products per Store"
LANG = "pyspark"
PARAMS = ["spark", "sales_df"]
MINUTES = 20
TAGS = ["somme cumulée", "part en pourcentage", "fenêtre avec ordre et départage", "seuil 80 %"]
DESC = """
<p>Store managers want to know which products make most of their revenue. <code>sales_df</code> has the columns <code>store_id</code>, <code>product_id</code> (strings) and <code>revenue</code> (double, can be <code>null</code>, which counts as <code>0</code>). A product can have many rows in the same store.</p>
<p>For each store:</p>
<ol><li>compute the total revenue of each product; products with a total of <code>0</code> are ignored;</li><li>sort the products by total revenue, highest first, and by <code>product_id</code> when two totals are equal;</li><li>the <b>cumulative share</b> of a product is the sum of the totals of this product and of all the products before it, divided by the store total, in percent;</li><li>the <b>core products</b> are the first products of this order, up to and including the first product whose cumulative share is at least <code>80</code> percent.</li></ol>
<p>Your task is to return the core products of every store, with the columns <code>store_id</code>, <code>rank</code> (integer, position in the order, starting at 1), <code>product_id</code>, <code>revenue</code> (double, rounded to 2 decimals) and <code>cum_share_pct</code> (double, rounded to 1 decimal), sorted by <code>store_id</code>, then <code>rank</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F
from pyspark.sql.window import Window


def solve(spark: SparkSession, sales_df: DataFrame) -> DataFrame:
    # write your code here
    return sales_df
"""
SOLUTION = """
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def solve(spark, sales_df):
    p = (sales_df.groupBy("store_id", "product_id")
         .agg(F.sum(F.coalesce(F.col("revenue"), F.lit(0.0))).alias("revenue"))
         .filter(F.col("revenue") > 0))
    w = Window.partitionBy("store_id").orderBy(F.col("revenue").desc(), F.col("product_id"))
    run = w.rowsBetween(Window.unboundedPreceding, Window.currentRow)
    p = (p.withColumn("rank", F.row_number().over(w))
         .withColumn("cum", F.sum("revenue").over(run))
         .withColumn("total", F.sum("revenue").over(Window.partitionBy("store_id")))
         .withColumn("share", 100.0 * F.col("cum") / F.col("total"))
         .withColumn("prev_share", F.lag("share").over(w)))
    core = p.filter(F.col("prev_share").isNull() | (F.col("prev_share") < 80))
    return (core.select("store_id", F.col("rank").cast("int"), "product_id", F.round("revenue", 2).alias("revenue"),
                        F.round("share", 1).alias("cum_share_pct"))
            .orderBy("store_id", "rank"))
"""
MUTANTS = [
    """
from pyspark.sql import functions as F
from pyspark.sql.window import Window
def solve(spark, sales_df):
    p = sales_df.groupBy("store_id", "product_id").agg(F.sum(F.coalesce(F.col("revenue"), F.lit(0.0))).alias("revenue")).filter(F.col("revenue") > 0)
    w = Window.partitionBy("store_id").orderBy(F.col("revenue").desc(), F.col("product_id"))
    p = p.withColumn("rank", F.row_number().over(w)).withColumn("cum", F.sum("revenue").over(w.rowsBetween(Window.unboundedPreceding, Window.currentRow))).withColumn("total", F.sum("revenue").over(Window.partitionBy("store_id"))).withColumn("share", 100.0 * F.col("cum") / F.col("total"))
    return p.filter(F.col("share") <= 80).select("store_id", F.col("rank").cast("int"), "product_id", F.round("revenue", 2).alias("revenue"), F.round("share", 1).alias("cum_share_pct")).orderBy("store_id", "rank")
""",
    """
from pyspark.sql import functions as F
from pyspark.sql.window import Window
def solve(spark, sales_df):
    p = sales_df.groupBy("store_id", "product_id").agg(F.sum(F.coalesce(F.col("revenue"), F.lit(0.0))).alias("revenue")).filter(F.col("revenue") > 0)
    w = Window.partitionBy("store_id").orderBy(F.col("revenue").desc())
    p = p.withColumn("rank", F.row_number().over(w)).withColumn("cum", F.sum("revenue").over(w)).withColumn("total", F.sum("revenue").over(Window.partitionBy("store_id"))).withColumn("share", 100.0 * F.col("cum") / F.col("total")).withColumn("prev", F.lag("share").over(w))
    return p.filter(F.col("prev").isNull() | (F.col("prev") < 80)).select("store_id", F.col("rank").cast("int"), "product_id", F.round("revenue", 2).alias("revenue"), F.round("share", 1).alias("cum_share_pct")).orderBy("store_id", "rank")
""",
]
S = "store_id string, product_id string, revenue double"


def tests():
    t = [{"sales_df": df(S, [["S1", "A", 500.0], ["S1", "B", 200.0], ["S1", "A", 100.0], ["S1", "C", 150.0], ["S1", "D", 50.0], ["S1", "E", None],
                             ["S2", "X", 40.0], ["S2", "Y", 40.0], ["S2", "Z", 20.0]])},
         {"sales_df": df(S, [["T", "p1", 80.0], ["T", "p2", 20.0], ["U", "q", 0.0], ["U", "r", 10.0]])}]
    r = rng(1602)
    for _ in range(6):
        rows = [[f"S{r.randint(1, 3)}", f"P{r.randint(1, 7)}", r.choice([None, 0.0, 10.0, 25.0, 50.0, round(r.uniform(1, 300), 2)])] for _ in range(r.randint(3, 25))]
        t.append({"sales_df": df(S, rows)})
    return t
