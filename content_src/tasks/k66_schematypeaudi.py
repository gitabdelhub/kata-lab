from kursad import inputs, SRC

ID = 'k66'
NAME = 'Schema type audit'
LANG = "pyspark"
PARAMS = ['spark', 'orders']
MINUTES = 12
ORDERED = False
TAGS = ['nettoyage', 'null', 'doublon', 'cdc', 'json', 'banque DE']
SOURCE = SRC + " · Q66"
IO = [("input", "DataFrame orders")]
DESC = '<p>Inspect the schema of <code>orders</code> and return a DataFrame with one row per field. Include <code>column</code> for the field name, <code>dtype</code> for its Spark simple type string, and <code>nullable</code> for whether the schema permits nulls. Report schema properties rather than inspecting individual values.</p><ul><li>Read field metadata rather than scanning rows to infer types or nullability.</li><li>Schema metadata may be inspected on the driver; do not collect the underlying orders.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with string <code>column</code>, string <code>dtype</code>, and Boolean <code>nullable</code>, one row per field in the <code>orders</code> schema. <code>nullable</code> describes schema permission, not whether nulls were observed.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return orders\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, orders):\n    result=spark.createDataFrame([(x.name,x.dataType.simpleString(),x.nullable) for x in orders.schema.fields],['column','dtype','nullable'])\n    return result\n"


def tests():
    return inputs(['orders'], ID)
