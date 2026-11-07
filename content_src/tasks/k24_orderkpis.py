from kursad import inputs, SRC

ID = 'k24'
NAME = 'Order KPIs'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 8
ORDERED = False
TAGS = ['groupBy', 'agrégation', 'banque DE']
SOURCE = SRC + " · Q24"
IO = [("input", "DataFrame orders")]
DESC = '<p>Produce order statistics by <code>status</code> from <code>orders</code>, including a null-status group when present. Return <code>status</code>, row count as <code>n</code>, and amount statistics as <code>avg</code>, <code>min</code>, and <code>max</code>. Count every order row, but exclude null amounts from the amount statistics.</p><ul><li>An order with a null amount still contributes to <code>n</code>.</li><li>Calculate the amount statistics within each distributed status group, without filling missing amounts with zero.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with <code>status</code>, <code>n</code>, <code>avg</code>, <code>min</code>, and <code>max</code>, one row per observed status including null. <code>n</code> counts records; the other measures use non-null amounts and are null when none exist.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    result = orders.groupBy('status').agg(F.count('*').alias('n'),F.avg('amount').alias('avg'),F.min('amount').alias('min'),F.max('amount').alias('max'))\n    return result\n"


def tests():
    return inputs(['orders'], ID)
