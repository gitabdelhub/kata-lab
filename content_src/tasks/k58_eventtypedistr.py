from kursad import inputs, SRC

ID = 'k58'
NAME = 'Event-type distribution'
LANG = "pyspark"
PARAMS = ['spark', 'events']
MINUTES = 12
ORDERED = False
TAGS = ['dates', 'timestamps', 'événements', 'banque DE']
SOURCE = SRC + " · Q58"
IO = [("input", "DataFrame events")]
DESC = '<p>Summarize <code>events</code> by <code>event_type</code>, returning the type and its row count as <code>count</code>. Include a null-type group when present. Count all event records rather than distinct users or sessions.</p><ul><li>Do not deduplicate event IDs before counting.</li><li>Aggregate by stored event type on distributed data, preserving a null-type group.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>events</code>: <code>event_id</code>, <code>user_id</code>, <code>event_type</code>, <code>event_ts</code>, <code>session_id</code>, <code>properties</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with <code>event_type</code> and integer <code>count</code>, one row per observed type including null when present. Counts together account for every event record.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, events: DataFrame) -> DataFrame:\n    # write your code here\n    return events\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, events):\n    result = events.groupBy('event_type').count()\n    return result\n"


def tests():
    return inputs(['events'], ID)
