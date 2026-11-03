from kit import folder, rng

ID = "e06t1"
NAME = "Service Log Health"
LANG = "pyspark"
PARAMS = ["spark", "input_dir"]
MINUTES = 20
TAGS = ["dossiers imbriqués", "regexp_extract", "date_trunc heure", "moyenne avec NULL"]
DESC = """
<p>Several services write their logs to <code>input_dir</code>, one folder per service and per day:</p>
<pre class="exv">input_dir/
  &lt;service&gt;/
    &lt;YYYY&gt;/&lt;MM&gt;/&lt;DD&gt;/
      &lt;anything&gt;.log</pre>
<p>A valid log line looks like <code>2026-03-01T10:15:02Z [ERROR] payment failed (latency=120ms)</code>: a UTC timestamp, a level between brackets (<code>INFO</code>, <code>WARN</code> or <code>ERROR</code>), a message, and optionally a latency at the end of the line. Lines that do not start with a timestamp and a level (for example stack traces) are ignored. The service is the first folder of the path.</p>
<p>Your task is to return, for every service and hour that has at least one valid line, the columns <code>service</code> (string), <code>hour</code> (timestamp, the start of the hour), <code>lines</code> (long, the number of valid lines), <code>errors</code> (long, lines with level <code>ERROR</code>) and <code>avg_latency_ms</code> (double, average latency of the lines that have one, rounded to 1 decimal, <code>null</code> if none), sorted by <code>service</code>, then <code>hour</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
import os
from pyspark.sql import SparkSession, DataFrame, functions as F


def solve(spark: SparkSession, input_dir: str) -> DataFrame:
    # write your code here
    return spark.read.text(input_dir)
"""
SOLUTION = """
import os
from pyspark.sql import functions as F

LINE = r"^(\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2})Z \\[(INFO|WARN|ERROR)\\] "


def solve(spark, input_dir):
    df = (spark.read.option("recursiveFileLookup", "true").option("pathGlobFilter", "*.log").text(input_dir)
          .withColumn("path", F.col("_metadata.file_path")))
    root = os.path.abspath(input_dir).rstrip("/") + "/"
    df = df.withColumn("rel", F.substring_index(F.col("path"), root, -1))
    df = df.select(
        F.split("rel", "/")[0].alias("service"),
        F.regexp_extract("value", LINE, 1).alias("ts"),
        F.regexp_extract("value", LINE, 2).alias("level"),
        F.regexp_extract("value", r"\\(latency=(\\d+)ms\\)\\s*$", 1).alias("lat"))
    df = df.filter(F.col("ts") != "")
    df = df.select("service", F.date_trunc("hour", F.to_timestamp("ts", "yyyy-MM-dd'T'HH:mm:ss")).alias("hour"), "level",
                   F.when(F.col("lat") != "", F.col("lat").cast("double")).alias("lat"))
    return (df.groupBy("service", "hour").agg(
                F.count("*").alias("lines"),
                F.sum(F.when(F.col("level") == "ERROR", 1).otherwise(0)).cast("long").alias("errors"),
                F.round(F.avg("lat"), 1).alias("avg_latency_ms"))
            .orderBy("service", "hour"))
"""
MUTANTS = [
    """
import os
from pyspark.sql import functions as F
LINE = r"^(\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2})Z \\[(INFO|WARN|ERROR)\\] "
def solve(spark, input_dir):
    df = spark.read.option("recursiveFileLookup", "true").option("pathGlobFilter", "*.log").text(input_dir).withColumn("path", F.col("_metadata.file_path"))
    root = os.path.abspath(input_dir).rstrip("/") + "/"
    df = df.withColumn("rel", F.substring_index(F.col("path"), root, -1))
    df = df.select(F.split("rel", "/")[0].alias("service"), F.regexp_extract("value", LINE, 1).alias("ts"), F.regexp_extract("value", LINE, 2).alias("level"), F.regexp_extract("value", r"latency=(\\d+)ms", 1).alias("lat"))
    df = df.filter(F.col("ts") != "")
    df = df.select("service", F.date_trunc("hour", F.to_timestamp("ts", "yyyy-MM-dd'T'HH:mm:ss")).alias("hour"), "level", F.coalesce(F.when(F.col("lat") != "", F.col("lat").cast("double")), F.lit(0.0)).alias("lat"))
    return df.groupBy("service", "hour").agg(F.count("*").alias("lines"), F.sum(F.when(F.col("level") == "ERROR", 1).otherwise(0)).cast("long").alias("errors"), F.round(F.avg("lat"), 1).alias("avg_latency_ms")).orderBy("service", "hour")
""",
    """
import os
from pyspark.sql import functions as F
def solve(spark, input_dir):
    df = spark.read.option("recursiveFileLookup", "true").option("pathGlobFilter", "*.log").text(input_dir).withColumn("path", F.col("_metadata.file_path"))
    root = os.path.abspath(input_dir).rstrip("/") + "/"
    df = df.withColumn("rel", F.substring_index(F.col("path"), root, -1))
    df = df.select(F.split("rel", "/")[0].alias("service"), F.substring("value", 1, 19).alias("ts"), F.regexp_extract("value", r"\\[(\\w+)\\]", 1).alias("level"), F.regexp_extract("value", r"\\(latency=(\\d+)ms\\)\\s*$", 1).alias("lat"))
    df = df.select("service", F.date_trunc("hour", F.expr("try_to_timestamp(ts, \\"yyyy-MM-dd'T'HH:mm:ss\\")")).alias("hour"), "level", F.when(F.col("lat") != "", F.col("lat").cast("double")).alias("lat"))
    return df.groupBy("service", "hour").agg(F.count("*").alias("lines"), F.sum(F.when(F.col("level") == "ERROR", 1).otherwise(0)).cast("long").alias("errors"), F.round(F.avg("lat"), 1).alias("avg_latency_ms")).orderBy("service", "hour")
""",
]


