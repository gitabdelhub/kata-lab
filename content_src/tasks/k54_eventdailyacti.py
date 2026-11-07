from kursad import inputs, SRC

ID = 'k54'
NAME = 'Event daily active users'
LANG = "pyspark"
PARAMS = ['spark', 'events']
MINUTES = 12
ORDERED = False
TAGS = ['dates', 'timestamps', 'événements', 'banque DE']
SOURCE = SRC + " · Q54"
IO = [("input", "DataFrame events")]
DESC = '<p>Calculate daily active users from <code>events</code>, deriving <code>day</code> from <code>event_ts</code> in the configured UTC session. Return <code>day</code> and <code>dau</code>, the number of distinct non-null <code>user_id</code> values. Multiple events by the same user on a date should count once.</p><ul><li>Count each non-null user once per UTC day across all event types and sessions.</li><li>Keep the distinct-user calculation distributed; the same user may contribute on multiple days.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>events</code>: <code>event_id</code>, <code>user_id</code>, <code>event_type</code>, <code>event_ts</code>, <code>session_id</code>, <code>properties</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with date <code>day</code> and integer <code>dau</code>, one row per represented UTC day. Multiple events by a user on that date contribute one to its active-user count.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, events: DataFrame) -> DataFrame:\n    # write your code here\n    return events\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, events):\n    result = events.withColumn('day',F.to_date('event_ts')).groupBy('day').agg(F.countDistinct('user_id').alias('dau'))\n    return result\n"


def tests():
    return inputs(['events'], ID)
