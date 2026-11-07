from kursad import inputs, SRC

ID = 'k71'
NAME = 'Idempotent union'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 10
ORDERED = False
TAGS = ['etl production', 'agrégation', 'banque DE']
SOURCE = SRC + " · Q71"
IO = [("input", "DataFrame orders")]
DESC = '<p>Create two overlapping batches from <code>orders</code>: records with <code>order_id</code> at most 100, and records with <code>order_id</code> at most 150. Combine the batches and retain one record per <code>order_id</code>, preserving all original order columns. The overlap must not produce duplicate order IDs in the final result.</p><ul><li>Define batches by order-ID thresholds, not physical row positions.</li><li>Combine records on the distributed dataset and deduplicate by order ID; no winner rule for conflicting versions is specified.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with all original order columns and one record per order ID present in either batch. The shared records from the two batches appear only once.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    a=orders.filter(F.col('order_id')<=100)\n    b=orders.filter(F.col('order_id')<=150)\n    result=a.unionByName(b).dropDuplicates(['order_id'])\n    return result\n"


def tests():
    return inputs(['orders'], ID)
