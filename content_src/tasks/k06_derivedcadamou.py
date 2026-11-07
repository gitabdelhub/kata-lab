from kursad import inputs, SRC

ID = 'k06'
NAME = 'Derived CAD amount'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 6
ORDERED = False
TAGS = ['bases DataFrame', 'select', 'filtre', 'banque DE']
SOURCE = SRC + " · Q06"
IO = [("input", "DataFrame orders")]
DESC = '<p>Add <code>amount_cad</code> to <code>orders</code> by multiplying each <code>amount</code> by the illustrative conversion rate 1.35. Return every original order column and record alongside the new amount. Keep the original <code>amount</code> values unchanged.</p><ul><li>Use the fixed rate of 1.35 for every order, not a live exchange-rate lookup.</li><li>Calculate on the distributed records and preserve null amounts as null derived values.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame containing all original order columns plus numeric <code>amount_cad</code>. Each value is the corresponding amount multiplied by 1.35, with all original records and amount values preserved.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    result = orders.withColumn('amount_cad',F.col('amount')*F.lit(1.35))\n    return result\n"


def tests():
    return inputs(['orders'], ID)
