from kit import folder, rng

ID = "e07t1"
NAME = "Fixed-Width Meter Files"
LANG = "pyspark"
PARAMS = ["spark", "input_dir"]
MINUTES = 22
TAGS = ["largeur fixe", "substring", "en-tête et fin de fichier", "rejeter un fichier entier"]
DESC = """
<p>An energy company receives meter readings from an old system in <b>fixed-width</b> text files, stored in <code>input_dir</code> (no sub-folders, every file ends with <code>.dat</code>). Each file has three kinds of lines, identified by their first 3 characters:</p>
<ul><li><code>HDR</code>: the header, first line of the file, followed by the reading date written <code>YYYYMMDD</code> (characters 4 to 11);</li><li><code>REC</code>: one reading. Characters 4 to 11 are the meter id (8 characters, padded with spaces on the right), characters 12 to 21 are the reading in watt-hours (10 digits, padded with zeros on the left), and character 22 is a quality flag: <code>A</code> for an actual reading, <code>E</code> for an estimate;</li><li><code>TRL</code>: the trailer, last line of the file, followed by the number of <code>REC</code> lines of the file (6 digits, characters 4 to 9).</li></ul>
<p>Character positions start at <code>1</code>. A file is <b>valid</b> only if its trailer count is equal to the real number of <code>REC</code> lines of the file. Invalid files are rejected <b>entirely</b>. Lines with a reading that is not made only of digits are dropped, but they still count for the trailer check.</p>
<p>Your task is to return the readings of the valid files, with the columns <code>meter_id</code> (string, without padding), <code>reading_date</code> (date), <code>kwh</code> (double, the reading divided by <code>1000</code>), <code>estimated</code> (boolean) and <code>file</code> (string, the file name), sorted by <code>meter_id</code>, <code>reading_date</code>, <code>file</code>, then <code>kwh</code>.</p>
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
    for name in sorted(os.listdir(input_dir)):
        if not name.endswith(".dat"):
            continue
        d = spark.read.text(os.path.join(input_dir, name)).withColumn("file", F.lit(name))
        kind = F.substring("value", 1, 3)
        info = d.agg(
            F.max(F.when(kind == "HDR", F.substring("value", 4, 8))).alias("day"),
            F.max(F.when(kind == "TRL", F.substring("value", 4, 6).cast("int"))).alias("trl"),
            F.sum(F.when(kind == "REC", 1).otherwise(0)).alias("n")).first()
        if info["trl"] is None or info["trl"] != info["n"]:
            continue
        rec = d.filter(kind == "REC").select(
            F.trim(F.substring("value", 4, 8)).alias("meter_id"),
            F.substring("value", 12, 10).alias("raw"),
            (F.substring("value", 22, 1) == "E").alias("estimated"), "file")
        rec = rec.filter(F.col("raw").rlike("^[0-9]{10}$"))
        parts.append(rec.select("meter_id", F.to_date(F.lit(info["day"]), "yyyyMMdd").alias("reading_date"),
                                (F.col("raw").cast("long") / 1000.0).alias("kwh"), "estimated", "file"))
    if not parts:
        return spark.createDataFrame([], "meter_id string, reading_date date, kwh double, estimated boolean, file string")
    return reduce(lambda a, b: a.unionByName(b), parts).orderBy("meter_id", "reading_date", "file", "kwh")
"""
MUTANTS = [
    """
import os
from functools import reduce
from pyspark.sql import functions as F
def solve(spark, input_dir):
    parts = []
    for name in sorted(os.listdir(input_dir)):
        if not name.endswith(".dat"): continue
        d = spark.read.text(os.path.join(input_dir, name)).withColumn("file", F.lit(name))
        kind = F.substring("value", 1, 3)
        day = d.filter(kind == "HDR").first()["value"][3:11]
        rec = d.filter(kind == "REC").select(F.trim(F.substring("value", 4, 8)).alias("meter_id"), F.substring("value", 12, 10).alias("raw"), (F.substring("value", 22, 1) == "E").alias("estimated"), "file").filter(F.col("raw").rlike("^[0-9]{10}$"))
        parts.append(rec.select("meter_id", F.to_date(F.lit(day), "yyyyMMdd").alias("reading_date"), (F.col("raw").cast("long") / 1000.0).alias("kwh"), "estimated", "file"))
    return reduce(lambda a, b: a.unionByName(b), parts).orderBy("meter_id", "reading_date", "file", "kwh")
""",
    """
import os
from functools import reduce
from pyspark.sql import functions as F
def solve(spark, input_dir):
    parts = []
    for name in sorted(os.listdir(input_dir)):
        if not name.endswith(".dat"): continue
        d = spark.read.text(os.path.join(input_dir, name)).withColumn("file", F.lit(name))
        kind = F.substring("value", 1, 3)
        rec = d.filter(kind == "REC").select(F.trim(F.substring("value", 4, 8)).alias("meter_id"), F.substring("value", 12, 10).alias("raw"), (F.substring("value", 22, 1) == "E").alias("estimated"), "file").filter(F.col("raw").rlike("^[0-9]{10}$"))
        info = d.agg(F.max(F.when(kind == "HDR", F.substring("value", 4, 8))).alias("day"), F.max(F.when(kind == "TRL", F.substring("value", 4, 6).cast("int"))).alias("trl")).first()
        if info["trl"] != rec.count(): continue
        parts.append(rec.select("meter_id", F.to_date(F.lit(info["day"]), "yyyyMMdd").alias("reading_date"), (F.col("raw").cast("long") / 1000.0).alias("kwh"), "estimated", "file"))
    if not parts:
        return spark.createDataFrame([], "meter_id string, reading_date date, kwh double, estimated boolean, file string")
    return reduce(lambda a, b: a.unionByName(b), parts).orderBy("meter_id", "reading_date", "file", "kwh")
""",
    """
import os
from functools import reduce
from pyspark.sql import functions as F
def solve(spark, input_dir):
    parts = []
    for name in sorted(os.listdir(input_dir)):
        if not name.endswith(".dat"): continue
        d = spark.read.text(os.path.join(input_dir, name)).withColumn("file", F.lit(name))
        kind = F.substring("value", 1, 3)
        info = d.agg(F.max(F.when(kind == "HDR", F.substring("value", 4, 8))).alias("day"), F.max(F.when(kind == "TRL", F.substring("value", 4, 6).cast("int"))).alias("trl"), F.sum(F.when(kind == "REC", 1).otherwise(0)).alias("n")).first()
        if info["trl"] != info["n"]: continue
        rec = d.filter(kind == "REC").select(F.trim(F.substring("value", 3, 8)).alias("meter_id"), F.substring("value", 11, 10).alias("raw"), (F.substring("value", 21, 1) == "E").alias("estimated"), "file").filter(F.col("raw").rlike("^[0-9]+$"))
        parts.append(rec.select("meter_id", F.to_date(F.lit(info["day"]), "yyyyMMdd").alias("reading_date"), (F.col("raw").cast("long") / 1000.0).alias("kwh"), "estimated", "file"))
    if not parts:
        return spark.createDataFrame([], "meter_id string, reading_date date, kwh double, estimated boolean, file string")
    return reduce(lambda a, b: a.unionByName(b), parts).orderBy("meter_id", "reading_date", "file", "kwh")
""",
]


