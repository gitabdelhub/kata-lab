from kit import folder, rng

ID = "e09t1"
NAME = "Airport Departure Boards"
LANG = "pyspark"
PARAMS = ["spark", "input_dir"]
MINUTES = 22
TAGS = ["CSV avec guillemets", "virgules dans les champs", "retard en minutes", "annulations"]
DESC = """
<p>Airports publish their departure boards as CSV files in <code>input_dir/&lt;airport&gt;/&lt;YYYY-MM-DD&gt;.csv</code>. The columns are <code>flight</code>, <code>destination</code>, <code>scheduled</code>, <code>actual</code> and <code>remarks</code>. Times are written <code>HH:mm</code> and belong to the day of the file.</p>
<p>Some fields are between double quotes because they contain commas, for example <code>"Paris, CDG"</code> or <code>"Delayed, crew"</code>. A quote inside a quoted field is written as two double quotes (<code>""</code>).</p>
<p>Rules:</p>
<ul><li>A flight is <b>cancelled</b> if its <code>remarks</code> contain the word <code>cancel</code> in any case (for example <code>"CANCELLED"</code>). A cancelled flight has no delay.</li><li>For other flights, the <b>delay</b> is <code>actual - scheduled</code> in minutes. If <code>actual</code> is empty, the flight is ignored (unknown). If <code>actual</code> is earlier than <code>scheduled</code>, the delay is <code>0</code>.</li><li>A flight is <b>on time</b> if its delay is at most <code>15</code> minutes.</li></ul>
<p>Your task is to return, for every airport and day, the columns <code>airport</code>, <code>day</code> (date), <code>flights</code> (long, cancelled flights included, unknown flights excluded), <code>cancelled</code> (long), <code>avg_delay</code> (double, average delay of the non-cancelled flights, rounded to 1 decimal, <code>null</code> if none) and <code>on_time_pct</code> (double, <code>100 * on time / non-cancelled</code>, rounded to 1 decimal, <code>null</code> if none), sorted by <code>airport</code>, then <code>day</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
import os
from pyspark.sql import SparkSession, DataFrame, functions as F


def solve(spark: SparkSession, input_dir: str) -> DataFrame:
    # write your code here
    return spark.read.option("header", True).csv(input_dir)
"""
SOLUTION = """
import os
from functools import reduce
from pyspark.sql import functions as F


def solve(spark, input_dir):
    parts = []
    for ap in sorted(os.listdir(input_dir)):
        for name in sorted(os.listdir(os.path.join(input_dir, ap))):
            if not name.endswith(".csv"):
                continue
            d = (spark.read.option("header", True).option("quote", '"').option("escape", '"')
                 .csv(os.path.join(input_dir, ap, name)))
            parts.append(d.select(F.lit(ap).alias("airport"), F.lit(name[:10]).alias("day_s"), "scheduled", "actual", "remarks"))
    df = reduce(lambda a, b: a.unionByName(b), parts)
    cancelled = F.lower(F.coalesce(F.col("remarks"), F.lit(""))).contains("cancel")
    ts = lambda c: F.try_to_timestamp(F.concat_ws(" ", "day_s", F.trim(c)), F.lit("yyyy-MM-dd HH:mm"))
    df = df.select("airport", F.to_date("day_s").alias("day"), cancelled.alias("cancelled"),
                   F.greatest((F.unix_timestamp(ts("actual")) - F.unix_timestamp(ts("scheduled"))) / 60.0, F.lit(0.0)).alias("delay"),
                   F.trim(F.coalesce(F.col("actual"), F.lit(""))).alias("act"))
    df = df.filter(F.col("cancelled") | (F.col("act") != ""))
    delay = F.when(~F.col("cancelled"), F.col("delay"))
    return (df.groupBy("airport", "day").agg(
                F.count("*").alias("flights"),
                F.sum(F.col("cancelled").cast("int")).cast("long").alias("cancelled"),
                F.round(F.avg(delay), 1).alias("avg_delay"),
                F.round(F.try_divide(100.0 * F.sum(F.when(delay <= 15, 1).otherwise(0)), F.count(delay)), 1).alias("on_time_pct"))
            .orderBy("airport", "day"))
"""
MUTANTS = [
    """
import os
from functools import reduce
from pyspark.sql import functions as F
def solve(spark, input_dir):
    parts = []
    for ap in sorted(os.listdir(input_dir)):
        for name in sorted(os.listdir(os.path.join(input_dir, ap))):
            d = spark.read.option("header", True).csv(os.path.join(input_dir, ap, name))
            parts.append(d.select(F.lit(ap).alias("airport"), F.lit(name[:10]).alias("day_s"), "scheduled", "actual", "remarks"))
    df = reduce(lambda a, b: a.unionByName(b), parts)
    c = F.lower(F.coalesce(F.col("remarks"), F.lit(""))).contains("cancel")
    ts = lambda x: F.try_to_timestamp(F.concat_ws(" ", "day_s", F.trim(x)), F.lit("yyyy-MM-dd HH:mm"))
    df = df.select("airport", F.to_date("day_s").alias("day"), c.alias("cancelled"), F.greatest((F.unix_timestamp(ts("actual")) - F.unix_timestamp(ts("scheduled"))) / 60.0, F.lit(0.0)).alias("delay"), F.trim(F.coalesce(F.col("actual"), F.lit(""))).alias("act"))
    df = df.filter(F.col("cancelled") | (F.col("act") != ""))
    dl = F.when(~F.col("cancelled"), F.col("delay"))
    return df.groupBy("airport", "day").agg(F.count("*").alias("flights"), F.sum(F.col("cancelled").cast("int")).cast("long").alias("cancelled"), F.round(F.avg(dl), 1).alias("avg_delay"), F.round(100.0 * F.sum(F.when(dl <= 15, 1).otherwise(0)) / F.count(dl), 1).alias("on_time_pct")).orderBy("airport", "day")
""",
    """
import os
from functools import reduce
from pyspark.sql import functions as F
def solve(spark, input_dir):
    parts = []
    for ap in sorted(os.listdir(input_dir)):
        for name in sorted(os.listdir(os.path.join(input_dir, ap))):
            d = spark.read.option("header", True).option("escape", '"').csv(os.path.join(input_dir, ap, name))
            parts.append(d.select(F.lit(ap).alias("airport"), F.lit(name[:10]).alias("day_s"), "scheduled", "actual", "remarks"))
    df = reduce(lambda a, b: a.unionByName(b), parts)
    c = F.lower(F.coalesce(F.col("remarks"), F.lit(""))).contains("cancel")
    ts = lambda x: F.try_to_timestamp(F.concat_ws(" ", "day_s", F.trim(x)), F.lit("yyyy-MM-dd HH:mm"))
    df = df.select("airport", F.to_date("day_s").alias("day"), c.alias("cancelled"), ((F.unix_timestamp(ts("actual")) - F.unix_timestamp(ts("scheduled"))) / 60.0).alias("delay"), F.trim(F.coalesce(F.col("actual"), F.lit(""))).alias("act"))
    df = df.filter(F.col("cancelled") | (F.col("act") != ""))
    dl = F.when(~F.col("cancelled"), F.col("delay"))
    return df.groupBy("airport", "day").agg(F.count("*").alias("flights"), F.sum(F.col("cancelled").cast("int")).cast("long").alias("cancelled"), F.round(F.avg(dl), 1).alias("avg_delay"), F.round(100.0 * F.sum(F.when(dl <= 15, 1).otherwise(0)) / F.count(dl), 1).alias("on_time_pct")).orderBy("airport", "day")
""",
]
H = "flight,destination,scheduled,actual,remarks"


