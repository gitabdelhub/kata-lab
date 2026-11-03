from kit import folder, rng

ID = "e04t1"
NAME = "Courier Delivery Logs"
LANG = "pyspark"
PARAMS = ["spark", "input_dir"]
MINUTES = 20
TAGS = ["lire un dossier", "parser du texte", "pivot pickup/dropoff", "lignes invalides"]
DESC = """
<p>A food delivery company collects the event logs of its couriers. Every city uploads one log file per day to <code>input_dir</code>:</p>
<pre class="exv">input_dir/
  &lt;city&gt;/
    &lt;YYYY-MM-DD&gt;.log</pre>
<p>Each line of a log has the form <code>HH:MM:SS|courier_id|event|order_id</code>, where <code>event</code> is <code>PICKUP</code> or <code>DROPOFF</code>. The time is the time of the day of the file. Some lines are invalid and must be ignored: empty lines, lines that do not have exactly 4 fields, lines with an unknown event or a time that is not valid. Fields can have surrounding spaces, and events can be in lower case.</p>
<p>An order is <b>delivered</b> if its log file contains at least one <code>PICKUP</code> and at least one <code>DROPOFF</code> for it. Its <b>delivery time</b> is the time between its <b>first</b> <code>PICKUP</code> and its <b>last</b> <code>DROPOFF</code> of the file, in minutes. Orders where this time is not strictly positive are ignored. An order is <b>late</b> if its delivery time is strictly greater than 30 minutes.</p>
<p>Your task is to return, for every city and day with at least one delivered order, the columns <code>city</code> (string), <code>day</code> (date), <code>delivered</code> (long), <code>avg_minutes</code> (double, rounded to 1 decimal) and <code>late</code> (long), sorted by <code>city</code>, then <code>day</code>.</p>
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
from functools import reduce
from pyspark.sql import functions as F


def solve(spark, input_dir):
    parts = []
    for city in sorted(os.listdir(input_dir)):
        cdir = os.path.join(input_dir, city)
        if not os.path.isdir(cdir):
            continue
        for name in sorted(os.listdir(cdir)):
            if not name.endswith(".log"):
                continue
            d = spark.read.text(os.path.join(cdir, name))
            parts.append(d.select(F.lit(city).alias("city"), F.lit(name[:-4]).alias("day_s"), "value"))
    df = reduce(lambda a, b: a.unionByName(b), parts)
    f = F.split("value", r"\\|")
    df = df.filter(F.size(f) == 4).select(
        "city", F.to_date("day_s").alias("day"),
        F.expr("try_to_timestamp(concat(day_s, ' ', trim(split(value, '[|]')[0])), 'yyyy-MM-dd HH:mm:ss')").alias("ts"),
        F.upper(F.trim(f[2])).alias("event"), F.trim(f[3]).alias("order_id"))
    df = df.filter(F.col("ts").isNotNull() & F.col("event").isin("PICKUP", "DROPOFF"))
    o = df.groupBy("city", "day", "order_id").agg(
        F.min(F.when(F.col("event") == "PICKUP", F.col("ts"))).alias("p"),
        F.max(F.when(F.col("event") == "DROPOFF", F.col("ts"))).alias("d"))
    o = o.withColumn("mins", (F.unix_timestamp("d") - F.unix_timestamp("p")) / 60.0).filter(F.col("mins") > 0)
    return (o.groupBy("city", "day").agg(
                F.count("*").alias("delivered"),
                F.round(F.avg("mins"), 1).alias("avg_minutes"),
                F.sum(F.when(F.col("mins") > 30, 1).otherwise(0)).cast("long").alias("late"))
            .orderBy("city", "day"))
"""
MUTANTS = [
    """
import os
from functools import reduce
from pyspark.sql import functions as F
def solve(spark, input_dir):
    parts = []
    for city in sorted(os.listdir(input_dir)):
        for name in sorted(os.listdir(os.path.join(input_dir, city))):
            d = spark.read.text(os.path.join(input_dir, city, name))
            parts.append(d.select(F.lit(city).alias("city"), F.lit(name[:-4]).alias("day_s"), "value"))
    df = reduce(lambda a, b: a.unionByName(b), parts)
    f = F.split("value", r"\\|")
    df = df.filter(F.size(f) == 4).select("city", F.to_date("day_s").alias("day"), F.expr("try_to_timestamp(concat(day_s, ' ', trim(split(value, '[|]')[0])), 'yyyy-MM-dd HH:mm:ss')").alias("ts"), F.trim(f[2]).alias("event"), F.trim(f[3]).alias("order_id"))
    df = df.filter(F.col("ts").isNotNull() & F.col("event").isin("PICKUP", "DROPOFF"))
    o = df.groupBy("city", "day", "order_id").agg(F.min(F.when(F.col("event") == "PICKUP", F.col("ts"))).alias("p"), F.max(F.when(F.col("event") == "DROPOFF", F.col("ts"))).alias("d"))
    o = o.withColumn("mins", (F.unix_timestamp("d") - F.unix_timestamp("p")) / 60.0).filter(F.col("mins") > 0)
    return o.groupBy("city", "day").agg(F.count("*").alias("delivered"), F.round(F.avg("mins"), 1).alias("avg_minutes"), F.sum(F.when(F.col("mins") > 30, 1).otherwise(0)).cast("long").alias("late")).orderBy("city", "day")
""",
    """
import os
from functools import reduce
from pyspark.sql import functions as F
def solve(spark, input_dir):
    parts = []
    for city in sorted(os.listdir(input_dir)):
        for name in sorted(os.listdir(os.path.join(input_dir, city))):
            d = spark.read.text(os.path.join(input_dir, city, name))
            parts.append(d.select(F.lit(city).alias("city"), F.lit(name[:-4]).alias("day_s"), "value"))
    df = reduce(lambda a, b: a.unionByName(b), parts)
    f = F.split("value", r"\\|")
    df = df.filter(F.size(f) == 4).select("city", F.to_date("day_s").alias("day"), F.expr("try_to_timestamp(concat(day_s, ' ', trim(split(value, '[|]')[0])), 'yyyy-MM-dd HH:mm:ss')").alias("ts"), F.upper(F.trim(f[2])).alias("event"), F.trim(f[3]).alias("order_id"))
    df = df.filter(F.col("ts").isNotNull() & F.col("event").isin("PICKUP", "DROPOFF"))
    o = df.groupBy("city", "day", "order_id").agg(F.max(F.when(F.col("event") == "PICKUP", F.col("ts"))).alias("p"), F.min(F.when(F.col("event") == "DROPOFF", F.col("ts"))).alias("d"))
    o = o.withColumn("mins", (F.unix_timestamp("d") - F.unix_timestamp("p")) / 60.0).filter(F.col("mins") > 0)
    return o.groupBy("city", "day").agg(F.count("*").alias("delivered"), F.round(F.avg("mins"), 1).alias("avg_minutes"), F.sum(F.when(F.col("mins") > 30, 1).otherwise(0)).cast("long").alias("late")).orderBy("city", "day")
""",
    """
import os
from functools import reduce
from pyspark.sql import functions as F
def solve(spark, input_dir):
    parts = []
    for city in sorted(os.listdir(input_dir)):
        for name in sorted(os.listdir(os.path.join(input_dir, city))):
            d = spark.read.text(os.path.join(input_dir, city, name))
            parts.append(d.select(F.lit(city).alias("city"), F.lit(name[:-4]).alias("day_s"), "value"))
    df = reduce(lambda a, b: a.unionByName(b), parts)
    f = F.split("value", r"\\|")
    df = df.filter(F.size(f) == 4).select("city", F.to_date("day_s").alias("day"), F.expr("try_to_timestamp(concat(day_s, ' ', trim(split(value, '[|]')[0])), 'yyyy-MM-dd HH:mm:ss')").alias("ts"), F.upper(F.trim(f[2])).alias("event"), F.trim(f[3]).alias("order_id"))
    df = df.filter(F.col("ts").isNotNull() & F.col("event").isin("PICKUP", "DROPOFF"))
    o = df.groupBy("city", "day", "order_id").agg(F.min(F.when(F.col("event") == "PICKUP", F.col("ts"))).alias("p"), F.max(F.when(F.col("event") == "DROPOFF", F.col("ts"))).alias("d"))
    o = o.withColumn("mins", (F.unix_timestamp("d") - F.unix_timestamp("p")) / 60.0).filter(F.col("mins") > 0)
    return o.groupBy("city", "day").agg(F.count("*").alias("delivered"), F.round(F.avg("mins"), 1).alias("avg_minutes"), F.sum(F.when(F.col("mins") >= 30, 1).otherwise(0)).cast("long").alias("late")).orderBy("city", "day")
""",
]


