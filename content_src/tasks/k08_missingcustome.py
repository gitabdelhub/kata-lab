from kursad import inputs, SRC

ID = 'k08'
NAME = 'Missing customer IDs'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 6
ORDERED = False
TAGS = ['bases DataFrame', 'select', 'filtre', 'banque DE']
SOURCE = SRC + " · Q08"
IO = [("input", "DataFrame orders")]
DESC = '<p>Count records in <code>orders</code> whose <code>customer_id</code> is null. Return a one-row DataFrame containing only <code>missing_customer_ids</code>. Count order rows rather than distinct orders or customers; zero is a valid count when no rows have a missing customer ID.</p><ul><li>Count null customer-ID occurrences, not nulls in other fields or distinct order IDs.</li><li>Calculate the metric on the distributed orders rather than transferring all records to the driver.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A one-row PySpark DataFrame with the single column <code>missing_customer_ids</code>, reporting the number of orders with null customer IDs. Count records rather than distinct identifiers.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    result = orders.agg(F.when(F.count('*') == 0, 0).otherwise(F.sum(F.when(F.col('customer_id').isNull(),1).otherwise(0))).alias('missing_customer_ids'))\n    return result\n"


def tests():
    return inputs(['orders'], ID)
