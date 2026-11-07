from kursad import inputs, SRC

ID = 'k22'
NAME = 'Revenue by status'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 8
ORDERED = False
TAGS = ['groupBy', 'agrégation', 'banque DE']
SOURCE = SRC + " · Q22"
IO = [("input", "DataFrame orders")]
DESC = "<p>Summarize <code>orders</code> by <code>status</code>, returning one row per status with its total <code>amount</code> as <code>revenue</code>. Include a null-status group when present. Ignore null amounts in a group's total, returning null revenue if that group has no non-null amounts.</p><ul><li>Do not convert null amounts to zero before summing.</li><li>Aggregate across distributed records and retain a null-status group.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with <code>status</code> and <code>revenue</code>, one row per observed status. Revenue sums non-null amounts and remains null for a group containing only null amounts.</p><h4>Example</h4>{{EXAMPLE}}"
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    result = orders.groupBy('status').agg(F.sum('amount').alias('revenue'))\n    return result\n"


def tests():
    return inputs(['orders'], ID)
