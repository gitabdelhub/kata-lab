from kursad import inputs, SRC

ID = 'k69'
NAME = 'Parse nested JSON'
LANG = "pyspark"
PARAMS = ['spark', 'events']
MINUTES = 12
ORDERED = False
TAGS = ['nettoyage', 'null', 'doublon', 'cdc', 'json', 'banque DE']
SOURCE = SRC + " · Q69"
IO = [("input", "DataFrame events")]
DESC = '<p>Read <code>events.jsonl</code> with an inferred schema that preserves nested <code>properties</code> as a struct. Return a DataFrame containing only <code>event_id</code>, <code>event_type</code>, and <code>properties</code> for every event. Keep the properties nested rather than flattening its fields into separate columns.</p><ul><li>Use the inferred nested schema required by the Task and keep <code>properties</code> as a struct.</li><li>Read and project events as distributed records rather than loading the whole JSONL file on the driver.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>events</code>: <code>event_id</code>, <code>user_id</code>, <code>event_type</code>, <code>event_ts</code>, <code>session_id</code>, <code>properties</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with only <code>event_id</code>, <code>event_type</code>, and struct <code>properties</code>, one row per event. Nested property fields remain inside the struct rather than becoming top-level columns.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, events: DataFrame) -> DataFrame:\n    # write your code here\n    return events\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, events):\n    result = events.select('event_id','event_type','properties')\n    return result\n"


def tests():
    return inputs(['events'], ID)
