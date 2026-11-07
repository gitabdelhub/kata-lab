from kursad import inputs, SRC

ID = 'k36'
NAME = 'Left anti join'
LANG = "pyspark"
PARAMS = ['spark', 'customers', 'orders']
MINUTES = 10
ORDERED = False
TAGS = ['jointure', 'join', 'banque DE']
SOURCE = SRC + " · Q36"
IO = [("input", "DataFrame customers, orders")]
DESC = '<p>Use a left anti join to find customers in <code>customers</code> whose <code>customer_id</code> has no matching row in <code>orders</code>. Return all original customer columns. Orders in any status count as matches, but null keys should not match each other.</p><ul><li>Use the left anti join required by the Task with ordinary, not null-safe, key matching.</li><li>Check all orders regardless of status, without collecting their keys into a driver-side lookup.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>customers</code>: <code>customer_id</code>, <code>name</code>, <code>email</code>, <code>segment</code>, <code>country</code>, <code>signup_date</code></li><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame of complete customer records with no matching order key. Null-key customers are included; no order fields are added.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, customers: DataFrame, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return customers\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, customers, orders):\n    result = customers.join(orders.select('customer_id').distinct(),'customer_id','left_anti')\n    return result\n"


def tests():
    return inputs(['customers', 'orders'], ID)
