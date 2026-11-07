from kursad import inputs, SRC

ID = 'k72'
NAME = 'Partition distribution'
LANG = "pyspark"
PARAMS = ['spark', 'customers']
MINUTES = 10
ORDERED = False
TAGS = ['etl production', 'agrégation', 'banque DE']
SOURCE = SRC + " · Q72"
IO = [("input", "DataFrame customers")]
DESC = '<p>Profile <code>customers</code> by counting records for each <code>country</code>, including null country values. Return <code>country</code> and <code>count</code>, sorted by count descending, so the distribution can inform a partitioning strategy. This exercise asks for the distribution report, not a repartitioned DataFrame.</p><ul><li>Count customer occurrences, including the null-country group, without changing physical partitions.</li><li>Aggregate and sort the distributed summary by count only; no country tie-breaker is required.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>customers</code>: <code>customer_id</code>, <code>name</code>, <code>email</code>, <code>segment</code>, <code>country</code>, <code>signup_date</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with <code>country</code> and integer <code>count</code>, one row per observed country including null. Rows are sorted by count descending, with no prescribed order among equal counts.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, customers: DataFrame) -> DataFrame:\n    # write your code here\n    return customers\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, customers):\n    result = customers.groupBy('country').count().orderBy(F.desc('count'))\n    return result\n"


def tests():
    return inputs(['customers'], ID)
