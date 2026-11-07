from kursad import inputs, SRC

ID = 'k13'
NAME = 'Exclude cancelled'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 7
ORDERED = False
TAGS = ['filtre', 'tri', 'expression', 'banque DE']
SOURCE = SRC + " · Q13"
IO = [("input", "DataFrame orders")]
DESC = '<p>Return rows of <code>orders</code> whose <code>status</code> is not <code>cancelled</code>. Exclude null statuses as well as cancelled orders. Preserve all original columns for the remaining records; do not replace or normalize status values.</p><ul><li>Null status is not treated as an alternative status and must be excluded.</li><li>Filter without changing status text or collecting the complete order dataset.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with the original order columns containing only non-null statuses other than <code>cancelled</code>. All qualifying record occurrences remain.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    result = orders.filter(F.col('status') != 'cancelled')\n    return result\n"


def tests():
    return inputs(['orders'], ID)
