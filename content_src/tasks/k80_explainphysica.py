from kursad import inputs, SRC

ID = 'k80'
NAME = 'Explain physical plan'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 10
ORDERED = False
TAGS = ['etl production', 'agrégation', 'banque DE']
SOURCE = SRC + " · Q80"
IO = [("input", "DataFrame orders")]
DESC = "<p>Build a customer-level revenue summary from <code>orders</code>, including only rows whose <code>status</code> is <code>completed</code>. Return <code>customer_id</code> and summed <code>amount</code> as <code>revenue</code>. Print the query's physical execution plan as well as the result so its distributed execution can be inspected.</p><ul><li>Match <code>completed</code> exactly and retain a customer-key group only when qualifying orders exist.</li><li>Inspect the distributed query plan in addition to producing revenue data; a plan alone is not the result.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with <code>customer_id</code> and <code>revenue</code>, one row per key represented by completed orders, together with a printed physical execution plan and a display of the result. Revenue sums qualifying order amounts.</p><h4>Example</h4>{{EXAMPLE}}"
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    result=orders.filter(F.col('status')=='completed').groupBy('customer_id').agg(F.sum('amount').alias('revenue'))\n    result.explain(mode='formatted')\n    return result\n"


def tests():
    return inputs(['orders'], ID)
