from kursad import inputs, SRC

ID = 'k30'
NAME = 'Approx distinct'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 8
ORDERED = False
TAGS = ['groupBy', 'agrégation', 'banque DE']
SOURCE = SRC + " · Q30"
IO = [("input", "DataFrame orders")]
DESC = '<p>Estimate the number of distinct non-null <code>customer_id</code> values for each <code>status</code> in <code>orders</code> using approximate distinct counting. Return <code>status</code> and <code>approx_customers</code>, including a null-status group when present. Do not substitute the number of order rows for the number of customers.</p><ul><li>Use the approximate distinct-counting technique required by the Task, excluding null customer IDs.</li><li>Repeated customer IDs within a status must not count as additional customers; keep the estimation distributed.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with <code>status</code> and integer estimate <code>approx_customers</code>, one row per observed status including null. Estimates describe distinct non-null customers and need not equal exact counts.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    result = orders.groupBy('status').agg(F.approx_count_distinct('customer_id').alias('approx_customers'))\n    return result\n"


def tests():
    return inputs(['orders'], ID)
