from kursad import inputs, SRC

ID = 'k29'
NAME = 'Conditional counts'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 8
ORDERED = False
TAGS = ['groupBy', 'agrégation', 'banque DE']
SOURCE = SRC + " · Q29"
IO = [("input", "DataFrame orders")]
DESC = "<p>Count completed and cancelled orders separately for every customer key represented in <code>orders</code>. Return <code>customer_id</code>, <code>completed</code>, and <code>cancelled</code>, matching those status strings exactly. Include a null customer-key group when present and report zero for either status absent from a customer's orders.</p><ul><li>Customers represented only by other statuses must remain with zero in both counts.</li><li>Count order occurrences within the distributed customer groups, including the null-key group.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with <code>customer_id</code>, <code>completed</code>, and <code>cancelled</code>, one row per observed customer key. The two numeric fields are status-specific record counts, with zero for an absent status.</p><h4>Example</h4>{{EXAMPLE}}"
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    result = orders.groupBy('customer_id').agg(F.sum(F.when(F.col('status')=='completed',1).otherwise(0)).alias('completed'),F.sum(F.when(F.col('status')=='cancelled',1).otherwise(0)).alias('cancelled'))\n    return result\n"


def tests():
    return inputs(['orders'], ID)
