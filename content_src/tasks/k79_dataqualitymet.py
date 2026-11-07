from kursad import inputs, SRC

ID = 'k79'
NAME = 'Data quality metrics'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 10
ORDERED = False
TAGS = ['etl production', 'agrégation', 'banque DE']
SOURCE = SRC + " · Q79"
IO = [("input", "DataFrame orders")]
DESC = '<p>Produce a one-row quality summary from <code>orders</code> with <code>rows</code>, <code>missing_customer_ids</code>, and <code>negative_amounts</code>. Count all order records, those with a null <code>customer_id</code>, and those with <code>amount</code> strictly below zero, respectively. Do not count null or zero amounts as negative.</p><ul><li>Count each metric independently: an order may contribute to both issue counts.</li><li>Keep the summary distributed and exclude null and zero amounts from the negative-amount metric.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A one-row PySpark DataFrame with <code>rows</code>, <code>missing_customer_ids</code>, and <code>negative_amounts</code>. These fields report the total order count, null-customer-ID count, and strictly negative-amount count respectively.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    result=orders.agg(F.count('*').alias('rows'),F.when(F.count('*') == 0, 0).otherwise(F.sum(F.when(F.col('customer_id').isNull(),1).otherwise(0))).alias('missing_customer_ids'),F.when(F.count('*') == 0, 0).otherwise(F.sum(F.when(F.col('amount')<0,1).otherwise(0))).alias('negative_amounts'))\n    return result\n"


def tests():
    return inputs(['orders'], ID)
