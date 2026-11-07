from kit import df, rng

ID = "g05"
NAME = "Taxi Drivers and Rides Summary"
LANG = "pyspark"
PARAMS = ["spark", "drivers_df", "rides_1_df", "rides_2_df", "rides_3_df", "rides_4_df"]
MINUTES = 15
TAGS = ["union de partitions", "agrégation", "ratio", "égalité exacte", "BCG"]
SOURCE = "Question rapportée du test BCG (fastprep.io, à l'origine en Pandas), réécrite en PySpark et testée par Kata Lab"
SUMMARY_FR = "Une seule ligne : la note moyenne des chauffeurs, la part de chauffeurs avec une deuxième langue (valeur différente de \"no\" exactement), et la part de courses au statut \"Success\" exactement, sur les 4 morceaux de rides réunis."
HINTS = ["Les courses sont coupées en 4 DataFrames : réunis-les d'abord avec unionByName, sinon tu ne comptes qu'un quart des courses.",
         "« Exactement » veut dire sans lower ni trim : \"No\" n'est pas \"no\", \"success\" n'est pas \"Success\". Un ratio = F.sum(F.when(condition, 1).otherwise(0)) / F.count(\"*\")."]
DESC = """
<p>A taxi company stores its drivers in <code>drivers_df</code> (<code>driver_id</code> int, <code>age</code> int, <code>second_language</code> string, <code>rating</code> double). Its rides are too large for one file, so they arrive split into four DataFrames <code>rides_1_df</code>, <code>rides_2_df</code>, <code>rides_3_df</code> and <code>rides_4_df</code>, all with the columns <code>ride_id</code> int, <code>driver_id</code> int and <code>status</code> string. Together, the four parts form the full ride history.</p>
<p>Return a DataFrame with exactly one row and these columns, in this order:</p>
<ul><li><code>average_rating</code> (double): the mean of <code>rating</code> over all drivers;</li>
<li><code>second_language_ratio</code> (double): the number of drivers whose <code>second_language</code> is not exactly the string <code>"no"</code>, divided by the number of drivers;</li>
<li><code>successful_ride_ratio</code> (double): the number of rides (over the four parts) whose <code>status</code> is exactly <code>"Success"</code>, divided by the total number of rides.</li></ul>
<p>Values are compared exactly as stored: no trimming, no case change. There is at least one driver and at least one ride.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
IO = [("input", "DataFrame drivers_df, rides_1_df, rides_2_df, rides_3_df, rides_4_df")]
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F


def solve(spark: SparkSession, drivers_df: DataFrame, rides_1_df: DataFrame, rides_2_df: DataFrame,
          rides_3_df: DataFrame, rides_4_df: DataFrame) -> DataFrame:
    # write your code here
    return drivers_df
"""
SOLUTION = """
from pyspark.sql import functions as F


def solve(spark, drivers_df, rides_1_df, rides_2_df, rides_3_df, rides_4_df):
    rides = rides_1_df.unionByName(rides_2_df).unionByName(rides_3_df).unionByName(rides_4_df)
    d = drivers_df.agg(
        F.avg("rating").alias("average_rating"),
        (F.sum(F.when(F.col("second_language") != "no", 1).otherwise(0)) / F.count("*")).alias("second_language_ratio"))
    r = rides.agg((F.sum(F.when(F.col("status") == "Success", 1).otherwise(0)) / F.count("*")).alias("successful_ride_ratio"))
    return d.crossJoin(r)
"""
_M = """
from pyspark.sql import functions as F
def solve(spark, drivers_df, rides_1_df, rides_2_df, rides_3_df, rides_4_df):
    rides = {RIDES}
    d = drivers_df.agg(F.avg("rating").alias("average_rating"),
        (F.sum(F.when({LANG}, 1).otherwise(0)) / F.count("*")).alias("second_language_ratio"))
    r = rides.agg((F.sum(F.when({OK}, 1).otherwise(0)) / F.count("*")).alias("successful_ride_ratio"))
    return d.crossJoin(r)
"""
_ALL = "rides_1_df.unionByName(rides_2_df).unionByName(rides_3_df).unionByName(rides_4_df)"
_L = 'F.col("second_language") != "no"'
_S = 'F.col("status") == "Success"'
MUTANTS = [
    _M.replace("{RIDES}", "rides_1_df").replace("{LANG}", _L).replace("{OK}", _S),
    _M.replace("{RIDES}", _ALL).replace("{LANG}", 'F.lower(F.col("second_language")) != "no"').replace("{OK}", _S),
    _M.replace("{RIDES}", _ALL).replace("{LANG}", _L).replace("{OK}", 'F.lower(F.col("status")) == "success"'),
    _M.replace("{RIDES}", _ALL + ".dropDuplicates(['driver_id', 'status'])").replace("{LANG}", _L).replace("{OK}", _S),
]
SD = "driver_id int, age int, second_language string, rating double"
SR = "ride_id int, driver_id int, status string"
STATUSES = ["Success", "Success", "Success", "Rejected by the driver", "Cancelled by the client", "success"]
LANGS = ["no", "no", "English", "French", "No", "Spanish"]


def _case(r, nd, nr):
    drivers = [[i, r.randint(21, 64), r.choice(LANGS), round(r.uniform(3.0, 5.0), 2)] for i in range(1, nd + 1)]
    rides = [[k, r.randint(1, nd), r.choice(STATUSES)] for k in range(1, nr + 1)]
    parts = [[], [], [], []]
    for x in rides:
        parts[r.randrange(4)].append(x)
    out = {"drivers_df": df(SD, drivers)}
    for i in range(4):
        out[f"rides_{i + 1}_df"] = df(SR, parts[i])
    return out


def tests():
    t = [{"drivers_df": df(SD, [[1, 34, "no", 4.5], [2, 41, "French", 4.0], [3, None, "No", 3.5], [4, 29, "English", 5.0]]),
          "rides_1_df": df(SR, [[10, 1, "Success"], [11, 2, "Rejected by the driver"]]),
          "rides_2_df": df(SR, [[12, 1, "Success"], [13, 3, "success"]]),
          "rides_3_df": df(SR, [[14, 4, "Success"]]),
          "rides_4_df": df(SR, [[15, 2, "Cancelled by the client"], [16, 4, "Success"], [17, 1, "Success"]])},
         {"drivers_df": df(SD, [[7, 50, "no", 4.25]]),
          "rides_1_df": df(SR, []), "rides_2_df": df(SR, [[1, 7, "Success"], [2, 7, "Success"]]),
          "rides_3_df": df(SR, []), "rides_4_df": df(SR, [[3, 7, " Success"]])}]
    r = rng(1905)
    for _ in range(5):
        t.append(_case(r, r.randint(1, 9), r.randint(1, 25)))
    return t
