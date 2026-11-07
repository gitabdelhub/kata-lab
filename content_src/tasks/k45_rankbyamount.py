from kursad import inputs, SRC

ID = 'k45'
NAME = 'Rank by amount'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 12
ORDERED = False
TAGS = ['window', 'row_number', 'lag', 'banque DE']
SOURCE = SRC + " · Q45"
IO = [("input", "DataFrame orders")]
DESC = "<p>Assign a dense rank to orders by <code>amount</code> descending within each <code>status</code> in <code>orders</code>. Add the result as <code>dense_rank</code>, with equal amounts sharing a rank and no gaps between ranks. Preserve all original records and columns.</p><ul><li>Rank within status groups on the distributed orders.</li><li>Do not add order ID to the ranking key, since equal amounts must share the same dense rank.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame containing all order columns plus integer <code>dense_rank</code>, starting at 1 for each status's largest amount. Equal amounts share ranks and the next distinct amount receives the next rank without a gap.</p><h4>Example</h4>{{EXAMPLE}}"
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    w=Window.partitionBy('status').orderBy(F.desc('amount'))\n    result=orders.withColumn('dense_rank',F.dense_rank().over(w))\n    return result\n"


def tests():
    return inputs(['orders'], ID)