def tests():
    t = [folder({"rabat/2026-03-01.log": "09:00:00|c1|PICKUP|o1\n09:25:00|c1|DROPOFF|o1\n09:10:00| c2 |pickup| o2\n09:50:30|c2|DROPOFF|o2\nbad line\n10:00:00|c3|PICKUP|o3\n",
                 "rabat/2026-03-02.log": "12:00:00|c1|PICKUP|o9\n12:05:00|c1|PICKUP|o9\n12:30:00|c1|DROPOFF|o9\n12:31:00|c1|DROPOFF|o9\n25:99:00|c1|DROPOFF|o9\n",
                 "fes/2026-03-01.log": "08:00:00|c7|PICKUP|o4|extra\n08:00:00|c7|PICKUP|o4\n08:30:00|c7|DROPOFF|o4\n08:40:00|c7|LOST|o4\n"}),
         folder({"lome/2026-04-10.log": "\n10:00:00|k|DROPOFF|z1\n10:30:00|k|PICKUP|z1\n11:00:00|k|PICKUP|z2\n11:31:00|k|DROPOFF|z2\n", "lome/notes.txt": "x\n"})]
    r = rng(401)
    for _ in range(6):
        files = {}
        for city in r.sample(["rabat", "fes", "lome", "dakar"], r.randint(1, 3)):
            for day in r.sample(["2026-03-01", "2026-03-02", "2026-03-03"], r.randint(1, 2)):
                lines = []
                for k in range(r.randint(1, 6)):
                    h, m = r.randint(8, 21), r.randint(0, 59)
                    oid = f"o{k}"
                    lines.append(f"{h:02d}:{m:02d}:00|c{k % 3}|{r.choice(['PICKUP', 'pickup'])}|{oid}")
                    if r.random() < 0.85:
                        dm = m + r.choice([5, 20, 30, 31, 45])
                        lines.append(f"{h + dm // 60:02d}:{dm % 60:02d}:00|c{k % 3}|DROPOFF|{oid}")
                    if r.random() < 0.2:
                        lines.append(r.choice(["oops", "99:00:00|c1|PICKUP|o1", "10:00:00|c1|CANCEL|o1"]))
                r.shuffle(lines)
                files[f"{city}/{day}.log"] = "\n".join(lines) + "\n"
        t.append(folder(files))
    return [{"input_dir": x} for x in t]
