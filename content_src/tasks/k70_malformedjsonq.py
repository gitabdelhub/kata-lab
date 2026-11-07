from kursad import inputs, SRC

ID = 'k70'
NAME = 'Malformed JSON quarantine'
LANG = "pyspark"
PARAMS = ['spark', 'malformed_events']
MINUTES = 12
ORDERED = False
TAGS = ['nettoyage', 'null', 'doublon', 'cdc', 'json', 'banque DE']
SOURCE = SRC + " · Q70"
IO = [("input", "DataFrame malformed_events")]
DESC = '<p>Read <code>malformed_events.jsonl</code> in PERMISSIVE mode, retaining corrupt input text in <code>_corrupt_record</code>. Return only malformed records with <code>event_id</code>, <code>event_type</code>, and <code>_corrupt_record</code>. Keep the corrupt text available for investigation and exclude successfully parsed records from the quarantine result.</p><ul><li>Use PERMISSIVE parsing and preserve <code>_corrupt_record</code> as required by the Task.</li><li>Quarantine distributed malformed records without dropping their raw text or including successfully parsed rows.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>malformed_events</code>: <code>event_id</code>, <code>event_type</code>, <code>_corrupt_record</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with <code>event_id</code>, <code>event_type</code>, and <code>_corrupt_record</code>, containing only malformed input records. The corrupt-record field retains their source text for investigation.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, malformed_events: DataFrame) -> DataFrame:\n    # write your code here\n    return malformed_events\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, malformed_events):\n    malformed_events.cache().count()\n    result=malformed_events.filter(F.col('_corrupt_record').isNotNull()).select('event_id','event_type','_corrupt_record')\n    return result\n"


def tests():
    return inputs(['malformed_events'], ID)