def tests():
    t = [folder({"CMN/2026-03-01.csv": H + '\nAT200,"Paris, CDG",08:00,08:10,\nAT202,Dakar,09:00,09:45,"Delayed, crew"\nAT204,"Lome ""Eyadema""",10:00,,CANCELLED\nAT206,Fes,11:00,10:55,early\nAT208,Rabat,12:00,,\n',
                 "LFW/2026-03-01.csv": H + "\nTG10,Abidjan,07:00,07:16,\nTG12,Accra,08:00,,Cancelled by airline\n"}),
         folder({"DSS/2026-03-02.csv": H + '\nHC1,"Banjul, GM",06:00,,"weather, cancel"\nHC2,Bamako,06:30,,\n'})]
    r = rng(901)
    for _ in range(6):
        files = {}
        for ap in r.sample(["CMN", "LFW", "DSS", "ABJ"], r.randint(1, 3)):
            for day in r.sample(["2026-03-01", "2026-03-02"], r.randint(1, 2)):
                lines = [H]
                for k in range(r.randint(1, 7)):
                    h, m = r.randint(6, 20), r.choice([0, 15, 30, 45])
                    dm = m + r.choice([-5, 0, 10, 15, 16, 40, 90])
                    act = f"{h + dm // 60:02d}:{dm % 60:02d}" if dm >= 0 else f"{h - 1:02d}:{60 + dm:02d}"
                    rem = r.choice(["", "", '"Delayed, ATC"', "CANCELLED", '"Gate ""B2"""', "cancel"])
                    if "ANCEL" in rem.upper():
                        act = ""
                    elif r.random() < 0.1:
                        act = ""
                    lines.append(f'F{k},"City {k}, X",{h:02d}:{m:02d},{act},{rem}')
                files[f"{ap}/{day}.csv"] = "\n".join(lines) + "\n"
        t.append(folder(files))
    return [{"input_dir": x} for x in t]
