from kursad import inputs, SRC

ID = 'k51'
NAME = 'Parse timestamps'
LANG = "pyspark"
PARAMS = ['spark', 'transactions']
MINUTES = 12
ORDERED = False
TAGS = ['dates', 'timestamps', 'événements', 'banque DE']
SOURCE = SRC + " · Q51"
IO = [("input", "DataFrame transactions")]
DESC = '<p>Parse <code>transaction_ts</code> from <code>transactions</code> into a Spark timestamp column named <code>ts</code>. Return all original transaction rows and columns alongside the parsed timestamp. Keep the original <code>transaction_ts</code> field unchanged.</p><ul><li>The added field must have Spark timestamp type, not a reformatted string.</li><li>Parse on the distributed transactions and preserve the source timestamp field and all other values.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>transactions</code>: <code>transaction_id</code>, <code>customer_id</code>, <code>amount</code>, <code>currency</code>, <code>transaction_ts</code>, <code>type</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with all original transaction columns plus timestamp <code>ts</code>. Every input transaction remains, and <code>transaction_ts</code> retains its original values and type.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, transactions: DataFrame) -> DataFrame:\n    # write your code here\n    return transactions\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, transactions):\n    result = transactions.withColumn('ts',F.to_timestamp('transaction_ts'))\n    return result\n"


def tests():
    return inputs(['transactions'], ID)
