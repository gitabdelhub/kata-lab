from kursad import inputs, SRC

ID = 'k55'
NAME = 'Session duration'
LANG = "pyspark"
PARAMS = ['spark', 'events']
MINUTES = 12
ORDERED = False
TAGS = ['dates', 'timestamps', 'événements', 'banque DE']
SOURCE = SRC + " · Q55"
IO = [("input", "DataFrame events")]
DESC = "<p>Summarize <code>events</code> by <code>session_id</code> after interpreting <code>event_ts</code> as a timestamp. Return <code>session_id</code>, earliest timestamp as <code>start</code>, latest timestamp as <code>end</code>, event count as <code>events</code>, and <code>duration_seconds</code> from first to last event. A single-event session has zero duration.</p><ul><li>Count input event records within each session, rather than distinct users or event IDs.</li><li>Keep the session aggregation distributed; do not collect the complete event dataset to the driver.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>events</code>: <code>event_id</code>, <code>user_id</code>, <code>event_type</code>, <code>event_ts</code>, <code>session_id</code>, <code>properties</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with one row per <code>session_id</code> and columns <code>session_id</code>, <code>start</code>, <code>end</code>, <code>events</code>, and <code>duration_seconds</code>. The <code>start</code> and <code>end</code> fields are the session's earliest and latest timestamps; <code>events</code> is its record count. <code>duration_seconds</code> is the elapsed time between those boundaries, with zero for a single-event session.</p><h4>Example</h4>{{EXAMPLE}}"
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, events: DataFrame) -> DataFrame:\n    # write your code here\n    return events\n'
SOLUTION = 'from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, events):\n    from pyspark.sql import functions as F\n\n    # Convert ISO 8601 strings to timestamps\n    events_fixed = events.withColumn(\n    "event_ts",\n    F.to_timestamp("event_ts", "yyyy-MM-dd\'T\'HH:mm:ssX")\n    )\n\n    # Calculate session boundaries\n    result = (\n    events_fixed\n    .groupBy("session_id")\n    .agg(\n    F.min("event_ts").alias("start"),\n    F.max("event_ts").alias("end"),\n    F.count("*").alias("events")\n    )\n    .withColumn(\n    "duration_seconds",\n    F.unix_timestamp("end") - F.unix_timestamp("start")\n    )\n    )\n    return result\n'


def tests():
    return inputs(['events'], ID)
