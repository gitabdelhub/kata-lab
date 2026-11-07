from kursad import inputs, SRC

ID = 'k35'
NAME = 'Category revenue'
LANG = "pyspark"
PARAMS = ['spark', 'order_items', 'products']
MINUTES = 10
ORDERED = False
TAGS = ['jointure', 'join', 'banque DE']
SOURCE = SRC + " · Q35"
IO = [("input", "DataFrame order_items, products")]
DESC = '<p>Calculate item revenue by product category using <code>order_items</code> and <code>products</code>. Match on <code>product_id</code> and value each item using its quantity and sale-time unit price. Return <code>category</code> and <code>revenue</code>, retaining unmatched items in the null-category group.</p><ul><li>Keep unmatched items in the category aggregation rather than dropping them.</li><li>Use item-level sale-time values and compute the grouped totals without collecting the complete sources.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>order_items</code>: <code>item_id</code>, <code>order_id</code>, <code>product_id</code>, <code>quantity</code>, <code>unit_price</code></li><li><code>products</code>: <code>product_id</code>, <code>sku</code>, <code>category</code>, <code>price</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with <code>category</code> and <code>revenue</code>, one row per represented category. Unmatched items and items with null category contribute to the null-category group; revenue sums item quantities multiplied by unit prices.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, order_items: DataFrame, products: DataFrame) -> DataFrame:\n    # write your code here\n    return order_items\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, order_items, products):\n    result = order_items.join(products.select('product_id','category'),'product_id','left').groupBy('category').agg(F.sum(F.col('quantity')*F.col('unit_price')).alias('revenue'))\n    return result\n"


def tests():
    return inputs(['order_items', 'products'], ID)
