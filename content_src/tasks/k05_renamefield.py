from kursad import inputs, SRC

ID = 'k05'
NAME = 'Rename field'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 6
ORDERED = False
TAGS = ['bases DataFrame', 'select', 'filtre', 'banque DE']
SOURCE = SRC + " · Q05"
IO = [("input", "DataFrame orders")]
DESC = "<p>Return a version of <code>orders</code> with the <code>amount</code> column renamed to <code>order_amount</code>. Keep every record, retain all other columns, and preserve the renamed column's values and data type. Leave the original DataFrame unchanged.</p><ul><li>Rename rather than copy the field: the result should not also contain <code>amount</code>.</li><li>Keep the rename as a distributed transformation without changing any field values.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, and <code>order_amount</code>. Record count and field types are unchanged; only the amount field's name differs.</p><h4>Example</h4>{{EXAMPLE}}"
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    result = orders.withColumnRenamed('amount','order_amount')\n    return result\n"


def tests():
    return inputs(['orders'], ID)
