from kursad import inputs, SRC

ID = 'k32'
NAME = 'Customer order counts'
LANG = "pyspark"
PARAMS = ['spark', 'customers', 'orders']
MINUTES = 10
ORDERED = False
TAGS = ['jointure', 'join', 'banque DE']
SOURCE = SRC + " · Q32"
IO = [("input", "DataFrame customers, orders")]
DESC = '<p>Attach an <code>order_count</code> to every record in <code>customers</code>, counting matching <code>orders</code> by <code>customer_id</code> across all statuses. Preserve all original customer columns and use zero where no order matches. Null customer keys should not match null order keys.</p><ul><li>Count order occurrences rather than distinct order IDs, across all statuses.</li><li>Keep null-key customers unmatched and perform the counts and enrichment on the distributed data.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>customers</code>: <code>customer_id</code>, <code>name</code>, <code>email</code>, <code>segment</code>, <code>country</code>, <code>signup_date</code></li><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame containing all customer columns plus <code>order_count</code>, one row per input customer record. Customers without matching non-null order keys receive zero.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, customers: DataFrame, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return customers\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, customers, orders):\n    counts=orders.groupBy('customer_id').count().withColumnRenamed('count','order_count')\n    result=customers.join(counts,'customer_id','left').fillna({'order_count':0})\n    return result\n"


def tests():
    return inputs(['customers', 'orders'], ID)
