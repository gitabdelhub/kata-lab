from kursad import inputs, SRC

ID = 'k38'
NAME = 'Broadcast dimension'
LANG = "pyspark"
PARAMS = ['spark', 'orders', 'customers']
MINUTES = 10
ORDERED = False
TAGS = ['jointure', 'join', 'banque DE']
SOURCE = SRC + " · Q38"
IO = [("input", "DataFrame orders, customers")]
DESC = '<p>Enrich <code>orders</code> with customer <code>segment</code>, using a broadcast join for the <code>customers</code> dimension and matching on <code>customer_id</code>. Return all original order columns and the segment. Retain unmatched orders with a null segment.</p><ul><li>Broadcast the customer dimension as required by the Task, not the orders dataset.</li><li>Keep orders distributed and add only <code>segment</code>; unmatched and null-key orders remain.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li><li><code>customers</code>: <code>customer_id</code>, <code>name</code>, <code>email</code>, <code>segment</code>, <code>country</code>, <code>signup_date</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with all original order columns plus <code>segment</code>, populated from the broadcast customer lookup. Unmatched orders have null segment values.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame, customers: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders, customers):\n    result = orders.join(F.broadcast(customers.select('customer_id','segment')),'customer_id','left')\n    return result\n"


def tests():
    return inputs(['orders', 'customers'], ID)
