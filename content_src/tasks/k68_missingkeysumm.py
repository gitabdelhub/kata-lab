from kursad import inputs, SRC

ID = 'k68'
NAME = 'Missing key summary'
LANG = "pyspark"
PARAMS = ['spark', 'orders', 'customers']
MINUTES = 12
ORDERED = False
TAGS = ['nettoyage', 'null', 'doublon', 'cdc', 'json', 'banque DE']
SOURCE = SRC + " · Q68"
IO = [("input", "DataFrame orders, customers")]
DESC = '<p>Return a two-row DataFrame profiling missing keys in <code>orders</code> and <code>customers</code>. Use columns <code>dataset</code> and <code>null_key_rows</code>: the orders row should count null <code>order_id</code> values, and the customers row should count null <code>customer_id</code> values. Include both rows even when either count is zero.</p><ul><li>Inspect <code>order_id</code> for orders and <code>customer_id</code> for customers, not every nullable field.</li><li>Count on the distributed inputs; only the two scalar totals are needed for the report.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li><li><code>customers</code>: <code>customer_id</code>, <code>name</code>, <code>email</code>, <code>segment</code>, <code>country</code>, <code>signup_date</code></li></ul><p><b>Expected output:</b> A two-row PySpark DataFrame with <code>dataset</code> and integer <code>null_key_rows</code>. The dataset labels are <code>orders</code> and <code>customers</code>; both rows are present even when a count is zero.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame, customers: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders, customers):\n    result=spark.createDataFrame([('orders',orders.filter(F.col('order_id').isNull()).count()),('customers',customers.filter(F.col('customer_id').isNull()).count())],['dataset','null_key_rows'])\n    return result\n"


def tests():
    return inputs(['orders', 'customers'], ID)
