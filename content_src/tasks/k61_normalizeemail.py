from kursad import inputs, SRC

ID = 'k61'
NAME = 'Normalize email'
LANG = "pyspark"
PARAMS = ['spark', 'customers']
MINUTES = 12
ORDERED = False
TAGS = ['nettoyage', 'null', 'doublon', 'cdc', 'json', 'banque DE']
SOURCE = SRC + " · Q61"
IO = [("input", "DataFrame customers")]
DESC = '<p>Add <code>email_normalized</code> to <code>customers</code> by trimming surrounding whitespace from <code>email</code> and converting it to lowercase. Preserve null emails as null. Retain every original row and column, including the unchanged email field.</p><ul><li>Preserve nulls instead of turning them into replacement text.</li><li>Normalize into the added column on distributed records; do not overwrite the original email or discard repeated addresses.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>customers</code>: <code>customer_id</code>, <code>name</code>, <code>email</code>, <code>segment</code>, <code>country</code>, <code>signup_date</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame containing all original customer columns plus <code>email_normalized</code>, with lowercase trimmed email values or null. All input customer occurrences remain.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, customers: DataFrame) -> DataFrame:\n    # write your code here\n    return customers\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, customers):\n    result = customers.withColumn('email_normalized',F.lower(F.trim('email')))\n    return result\n"


def tests():
    return inputs(['customers'], ID)
