from kursad import inputs, SRC

ID = 'k50'
NAME = 'Days since prior order'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 12
ORDERED = False
TAGS = ['window', 'row_number', 'lag', 'banque DE']
SOURCE = SRC + " · Q50"
IO = [("input", "DataFrame orders")]
DESC = "<p>Add <code>days_since_previous</code> to <code>orders</code>, measuring calendar days between the current order date and the preceding order date for the same customer. Sequence orders by <code>order_date</code> ascending, then <code>order_id</code> ascending. Keep all original rows and columns, with null gaps for first orders.</p><ul><li>Calculate calendar-date gaps within each customer's ordered history.</li><li>Retain same-day gaps as zero and first-order gaps as null; perform the calculation on distributed rows.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with all order columns plus integer <code>days_since_previous</code>, one row per order. Values describe the gap to the preceding order under the date and order-ID sequence, without requiring global output sorting.</p><h4>Example</h4>{{EXAMPLE}}"
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    w=Window.partitionBy('customer_id').orderBy('order_date','order_id')\n    result=orders.withColumn('days_since_previous',F.datediff(F.to_date('order_date'),F.to_date(F.lag('order_date').over(w))))\n    return result\n"


def tests():
    return inputs(['orders'], ID)
