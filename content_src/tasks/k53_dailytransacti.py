from kursad import inputs, SRC

ID = 'k53'
NAME = 'Daily transaction count'
LANG = "pyspark"
PARAMS = ['spark', 'transactions']
MINUTES = 12
ORDERED = False
TAGS = ['dates', 'timestamps', 'événements', 'banque DE']
SOURCE = SRC + " · Q53"
IO = [("input", "DataFrame transactions")]
DESC = '<p>Count transaction records in <code>transactions</code> by the UTC calendar date of <code>transaction_ts</code>. Return <code>day</code> and <code>count</code>, with one row per represented date. Count records regardless of their amount, currency, or type.</p><ul><li>Use UTC calendar dates and count every transaction occurrence.</li><li>Keep daily aggregation distributed without filtering currency, type, or amount.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>transactions</code>: <code>transaction_id</code>, <code>customer_id</code>, <code>amount</code>, <code>currency</code>, <code>transaction_ts</code>, <code>type</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with date <code>day</code> and integer <code>count</code>, one row per represented transaction date. Counts measure transaction records, not distinct customers.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, transactions: DataFrame) -> DataFrame:\n    # write your code here\n    return transactions\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, transactions):\n    result = transactions.withColumn('day',F.to_date('transaction_ts')).groupBy('day').count()\n    return result\n"


def tests():
    return inputs(['transactions'], ID)
