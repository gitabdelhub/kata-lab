from kursad import inputs, SRC

ID = 'k43'
NAME = 'Previous amount'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 12
ORDERED = False
TAGS = ['window', 'row_number', 'lag', 'banque DE']
SOURCE = SRC + " · Q43"
IO = [("input", "DataFrame orders")]
DESC = "<p>Add <code>previous_amount</code> to each record in <code>orders</code>, using the preceding order for the same customer. Sequence each customer's orders by <code>order_date</code> ascending, then <code>order_id</code> ascending. Preserve all original rows and columns and use null for a customer's first previous amount.</p><ul><li>Use the immediately preceding record, even if its amount is null; do not search for an earlier non-null amount.</li><li>Evaluate customer histories on the distributed DataFrame without mixing customers.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with all original order columns plus <code>previous_amount</code>. Each customer's first order has null in the added field; other rows carry their predecessor's amount. No global result ordering is required.</p><h4>Example</h4>{{EXAMPLE}}"
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    w=Window.partitionBy('customer_id').orderBy('order_date','order_id')\n    result=orders.withColumn('previous_amount',F.lag('amount').over(w))\n    return result\n"


def tests():
    return inputs(['orders'], ID)
