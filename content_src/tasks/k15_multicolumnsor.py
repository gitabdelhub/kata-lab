from kursad import inputs, SRC

ID = 'k15'
NAME = 'Multi-column sort'
LANG = "pyspark"
PARAMS = ['spark', 'customers']
MINUTES = 7
ORDERED = True
TAGS = ['filtre', 'tri', 'expression', 'banque DE']
SOURCE = SRC + " · Q15"
IO = [("input", "DataFrame customers")]
DESC = '<p>Sort all records in <code>customers</code> by <code>country</code> ascending, then <code>signup_date</code> ascending within each country. Place null values before non-null values for both sort keys. Retain every original record and column in the ordered result.</p><ul><li>Retain null-key records and place nulls first for each specified sort key.</li><li>Sort the distributed customer records and break remaining ties with <code>customer_id</code> ascending.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>customers</code>: <code>customer_id</code>, <code>name</code>, <code>email</code>, <code>segment</code>, <code>country</code>, <code>signup_date</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame containing all customer records and columns, ordered by country and then signup date ascending, with nulls first on both keys. Records tied on both keys are ordered by <code>customer_id</code> ascending.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, customers: DataFrame) -> DataFrame:\n    # write your code here\n    return customers\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, customers):\n    result = customers.orderBy('country','signup_date','customer_id')\n    return result\n"


def tests():
    return inputs(['customers'], ID)
