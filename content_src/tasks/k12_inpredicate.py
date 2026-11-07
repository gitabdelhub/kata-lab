from kursad import inputs, SRC

ID = 'k12'
NAME = 'IN predicate'
LANG = "pyspark"
PARAMS = ['spark', 'customers']
MINUTES = 7
ORDERED = False
TAGS = ['filtre', 'tri', 'expression', 'banque DE']
SOURCE = SRC + " · Q12"
IO = [("input", "DataFrame customers")]
DESC = '<p>Find customer records in <code>customers</code> whose <code>country</code> equals <code>CA</code> or <code>US</code>. Return the complete matching records and preserve every original column. Compare the stored country codes exactly.</p><ul><li>Do not translate country names, trim codes, or ignore case.</li><li>Retain each matching customer occurrence in the distributed result.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>customers</code>: <code>customer_id</code>, <code>name</code>, <code>email</code>, <code>segment</code>, <code>country</code>, <code>signup_date</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame containing complete customer records with country exactly <code>CA</code> or <code>US</code>, with the original customer schema.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, customers: DataFrame) -> DataFrame:\n    # write your code here\n    return customers\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, customers):\n    result = customers.filter(F.col('country').isin('CA','US'))\n    return result\n"


def tests():
    return inputs(['customers'], ID)
