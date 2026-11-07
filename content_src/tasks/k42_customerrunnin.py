from kursad import inputs, SRC

ID = 'k42'
NAME = 'Customer running spend'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 12
ORDERED = False
TAGS = ['window', 'row_number', 'lag', 'banque DE']
SOURCE = SRC + " · Q42"
IO = [("input", "DataFrame orders")]
DESC = "<p>Add <code>running_spend</code> to every record in <code>orders</code>, totaling <code>amount</code> through the current order separately for each customer. Sequence each customer's history by <code>order_date</code> ascending and then <code>order_id</code> ascending. Preserve all original records and columns; do not collapse them into a customer-level summary.</p><ul><li>The cumulative range runs from the customer's first order through the current row, not through later rows sharing its date.</li><li>Keep the calculation distributed and use order ID to sequence same-date orders.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with all original order fields plus <code>running_spend</code>, one row per input order. The value is the customer's cumulative amount in the specified history sequence; a global result sort is not required.</p><h4>Example</h4>{{EXAMPLE}}"
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    w=Window.partitionBy('customer_id').orderBy('order_date','order_id').rowsBetween(Window.unboundedPreceding,Window.currentRow)\n    result=orders.withColumn('running_spend',F.sum('amount').over(w))\n    return result\n"


def tests():
    return inputs(['orders'], ID)
