from kursad import inputs, SRC

ID = 'k31'
NAME = 'Enrich orders'
LANG = "pyspark"
PARAMS = ['spark', 'orders', 'customers']
MINUTES = 10
ORDERED = False
TAGS = ['jointure', 'join', 'banque DE']
SOURCE = SRC + " · Q31"
IO = [("input", "DataFrame orders, customers")]
DESC = '<p>Enrich every row of <code>orders</code> with <code>name</code> and <code>segment</code> from <code>customers</code>, matching on <code>customer_id</code>. Return all original order columns and the two added fields. Keep unmatched orders with null customer fields; null keys should not match each other.</p><ul><li>Use ordinary key equality so null keys do not match.</li><li>Keep the enrichment distributed and add only the requested customer fields.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li><li><code>customers</code>: <code>customer_id</code>, <code>name</code>, <code>email</code>, <code>segment</code>, <code>country</code>, <code>signup_date</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame containing all original order columns plus <code>name</code> and <code>segment</code>. Matching orders carry customer values; unmatched orders, including null-key orders, remain with null added fields.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame, customers: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders, customers):\n    result = orders.join(customers.select('customer_id','name','segment'),'customer_id','left')\n    return result\n"


def tests():
    return inputs(['orders', 'customers'], ID)
