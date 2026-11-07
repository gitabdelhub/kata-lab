from kursad import inputs, SRC

ID = 'k25'
NAME = 'Segment distribution'
LANG = "pyspark"
PARAMS = ['spark', 'customers']
MINUTES = 8
ORDERED = False
TAGS = ['groupBy', 'agrégation', 'banque DE']
SOURCE = SRC + " · Q25"
IO = [("input", "DataFrame customers")]
DESC = '<p>Count records in <code>customers</code> for each distinct combination of <code>country</code> and <code>segment</code>. Return <code>country</code>, <code>segment</code>, and <code>count</code>, including combinations containing null grouping values. Count customer rows rather than distinct customer IDs.</p><ul><li>Count records rather than distinct customer identifiers.</li><li>Preserve observed null-key combinations during the distributed aggregation; do not generate unobserved combinations.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>customers</code>: <code>customer_id</code>, <code>name</code>, <code>email</code>, <code>segment</code>, <code>country</code>, <code>signup_date</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with <code>country</code>, <code>segment</code>, and integer <code>count</code>, one row per observed country-segment combination. Null country or segment values remain valid grouping values.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, customers: DataFrame) -> DataFrame:\n    # write your code here\n    return customers\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, customers):\n    result = customers.groupBy('country','segment').count()\n    return result\n"


def tests():
    return inputs(['customers'], ID)
