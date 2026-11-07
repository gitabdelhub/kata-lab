from kursad import inputs, SRC

ID = 'k41'
NAME = 'Latest order'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 12
ORDERED = False
TAGS = ['window', 'row_number', 'lag', 'banque DE']
SOURCE = SRC + " · Q41"
IO = [("input", "DataFrame orders")]
DESC = "<p>Return exactly one most recent row from <code>orders</code> for each <code>customer_id</code>. Choose the latest <code>order_date</code>, breaking equal-date ties with the largest <code>order_id</code>. Preserve the selected records' original columns and remove any temporary selection fields; the comparison order does not require a global result ordering.</p><ul><li>Select a complete record per customer, not independent maxima from different orders.</li><li>Resolve selection on distributed data and omit temporary rank fields; no global output sort is required.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with the original order columns and exactly one latest order per customer key. The winning record has the greatest order date and then greatest order ID within that customer.</p><h4>Example</h4>{{EXAMPLE}}"
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    w=Window.partitionBy('customer_id').orderBy(F.desc('order_date'),F.desc('order_id'))\n    result=orders.withColumn('rn',F.row_number().over(w)).filter('rn = 1').drop('rn')\n    return result\n"


def tests():
    return inputs(['orders'], ID)
