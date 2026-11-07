from kursad import inputs, SRC

ID = 'k19'
NAME = 'Null-safe fallback'
LANG = "pyspark"
PARAMS = ['spark', 'customers']
MINUTES = 7
ORDERED = False
TAGS = ['filtre', 'tri', 'expression', 'banque DE']
SOURCE = SRC + " · Q19"
IO = [("input", "DataFrame customers")]
DESC = '<p>Add <code>cleaned_email</code> to <code>customers</code>, copying the existing <code>email</code> value unless it is null, in which case use the string <code>unknown</code>. Do not replace blank but non-null strings. Preserve all rows and original columns, including the unchanged email field.</p><ul><li>Only null triggers the fallback; empty and whitespace-only strings remain unchanged.</li><li>Do not trim, lowercase, or validate emails while adding the distributed derived field.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>customers</code>: <code>customer_id</code>, <code>name</code>, <code>email</code>, <code>segment</code>, <code>country</code>, <code>signup_date</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with all original customer columns plus <code>cleaned_email</code>. The new field copies non-null email values exactly and contains <code>unknown</code> for nulls; all customers remain.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, customers: DataFrame) -> DataFrame:\n    # write your code here\n    return customers\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, customers):\n    result = customers.withColumn('cleaned_email',F.coalesce(F.col('email'),F.lit('unknown')))\n    return result\n"


def tests():
    return inputs(['customers'], ID)
