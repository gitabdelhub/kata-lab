from kursad import inputs, SRC

ID = 'k07'
NAME = 'Distinct statuses'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 6
ORDERED = False
TAGS = ['bases DataFrame', 'select', 'filtre', 'banque DE']
SOURCE = SRC + " · Q07"
IO = [("input", "DataFrame orders")]
DESC = '<p>Return a one-column DataFrame containing each distinct <code>status</code> value in <code>orders</code> once. Keep the column name <code>status</code> and include a single null row if any orders have a null status. Do not return other order fields.</p><ul><li>Do not normalize status text before identifying distinct values.</li><li>Keep the distinct calculation distributed and retain one null entry when null statuses exist.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with only <code>status</code>, one row per distinct input status including null when present. There is no count column or required ordering.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    result = orders.select('status').distinct()\n    return result\n"


def tests():
    return inputs(['orders'], ID)
