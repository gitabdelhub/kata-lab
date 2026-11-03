from kit import folder, rng

ID = "p1x5"
NAME = "Daily revenue from city files"
LANG = "pyspark"
PARAMS = ["spark", "input_dir"]
MINUTES = 20
TAGS = ["lire un dossier", "regexp_extract", "to_date", "toDF", "groupBy / agg"]
SUMMARY_FR = "Un fichier CSV par ville et par jour, nommé ville_AAAA-MM-JJ.csv. Les en-têtes ont des espaces et des majuscules. Prends la ville et la date dans le NOM du fichier, garde les courses completed (sans tenir compte de la casse et des espaces), somme fare_mad par ville et jour, arrondi 2. Trie par date puis ville."
DESC = """
<p>A ride-hailing company drops one CSV file per city and per day into <code>input_dir</code>. File names follow the pattern <code>&lt;city&gt;_&lt;YYYY-MM-DD&gt;.csv</code>, for example <code>rabat_2026-03-01.csv</code>. Every file has a header line with the columns <code>ride_id</code>, <code>status</code>, <code>fare_mad</code>, always in this order, but city teams type header names with extra spaces and capital letters (for example <code>" Status "</code>).</p>
<p>Your task is to return the completed revenue per city and per day:</p>
<ol><li>the city and the date come from the file name, not from the content;</li><li>a ride is completed when <code>status</code> equals <code>completed</code>, ignoring case and surrounding spaces;</li><li><code>fare_mad</code> is written with a dot (<code>"45.50"</code>); an empty fare counts as <code>0</code>.</li></ol>
<p>Return <code>city</code>, <code>ride_date</code> (date) and <code>revenue_mad</code> (sum of fares of completed rides, rounded to 2 decimals). A city-day with no completed ride is returned with <code>0.0</code>. Sort by <code>ride_date</code>, then <code>city</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F


def solve(spark: SparkSession, input_dir: str) -> DataFrame:
    rides = spark.read.option("header", True).csv(input_dir)
    # write your code here
    return rides
"""
SOLUTION = """
from pyspark.sql import functions as F


def solve(spark, input_dir):
    raw = spark.read.option("header", True).csv(input_dir)
    rides = raw.toDF(*[c.strip().lower() for c in raw.columns])
    name = F.col("_metadata.file_name")
    rides = (rides
             .withColumn("city", F.regexp_extract(name, r"^(.+)_(\\d{4}-\\d{2}-\\d{2})\\.csv$", 1))
             .withColumn("ride_date", F.to_date(F.regexp_extract(name, r"^(.+)_(\\d{4}-\\d{2}-\\d{2})\\.csv$", 2)))
             .withColumn("fare", F.coalesce(F.col("fare_mad").cast("double"), F.lit(0.0))))
    done = F.lower(F.trim(F.col("status"))) == "completed"
    return (rides.groupBy("city", "ride_date")
            .agg(F.round(F.sum(F.when(done, F.col("fare")).otherwise(0.0)), 2).alias("revenue_mad"))
            .orderBy("ride_date", "city"))
"""
MUTANTS = [
    """
from pyspark.sql import functions as F
def solve(spark, input_dir):
    raw = spark.read.option("header", True).csv(input_dir)
    rides = raw.toDF(*[c.strip().lower() for c in raw.columns])
    name = F.col("_metadata.file_name")
    rides = rides.withColumn("city", F.regexp_extract(name, r"^(.+)_(\\d{4}-\\d{2}-\\d{2})\\.csv$", 1)).withColumn("ride_date", F.to_date(F.regexp_extract(name, r"^(.+)_(\\d{4}-\\d{2}-\\d{2})\\.csv$", 2)))
    rides = rides.filter(F.col("status") == "completed")
    return rides.groupBy("city", "ride_date").agg(F.round(F.sum(F.coalesce(F.col("fare_mad").cast("double"), F.lit(0.0))), 2).alias("revenue_mad")).orderBy("ride_date", "city")
""",
]
HINTS = [
    "Nettoie d'abord les en-têtes : raw.toDF(*[c.strip().lower() for c in raw.columns]).",
    "Ville et date : F.regexp_extract(F.col(\"_metadata.file_name\"), r\"^(.+)_(\\d{4}-\\d{2}-\\d{2})\\.csv$\", 1) puis 2, et F.to_date(...) pour la date.",
    "Pour garder les jours sans course terminée à 0.0, ne filtre pas : somme F.when(terminée, fare).otherwise(0.0).",
]
HEAD = ["ride_id,status,fare_mad", " Ride_ID , Status ,FARE_MAD", "RIDE_ID,status , Fare_Mad "]


def tests():
    t = [folder({"casablanca_2026-03-01.csv": " Ride_ID , Status ,FARE_MAD\nR1,COMPLETED,45.50\nR2, completed ,30.00\nR3,cancelled,12.00\nR4,COMPLETED,\n",
                 "rabat_2026-03-01.csv": "ride_id,status,fare_mad\nR7,completed,61.00\n",
                 "rabat_2026-03-02.csv": "RIDE_ID,status , Fare_Mad \nR8,cancelled,20.00\n"}),
         folder({"fes_2026-02-28.csv": "ride_id,status,fare_mad\nA,Completed,10.10\nB,completed,0.20\n", "el_jadida_2026-02-28.csv": "ride_id,status,fare_mad\nC,completed,5.00\n"})]
    r = rng(9)
    for k in range(4):
        files = {}
        for f in range(3 + k):
            city = r.choice(["rabat", "fes", "tanger", "sale", "el_jadida"])
            day = f"2026-03-{r.randint(1, 4):02d}"
            lines = [r.choice(HEAD)]
            for i in range(r.randint(1, 6)):
                st = r.choice(["completed", " COMPLETED", "Completed ", "cancelled", "no_show"])
                fare = r.choice([f"{r.uniform(5, 90):.2f}", ""])
                lines.append(f"R{k}{f}{i},{st},{fare}")
            files[f"{city}_{day}.csv"] = "\n".join(lines) + "\n"
        t.append(folder(files))
    return [{"input_dir": x} for x in t]
