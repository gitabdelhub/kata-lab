from kursad import inputs, SRC

ID = 'k39'
NAME = 'Semi join'
LANG = "pyspark"
PARAMS = ['spark', 'customers', 'orders']
MINUTES = 10
ORDERED = False
TAGS = ['jointure', 'join', 'banque DE']
SOURCE = SRC + " · Q39"
IO = [("input", "DataFrame customers, orders")]
DESC = '<p>Use a semi join to return customers in <code>customers</code> who have at least one matching order in <code>orders</code> by <code>customer_id</code>. Return only the original customer columns, without multiplying customer rows for multiple orders. Null keys should not match each other.</p><ul><li>Use the semi-join technique required by the Task; order multiplicity must not multiply customer records.</li><li>Match non-null keys on distributed data without copying order columns into the result.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>customers</code>: <code>customer_id</code>, <code>name</code>, <code>email</code>, <code>segment</code>, <code>country</code>, <code>signup_date</code></li><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame containing original customer records that have at least one matching order. Each qualifying input occurrence appears once, with no order fields; null keys do not qualify.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, customers: DataFrame, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return customers\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, customers, orders):\n    result = customers.join(orders.select('customer_id').distinct(),'customer_id','left_semi')\n    return result\n"


def tests():
    return inputs(['customers', 'orders'], ID)
