from kursad import inputs, SRC

ID = 'k63'
NAME = 'Invalid transaction amounts'
LANG = "pyspark"
PARAMS = ['spark', 'transactions']
MINUTES = 12
ORDERED = False
TAGS = ['nettoyage', 'null', 'doublon', 'cdc', 'json', 'banque DE']
SOURCE = SRC + " · Q63"
IO = [("input", "DataFrame transactions")]
DESC = '<p>Identify records in <code>transactions</code> whose <code>amount</code> is null, zero, or negative. Return the complete qualifying transaction rows with all original columns. Strictly positive amounts should be excluded.</p><ul><li>Retain zero amounts as invalid alongside negative and null amounts.</li><li>Apply the distributed check across all transaction types; do not modify offending values.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>transactions</code>: <code>transaction_id</code>, <code>customer_id</code>, <code>amount</code>, <code>currency</code>, <code>transaction_ts</code>, <code>type</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame containing complete transaction records with null or nonpositive amounts. Original columns and qualifying duplicate occurrences are retained.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, transactions: DataFrame) -> DataFrame:\n    # write your code here\n    return transactions\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, transactions):\n    result = transactions.filter(F.col('amount').isNull() | (F.col('amount')<=0))\n    return result\n"


def tests():
    return inputs(['transactions'], ID)
