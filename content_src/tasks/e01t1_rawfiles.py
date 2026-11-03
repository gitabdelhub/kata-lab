from kit import folder, rng

ID = "e01t1"
NAME = "Daily Revenue from Raw Ride Files"
LANG = "pyspark"
PARAMS = ["spark", "input_dir"]
MINUTES = 15
TAGS = ["lire un dossier", "dédoublonnage", "Window", "nettoyage", "try_cast"]
DESC = """
<p>A ride-hailing company drops one CSV file per city and per day into a folder. Files come from different city teams, so header names and number formats are not consistent. Finance needs one table with the completed revenue per city and per day.</p>
<p>Implement <code>solve(spark, input_dir)</code>. Every file in <code>input_dir</code> has a header line and the columns below, always in this order:</p>
<ul><li><code>ride_id</code> - the ID of the ride. Because of a retry bug, the same ride can appear in two files;</li><li><code>status</code> - the status of the ride, for example <code>"COMPLETED"</code>, <code>" completed "</code> or <code>"cancelled"</code>;</li><li><code>fare_mad</code> - the fare in dirhams, written <code>"45.50"</code>, <code>"30,00"</code>, empty, or with a typo such as <code>"4O.00"</code>.</li></ul>
<p>Header names may contain extra spaces and capital letters. File names follow the pattern <code>&lt;city&gt;_&lt;YYYY-MM-DD&gt;.csv</code>, and a city name can contain an underscore (<code>el_jadida_2026-03-01.csv</code>).</p>
<p>Your task is to return one row per city and per day with the completed revenue, following these rules:</p>
<ol><li>city and date come from the file name, not from the content;</li><li>a ride found in several files is kept once, from the file with the earliest date; if the dates are equal, keep the one from the city that comes first alphabetically;</li><li>only completed rides count; compare <code>status</code> ignoring case and surrounding spaces;</li><li>a fare that cannot be parsed counts as <code>0</code>;</li><li>every city and day that has a file appears in the output, with <code>0.0</code> if nothing counts.</li></ol>
<p>The output must have the columns <code>city</code>, <code>ride_date</code> (date) and <code>revenue_mad</code> (rounded to 2 decimals), sorted by <code>ride_date</code>, then <code>city</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
<p>Ride <code>R1</code> appears in both files of 2026-03-01, so it is kept for <code>casablanca</code> only. <code>R3</code> is cancelled and <code>R4</code> has no fare, so both add nothing.</p>
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F
from pyspark.sql.window import Window


def solve(spark: SparkSession, input_dir: str) -> DataFrame:
    rides = spark.read.option("header", True).csv(input_dir)
    # write your code here
    return rides
"""
SOLUTION = """
from pyspark.sql import functions as F
from pyspark.sql.window import Window

PATTERN = r"^(.+)_(\\d{4}-\\d{2}-\\d{2})\\.csv$"


def solve(spark, input_dir):
    raw = spark.read.option("header", True).csv(input_dir)
    rides = raw.toDF(*[c.strip().lower() for c in raw.columns])
    name = F.col("_metadata.file_name")
    rides = (rides.withColumn("city", F.regexp_extract(name, PATTERN, 1))
             .withColumn("ride_date", F.to_date(F.regexp_extract(name, PATTERN, 2))))
    files = rides.select("city", "ride_date").distinct()
    w = Window.partitionBy("ride_id").orderBy("ride_date", "city")
    kept = rides.withColumn("rn", F.row_number().over(w)).filter("rn = 1")
    fare = F.expr("try_cast(replace(trim(fare_mad), ',', '.') AS DOUBLE)")
    done = F.lower(F.trim(F.col("status"))) == "completed"
    revenue = (kept.filter(done)
               .groupBy("city", "ride_date")
               .agg(F.sum(F.coalesce(fare, F.lit(0.0))).alias("rev")))
    return (files.join(revenue, ["city", "ride_date"], "left")
            .select("city", "ride_date", F.round(F.coalesce("rev", F.lit(0.0)), 2).alias("revenue_mad"))
            .orderBy("ride_date", "city"))
"""
MUTANTS = [
    """
from pyspark.sql import functions as F
from pyspark.sql.window import Window
PATTERN = r"^(.+)_(\\d{4}-\\d{2}-\\d{2})\\.csv$"
def solve(spark, input_dir):
    raw = spark.read.option("header", True).csv(input_dir)
    rides = raw.toDF(*[c.strip().lower() for c in raw.columns])
    name = F.col("_metadata.file_name")
    rides = rides.withColumn("city", F.regexp_extract(name, PATTERN, 1)).withColumn("ride_date", F.to_date(F.regexp_extract(name, PATTERN, 2)))
    files = rides.select("city", "ride_date").distinct()
    kept = rides.dropDuplicates(["ride_id"])
    fare = F.expr("try_cast(replace(trim(fare_mad), ',', '.') AS DOUBLE)")
    rev = kept.filter(F.lower(F.trim("status")) == "completed").groupBy("city", "ride_date").agg(F.sum(F.coalesce(fare, F.lit(0.0))).alias("rev"))
    return files.join(rev, ["city", "ride_date"], "left").select("city", "ride_date", F.round(F.coalesce("rev", F.lit(0.0)), 2).alias("revenue_mad")).orderBy("ride_date", "city")
""",
    """
from pyspark.sql import functions as F
from pyspark.sql.window import Window
PATTERN = r"^(.+)_(\\d{4}-\\d{2}-\\d{2})\\.csv$"
def solve(spark, input_dir):
    raw = spark.read.option("header", True).csv(input_dir)
    rides = raw.toDF(*[c.strip().lower() for c in raw.columns])
    name = F.col("_metadata.file_name")
    rides = rides.withColumn("city", F.regexp_extract(name, PATTERN, 1)).withColumn("ride_date", F.to_date(F.regexp_extract(name, PATTERN, 2)))
    w = Window.partitionBy("ride_id").orderBy("ride_date", "city")
    kept = rides.withColumn("rn", F.row_number().over(w)).filter("rn = 1")
    fare = F.expr("try_cast(replace(trim(fare_mad), ',', '.') AS DOUBLE)")
    rev = kept.filter(F.lower(F.trim("status")) == "completed").groupBy("city", "ride_date").agg(F.round(F.sum(F.coalesce(fare, F.lit(0.0))), 2).alias("revenue_mad"))
    return rev.orderBy("ride_date", "city")
""",
    """
from pyspark.sql import functions as F
from pyspark.sql.window import Window
def solve(spark, input_dir):
    raw = spark.read.option("header", True).csv(input_dir)
    rides = raw.toDF(*[c.strip().lower() for c in raw.columns])
    name = F.col("_metadata.file_name")
    rides = rides.withColumn("city", F.split(name, "_")[0]).withColumn("ride_date", F.to_date(F.regexp_extract(name, r"(\\d{4}-\\d{2}-\\d{2})", 1)))
    files = rides.select("city", "ride_date").distinct()
    w = Window.partitionBy("ride_id").orderBy("ride_date", "city")
    kept = rides.withColumn("rn", F.row_number().over(w)).filter("rn = 1")
    fare = F.expr("try_cast(replace(trim(fare_mad), ',', '.') AS DOUBLE)")
    rev = kept.filter(F.lower(F.trim("status")) == "completed").groupBy("city", "ride_date").agg(F.sum(F.coalesce(fare, F.lit(0.0))).alias("rev"))
    return files.join(rev, ["city", "ride_date"], "left").select("city", "ride_date", F.round(F.coalesce("rev", F.lit(0.0)), 2).alias("revenue_mad")).orderBy("ride_date", "city")
""",
]
HEAD = ["ride_id,status,fare_mad", " Ride_ID , Status ,FARE_MAD", "RIDE_ID,status , Fare_Mad "]


