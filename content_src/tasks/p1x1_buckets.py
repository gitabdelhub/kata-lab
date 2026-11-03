from kit import df, rng

ID = "p1x1"
NAME = "Bucket rides by duration"
LANG = "pyspark"
PARAMS = ["spark", "rides_df"]
MINUTES = 15
ORDERED = False
TAGS = ["when / otherwise", "null", "between"]
SUMMARY_FR = "Classe chaque course selon sa durée (short, medium, long), avec deux cas spéciaux : durée null = unknown, durée négative ou plus de 600 min = invalid. Une colonne is_night en plus selon l'heure."
DESC = """
<p>A ride-hailing app stores one row per ride in <code>rides_df</code>:</p>
<ul><li><code>ride_id</code> - the ID of the ride (string);</li><li><code>start_hour</code> - the hour the ride started, from <code>0</code> to <code>23</code> (integer);</li><li><code>minutes</code> - the duration of the ride in minutes (integer, can be null).</li></ul>
<p>The analytics team wants each ride labelled. Your task is to return <code>ride_id</code>, <code>minutes</code>, <code>bucket</code> and <code>is_night</code>, where <code>bucket</code> follows these rules, checked in this order:</p>
<ol><li><code>"unknown"</code> if <code>minutes</code> is null;</li><li><code>"invalid"</code> if <code>minutes</code> is negative or greater than <code>600</code>;</li><li><code>"short"</code> if <code>minutes</code> is less than <code>15</code>;</li><li><code>"medium"</code> if <code>minutes</code> is less than <code>45</code>;</li><li><code>"long"</code> otherwise.</li></ol>
<p><code>is_night</code> is a boolean: <code>true</code> when <code>start_hour</code> is <code>22</code> or later, or before <code>6</code>; otherwise <code>false</code>.</p>
<p>Row order does not matter.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F


def solve(spark: SparkSession, rides_df: DataFrame) -> DataFrame:
    # write your code here
    return rides_df
"""
SOLUTION = """
from pyspark.sql import functions as F


def solve(spark, rides_df):
    m = F.col("minutes")
    bucket = (F.when(m.isNull(), "unknown")
               .when((m < 0) | (m > 600), "invalid")
               .when(m < 15, "short")
               .when(m < 45, "medium")
               .otherwise("long"))
    h = F.col("start_hour")
    night = (h >= 22) | (h < 6)
    return rides_df.select("ride_id", "minutes", bucket.alias("bucket"), night.alias("is_night"))
"""
MUTANTS = [
    """
from pyspark.sql import functions as F
def solve(spark, rides_df):
    m = F.col("minutes")
    b = F.when(m < 15, "short").when(m < 45, "medium").when(m.isNull(), "unknown").otherwise("long")
    h = F.col("start_hour")
    return rides_df.select("ride_id", "minutes", b.alias("bucket"), ((h >= 22) | (h < 6)).alias("is_night"))
""",
    """
from pyspark.sql import functions as F
def solve(spark, rides_df):
    m = F.col("minutes")
    b = F.when(m.isNull(), "unknown").when((m < 0) | (m > 600), "invalid").when(m < 15, "short").when(m < 45, "medium").otherwise("long")
    h = F.col("start_hour")
    return rides_df.select("ride_id", "minutes", b.alias("bucket"), ((h >= 22) & (h < 6)).alias("is_night"))
""",
]
HINTS = [
    "Range les when dans l'ordre de la consigne : null d'abord, puis invalid, puis les seuils du plus petit au plus grand.",
    "En PySpark, « ou » s'écrit | et chaque condition va entre parenthèses : (m < 0) | (m > 600).",
]
S = "ride_id STRING, start_hour INT, minutes INT"


def tests():
    t = [df(S, [["R1", 8, 12], ["R2", 23, 50], ["R3", 14, None], ["R4", 5, 30], ["R5", 9, -3]]),
         df(S, [["R6", 22, 15], ["R7", 6, 45], ["R8", 0, 600], ["R9", 21, 601]])]
    r = rng(2)
    for k in range(5):
        rows = [[f"Q{k}_{i}", r.randint(0, 23), r.choice([None, r.randint(-5, 5), r.randint(0, 80), r.randint(550, 700), 14, 15, 44, 45])]
                for i in range(10 + 4 * k)]
        t.append(df(S, rows))
    return [{"rides_df": x} for x in t]
