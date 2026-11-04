from kit import df, rng

ID = "f12t2"
NAME = "Products Bought Together"
LANG = "pyspark"
PARAMS = ["spark", "lines_df"]
MINUTES = 22
TAGS = ["consigne longue", "auto-jointure", "paires sans doublon", "top N avec départage"]
DESC = """
<p>The category managers want to place products that are often bought together next to each other on the shelves. <code>lines_df</code> holds the lines of the receipts of all shops, with the columns <code>receipt_id</code>, <code>store</code> and <code>product</code> (strings). A product appears on one line per unit sold, so the same product can appear several times on a receipt, and product names were typed with inconsistent case and spaces (<code>" Milk"</code> and <code>"milk"</code> are the same product; use the trimmed lower-case name).</p>
<p>Two different products are <b>bought together</b> in a receipt when both appear on it, whatever their quantities. For each store, the managers want the pairs of products bought together in the largest number of receipts of that store. A pair is written once, with the product that comes first alphabetically in <code>product_a</code>, and a pair seen in a single receipt is a coincidence and must never be reported.</p>
<p>Your task is to return, for each store, its 3 best pairs, ranked by number of receipts (highest first); when two pairs have the same number of receipts, the pair that comes first alphabetically (by <code>product_a</code>, then <code>product_b</code>) gets the better rank. A store can have fewer than 3 pairs. Return the columns <code>store</code>, <code>rank</code> (integer from 1), <code>product_a</code>, <code>product_b</code> and <code>receipts</code> (long), sorted by <code>store</code>, then <code>rank</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F
from pyspark.sql.window import Window


def solve(spark: SparkSession, lines_df: DataFrame) -> DataFrame:
    # write your code here
    return lines_df
"""
SOLUTION = """
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def solve(spark, lines_df):
    p = lines_df.select("receipt_id", "store", F.lower(F.trim("product")).alias("product")).dropDuplicates()
    a, b = p.alias("a"), p.alias("b")
    pairs = (a.join(b, (F.col("a.receipt_id") == F.col("b.receipt_id")) & (F.col("a.store") == F.col("b.store"))
                    & (F.col("a.product") < F.col("b.product")))
             .groupBy(F.col("a.store").alias("store"), F.col("a.product").alias("product_a"), F.col("b.product").alias("product_b"))
             .agg(F.count("*").alias("receipts"))
             .filter(F.col("receipts") >= 2))
    w = Window.partitionBy("store").orderBy(F.col("receipts").desc(), "product_a", "product_b")
    return (pairs.withColumn("rank", F.row_number().over(w).cast("int")).filter(F.col("rank") <= 3)
            .select("store", "rank", "product_a", "product_b", "receipts").orderBy("store", "rank"))
"""
MUTANTS = [
    SOLUTION.replace('.dropDuplicates()', ''),
    SOLUTION.replace('(F.col("a.product") < F.col("b.product"))', '(F.col("a.product") != F.col("b.product"))'),
    SOLUTION.replace('.filter(F.col("receipts") >= 2)', ''),
    SOLUTION.replace('orderBy(F.col("receipts").desc(), "product_a", "product_b")', 'orderBy(F.col("receipts").desc())').replace('F.row_number()', 'F.rank()'),
]
S = "receipt_id string, store string, product string"


def tests():
    t = [{"lines_df": df(S, [["r1", "S1", "Milk"], ["r1", "S1", "bread"], ["r1", "S1", "milk"], ["r2", "S1", " Milk"], ["r2", "S1", "Bread"], ["r2", "S1", "tea"],
                             ["r3", "S1", "tea"], ["r3", "S1", "milk"], ["r4", "S1", "tea"], ["r4", "S1", "bread"], ["r5", "S1", "tea"], ["r5", "S1", "milk"],
                             ["r6", "S2", "rice"], ["r6", "S2", "oil"], ["r7", "S2", "oil"], ["r7", "S2", "salt"]])},
         {"lines_df": df(S, [["a", "X", "p"], ["a", "X", "q"], ["b", "X", "q"], ["b", "X", "p"], ["c", "X", "p"], ["c", "X", "r"], ["d", "X", "r"], ["d", "X", "p"],
                             ["e", "X", "s"], ["e", "X", "t"], ["f", "X", "t"], ["f", "X", "s"], ["g", "X", "a"], ["g", "X", "b"], ["h", "X", "a"], ["h", "X", "b"]])}]
    r = rng(3122)
    for _ in range(6):
        rows = []
        for k in range(r.randint(4, 14)):
            st = r.choice(["S1", "S2"])
            for prod in r.sample(["milk", "Bread", "tea", " eggs", "rice", "Milk "], r.randint(1, 4)):
                rows += [[f"r{k}", st, prod]] * r.choice([1, 1, 2])
        t.append({"lines_df": df(S, rows)})
    return t