def tests():
    t = [folder({"casablanca_2026-03-01.csv": "ride_id, Status ,fare_mad\nR1,COMPLETED,45.50\nR2, completed ,\"30,00\"\nR3,cancelled,12.00\nR4,COMPLETED,\n",
                 "rabat_2026-03-01.csv": "Ride_ID,status,FARE_MAD\nR7,completed,61.00\nR1,completed,45.50\n"}),
         folder({"el_jadida_2026-03-02.csv": "ride_id,status,fare_mad\nA1,completed,4O.00\nA2,completed,10.00\n",
                 "fes_2026-03-01.csv": "ride_id,status,fare_mad\nA2,COMPLETED,99.00\nA3,no_show,5.00\n",
                 "fes_2026-03-02.csv": "ride_id,status,fare_mad\nA4,cancelled,8.00\n"})]
    r = rng(30)
    for k in range(6):
        files = {}
        ids = [f"R{k}{i}" for i in range(8 + 3 * k)]
        for f in range(3 + k):
            city = r.choice(["rabat", "fes", "tanger", "el_jadida", "casablanca"])
            day = f"2026-03-{r.randint(1, 3):02d}"
            lines = [r.choice(HEAD)]
            for rid in r.sample(ids, r.randint(1, 5)):
                st = r.choice(["completed", " COMPLETED", "Completed ", "cancelled", "no_show"])
                fare = r.choice([f"{r.uniform(5, 90):.2f}", f"\"{r.randint(5, 90)},{r.randint(0, 99):02d}\"", "", "4O.00"])
                lines.append(f"{rid},{st},{fare}")
            files[f"{city}_{day}.csv"] = "\n".join(lines) + "\n"
        t.append(folder(files))
    return [{"input_dir": x} for x in t]
