from kursad import inputs, SRC

ID = 'k37'
NAME = 'Orphan orders'
LANG = "pyspark"
PARAMS = ['spark', 'orders', 'customers']
MINUTES = 10
ORDERED = False
TAGS = ['jointure', 'join', 'banque DE']
SOURCE = SRC + " · Q37"
IO = [("input", "DataFrame orders, customers")]
DESC = '<p>Return records in <code>orders</code> whose <code>customer_id</code> does not match any customer in <code>customers</code>. Treat orders with a null customer ID as orphans as well. Preserve all original order columns and do not add customer fields to the result.</p><ul><li>Treat null order customer IDs as unmatched even if a null key exists in <code>customers</code>.</li><li>Keep each orphan occurrence in the distributed result rather than returning only distinct keys.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li><li><code>customers</code>: <code>customer_id</code>, <code>name</code>, <code>email</code>, <code>segment</code>, <code>country</code>, <code>signup_date</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame of complete orphan orders with all original order columns. It includes null-key orders and non-null keys absent from the customer lookup.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame, customers: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders, customers):\n    result = orders.join(customers.select('customer_id'),'customer_id','left_anti')\n    return result\n"


def tests():
    return inputs(['orders', 'customers'], ID)
