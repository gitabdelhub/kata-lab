from kursad import inputs, SRC

ID = 'k44'
NAME = 'Next order date'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 12
ORDERED = False
TAGS = ['window', 'row_number', 'lag', 'banque DE']
SOURCE = SRC + " · Q44"
IO = [("input", "DataFrame orders")]
DESC = "<p>Add <code>next_order_date</code> to every record in <code>orders</code>, containing the date of the next order from the same customer. Sequence by <code>order_date</code> ascending and then <code>order_id</code> ascending. Retain all original rows and columns; the last order in each customer's sequence should have a null next date.</p><ul><li>Use the next record in the same customer's sequence, not the next distinct date.</li><li>Keep the calculation distributed and preserve last orders with null next dates.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with every original order column plus <code>next_order_date</code>, one row per order. Same-day successors can have the same date; the final order per customer has null.</p><h4>Example</h4>{{EXAMPLE}}"
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    w=Window.partitionBy('customer_id').orderBy('order_date','order_id')\n    result=orders.withColumn('next_order_date',F.lead('order_date').over(w))\n    return result\n"


def tests():
    return inputs(['orders'], ID)
