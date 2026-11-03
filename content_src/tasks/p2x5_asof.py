from kit import df, rng

ID = "p2x5"
NAME = "Price at Order Time"
LANG = "pyspark"
PARAMS = ["spark", "orders_df", "prices_df"]
MINUTES = 22
TAGS = ["jointure as-of", "jointure avec inégalité", "row_number", "left join"]
SUMMARY_FR = "Pour chaque ligne de commande, trouver le prix du produit en vigueur au moment de la commande (le dernier changement de prix avant ou au même instant), puis calculer le montant. Sans prix connu : montant NULL, mais la ligne reste."
HINTS = ["Jointure LEFT sur sku ET valid_from <= ordered_at : chaque commande récupère tous les prix passés.",
         "Puis Window.partitionBy('order_id', 'line_no').orderBy(valid_from desc) et row_number() == 1 pour garder le plus récent.",
         "Le partitionBy doit identifier UNE ligne de commande : une commande a plusieurs lignes."]
DESC = """
<p>A shop changes its prices often. To audit old invoices, you must find the price that applied when each order line was created.</p>
<p><code>orders_df</code> has one row per order line: <code>order_id</code> (string), <code>line_no</code> (integer), <code>sku</code> (string), <code>qty</code> (integer) and <code>ordered_at</code> (timestamp). The pair <code>(order_id, line_no)</code> is unique.</p>
<p><code>prices_df</code> is the history of price changes: <code>sku</code> (string), <code>price</code> (double) and <code>valid_from</code> (timestamp). A price applies from <code>valid_from</code> <b>included</b> until the next change of the same SKU. <code>(sku, valid_from)</code> is unique.</p>
<p>Your task is to return, for every order line, the columns <code>order_id</code>, <code>line_no</code>, <code>sku</code>, <code>unit_price</code> (the price that applied at <code>ordered_at</code>) and <code>amount</code> (<code>qty * unit_price</code>, rounded to 2 decimals). If no price applied yet (the order is before the first price of the SKU, or the SKU has no price), <code>unit_price</code> and <code>amount</code> are <code>null</code>, but the line is still returned. Sort by <code>order_id</code>, then <code>line_no</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F
from pyspark.sql.window import Window


def solve(spark: SparkSession, orders_df: DataFrame, prices_df: DataFrame) -> DataFrame:
    # write your code here
    return orders_df
"""
SOLUTION = """
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def solve(spark, orders_df, prices_df):
    p = prices_df.select(F.col("sku").alias("p_sku"), "price", "valid_from")
    j = orders_df.join(p, (orders_df.sku == p.p_sku) & (p.valid_from <= orders_df.ordered_at), "left")
    w = Window.partitionBy("order_id", "line_no").orderBy(F.col("valid_from").desc_nulls_last())
    j = j.withColumn("rn", F.row_number().over(w)).filter("rn = 1")
    return (j.select("order_id", "line_no", "sku", F.col("price").alias("unit_price"),
                     F.round(F.col("qty") * F.col("price"), 2).alias("amount"))
            .orderBy("order_id", "line_no"))
"""
MUTANTS = [
    """
from pyspark.sql import functions as F
from pyspark.sql.window import Window
def solve(spark, orders_df, prices_df):
    p = prices_df.select(F.col("sku").alias("p_sku"), "price", "valid_from")
    j = orders_df.join(p, (orders_df.sku == p.p_sku) & (p.valid_from <= orders_df.ordered_at), "inner")
    w = Window.partitionBy("order_id", "line_no").orderBy(F.col("valid_from").desc())
    j = j.withColumn("rn", F.row_number().over(w)).filter("rn = 1")
    return j.select("order_id", "line_no", "sku", F.col("price").alias("unit_price"), F.round(F.col("qty") * F.col("price"), 2).alias("amount")).orderBy("order_id", "line_no")
""",
    """
from pyspark.sql import functions as F
from pyspark.sql.window import Window
def solve(spark, orders_df, prices_df):
    p = prices_df.select(F.col("sku").alias("p_sku"), "price", "valid_from")
    j = orders_df.join(p, (orders_df.sku == p.p_sku) & (p.valid_from < orders_df.ordered_at), "left")
    w = Window.partitionBy("order_id", "line_no").orderBy(F.col("valid_from").desc())
    j = j.withColumn("rn", F.row_number().over(w)).filter("rn = 1")
    return j.select("order_id", "line_no", "sku", F.col("price").alias("unit_price"), F.round(F.col("qty") * F.col("price"), 2).alias("amount")).orderBy("order_id", "line_no")
""",
    """
from pyspark.sql import functions as F
from pyspark.sql.window import Window
def solve(spark, orders_df, prices_df):
    p = prices_df.select(F.col("sku").alias("p_sku"), "price", "valid_from")
    j = orders_df.join(p, (orders_df.sku == p.p_sku) & (p.valid_from <= orders_df.ordered_at), "left")
    w = Window.partitionBy("order_id").orderBy(F.col("valid_from").desc())
    j = j.withColumn("rn", F.row_number().over(w)).filter("rn = 1")
    return j.select("order_id", "line_no", "sku", F.col("price").alias("unit_price"), F.round(F.col("qty") * F.col("price"), 2).alias("amount")).orderBy("order_id", "line_no")
""",
]
O = "order_id string, line_no int, sku string, qty int, ordered_at timestamp"
P = "sku string, price double, valid_from timestamp"


def tests():
    t = [{"orders_df": df(O, [["o1", 1, "A", 2, "2026-03-01 10:00:00"], ["o1", 2, "B", 1, "2026-03-01 10:00:00"], ["o2", 1, "A", 3, "2026-03-05 09:00:00"],
                              ["o3", 1, "C", 1, "2026-03-05 09:00:00"], ["o4", 1, "A", 1, "2026-02-01 00:00:00"]]),
          "prices_df": df(P, [["A", 10.0, "2026-02-15 00:00:00"], ["A", 12.5, "2026-03-05 09:00:00"], ["B", 99.99, "2026-01-01 00:00:00"]])},
         {"orders_df": df(O, [["k", 1, "Z", 4, "2026-06-01 12:00:00"], ["k", 2, "Z", 1, "2026-06-03 12:00:00"]]),
          "prices_df": df(P, [["Z", 1.1, "2026-06-02 00:00:00"], ["Z", 0.5, "2026-05-01 00:00:00"], ["Y", 3.0, "2026-01-01 00:00:00"]])}]
    r = rng(305)
    for _ in range(6):
        prices, seen = [], set()
        for _ in range(r.randint(1, 8)):
            k = (r.choice("ABC"), r.randint(1, 9))
            if k in seen:
                continue
            seen.add(k)
            prices.append([k[0], round(r.uniform(1, 50), 2), f"2026-03-0{k[1]} 00:00:00"])
        orders = [[f"o{i // 2}", i % 2 + 1, r.choice("ABCD"), r.randint(1, 5), f"2026-03-0{r.randint(1, 9)} {r.choice(['00', '12'])}:00:00"] for i in range(r.randint(2, 10))]
        t.append({"orders_df": df(O, orders), "prices_df": df(P, prices)})
    return t
