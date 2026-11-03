from kit import df, rng

ID = "p1x3"
NAME = "City ride KPIs"
LANG = "pyspark"
PARAMS = ["spark", "rides_df"]
MINUTES = 15
TAGS = ["groupBy / agg", "sum(when)", "countDistinct", "division"]
SUMMARY_FR = "Par ville : nombre de courses, courses terminées, taux d'annulation (annulées / total, arrondi 2), revenu des terminées, nombre de chauffeurs distincts. Ignore les lignes sans ville. Trie par revenu décroissant puis ville."
DESC = """
<p>The operations team monitors cities every morning. You are given <code>rides_df</code>:</p>
<ul><li><code>ride_id</code> - the ID of the ride (string);</li><li><code>city</code> - the city (string, can be null);</li><li><code>driver_id</code> - the driver (string);</li><li><code>status</code> - <code>"completed"</code>, <code>"cancelled"</code> or <code>"no_show"</code>;</li><li><code>fare</code> - the fare (double; cancelled rides can still have a fare, which must be ignored).</li></ul>
<p>Your task is to return one row per city with:</p>
<ol><li><code>city</code>;</li><li><code>rides</code> - the number of rides;</li><li><code>completed</code> - the number of completed rides;</li><li><code>cancel_rate</code> - cancelled rides divided by all rides of the city, rounded to 2 decimals (<code>no_show</code> is not a cancellation);</li><li><code>revenue</code> - the sum of <code>fare</code> over completed rides only, rounded to 2 decimals, <code>0.0</code> if there is none;</li><li><code>drivers</code> - the number of distinct drivers in the city.</li></ol>
<p>Rows with a null <code>city</code> are ignored. Sort by <code>revenue</code> descending, then <code>city</code> ascending.</p>
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
    done = F.col("status") == "completed"
    return (rides_df.filter(F.col("city").isNotNull())
            .groupBy("city")
            .agg(F.count("*").alias("rides"),
                 F.sum(F.when(done, 1).otherwise(0)).alias("completed"),
                 F.round(F.sum(F.when(F.col("status") == "cancelled", 1).otherwise(0)) / F.count("*"), 2).alias("cancel_rate"),
                 F.round(F.coalesce(F.sum(F.when(done, F.col("fare"))), F.lit(0.0)), 2).alias("revenue"),
                 F.countDistinct("driver_id").alias("drivers"))
            .orderBy(F.col("revenue").desc(), "city"))
"""
MUTANTS = [
    """
from pyspark.sql import functions as F
def solve(spark, rides_df):
    done = F.col("status") == "completed"
    return (rides_df.filter(F.col("city").isNotNull()).groupBy("city")
            .agg(F.count("*").alias("rides"), F.sum(F.when(done, 1).otherwise(0)).alias("completed"),
                 F.round(F.sum(F.when(F.col("status") == "cancelled", 1).otherwise(0)) / F.count("*"), 2).alias("cancel_rate"),
                 F.round(F.coalesce(F.sum("fare"), F.lit(0.0)), 2).alias("revenue"),
                 F.countDistinct("driver_id").alias("drivers")).orderBy(F.col("revenue").desc(), "city"))
""",
    """
from pyspark.sql import functions as F
def solve(spark, rides_df):
    done = F.col("status") == "completed"
    return (rides_df.filter(F.col("city").isNotNull()).groupBy("city")
            .agg(F.count("*").alias("rides"), F.sum(F.when(done, 1).otherwise(0)).alias("completed"),
                 F.round(F.sum(F.when(F.col("status") != "completed", 1).otherwise(0)) / F.count("*"), 2).alias("cancel_rate"),
                 F.round(F.coalesce(F.sum(F.when(done, F.col("fare"))), F.lit(0.0)), 2).alias("revenue"),
                 F.count("driver_id").alias("drivers")).orderBy(F.col("revenue").desc(), "city"))
""",
]
HINTS = [
    "Compter sous condition : F.sum(F.when(cond, 1).otherwise(0)). Sommer sous condition : F.sum(F.when(cond, F.col(\"fare\"))) (le reste vaut null et n'est pas compté).",
    "Une ville sans course terminée donne un revenu null : entoure avec F.coalesce(..., F.lit(0.0)).",
]
S = "ride_id STRING, city STRING, driver_id STRING, status STRING, fare DOUBLE"


def tests():
    t = [df(S, [["R1", "Rabat", "D1", "completed", 40.0], ["R2", "Rabat", "D2", "cancelled", 15.0], ["R3", "Fes", "D3", "completed", 22.5],
                ["R4", "Rabat", "D1", "completed", 18.0], ["R5", None, "D4", "completed", 99.0], ["R6", "Fes", "D3", "no_show", 0.0]]),
         df(S, [["R1", "Tanger", "D1", "cancelled", 10.0], ["R2", "Agadir", "D2", "no_show", 5.0]])]
    r = rng(5)
    cities = ["Rabat", "Fes", "Tanger", "Casablanca", None]
    for k in range(5):
        rows = []
        for i in range(15 + 5 * k):
            rows.append([f"R{k}{i}", r.choice(cities), f"D{r.randint(1, 7)}", r.choice(["completed", "completed", "cancelled", "no_show"]), round(r.uniform(5, 120), 2)])
        t.append(df(S, rows))
    return [{"rides_df": x} for x in t]
