from kursad import inputs, SRC

ID = 'k59'
NAME = 'Pipeline daily failures'
LANG = "pyspark"
PARAMS = ['spark', 'pipeline_logs']
MINUTES = 12
ORDERED = False
TAGS = ['dates', 'timestamps', 'événements', 'banque DE']
SOURCE = SRC + " · Q59"
IO = [("input", "DataFrame pipeline_logs")]
DESC = '<p>Count <code>pipeline_logs</code> records whose <code>level</code> equals <code>ERROR</code>, ignoring case, for each <code>pipeline</code> and UTC calendar date of <code>timestamp</code>. Return <code>pipeline</code>, <code>day</code>, and <code>count</code>. Include only pipeline-date groups with matching error records.</p><ul><li>Classify errors from <code>level</code>, not message text, and count records rather than distinct log IDs.</li><li>Group qualifying logs by pipeline and UTC date on distributed data; do not add zero-count dates.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>pipeline_logs</code>: <code>log_id</code>, <code>pipeline</code>, <code>level</code>, <code>duration_ms</code>, <code>timestamp</code>, <code>message</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with <code>pipeline</code>, date <code>day</code>, and integer <code>count</code>, one row per pipeline-day containing errors. Pipelines or dates without matching errors are absent.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, pipeline_logs: DataFrame) -> DataFrame:\n    # write your code here\n    return pipeline_logs\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, pipeline_logs):\n    result = pipeline_logs.withColumn('day',F.to_date('timestamp')).filter(F.upper('level')=='ERROR').groupBy('pipeline','day').count()\n    return result\n"


def tests():
    return inputs(['pipeline_logs'], ID)
