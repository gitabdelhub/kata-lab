from kursad import inputs, SRC

ID = 'k64'
NAME = 'Duplicate customer emails'
LANG = "pyspark"
PARAMS = ['spark', 'customers']
MINUTES = 12
ORDERED = False
TAGS = ['nettoyage', 'null', 'doublon', 'cdc', 'json', 'banque DE']
SOURCE = SRC + " · Q64"
IO = [("input", "DataFrame customers")]
DESC = '<p>Normalize <code>customers.email</code> by trimming surrounding whitespace and converting to lowercase. Return all customer records whose non-null normalized value occurs more than once, including every occurrence. Preserve the original customer columns and add the normalized value as <code>normalized</code>; do not return a grouped count table.</p><ul><li>Return every record in each repeated non-null normalized-email group, including its first occurrence.</li><li>Exclude null normalized emails, retain original email values, and detect duplicates on distributed data.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>customers</code>: <code>customer_id</code>, <code>name</code>, <code>email</code>, <code>segment</code>, <code>country</code>, <code>signup_date</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with all customer columns plus <code>normalized</code>, containing all records whose normalized email occurs more than once. It has no count column and no required ordering.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, customers: DataFrame) -> DataFrame:\n    # write your code here\n    return customers\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, customers):\n    x=customers.withColumn('normalized',F.lower(F.trim('email')))\n    dups=x.groupBy('normalized').count().filter('count > 1')\n    result=x.join(dups.select('normalized'),'normalized','inner')\n    return result\n"


def tests():
    return inputs(['customers'], ID)
