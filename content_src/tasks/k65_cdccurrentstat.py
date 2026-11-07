from kursad import inputs, SRC

ID = 'k65'
NAME = 'CDC current state'
LANG = "pyspark"
PARAMS = ['spark', 'cdc_changes']
MINUTES = 12
ORDERED = False
TAGS = ['nettoyage', 'null', 'doublon', 'cdc', 'json', 'banque DE']
SOURCE = SRC + " · Q65"
IO = [("input", "DataFrame cdc_changes")]
DESC = '<p>Build current state from <code>cdc_changes</code> by selecting the latest <code>changed_at</code> for each customer, breaking ties with the largest <code>change_id</code>. Then exclude selected records whose operation is <code>DELETE</code> or <code>D</code>, ignoring case. Return original change columns without temporary ranks; do not substitute an earlier record for a deleted customer.</p><ul><li>Resolve latest-change ties before excluding deletes, so deleted customers are not resurrected.</li><li>Perform selection on distributed CDC records and remove temporary ranking fields from the output.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>cdc_changes</code>: <code>change_id</code>, <code>customer_id</code>, <code>operation</code>, <code>changed_at</code>, <code>email</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with the original CDC columns and at most one current change per customer. Selected <code>DELETE</code> or <code>D</code> operations are excluded case-insensitively; no earlier replacement record is returned.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, cdc_changes: DataFrame) -> DataFrame:\n    # write your code here\n    return cdc_changes\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, cdc_changes):\n    w=Window.partitionBy('customer_id').orderBy(F.desc('changed_at'),F.desc('change_id'))\n    result=cdc_changes.withColumn('rn',F.row_number().over(w)).filter('rn = 1').filter(~F.upper('operation').isin('DELETE','D')).drop('rn')\n    return result\n"


def tests():
    return inputs(['cdc_changes'], ID)
