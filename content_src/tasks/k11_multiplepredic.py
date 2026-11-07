from kursad import inputs, SRC

ID = 'k11'
NAME = 'Multiple predicates'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 7
ORDERED = False
TAGS = ['filtre', 'tri', 'expression', 'banque DE']
SOURCE = SRC + " · Q11"
IO = [("input", "DataFrame orders")]
DESC = '<p>Return rows of <code>orders</code> whose <code>status</code> is exactly <code>completed</code> and whose <code>amount</code> is at least 200. Both conditions must be satisfied. Keep all original fields for qualifying orders and exclude rows with null amounts.</p><ul><li>The same order must satisfy the exact status match and the inclusive amount threshold.</li><li>Keep matching records distributed, including duplicates, without changing original fields.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame of complete completed-order records whose non-null amount is at least 200. No other statuses or null amounts appear.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    result = orders.filter((F.col('status')=='completed') & (F.col('amount')>=200))\n    return result\n"


def tests():
    return inputs(['orders'], ID)
