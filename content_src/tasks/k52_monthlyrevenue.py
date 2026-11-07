from kursad import inputs, SRC

ID = 'k52'
NAME = 'Monthly revenue'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 12
ORDERED = False
TAGS = ['dates', 'timestamps', 'événements', 'banque DE']
SOURCE = SRC + " · Q52"
IO = [("input", "DataFrame orders")]
DESC = '<p>Summarize total <code>amount</code> in <code>orders</code> by calendar month of <code>order_date</code>, including every order status. Return <code>month</code>, represented by the timestamp at the start of the month, and <code>revenue</code>. Keep different year-month combinations separate.</p><ul><li>Use year and month together and include every order status.</li><li>Compute monthly totals on the distributed data without replacing the original source dates.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with timestamp <code>month</code> and numeric <code>revenue</code>, one row per represented calendar month. <code>month</code> identifies the start of that month, and revenue sums its order amounts.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    result = orders.withColumn('month',F.date_trunc('month',F.to_timestamp('order_date'))).groupBy('month').agg(F.sum('amount').alias('revenue'))\n    return result\n"


def tests():
    return inputs(['orders'], ID)
