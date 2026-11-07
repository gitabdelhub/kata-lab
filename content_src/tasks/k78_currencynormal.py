from kursad import inputs, SRC

ID = 'k78'
NAME = 'Currency normalization'
LANG = "pyspark"
PARAMS = ['spark', 'transactions']
MINUTES = 10
ORDERED = False
TAGS = ['etl production', 'agrégation', 'banque DE']
SOURCE = SRC + " · Q78"
IO = [("input", "DataFrame transactions")]
DESC = "<p>Add <code>amount_cad</code> to <code>transactions</code> by converting <code>amount</code> using these illustrative rates: USD 1.35, CAD 1.00, EUR 1.48, and GBP 1.72. Use the transaction's <code>currency</code> to select the rate. Set <code>amount_cad</code> to null for unrecognized currencies, and preserve all original rows and columns.</p><ul><li>Match currency codes exactly to the fixed illustrative rates, without fetching external rates.</li><li>Calculate on distributed transactions and retain unsupported-currency records with null converted amounts.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>transactions</code>: <code>transaction_id</code>, <code>customer_id</code>, <code>amount</code>, <code>currency</code>, <code>transaction_ts</code>, <code>type</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame containing all original transaction columns plus <code>amount_cad</code>. The added field uses the currency-specific rate and is null for unrecognized currencies or null amounts; no records are removed.</p><h4>Example</h4>{{EXAMPLE}}"
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, transactions: DataFrame) -> DataFrame:\n    # write your code here\n    return transactions\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, transactions):\n    rates=F.create_map(F.lit('USD'),F.lit(1.35),F.lit('CAD'),F.lit(1.0),F.lit('EUR'),F.lit(1.48),F.lit('GBP'),F.lit(1.72))\n    result=transactions.withColumn('amount_cad',F.col('amount')*F.element_at(rates,F.col('currency')))\n    return result\n"


def tests():
    return inputs(['transactions'], ID)
