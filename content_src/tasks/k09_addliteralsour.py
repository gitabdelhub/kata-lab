from kursad import inputs, SRC

ID = 'k09'
NAME = 'Add literal source'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 6
ORDERED = False
TAGS = ['bases DataFrame', 'select', 'filtre', 'banque DE']
SOURCE = SRC + " · Q09"
IO = [("input", "DataFrame orders")]
DESC = '<p>Add a string column named <code>source_system</code> to <code>orders</code> with the value <code>ecommerce</code> on every row. Return all original records and columns together with the added source label, leaving the original order values unchanged.</p><ul><li>Apply the same string label regardless of order status or amount.</li><li>Add the field in the distributed DataFrame without replacing any existing order values.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with every original order column plus string <code>source_system</code>, set to <code>ecommerce</code> on every row. All input record occurrences remain.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    result = orders.withColumn('source_system',F.lit('ecommerce'))\n    return result\n"


def tests():
    return inputs(['orders'], ID)
