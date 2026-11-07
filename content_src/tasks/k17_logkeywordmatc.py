from kursad import inputs, SRC

ID = 'k17'
NAME = 'Log keyword match'
LANG = "pyspark"
PARAMS = ['spark', 'pipeline_logs']
MINUTES = 7
ORDERED = False
TAGS = ['filtre', 'tri', 'expression', 'banque DE']
SOURCE = SRC + " · Q17"
IO = [("input", "DataFrame pipeline_logs")]
DESC = '<p>Identify <code>pipeline_logs</code> records whose <code>message</code> contains <code>error</code> or <code>fail</code> anywhere in the text, ignoring letter case. Return all original fields for qualifying logs and exclude records with null messages.</p><ul><li>Search <code>message</code>, not <code>level</code>, and retain a record only once even if both keywords match.</li><li>Run the text filter on the distributed logs; null messages do not qualify.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>pipeline_logs</code>: <code>log_id</code>, <code>pipeline</code>, <code>level</code>, <code>duration_ms</code>, <code>timestamp</code>, <code>message</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame containing complete log records with a case-insensitive <code>error</code> or <code>fail</code> substring in their message. Original message text and all other log fields are preserved.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, pipeline_logs: DataFrame) -> DataFrame:\n    # write your code here\n    return pipeline_logs\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, pipeline_logs):\n    result = pipeline_logs.filter(F.lower(F.col('message')).rlike('error|fail'))\n    return result\n"


def tests():
    return inputs(['pipeline_logs'], ID)
