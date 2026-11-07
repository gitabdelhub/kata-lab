from kursad import inputs, SRC

ID = 'k28'
NAME = 'Line sales'
LANG = "pyspark"
PARAMS = ['spark', 'order_items']
MINUTES = 8
ORDERED = False
TAGS = ['groupBy', 'agrégation', 'banque DE']
SOURCE = SRC + " · Q28"
IO = [("input", "DataFrame order_items")]
DESC = "<p>Calculate sales per product from <code>order_items</code>, valuing each item as <code>quantity</code> multiplied by its sale-time <code>unit_price</code>. Return one row per <code>product_id</code> with the sum as <code>sales</code>. The result should contain product-level totals rather than individual item records.</p><ul><li>Use the item's sale-time <code>unit_price</code>, not a catalog price.</li><li>Calculate item values and product totals on the distributed records, retaining a null product-key group when present.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>order_items</code>: <code>item_id</code>, <code>order_id</code>, <code>product_id</code>, <code>quantity</code>, <code>unit_price</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with <code>product_id</code> and <code>sales</code>, one row per observed product key. Sales sum non-null item values; no individual item columns or intermediate line totals are returned.</p><h4>Example</h4>{{EXAMPLE}}"
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, order_items: DataFrame) -> DataFrame:\n    # write your code here\n    return order_items\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, order_items):\n    result = order_items.withColumn('line_total',F.col('quantity')*F.col('unit_price')).groupBy('product_id').agg(F.sum('line_total').alias('sales'))\n    return result\n"


def tests():
    return inputs(['order_items'], ID)
