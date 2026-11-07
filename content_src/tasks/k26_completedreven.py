from kursad import inputs, SRC

ID = 'k26'
NAME = 'Completed revenue'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 8
ORDERED = False
TAGS = ['groupBy', 'agrégation', 'banque DE']
SOURCE = SRC + " · Q26"
IO = [("input", "DataFrame orders")]
DESC = '<p>Calculate revenue from <code>orders</code> whose <code>status</code> is exactly <code>completed</code>. Return <code>customer_id</code> and <code>completed_revenue</code>, summing amounts separately for each customer key. Include only keys represented by qualifying orders, including a null customer key if present.</p><ul><li>Match <code>completed</code> exactly and omit keys with no qualifying orders.</li><li>Sum non-null amounts in each distributed customer group rather than replacing null amounts with zero.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with <code>customer_id</code> and <code>completed_revenue</code>, one row per key present among completed orders, including null keys. A qualifying group containing only null amounts has null revenue.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    result = orders.filter(F.col('status')=='completed').groupBy('customer_id').agg(F.sum('amount').alias('completed_revenue'))\n    return result\n"


def tests():
    return inputs(['orders'], ID)
