from kursad import inputs, SRC

ID = 'k10'
NAME = 'Conditional band'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 6
ORDERED = False
TAGS = ['bases DataFrame', 'select', 'filtre', 'banque DE']
SOURCE = SRC + " · Q10"
IO = [("input", "DataFrame orders")]
DESC = '<p>Classify each record in <code>orders</code> with a new <code>value_band</code> column. Use <code>high</code> when <code>amount</code> is at least 250 and <code>standard</code> otherwise, including null amounts. Retain every original row and column without changing the amount.</p><ul><li>Use exactly <code>high</code> and <code>standard</code> as the two labels.</li><li>Classify each distributed order independently; a null amount receives <code>standard</code>, not a null label.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with all order columns plus string <code>value_band</code>. Amounts of 250 or more are <code>high</code>; all other amounts, including nulls, are <code>standard</code>. Record count is unchanged.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    result = orders.withColumn('value_band',F.when(F.col('amount')>=250,'high').otherwise('standard'))\n    return result\n"


def tests():
    return inputs(['orders'], ID)
