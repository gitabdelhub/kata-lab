from kursad import inputs, SRC

ID = 'k48'
NAME = 'Spend share'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 12
ORDERED = False
TAGS = ['window', 'row_number', 'lag', 'banque DE']
SOURCE = SRC + " · Q48"
IO = [("input", "DataFrame orders")]
DESC = "<p>For each row in <code>orders</code>, calculate its <code>amount</code> as a percentage of the total amount for the same customer across all statuses. Add this value as <code>share_pct</code>, returning null when the customer's total is zero. Preserve all original order rows and columns.</p><ul><li>Use each customer's total across all statuses as the denominator, not the overall order total.</li><li>Keep the calculation distributed and use null, not an exception or zero, for a zero-total customer.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame containing every original order column plus <code>share_pct</code>, one row per order. Shares are percentages; rows whose customer total is zero have null share values.</p><h4>Example</h4>{{EXAMPLE}}"
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    w=Window.partitionBy('customer_id')\n    result=orders.withColumn('share_pct',F.when(F.sum('amount').over(w)!=0,F.col('amount')/F.sum('amount').over(w)*100))\n    return result\n"


def tests():
    return inputs(['orders'], ID)
