from kursad import inputs, SRC

ID = 'k40'
NAME = 'Join validation'
LANG = "pyspark"
PARAMS = ['spark', 'orders', 'customers']
MINUTES = 10
ORDERED = False
TAGS = ['jointure', 'join', 'banque DE']
SOURCE = SRC + " · Q40"
IO = [("input", "DataFrame orders, customers")]
DESC = '<p>Compare the row count of <code>orders</code> before and after enrichment with customer <code>name</code> from <code>customers</code> on <code>customer_id</code>. The join must retain unmatched orders. Return a one-row DataFrame with <code>before</code> and <code>after</code>, using the actual joined row count rather than assuming it is unchanged.</p><ul><li>Measure the actual joined result so duplicate customer matches, if present, are reflected in <code>after</code>.</li><li>Execute counting on distributed data; only the two scalar counts are needed to construct the report.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li><li><code>customers</code>: <code>customer_id</code>, <code>name</code>, <code>email</code>, <code>segment</code>, <code>country</code>, <code>signup_date</code></li></ul><p><b>Expected output:</b> A one-row PySpark DataFrame with integer <code>before</code> and <code>after</code> fields. They contain the original and joined order counts respectively; equality is observed, not assumed.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame, customers: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders, customers):\n    joined=orders.join(customers.select('customer_id','name'),'customer_id','left')\n    result=spark.createDataFrame([(orders.count(),joined.count())],['before','after'])\n    return result\n"


def tests():
    return inputs(['orders', 'customers'], ID)
