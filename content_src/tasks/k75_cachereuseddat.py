from kursad import inputs, SRC

ID = 'k75'
NAME = 'Cache reused data'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 10
ORDERED = False
TAGS = ['etl production', 'agrégation', 'banque DE']
SOURCE = SRC + " · Q75"
IO = [("input", "DataFrame orders")]
DESC = '<p>Cache <code>orders</code> for reuse and trigger an action that materializes the cache. From the cached data, return complete records whose <code>status</code> is exactly <code>completed</code>. Preserve all original order columns and leave the cached input available for subsequent work.</p><ul><li>Materialize the cache with an action; merely declaring caching is insufficient.</li><li>Filter the cached distributed input and leave it available for reuse rather than collecting all orders or releasing the cache.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame of complete completed-order records, plus a materialized cached version of the original orders available for later work. The result retains all original order columns.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    cached=orders.cache()\n    cached.count()\n    result=cached.filter(F.col('status')=='completed')\n    return result\n"


def tests():
    return inputs(['orders'], ID)
