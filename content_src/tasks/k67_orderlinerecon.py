from kursad import inputs, SRC

ID = 'k67'
NAME = 'Order-line reconciliation'
LANG = "pyspark"
PARAMS = ['spark', 'orders', 'order_items']
MINUTES = 12
ORDERED = False
TAGS = ['nettoyage', 'null', 'doublon', 'cdc', 'json', 'banque DE']
SOURCE = SRC + " · Q67"
IO = [("input", "DataFrame orders, order_items")]
DESC = "<p>Reconcile <code>orders</code> with <code>order_items</code> by <code>order_id</code>, calculating each item's value from quantity and sale-time unit price. Return original order columns plus <code>line_total</code> where the absolute difference from <code>amount</code> exceeds 0.01. Use zero for absent item totals during comparison, but keep the returned <code>line_total</code> null for orders without items.</p><ul><li>Use sale-time item prices and compare unrounded totals against the strict 0.01 tolerance.</li><li>Compute the reconciliation on distributed data; zero-filling for comparison must not overwrite the returned null item total.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li><li><code>order_items</code>: <code>item_id</code>, <code>order_id</code>, <code>product_id</code>, <code>quantity</code>, <code>unit_price</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with all original order columns plus <code>line_total</code>, containing only mismatches greater than 0.01. An order without items is compared against zero but retains null <code>line_total</code> if returned.</p><h4>Example</h4>{{EXAMPLE}}"
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame, order_items: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders, order_items):\n    lines=order_items.groupBy('order_id').agg(F.sum(F.col('quantity')*F.col('unit_price')).alias('line_total'))\n    result=orders.join(lines,'order_id','left').filter(F.abs(F.col('amount')-F.coalesce(F.col('line_total'),F.lit(0)))>0.01)\n    return result\n"


def tests():
    return inputs(['orders', 'order_items'], ID)
