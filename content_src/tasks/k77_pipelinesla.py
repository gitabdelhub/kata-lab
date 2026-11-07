from kursad import inputs, SRC

ID = 'k77'
NAME = 'Pipeline SLA'
LANG = "pyspark"
PARAMS = ['spark', 'pipeline_logs']
MINUTES = 10
ORDERED = False
TAGS = ['etl production', 'agrégation', 'banque DE']
SOURCE = SRC + " · Q77"
IO = [("input", "DataFrame pipeline_logs")]
DESC = '<p>Summarize <code>pipeline_logs</code> by <code>pipeline</code>, returning the total number of log records as <code>runs</code> and the number whose <code>duration_ms</code> exceeds 60,000 as <code>sla_breaches</code>. Retain pipelines with no breaches and report zero for that count. A duration exactly at the threshold is not a breach.</p><ul><li>Count every log record in <code>runs</code>, including records with missing durations.</li><li>Count only durations strictly above 60,000 as breaches and keep the per-pipeline aggregation distributed.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>pipeline_logs</code>: <code>log_id</code>, <code>pipeline</code>, <code>level</code>, <code>duration_ms</code>, <code>timestamp</code>, <code>message</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with <code>pipeline</code>, integer <code>runs</code>, and integer <code>sla_breaches</code>, one row per observed pipeline. Pipelines with no qualifying durations have zero breaches.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, pipeline_logs: DataFrame) -> DataFrame:\n    # write your code here\n    return pipeline_logs\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, pipeline_logs):\n    result = pipeline_logs.groupBy('pipeline').agg(F.count('*').alias('runs'),F.sum(F.when(F.col('duration_ms')>60000,1).otherwise(0)).alias('sla_breaches'))\n    return result\n"


def tests():
    return inputs(['pipeline_logs'], ID)
