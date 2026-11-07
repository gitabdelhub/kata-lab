from kursad import inputs, SRC

ID = 'k57'
NAME = 'Hour buckets'
LANG = "pyspark"
PARAMS = ['spark', 'events']
MINUTES = 12
ORDERED = False
TAGS = ['dates', 'timestamps', 'événements', 'banque DE']
SOURCE = SRC + " · Q57"
IO = [("input", "DataFrame events")]
DESC = '<p>Count records in <code>events</code> in calendar-hour buckets derived from <code>event_ts</code>. Return <code>hour</code> as the timestamp at the start of each represented hour and <code>count</code>. Keep hours on different dates separate rather than combining the same hour of day.</p><ul><li>Use full calendar-hour timestamps rather than hour-of-day numbers.</li><li>Count event occurrences across all types and users in each distributed hourly group.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>events</code>: <code>event_id</code>, <code>user_id</code>, <code>event_type</code>, <code>event_ts</code>, <code>session_id</code>, <code>properties</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with timestamp <code>hour</code> and integer <code>count</code>, one row per represented hour. Hour values mark the start of each calendar-hour bucket, keeping different dates separate.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, events: DataFrame) -> DataFrame:\n    # write your code here\n    return events\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, events):\n    result = events.groupBy(F.date_trunc('hour',F.to_timestamp('event_ts')).alias('hour')).count()\n    return result\n"


def tests():
    return inputs(['events'], ID)
