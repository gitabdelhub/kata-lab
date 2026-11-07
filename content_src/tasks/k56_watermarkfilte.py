from kursad import inputs, SRC

ID = 'k56'
NAME = 'Watermark filter'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 12
ORDERED = False
TAGS = ['dates', 'timestamps', 'événements', 'banque DE']
SOURCE = SRC + " · Q56"
IO = [("input", "DataFrame orders")]
DESC = "<p>Return complete records from <code>orders</code> whose <code>order_date</code> is strictly later than September 1, 2025. Compare calendar dates, exclude orders on the watermark date, and preserve all original order columns.</p><ul><li>Compare dates without altering the output's original <code>order_date</code> field.</li><li>Apply the strict boundary on distributed orders; null dates do not qualify.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame of complete orders with dates later than September 1, 2025. All original order fields remain, and records on the boundary date are excluded.</p><h4>Example</h4>{{EXAMPLE}}"
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    result = orders.filter(F.to_date('order_date')>F.lit('2025-09-01').cast('date'))\n    return result\n"


def tests():
    return inputs(['orders'], ID)
