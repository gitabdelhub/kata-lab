from kursad import inputs, SRC

ID = 'k27'
NAME = 'Product units'
LANG = "pyspark"
PARAMS = ['spark', 'order_items']
MINUTES = 8
ORDERED = False
TAGS = ['groupBy', 'agrégation', 'banque DE']
SOURCE = SRC + " · Q27"
IO = [("input", "DataFrame order_items")]
DESC = '<p>Calculate total ordered quantity per product in <code>order_items</code>. Return one row per <code>product_id</code> with the summed <code>quantity</code> as <code>units</code>. Count units rather than item rows and retain a null product-key group if present.</p><ul><li>Use quantities, not item-record counts or prices.</li><li>Aggregate items by product in the distributed dataset without discarding the null-key group.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>order_items</code>: <code>item_id</code>, <code>order_id</code>, <code>product_id</code>, <code>quantity</code>, <code>unit_price</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with <code>product_id</code> and <code>units</code>, one row per observed product key including null. <code>units</code> sums non-null quantities and is null when a group has none.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, order_items: DataFrame) -> DataFrame:\n    # write your code here\n    return order_items\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, order_items):\n    result = order_items.groupBy('product_id').agg(F.sum('quantity').alias('units'))\n    return result\n"


def tests():
    return inputs(['order_items'], ID)