def rec(meter, wh, flag="A"):
    raw = wh if isinstance(wh, str) else f"{wh:010d}"
    return "REC" + meter.ljust(8) + raw + flag


def dat(day, recs, trl=None):
    n = len(recs) if trl is None else trl
    return "\n".join(["HDR" + day] + recs + [f"TRL{n:06d}"]) + "\n"


def tests():
    t = [folder({"north_0301.dat": dat("20260301", [rec("M001", 1234567), rec("M02", 50, "E"), rec("M003", "12A4567890")]),
                 "north_0302.dat": dat("20260302", [rec("M001", 1240000), rec("M02", 1500)], trl=3),
                 "south_0301.dat": dat("20260301", [rec("S9", 999)]),
                 "readme.txt": "fixed width v1\n"}),
         folder({"a.dat": dat("20261231", [rec("X1", 1000, "E"), rec("X1", 2000)]), "b.dat": dat("20270101", [])})]
    r = rng(701)
    for _ in range(6):
        files = {}
        for k in range(r.randint(1, 4)):
            recs = [rec(f"M{r.randint(1, 5):03d}", r.randint(0, 9999999), r.choice("AAE")) if r.random() < 0.9 else rec("M001", "ABC0000000") for _ in range(r.randint(0, 5))]
            files[f"f{k}.dat"] = dat(f"202603{r.randint(1, 9):02d}", recs, trl=None if r.random() < 0.7 else len(recs) + r.choice([-1, 1]))
        t.append(folder(files))
    return [{"input_dir": x} for x in t]
