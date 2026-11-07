from kursad import inputs, SRC

ID = 'k21'
NAME = 'Order status counts'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 8
ORDERED = False
TAGS = ['groupBy', 'agrégation', 'banque DE']
SOURCE = SRC + " · Q21"
IO = [("input", "DataFrame orders")]
DESC = '<p>Create a DataFrame with one row for each distinct <code>status</code> value in <code>orders</code>, including null statuses. Return the status and the number of order rows in that group as <code>count</code>. Keep the aggregation distributed and do not require a particular output order.</p><ul><li>Include every order occurrence even when other fields are null.</li><li>Keep null statuses together as a group rather than excluding them or labelling them with replacement text.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with <code>status</code> and integer <code>count</code>, one row per distinct status including null when present. Counts total the input record count; row order is unspecified.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    result = orders.groupBy('status').count()\n    return result\n"


def tests():
    return inputs(['orders'], ID)
