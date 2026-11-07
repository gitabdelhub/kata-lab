from kursad import inputs, SRC

ID = 'k04'
NAME = 'High value'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 6
ORDERED = False
TAGS = ['bases DataFrame', 'select', 'filtre', 'banque DE']
SOURCE = SRC + " · Q04"
IO = [("input", "DataFrame orders")]
DESC = '<p>Filter <code>orders</code> to records whose <code>amount</code> is at least 300, including those exactly at the threshold. Return all original columns for the qualifying orders. Missing amounts do not qualify.</p><ul><li>Include 300 and exclude null amounts; do not normalize or round amounts before comparing.</li><li>Retain all qualifying occurrences in the distributed result.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame of complete orders with <code>amount</code> at least 300. All original fields and their types remain, and no output sorting is required.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    result = orders.filter(F.col('amount') >= 300)\n    return result\n"


def tests():
    return inputs(['orders'], ID)
