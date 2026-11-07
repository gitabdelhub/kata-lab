from kursad import inputs, SRC

ID = 'k02'
NAME = 'Project columns'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 6
ORDERED = False
TAGS = ['bases DataFrame', 'select', 'filtre', 'banque DE']
SOURCE = SRC + " · Q02"
IO = [("input", "DataFrame orders")]
DESC = '<p>Create a DataFrame from <code>orders</code> containing only <code>order_id</code>, <code>customer_id</code>, and <code>amount</code>, in that column order. Retain every input record without changing the values or schema of the selected columns.</p><ul><li>Keep duplicate records and null values in the selected fields.</li><li>Perform the projection on the distributed input without changing selected column types.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with exactly <code>order_id</code>, <code>customer_id</code>, and <code>amount</code>, in that order. Its record count equals the input count, and selected values and field schemas are unchanged.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    result = orders.select('order_id','customer_id','amount')\n    return result\n"


def tests():
    return inputs(['orders'], ID)
