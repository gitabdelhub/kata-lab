from kursad import inputs, SRC

ID = 'k60'
NAME = 'Event time windows'
LANG = "pyspark"
PARAMS = ['spark', 'events']
MINUTES = 12
ORDERED = False
TAGS = ['dates', 'timestamps', 'événements', 'banque DE']
SOURCE = SRC + " · Q60"
IO = [("input", "DataFrame events")]
DESC = '<p>Using the batch <code>events</code> DataFrame, count events separately for each <code>event_type</code> within non-overlapping, one-hour tumbling windows based on <code>event_ts</code>. Return <code>window</code>, containing its start and end timestamps, <code>event_type</code>, and <code>count</code>. Each window includes its start boundary and excludes its end boundary.</p><ul><li>Group only by the one-hour tumbling window and <code>event_type</code>; do not introduce user, customer, or session grouping.</li><li>Use start-inclusive, end-exclusive windows and count each event occurrence once within its type; keep the batch aggregation distributed.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>events</code>: <code>event_id</code>, <code>user_id</code>, <code>event_type</code>, <code>event_ts</code>, <code>session_id</code>, <code>properties</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with <code>window</code>, <code>event_type</code>, and integer <code>count</code>, one row per observed window-type combination. <code>window</code> is a struct with timestamp fields <code>start</code> and <code>end</code>, one hour apart. No individual event or customer/session columns are returned.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, events: DataFrame) -> DataFrame:\n    # write your code here\n    return events\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, events):\n    result = events.withColumn('ts',F.to_timestamp('event_ts')).groupBy(F.window('ts','1 hour'),'event_type').count()\n    return result\n"


def tests():
    return inputs(['events'], ID)
