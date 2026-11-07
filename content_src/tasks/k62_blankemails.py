from kursad import inputs, SRC

ID = 'k62'
NAME = 'Blank emails'
LANG = "pyspark"
PARAMS = ['spark', 'customers']
MINUTES = 12
ORDERED = False
TAGS = ['nettoyage', 'null', 'doublon', 'cdc', 'json', 'banque DE']
SOURCE = SRC + " · Q62"
IO = [("input", "DataFrame customers")]
DESC = '<p>Return complete records from <code>customers</code> whose <code>email</code> is null or becomes empty after surrounding whitespace is trimmed. Keep the original email values and every other customer field in the result. Do not replace blank values as part of this check.</p><ul><li>Use trimming only for the emptiness test; preserve the original email text in the result.</li><li>Check absence or blankness on distributed customers, not full email-format validity.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>customers</code>: <code>customer_id</code>, <code>name</code>, <code>email</code>, <code>segment</code>, <code>country</code>, <code>signup_date</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame of complete customer records whose email is null or blank after trimming. The result contains original fields only, without a normalized-email helper column.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, customers: DataFrame) -> DataFrame:\n    # write your code here\n    return customers\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, customers):\n    result = customers.filter(F.col('email').isNull() | (F.trim('email')==''))\n    return result\n"


def tests():
    return inputs(['customers'], ID)
