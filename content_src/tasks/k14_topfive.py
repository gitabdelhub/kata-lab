from kursad import inputs, SRC

ID = 'k14'
NAME = 'Top five'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 7
ORDERED = True
TAGS = ['filtre', 'tri', 'expression', 'banque DE']
SOURCE = SRC + " · Q14"
IO = [("input", "DataFrame orders")]
DESC = '<p>Return the five highest-value records in <code>orders</code>, ranking by <code>amount</code> descending. Break equal-amount ties with the smaller <code>order_id</code> first, including at the cutoff. Preserve all original columns and return the selected records in that order.</p><ul><li>Apply the five-record limit after resolving amount ties by order ID.</li><li>Rank orders in the distributed dataset; return all available orders if fewer than five exist.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame of up to five complete order records, sorted by amount descending and order ID ascending. The tie-breaker also determines which records survive the cutoff.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    result = orders.orderBy(F.desc('amount'),F.asc('order_id')).limit(5)\n    return result\n"


def tests():
    return inputs(['orders'], ID)
