from kursad import inputs, SRC

ID = 'k20'
NAME = 'SQL expression'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 7
ORDERED = False
TAGS = ['filtre', 'tri', 'expression', 'banque DE']
SOURCE = SRC + " · Q20"
IO = [("input", "DataFrame orders")]
DESC = "<p>Using the <code>orders</code> DataFrame, add a column named <code>gross_amount</code> containing each order's amount increased by 5%. Preserve all existing rows and columns, including the original <code>amount</code> values. Use PySpark SQL expressions through <code>expr</code> for the calculation.</p><ul><li>This is a row-level calculation: do not filter, duplicate, or aggregate orders.</li><li>Keep the calculation distributed and use the SQL expression technique required by the Task; do not transfer the complete <code>orders</code> dataset to the driver.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame containing every original <code>orders</code> column plus <code>gross_amount</code>. Each <code>gross_amount</code> is the corresponding <code>amount</code> increased by 5%. The output has the same number of records as <code>orders</code>, and the original <code>amount</code> values remain unchanged.</p><h4>Example</h4>{{EXAMPLE}}"
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    result = orders.withColumn('gross_amount',F.expr('amount * 1.05'))\n    return result\n"


def tests():
    return inputs(['orders'], ID)