def tests():
    t = [folder({"payments/2026/03/01/a.log": "2026-03-01T10:15:02Z [ERROR] payment failed (latency=120ms)\n  at Gateway.call(Gateway.java:42)\n2026-03-01T10:40:00Z [INFO] ok (latency=80ms)\n2026-03-01T11:01:00Z [WARN] slow call\n",
                 "payments/2026/03/01/b.log": "2026-03-01T10:59:59Z [INFO] retry ok\n",
                 "search/2026/03/01/x.log": "2026-03-01T10:00:00Z [DEBUG] noise\n2026-03-01T10:05:00Z [ERROR] index missing (latency=1000ms)\nERROR without timestamp\n",
                 "search/2026/03/01/x.log.gz.txt": "2026-03-01T10:06:00Z [ERROR] should be ignored\n"}),
         folder({"auth/2026/12/31/z.log": "2026-12-31T23:59:59Z [INFO] bye (latency=5ms)\n2027-01-01T00:00:00Z [INFO] hello (latency=6ms)\n2027-01-01T00:10:00Z [INFO] latency=99ms in text\n"})]
    r = rng(601)
    for _ in range(6):
        files = {}
        for svc in r.sample(["payments", "search", "auth", "orders"], r.randint(1, 3)):
            for f in range(r.randint(1, 3)):
                lines = []
                for _ in range(r.randint(1, 8)):
                    h, m = r.randint(8, 12), r.randint(0, 59)
                    lv = r.choice(["INFO", "INFO", "WARN", "ERROR", "DEBUG"])
                    lat = r.choice(["", f" (latency={r.randint(1, 900)}ms)"])
                    lines.append(f"2026-03-02T{h:02d}:{m:02d}:{r.randint(0, 59):02d}Z [{lv}] event {r.randint(1, 99)}{lat}")
                    if r.random() < 0.15:
                        lines.append("    at Module.fn(file.py:12)")
                files[f"{svc}/2026/03/02/part{f}.log"] = "\n".join(lines) + "\n"
        t.append(folder(files))
    return [{"input_dir": x} for x in t]
