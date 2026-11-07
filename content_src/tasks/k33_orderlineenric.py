from kursad import inputs, SRC

ID = 'k33'
NAME = 'Order line enrichment'
LANG = "pyspark"
PARAMS = ['spark', 'order_items', 'orders']
MINUTES = 10
ORDERED = False
TAGS = ['jointure', 'join', 'banque DE']
SOURCE = SRC + " · Q33"
IO = [("input", "DataFrame order_items, orders")]
DESC = '<p>Enrich <code>order_items</code> with <code>status</code> and <code>order_date</code> from <code>orders</code>, matching on <code>order_id</code>. Retain every item row and all original item columns. Leave the added fields null for items without a matching order.</p><ul><li>Match by order ID and add only <code>status</code> and <code>order_date</code>.</li><li>Keep unmatched and duplicate item occurrences in the distributed enrichment result.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>order_items</code>: <code>item_id</code>, <code>order_id</code>, <code>product_id</code>, <code>quantity</code>, <code>unit_price</code></li><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with all original item columns plus <code>status</code> and <code>order_date</code>. Each item is enriched from its matching order; unmatched items remain with null added fields.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, order_items: DataFrame, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return order_items\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, order_items, orders):\n    result = order_items.join(orders.select('order_id','status','order_date'),'order_id','left')\n    return result\n"


def tests():
    return inputs(['order_items', 'orders'], ID)
