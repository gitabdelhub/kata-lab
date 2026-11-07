from kursad import inputs, SRC

ID = 'k49'
NAME = 'Deduplicate CDC'
LANG = "pyspark"
PARAMS = ['spark', 'cdc_changes']
MINUTES = 12
ORDERED = False
TAGS = ['window', 'row_number', 'lag', 'banque DE']
SOURCE = SRC + " · Q49"
IO = [("input", "DataFrame cdc_changes")]
DESC = '<p>Deduplicate <code>cdc_changes</code> to one record per <code>customer_id</code>. Select the latest <code>changed_at</code> and, when timestamps tie, the largest <code>change_id</code>. Return all original columns of the selected rows without temporary ranking fields, retaining delete operations at this stage.</p><ul><li>Select the latest complete change without merging fields or filtering operations first.</li><li>Apply the timestamp and change-ID tie-breaker on distributed data, removing temporary selection fields.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>cdc_changes</code>: <code>change_id</code>, <code>customer_id</code>, <code>operation</code>, <code>changed_at</code>, <code>email</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with one latest change per customer ID and all original CDC columns. Delete operations remain eligible and no ranking column is included.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, cdc_changes: DataFrame) -> DataFrame:\n    # write your code here\n    return cdc_changes\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, cdc_changes):\n    w=Window.partitionBy('customer_id').orderBy(F.desc('changed_at'),F.desc('change_id'))\n    result=cdc_changes.withColumn('rn',F.row_number().over(w)).filter('rn = 1').drop('rn')\n    return result\n"


def tests():
    return inputs(['cdc_changes'], ID)
