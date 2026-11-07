from kursad import inputs, SRC

ID = 'k16'
NAME = 'Case insensitive'
LANG = "pyspark"
PARAMS = ['spark', 'customers']
MINUTES = 7
ORDERED = False
TAGS = ['filtre', 'tri', 'expression', 'banque DE']
SOURCE = SRC + " · Q16"
IO = [("input", "DataFrame customers")]
DESC = '<p>Filter <code>customers</code> to records whose <code>segment</code> equals <code>enterprise</code>, ignoring letter case. Return complete customer records with all original columns. A missing segment or a longer value merely containing that word should not qualify.</p><ul><li>Ignore case for comparison only, preserving the original segment values in returned records.</li><li>Keep the filter distributed and exclude null segments and non-exact matches.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>customers</code>: <code>customer_id</code>, <code>name</code>, <code>email</code>, <code>segment</code>, <code>country</code>, <code>signup_date</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame of complete customer records whose segment equals <code>enterprise</code> without regard to case. Original values and column types remain unchanged.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, customers: DataFrame) -> DataFrame:\n    # write your code here\n    return customers\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, customers):\n    result = customers.filter(F.lower(F.col('segment'))=='enterprise')\n    return result\n"


def tests():
    return inputs(['customers'], ID)
