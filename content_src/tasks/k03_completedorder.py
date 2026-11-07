from kursad import inputs, SRC

ID = 'k03'
NAME = 'Completed orders'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 6
ORDERED = False
TAGS = ['bases DataFrame', 'select', 'filtre', 'banque DE']
SOURCE = SRC + " · Q03"
IO = [("input", "DataFrame orders")]
DESC = '<p>Return complete records from <code>orders</code> whose <code>status</code> is exactly <code>completed</code>. Retain every original column for qualifying orders and leave the source DataFrame unchanged. Orders in any other status should be excluded.</p><ul><li>Match the stored status exactly; null statuses do not qualify.</li><li>Filter the distributed orders without aggregating or deduplicating matching records.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame containing every completed-order occurrence and all original order columns. It retains the input schema; no matching orders yields an empty DataFrame with that schema.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    result = orders.filter(F.col('status') == 'completed')\n    return result\n"


def tests():
    return inputs(['orders'], ID)
