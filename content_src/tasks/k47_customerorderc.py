from kursad import inputs, SRC

ID = 'k47'
NAME = 'Customer order count'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 12
ORDERED = False
TAGS = ['window', 'row_number', 'lag', 'banque DE']
SOURCE = SRC + " · Q47"
IO = [("input", "DataFrame orders")]
DESC = "<p>Add <code>customer_order_count</code> to each record in <code>orders</code>, showing the total number of order rows sharing its <code>customer_id</code>. Count every status and treat null customer IDs as one group. Preserve every original order row and column rather than returning one row per customer.</p><ul><li>Count all record occurrences, not distinct order IDs, and include every status.</li><li>Annotate the distributed orders rather than reducing each customer to one output row.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with all original order columns plus integer <code>customer_order_count</code>. Every row for a given customer key carries that group's total count, including the null-key group.</p><h4>Example</h4>{{EXAMPLE}}"
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    w=Window.partitionBy('customer_id')\n    result=orders.withColumn('customer_order_count',F.count('*').over(w))\n    return result\n"


def tests():
    return inputs(['orders'], ID)
