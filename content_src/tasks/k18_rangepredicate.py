from kursad import inputs, SRC

ID = 'k18'
NAME = 'Range predicate'
LANG = "pyspark"
PARAMS = ['spark', 'transactions']
MINUTES = 7
ORDERED = False
TAGS = ['filtre', 'tri', 'expression', 'banque DE']
SOURCE = SRC + " · Q18"
IO = [("input", "DataFrame transactions")]
DESC = '<p>Return complete rows from <code>transactions</code> whose <code>amount</code> is between 100 and 500, including both boundaries. Preserve every original transaction column. Null amounts should not qualify.</p><ul><li>Include amounts of exactly 100 and 500, excluding nulls.</li><li>Filter the distributed transaction records without aggregating or deduplicating them.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>transactions</code>: <code>transaction_id</code>, <code>customer_id</code>, <code>amount</code>, <code>currency</code>, <code>transaction_ts</code>, <code>type</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame of complete transactions with amounts in the inclusive range 100–500. It retains every original transaction column and all qualifying occurrences.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, transactions: DataFrame) -> DataFrame:\n    # write your code here\n    return transactions\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, transactions):\n    result = transactions.filter(F.col('amount').between(100,500))\n    return result\n"


def tests():
    return inputs(['transactions'], ID)
