from kursad import inputs, SRC

ID = 'k23'
NAME = 'Customer spend'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 8
ORDERED = False
TAGS = ['groupBy', 'agrégation', 'banque DE']
SOURCE = SRC + " · Q23"
IO = [("input", "DataFrame orders")]
DESC = '<p>Calculate total order spend for each <code>customer_id</code> in <code>orders</code>, including every status. Return <code>customer_id</code> and <code>total_spend</code>, with one row per customer key and a null-key group when present. Sum non-null amounts; a group with only null amounts has null spend.</p><ul><li>Do not restrict spend to completed orders or require a customer-dimension match.</li><li>Retain the null customer-key group and calculate totals without bringing the full order dataset to the driver.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with <code>customer_id</code> and <code>total_spend</code>, one row per observed customer key, including null. Totals cover all statuses; a group with no non-null amounts has null spend.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    result = orders.groupBy('customer_id').agg(F.sum('amount').alias('total_spend'))\n    return result\n"


def tests():
    return inputs(['orders'], ID)
